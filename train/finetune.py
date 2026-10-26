"""LoRA fine-tuning of a causal LM on the TrialGPT criterion split (train only).

    python train/finetune.py --name lora_r16 --epochs 3 [--hub-id user/repo]

Outputs go to train/runs/<name>/ : config.json, log.jsonl, curves.png,
epoch1/ epoch2/ ... (adapters) and best/ (lowest validation loss).
Loss is computed on the answer tokens only (prompt tokens are masked with -100).
The test split is never loaded here.
"""
import argparse
import json
import math
from collections import defaultdict
import os
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import torch  # noqa: E402
from peft import LoraConfig, get_peft_model  # noqa: E402
from transformers import AutoModelForCausalLM, AutoTokenizer, get_cosine_schedule_with_warmup  # noqa: E402

from data.build_prompts import encode_example, load_split  # noqa: E402

TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]


def collate(batch, pad_id):
    L = max(len(b["input_ids"]) for b in batch)
    ids = torch.full((len(batch), L), pad_id, dtype=torch.long)
    lab = torch.full((len(batch), L), -100, dtype=torch.long)
    att = torch.zeros((len(batch), L), dtype=torch.long)
    for i, b in enumerate(batch):
        n = len(b["input_ids"])
        ids[i, :n] = torch.tensor(b["input_ids"])
        lab[i, :n] = torch.tensor(b["labels"])
        att[i, :n] = 1
    return ids, att, lab


def batches(encs, bs, pad_id, shuffle, rng):
    order = list(range(len(encs)))
    if shuffle:
        rng.shuffle(order)
    for i in range(0, len(order), bs):
        yield collate([encs[j] for j in order[i:i + bs]], pad_id)


@torch.no_grad()
def eval_loss(model, encs, bs, pad_id):
    model.eval()
    total, count = 0.0, 0
    for ids, att, lab in batches(encs, bs, pad_id, False, None):
        ids, att, lab = ids.cuda(), att.cuda(), lab.cuda()
        with torch.autocast("cuda", dtype=torch.float16):
            loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
        n = int((lab[:, 1:] != -100).sum())
        total += loss.item() * n
        count += n
    model.train()
    return total / count


def push(folder, hub_id, subdir):
    try:
        from huggingface_hub import HfApi
        api = HfApi()
        api.create_repo(hub_id, exist_ok=True, private=True)
        api.upload_folder(folder_path=str(folder), repo_id=hub_id, path_in_repo=subdir)
        print(f"  uploaded {subdir} to {hub_id}")
    except Exception as e:  # never let an upload failure kill training
        print(f"  [warn] hub upload failed: {e}")


def plot(log_path, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    steps, losses, vsteps, vlosses = [], [], [], []
    for line in log_path.read_text().splitlines():
        r = json.loads(line)
        if "train_loss" in r:
            steps.append(r["step"]); losses.append(r["train_loss"])
        if "val_loss" in r:
            vsteps.append(r["step"]); vlosses.append(r["val_loss"])
    plt.figure(figsize=(6, 3.6))
    plt.plot(steps, losses, label="train loss (per optimizer step)", alpha=0.7)
    plt.plot(vsteps, vlosses, "o-", label="validation loss (per epoch)")
    plt.xlabel("optimizer step"); plt.ylabel("answer-token cross-entropy"); plt.legend(); plt.tight_layout()
    plt.savefig(out_png, dpi=200)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", default="Qwen/Qwen2.5-1.5B-Instruct")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--dropout", type=float, default=0.05)
    ap.add_argument("--warmup-frac", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--grad-ckpt", action="store_true", help="save memory if OOM")
    ap.add_argument("--oversample-min", type=int, default=0,
                    help="raise each (criterion_type, label) group to at least N training rows (0 = off)")
    ap.add_argument("--max-repeat", type=int, default=4,
                    help="cap on how many times a group may be multiplied by oversampling")
    ap.add_argument("--hub-id", default=None, help="e.g. username/trialgpt-qwen1.5b-lora")
    args = ap.parse_args()

    random.seed(args.seed); np.random.seed(args.seed); torch.manual_seed(args.seed)
    rng = random.Random(args.seed)
    out = ROOT / "train" / "runs" / args.name
    out.mkdir(parents=True, exist_ok=True)
    (out / "config.json").write_text(json.dumps(vars(args), indent=2))
    log_path = out / "log.jsonl"
    log_path.write_text("")

    tok = AutoTokenizer.from_pretrained(args.model)
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    train_rows = load_split("train")
    train_encs = [encode_example(tok, r, args.max_len) for r in train_rows]
    if args.oversample_min > 0:
        groups = defaultdict(list)
        for i, r in enumerate(train_rows):
            groups[(r["criterion_type"], r["expert_eligibility"])].append(i)
        extra = []
        for key, idx in sorted(groups.items()):
            target = min(max(len(idx), args.oversample_min), len(idx) * args.max_repeat)
            extra += [idx[j % len(idx)] for j in range(target - len(idx))]
            print(f"  oversample {key}: {len(idx)} -> {max(target, len(idx))}")
        train_encs += [train_encs[i] for i in extra]
        print(f"training rows after oversampling: {len(train_encs)}")
    val_encs = [encode_example(tok, r, args.max_len) for r in load_split("val")]
    print(f"train examples: {len(train_encs)}  val examples: {len(val_encs)}")

    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=torch.float16).cuda()
    model.config.use_cache = False
    if args.grad_ckpt:
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()
    model = get_peft_model(model, LoraConfig(r=args.rank, lora_alpha=args.alpha, lora_dropout=args.dropout,
                                             target_modules=TARGET_MODULES, task_type="CAUSAL_LM"))
    model.print_trainable_parameters()
    model.train()

    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=args.lr, weight_decay=0.01)
    micro_per_epoch = math.ceil(len(train_encs) / args.batch_size)
    steps_per_epoch = math.ceil(micro_per_epoch / args.grad_accum)
    total_steps = steps_per_epoch * args.epochs
    sched = get_cosine_schedule_with_warmup(opt, int(args.warmup_frac * total_steps), total_steps)
    scaler = torch.amp.GradScaler("cuda")

    base_val = eval_loss(model, val_encs, args.batch_size, pad_id)
    print(f"validation loss before training: {base_val:.4f}")
    with log_path.open("a") as f:
        f.write(json.dumps({"step": 0, "val_loss": base_val}) + "\n")

    step, best = 0, float("inf")
    t0 = time.time()
    for epoch in range(1, args.epochs + 1):
        micro, acc_loss = 0, 0.0
        for ids, att, lab in batches(train_encs, args.batch_size, pad_id, True, rng):
            ids, att, lab = ids.cuda(), att.cuda(), lab.cuda()
            with torch.autocast("cuda", dtype=torch.float16):
                loss = model(input_ids=ids, attention_mask=att, labels=lab).loss
            scaler.scale(loss / args.grad_accum).backward()
            acc_loss += loss.item()
            micro += 1
            if micro % args.grad_accum == 0 or micro == micro_per_epoch:
                scaler.unscale_(opt)
                torch.nn.utils.clip_grad_norm_(params, 1.0)
                scaler.step(opt); scaler.update(); opt.zero_grad(set_to_none=True); sched.step()
                step += 1
                n_in_step = args.grad_accum if micro % args.grad_accum == 0 else micro % args.grad_accum
                rec = {"step": step, "epoch": epoch, "train_loss": acc_loss / n_in_step,
                       "lr": sched.get_last_lr()[0]}
                acc_loss = 0.0
                with log_path.open("a") as f:
                    f.write(json.dumps(rec) + "\n")
                if step % 10 == 0:
                    print(f"epoch {epoch} step {step}/{total_steps} loss {rec['train_loss']:.4f}")
        vl = eval_loss(model, val_encs, args.batch_size, pad_id)
        print(f"== epoch {epoch}: val loss {vl:.4f}  ({time.time() - t0:.0f}s elapsed, "
              f"peak mem {torch.cuda.max_memory_allocated() / 2**30:.1f} GiB)")
        with log_path.open("a") as f:
            f.write(json.dumps({"step": step, "epoch": epoch, "val_loss": vl}) + "\n")
        ckpt = out / f"epoch{epoch}"
        model.save_pretrained(ckpt)
        if vl < best:
            best = vl
            model.save_pretrained(out / "best")
            (out / "best" / "info.json").write_text(json.dumps({"epoch": epoch, "val_loss": vl}))
        if args.hub_id:
            push(ckpt, args.hub_id, f"{args.name}/epoch{epoch}")

    plot(log_path, out / "curves.png")
    if args.hub_id:
        push(out / "best", args.hub_id, f"{args.name}/best")
    print(f"done. best val loss {best:.4f}. outputs in {out}")


if __name__ == "__main__":
    main()
