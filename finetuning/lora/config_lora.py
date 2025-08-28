import torch

# === Configuration file for LoRA fine-tuning ===
#
# This file defines configurations for fine-tuning different language models using LoRA.
# Each class corresponds to a specific base model with its LoRA settings.
#
# To choose which model to fine-tune, uncomment the desired `config = ...` line at the bottom.
# Shared training parameters (e.g. learning rate, batch size, number of epochs, etc.)
# can be adjusted in the `BaseConfig` class or at the top of the file.
#
# Update `dataset_path` and output paths


r=8
alpha = 16
dropout_rate = 0.05

class BaseConfig:
    dataset_path = "/home/jovyan/digdir-camp-2025-desKI/finetuning/lora/halvpart_brukerstotte.csv" #endre
    #subset = "train[:0.1%]"  # redusert for test
    batch_size = 1
    grad_acc_steps = 4
    num_epochs = 10
    lr = 5e-5
    weight_decay = 0.01
    warmup_steps = 50
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_save_path = "./trained_model"
    tokenizer_save_path = "./trained_model"
    max_length = 384
    use_lora = True
    fp16 = True
    save_steps = 500
    use_8bit = True


class MistralConfig(BaseConfig):
    model_name = "mistralai/Mistral-7B-Instruct-v0.3"
    lora_config = {
        "r": r,
        "lora_alpha": alpha,
        "dropout": dropout_rate,
        "target_modules": ["q_proj", "v_proj"],
    }


class LLaMA3InstructConfig(BaseConfig):
    model_name = "meta-llama/Llama-3.1-8B-Instruct"
    lora_config = {
        "r": r,
        "lora_alpha": alpha,
        "dropout": dropout_rate,
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    }
    

class NousHermesMistralConfig(BaseConfig):
    model_name = "NousResearch/Nous-Hermes-2-Mistral-7B-DPO"
    lora_config = {
        "r": r,
        "lora_alpha": alpha,
        "dropout": dropout_rate,
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    }


class Gemma3nConfig(BaseConfig):
    model_name = "google/gemma-3n-E4B-it"
    lora_config = {
        "r": r,
        "lora_alpha": alpha,
        "dropout": dropout_rate,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    }

class Gemma1BInstructConfig(BaseConfig):
    model_name = "google/gemma-3-1b-it"
    lora_config = {
        "r": r,
        "lora_alpha": alpha,
        "dropout": dropout_rate,
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    }



# Velg én:
#config = MistralConfig()
#config = LLaMA3InstructConfig()
#config = NousHermesMistralConfig()
config = Gemma3nConfig()
#config = Gemma1BInstructConfig