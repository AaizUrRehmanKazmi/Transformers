"""Greedy speculative decoding with explicit KV-cache management for target and draft.

Invariant at the start of every round (c = number of committed tokens - 1):
  * `last` is the most recently committed token and is in NEITHER cache yet;
  * target cache and draft cache both hold exactly c positions (prompt + committed tokens
    except `last`), i.e. positions 0..c-1.

One round:
  1. DRAFT   The draft model is fed `last`, then its own previous guess, k times in total, each a
             one-token step with explicit position_ids, giving proposals d1..dk.
             (draft cache grows to c + k: it holds last, d1..d_{k-1}; d_k was never fed.)
  2. VERIFY  The target runs ONE forward pass on [last, d1..dk] (k+1 tokens, positions c..c+k).
             logits[i] predicts the token after input i, so g_i = argmax logits[i] is what plain
             greedy decoding would emit after that prefix. g_0 judges d1, g_1 judges d2, ...
  3. ACCEPT  m = length of the longest prefix with d_j == g_{j-1}. Commit d1..dm and then g_m:
             g_m is the target's own token, a correction if m < k, a free bonus token if m == k.
             Every committed token is therefore exactly what greedy target decoding produces.
  4. SYNC    Target cache holds c + k + 1 positions; keep c + m + 1 (last, d1..dm) via crop().
             Draft cache: if m < k, crop to c + m + 1 as well. If m == k the draft never processed
             d_k, so feed it once to bring the draft cache to c + k + 1. Rejected tokens' K/V are
             thereby discarded from both caches. New `last` = g_m.

Output equals plain greedy target decoding mathematically. Numerically, verifying k+1 tokens in
one batched pass can differ from one-token steps by fp rounding (this matters in fp16 near ties).
Batch size 1 only.
"""
import time

import torch
from transformers import DynamicCache

from core.kv_cache import _is_eos, _positions, _sync


def tokenizers_compatible(tok_a, tok_b):
    """Draft and target must share a vocabulary so token ids mean the same thing."""
    return tok_a.get_vocab() == tok_b.get_vocab() and tok_a.eos_token == tok_b.eos_token


@torch.no_grad()
def generate_speculative(target, draft, input_ids, max_new_tokens, k=4, eos_ids=()):
    assert input_ids.shape[0] == 1 and k >= 1
    dev = input_ids.device
    n = input_ids.shape[1]
    t_cache, d_cache = DynamicCache(), DynamicCache()

    def fwd(model, cache, ids, start):
        pos_ids, cache_pos = _positions(start, ids.shape[1], dev)
        return model(input_ids=ids, past_key_values=cache, use_cache=True,
                     position_ids=pos_ids, cache_position=cache_pos)

    _sync(dev); t0 = time.perf_counter()
    last = fwd(target, t_cache, input_ids, 0).logits[:, -1].argmax(-1, keepdim=True)  # first token
    fwd(draft, d_cache, input_ids, 0)                                               # sync draft cache
    _sync(dev); t1 = time.perf_counter()

    out_tokens, generated, cur = [last], 1, n          # cur = positions in each cache
    done = _is_eos(last, eos_ids)
    rounds = proposed = accepted = 0
    hist = {}
    draft_s = verify_s = 0.0

    while generated < max_new_tokens and not done:
        k_eff = min(k, max_new_tokens - generated - 1)
        if k_eff == 0:                                  # only one token left: plain target step
            nxt = fwd(target, t_cache, last, cur).logits[:, -1].argmax(-1, keepdim=True)
            out_tokens.append(nxt); generated += 1
            break

        _sync(dev); a = time.perf_counter()
        props, tok_in = [], last
        for j in range(k_eff):                          # 1. draft k tokens, one step each
            tok_in = fwd(draft, d_cache, tok_in, cur + j).logits[:, -1].argmax(-1, keepdim=True)
            props.append(tok_in)
        draft_ids = torch.cat(props, dim=1)             # [1, k_eff]
        _sync(dev); b = time.perf_counter()

        verify_in = torch.cat([last, draft_ids], dim=1)  # 2. one target pass over k_eff + 1 tokens
        g = fwd(target, t_cache, verify_in, cur).logits.argmax(-1)           # [1, k_eff + 1]
        m = int(torch.cumprod((g[:, :k_eff] == draft_ids).int(), dim=1).sum())  # 3. accepted prefix
        _sync(dev); c = time.perf_counter()
        draft_s += b - a; verify_s += c - b

        new = torch.cat([draft_ids[:, :m], g[:, m:m + 1]], dim=1)            # m accepted + 1 target token
        rounds += 1; proposed += k_eff; accepted += m; hist[m] = hist.get(m, 0) + 1

        if eos_ids:                                     # stop at the first EOS, like plain greedy
            for idx, tk in enumerate(new[0].tolist()):
                if tk in eos_ids:
                    new, done = new[:, :idx + 1], True
                    break
        out_tokens.append(new); generated += new.shape[1]
        if done:
            break

        keep = cur + m + 1                              # 4. cache synchronisation
        t_cache.crop(keep)
        if m == k_eff:
            fwd(draft, d_cache, draft_ids[:, -1:], cur + k_eff)   # draft never saw d_k
        else:
            d_cache.crop(keep)
        cur, last = keep, new[:, -1:]

    _sync(dev); t2 = time.perf_counter()
    tokens = torch.cat(out_tokens, dim=1)
    return tokens, {
        "prefill_s": t1 - t0, "decode_s": t2 - t1, "new_tokens": tokens.shape[1],
        "rounds": rounds, "proposed": proposed, "accepted": accepted,
        "acceptance_rate": accepted / proposed if proposed else None,
        "tokens_per_round": (tokens.shape[1] - 1) / rounds if rounds else None,
        "accepted_hist": hist, "draft_s": draft_s, "verify_s": verify_s,
        "target_cache_len": t_cache.get_seq_length(), "draft_cache_len": d_cache.get_seq_length(),
    }
