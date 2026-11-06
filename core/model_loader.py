"""Single place that loads the target model (+ LoRA adapter), draft model and tokenizer."""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

TARGET_ID = "Qwen/Qwen2.5-1.5B-Instruct"
DRAFT_ID = "Qwen/Qwen2.5-0.5B-Instruct"
ADAPTER_REPO = "AK302/trialgpt-qwen1.5b-lora"   # Hugging Face Hub repo holding the adapters
ADAPTER_SUBFOLDER = "lora_r16_bal/epoch3"        # frozen final checkpoint

_DTYPES = {"float16": torch.float16, "float32": torch.float32, "bfloat16": torch.bfloat16}


def default_device():
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_tokenizer(model_id=TARGET_ID):
    return AutoTokenizer.from_pretrained(model_id)


def load_model(model_id=TARGET_ID, adapter=ADAPTER_REPO, subfolder=ADAPTER_SUBFOLDER,
               dtype="float16", device=None, merge=True):
    """Load a causal LM. If `adapter` is given (Hub id or local dir; use subfolder=None for a
    local adapter dir) the LoRA weights are applied and, with merge=True, folded into the base
    weights so the result is a plain model (no PEFT wrapper) for the custom decoders."""
    device = device or default_device()
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=_DTYPES[dtype]).to(device)
    if adapter:
        from peft import PeftModel
        kwargs = {"subfolder": subfolder} if subfolder else {}
        model = PeftModel.from_pretrained(model, adapter, **kwargs)
        if merge:
            model = model.merge_and_unload()
    return model.eval()
