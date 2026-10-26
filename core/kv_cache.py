"""Greedy decoding with an explicit KV cache, plus the uncached reference path.

Cached path
-----------
1. Prefill: one forward pass over the whole prompt, positions 0..n-1. This fills an
   (initially empty) DynamicCache with K/V for every layer. The causal mask is needed
   here because many query positions are processed at once.
2. Decode: each step feeds ONLY the newest token (shape [1, 1]). We pass
     position_ids   = [[cur]]   (the new token's absolute position; RoPE is applied to the
                                 new query/key using this position, so it must equal the
                                 number of tokens already in the cache)
     cache_position = [cur]     (the slot in the cache the new K/V is written to)
   The new K/V is appended to the cache, and the single query attends to all cached keys.
   No causal mask is needed for a single query token: every cached key is in its past.
3. The last generated token is never fed back, so after T new tokens the cache holds
   n + T - 1 positions.

Reference path: recompute the full sequence every step with use_cache=False.

Both use argmax (greedy), so outputs should match token for token. Small differences can
only come from numerics (different matmul shapes / fp16 rounding flipping a near-tie).
Batch size 1 only: no padding, so no attention-mask handling is required.
"""
import time

import torch
from transformers import DynamicCache


def _sync(device):
    if str(device).startswith("cuda"):
        torch.cuda.synchronize()


def _positions(start, length, device):
    p = torch.arange(start, start + length, device=device)
    return p.unsqueeze(0), p


def _is_eos(token, eos_ids):
    return bool(eos_ids) and int(token) in eos_ids


@torch.no_grad()
def generate_uncached(model, input_ids, max_new_tokens, eos_ids=()):
    """Reference: full forward over the growing sequence at every step (no cache)."""
    assert input_ids.shape[0] == 1, "batch size 1 only"
    dev = input_ids.device
    ids, new = input_ids, []
    _sync(dev); t0 = time.perf_counter(); t_first = None
    for step in range(max_new_tokens):
        logits = model(input_ids=ids, use_cache=False).logits[:, -1]
        nxt = logits.argmax(-1, keepdim=True)
        if step == 0:
            _sync(dev); t_first = time.perf_counter()
        new.append(nxt)
        ids = torch.cat([ids, nxt], dim=1)
        if _is_eos(nxt, eos_ids):
            break
    _sync(dev); t_end = time.perf_counter()
    return torch.cat(new, dim=1), {
        "prefill_s": t_first - t0, "decode_s": t_end - t_first, "new_tokens": len(new)}


@torch.no_grad()
def generate_cached(model, input_ids, max_new_tokens, eos_ids=()):
    """Greedy decoding that explicitly creates, fills and reuses a DynamicCache."""
    assert input_ids.shape[0] == 1, "batch size 1 only"
    dev = input_ids.device
    n = input_ids.shape[1]
    cache = DynamicCache()

    _sync(dev); t0 = time.perf_counter()
    pos_ids, cache_pos = _positions(0, n, dev)
    out = model(input_ids=input_ids, past_key_values=cache, use_cache=True,
                position_ids=pos_ids, cache_position=cache_pos)        # prefill
    nxt = out.logits[:, -1].argmax(-1, keepdim=True)
    _sync(dev); t1 = time.perf_counter()

    new, cur = [nxt], n                                                  # cur = tokens in cache
    for _ in range(max_new_tokens - 1):
        if _is_eos(nxt, eos_ids):
            break
        pos_ids, cache_pos = _positions(cur, 1, dev)
        out = model(input_ids=nxt, past_key_values=cache, use_cache=True,
                    position_ids=pos_ids, cache_position=cache_pos)    # one-token decode step
        cur += 1
        nxt = out.logits[:, -1].argmax(-1, keepdim=True)
        new.append(nxt)
    _sync(dev); t2 = time.perf_counter()
    return torch.cat(new, dim=1), {
        "prefill_s": t1 - t0, "decode_s": t2 - t1, "new_tokens": len(new),
        "cache_len": cache.get_seq_length(), "cache_bytes": cache_nbytes(cache)}


def cache_nbytes(cache):
    """Actual bytes held by the K/V tensors of a cache (works across transformers versions)."""
    tensors = []
    layers = getattr(cache, "layers", None)
    if layers is not None:
        for layer in layers:
            tensors += [getattr(layer, "keys", None), getattr(layer, "values", None)]
    else:
        tensors = list(cache.key_cache) + list(cache.value_cache)
    return sum(t.numel() * t.element_size() for t in tensors if t is not None and t.numel())


def kv_bytes_per_token(config, dtype_bytes=2):
    """Analytical cache growth: 2 (K and V) x layers x kv_heads x head_dim x bytes, per token."""
    head_dim = getattr(config, "head_dim", None) or config.hidden_size // config.num_attention_heads
    return 2 * config.num_hidden_layers * config.num_key_value_heads * head_dim * dtype_bytes
