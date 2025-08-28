from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType
import torch

# Loads a language model and tokenizer from Hugging Face.
# Applies LoRA if enabled in the config.

def load_model_and_tokenizer(config):
    tokenizer = AutoTokenizer.from_pretrained(config.model_name)
    tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        config.model_name,
        attn_implementation="eager",
        torch_dtype=torch.float16
    )

    if config.use_lora:
        lora_cfg = LoraConfig(
            r=config.lora_config["r"],
            lora_alpha=config.lora_config["lora_alpha"],
            lora_dropout=config.lora_config["dropout"],
            bias="none",
            task_type=TaskType.CAUSAL_LM,
            target_modules=config.lora_config["target_modules"],
        )
        model = get_peft_model(model, lora_cfg)
        #model.to(config.device)

    return model, tokenizer