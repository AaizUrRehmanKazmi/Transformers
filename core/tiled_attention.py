"""Scaled dot-product attention: a plain reference and a tiled online-softmax version.

Shapes: q [B, H, Tq, D], k and v [B, H, Tk, D] (grouped-query models expand K/V heads first).

Causal convention (bottom-right aligned, as used with a KV cache): query i sits at absolute
position i + (Tk - Tq) and may attend to keys j <= i + (Tk - Tq). With Tq == Tk this is the
usual lower-triangular mask; with Tq == 1 (a decode step) the query sees every cached key.
This differs from F.scaled_dot_product_attention(is_causal=True), which aligns top-left when
Tq != Tk, so sdpa_attention() builds an explicit mask in that case.

Tiled / online softmax (the FlashAttention idea, in plain PyTorch):
  For each block of queries we stream over blocks of keys keeping, per query row,
     m   running maximum of the scores seen so far
     l   running sum of exp(score - m)
     acc running sum of exp(score - m) * v
  When a new tile has a larger maximum m_new, everything accumulated so far is rescaled by
  alpha = exp(m_old - m_new). At the end the output is acc / l, which equals the full softmax
  but never materialises the [Tq, Tk] score matrix; only a [block_q, block_k] tile exists.
  Tiles lying entirely in the causal future are skipped.
All statistics are kept in float32 regardless of input dtype.
"""
import torch
import torch.nn.functional as F


def _causal_mask(tq, tk, device):
    """Bool [tq, tk], True where attention is allowed (bottom-right aligned)."""
    return torch.ones(tq, tk, dtype=torch.bool, device=device).tril(diagonal=tk - tq)


def reference_attention(q, k, v, causal=True):
    """Straightforward softmax(QK^T / sqrt(d)) V with a numerically stable softmax."""
    tq, tk = q.shape[-2], k.shape[-2]
    if causal:
        assert tk >= tq, "causal attention needs Tk >= Tq"
    scale = q.shape[-1] ** -0.5
    s = (q.float() @ k.float().transpose(-1, -2)) * scale
    if causal:
        s = s.masked_fill(~_causal_mask(tq, tk, q.device), float("-inf"))
    s = s - s.amax(dim=-1, keepdim=True)          # subtract row max: exp() cannot overflow
    p = torch.exp(s)
    p = p / p.sum(dim=-1, keepdim=True)
    return (p @ v.float()).to(q.dtype)


def tiled_attention(q, k, v, causal=True, block_q=64, block_k=64):
    """Blocked attention with online softmax; matches reference_attention."""
    B, H, tq, D = q.shape
    tk = k.shape[-2]
    assert k.shape == v.shape and k.shape[:2] == (B, H) and k.shape[-1] == D
    if causal:
        assert tk >= tq, "causal attention needs Tk >= Tq"
    scale = D ** -0.5
    offset = tk - tq
    dev = q.device
    out = torch.empty_like(q)

    for qs in range(0, tq, block_q):
        qe = min(qs + block_q, tq)
        qb = q[:, :, qs:qe].float()
        bq = qe - qs
        m = torch.full((B, H, bq), float("-inf"), device=dev, dtype=torch.float32)
        l = torch.zeros((B, H, bq), device=dev, dtype=torch.float32)
        acc = torch.zeros((B, H, bq, D), device=dev, dtype=torch.float32)
        q_pos = torch.arange(qs, qe, device=dev) + offset
        last_visible_key = (qe - 1) + offset if causal else tk - 1

        for ks in range(0, tk, block_k):
            if ks > last_visible_key:             # whole tile is in the future of every query
                break
            ke = min(ks + block_k, tk)
            s = (qb @ k[:, :, ks:ke].float().transpose(-1, -2)) * scale   # [B,H,bq,bk]
            if causal:
                allowed = torch.arange(ks, ke, device=dev)[None, :] <= q_pos[:, None]
                s = s.masked_fill(~allowed, float("-inf"))
            m_new = torch.maximum(m, s.amax(dim=-1))
            # If a row has seen only masked entries so far, m_new is -inf; use 0 as the
            # reference point so we never compute (-inf) - (-inf) = nan.
            m_ref = torch.where(torch.isinf(m_new), torch.zeros_like(m_new), m_new)
            p = torch.exp(s - m_ref[..., None])
            alpha = torch.exp(m - m_ref)          # rescales what was accumulated so far
            l = l * alpha + p.sum(dim=-1)
            acc = acc * alpha[..., None] + p @ v[:, :, ks:ke].float()
            m = m_new

        out[:, :, qs:qe] = (acc / l[..., None]).to(q.dtype)
    return out


def sdpa_attention(q, k, v, causal=True):
    """PyTorch's fused/optimised backend, with the same causal convention as above."""
    tq, tk = q.shape[-2], k.shape[-2]
    if not causal:
        return F.scaled_dot_product_attention(q, k, v)
    if tq == tk:
        return F.scaled_dot_product_attention(q, k, v, is_causal=True)
    return F.scaled_dot_product_attention(q, k, v, attn_mask=_causal_mask(tq, tk, q.device))
