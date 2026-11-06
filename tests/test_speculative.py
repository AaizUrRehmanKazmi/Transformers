"""Tiny random fp32 CPU models: speculative output must equal plain greedy target decoding,
for drafts that never agree, always agree, and agree sometimes (all rejection/accept paths)."""
import copy

import pytest
import torch
from transformers import Qwen2Config, Qwen2ForCausalLM

from core.kv_cache import generate_uncached
from core.speculative import generate_speculative


def make(layers, seed):
    torch.manual_seed(seed)
    cfg = Qwen2Config(vocab_size=128, hidden_size=64, intermediate_size=128, num_hidden_layers=layers,
                      num_attention_heads=4, num_key_value_heads=2, max_position_embeddings=512)
    return Qwen2ForCausalLM(cfg).eval()


@pytest.fixture(scope="module")
def models():
    target = make(2, 0)
    noisy = copy.deepcopy(target)
    torch.manual_seed(5)
    with torch.no_grad():
        for p in noisy.parameters():
            p.add_(torch.randn_like(p) * 0.01)
    return target, {"random": make(1, 1), "identical": copy.deepcopy(target), "noisy": noisy}


@pytest.mark.parametrize("kind", ["random", "identical", "noisy"])
@pytest.mark.parametrize("k", [1, 2, 4, 6])
@pytest.mark.parametrize("n_new", [1, 2, 7, 25])
def test_equals_plain_greedy(models, kind, k, n_new):
    target, drafts = models
    torch.manual_seed(3)
    ids = torch.randint(0, 128, (1, 10))
    ref, _ = generate_uncached(target, ids, n_new)
    got, st = generate_speculative(target, drafts[kind], ids, n_new, k=k)
    assert torch.equal(ref, got)
    assert st["accepted"] <= st["proposed"]


def test_identical_draft_accepts_everything(models):
    target, drafts = models
    ids = torch.randint(0, 128, (1, 10))
    _, st = generate_speculative(target, drafts["identical"], ids, 30, k=4)
    assert st["acceptance_rate"] == 1.0


def test_random_draft_is_mostly_rejected_but_still_correct(models):
    target, drafts = models
    ids = torch.randint(0, 128, (1, 10))
    ref, _ = generate_uncached(target, ids, 30)
    got, st = generate_speculative(target, drafts["random"], ids, 30, k=4)
    assert torch.equal(ref, got) and st["acceptance_rate"] < 0.5


def test_caches_stay_in_sync_with_committed_tokens(models):
    target, drafts = models
    ids = torch.randint(0, 128, (1, 10))
    got, st = generate_speculative(target, drafts["noisy"], ids, 20, k=3)
    # after finishing, the target cache holds prompt + all committed tokens but the last one
    assert st["target_cache_len"] <= 10 + got.shape[1]


def test_eos_stops_like_plain_greedy(models):
    target, drafts = models
    torch.manual_seed(4)
    ids = torch.randint(0, 128, (1, 10))
    full, _ = generate_uncached(target, ids, 20)
    eos = int(full[0, 6])
    ref, _ = generate_uncached(target, ids, 20, eos_ids=(eos,))
    for kind in ("random", "identical", "noisy"):
        got, _ = generate_speculative(target, drafts[kind], ids, 20, k=4, eos_ids=(eos,))
        assert torch.equal(ref, got)
