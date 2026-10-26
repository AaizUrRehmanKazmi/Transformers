"""Offline tests on a tiny randomly initialised Qwen2 (fp32, CPU): they check the decoding
logic (positions, cache reuse) independently of the real checkpoint."""
import pytest
import torch
from transformers import Qwen2Config, Qwen2ForCausalLM

from core.kv_cache import generate_cached, generate_uncached, kv_bytes_per_token


def tiny_model():
    torch.manual_seed(0)
    cfg = Qwen2Config(vocab_size=128, hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                      num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=512)
    return Qwen2ForCausalLM(cfg).eval()


@pytest.mark.parametrize("n_prompt,n_new", [(4, 8), (16, 32), (64, 16), (100, 40)])
def test_cached_matches_uncached(n_prompt, n_new):
    model = tiny_model()
    torch.manual_seed(1)
    ids = torch.randint(0, 128, (1, n_prompt))
    ref, _ = generate_uncached(model, ids, n_new)
    got, stats = generate_cached(model, ids, n_new)
    assert torch.equal(ref, got)
    assert stats["cache_len"] == n_prompt + n_new - 1   # last token is never fed back


def test_cache_growth_matches_formula():
    model = tiny_model()
    ids = torch.randint(0, 128, (1, 20))
    _, stats = generate_cached(model, ids, 10)
    assert stats["cache_bytes"] == kv_bytes_per_token(model.config, dtype_bytes=4) * stats["cache_len"]


def test_eos_stops_generation():
    model = tiny_model()
    ids = torch.randint(0, 128, (1, 8))
    full, _ = generate_cached(model, ids, 6)
    eos = int(full[0, 2])                                 # make the 3rd token an EOS
    short, _ = generate_cached(model, ids, 6, eos_ids=(eos,))
    ref, _ = generate_uncached(model, ids, 6, eos_ids=(eos,))
    assert short.shape[1] <= 3 and torch.equal(short, ref)
