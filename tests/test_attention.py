import pytest
import torch

from core.tiled_attention import reference_attention, sdpa_attention, tiled_attention

# (B, H, Tq, Tk, D, block_q, block_k)
SHAPES = [
    (1, 2, 64, 64, 16, 16, 16),      # square, blocks divide T
    (2, 4, 100, 100, 32, 32, 16),    # T not a multiple of the block sizes
    (1, 1, 33, 33, 8, 64, 64),       # blocks larger than T
    (1, 2, 1, 50, 16, 64, 64),       # single-query decode step against a cache
    (1, 2, 7, 50, 16, 4, 8),         # Tq < Tk (query offset), uneven blocks
    (2, 3, 129, 129, 64, 64, 32),    # more than two tiles each way
]


def rand_qkv(B, H, Tq, Tk, D, scale=1.0, dtype=torch.float32, seed=0):
    g = torch.Generator().manual_seed(seed)
    mk = lambda t: (torch.randn(B, H, t, D, generator=g) * scale).to(dtype)  # noqa: E731
    return mk(Tq), mk(Tk), mk(Tk)


@pytest.mark.parametrize("causal", [True, False])
@pytest.mark.parametrize("B,H,Tq,Tk,D,bq,bk", SHAPES)
def test_tiled_matches_reference(B, H, Tq, Tk, D, bq, bk, causal):
    q, k, v = rand_qkv(B, H, Tq, Tk, D)
    ref = reference_attention(q, k, v, causal)
    out = tiled_attention(q, k, v, causal, block_q=bq, block_k=bk)
    assert (out - ref).abs().max().item() < 1e-5


@pytest.mark.parametrize("causal", [True, False])
@pytest.mark.parametrize("B,H,Tq,Tk,D,bq,bk", SHAPES)
def test_reference_matches_pytorch_sdpa(B, H, Tq, Tk, D, bq, bk, causal):
    q, k, v = rand_qkv(B, H, Tq, Tk, D)
    err = (reference_attention(q, k, v, causal) - sdpa_attention(q, k, v, causal)).abs().max().item()
    assert err < 1e-5


def test_large_logits_stay_finite_and_correct():
    # Scores reach several hundred: a softmax without max-subtraction would overflow exp().
    q, k, v = rand_qkv(1, 2, 80, 80, 32, scale=10.0)
    ref = reference_attention(q, k, v, True)
    out = tiled_attention(q, k, v, True, block_q=16, block_k=16)
    assert torch.isfinite(out).all() and torch.isfinite(ref).all()
    assert (out - ref).abs().max().item() < 1e-4


def test_causality_future_tokens_do_not_leak():
    q, k, v = rand_qkv(1, 2, 40, 40, 16)
    base = tiled_attention(q, k, v, True, 16, 16)
    k2, v2 = k.clone(), v.clone()
    k2[:, :, 30:], v2[:, :, 30:] = torch.randn_like(k2[:, :, 30:]), torch.randn_like(v2[:, :, 30:])
    changed = tiled_attention(q, k2, v2, True, 16, 16)
    assert torch.allclose(base[:, :, :30], changed[:, :, :30], atol=1e-6)   # earlier rows unaffected


def test_fp16_inputs_close_to_fp32_reference():
    q, k, v = rand_qkv(1, 2, 64, 64, 32, dtype=torch.float16)
    ref = reference_attention(q.float(), k.float(), v.float(), True)
    out = tiled_attention(q, k, v, True, 16, 16).float()
    assert (out - ref).abs().max().item() < 5e-3     # output rounding to fp16 only


def test_causal_requires_enough_keys():
    q, k, v = rand_qkv(1, 1, 8, 4, 8)
    with pytest.raises(AssertionError):
        tiled_attention(q, k, v, True)
