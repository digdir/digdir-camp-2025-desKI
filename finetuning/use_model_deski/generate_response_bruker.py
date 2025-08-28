import re

import torch
from peft import PeftModel
from config import (
    TOP_P,
    DO_SAMPLE,
    MAX_LENGTH,
    TEMPERATURE,
    MAX_NEW_TOKENS,
    BASE_MODEL_NAME,
    REPETITION_PENALTY,
    MODEL_PATH_BRUKERSTOTTE,
)
from transformers import AutoTokenizer, AutoModelForCausalLM

# Loads a base model and LoRA adapter for the brukerstøtte fine-tuned model.
# Generates a cleaned response based on input prompt.


torch.set_float32_matmul_precision('high')

# === Last tokenizer og base model ===
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_NAME, local_files_only=True)

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_NAME,
    device_map="cuda:1",
    torch_dtype=torch.float16,
    trust_remote_code=True,
    local_files_only=True,
)


# === Last LoRA-adapter ===
model = PeftModel.from_pretrained(
    base_model,
    MODEL_PATH_BRUKERSTOTTE,
    device_map="cuda:1",
    torch_dtype=torch.float16,
    local_files_only=True,
)


def response_finetuned_brukerstotte(prompt: str) -> str:
    device = torch.device("cuda:1")
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(device)

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repetition_penalty=REPETITION_PENALTY
        )

    full_output = tokenizer.decode(output[0], skip_special_tokens=True)

    if "Svar:" in full_output:
        response = full_output.split("Svar:")[-1].strip()
    else: 
        response = full_output.strip()

    # Rydd opp
    response = response.replace("\\n", " ").replace("\n", " ").replace('\\"', '"')
    response = re.sub(r'\s{2,}', ' ', response)

    if not response:
        response = "Jeg klarte ikke å gi noe svar basert på dokumentasjonen."

    return response

'''

# USE this version to use the BASE MODEL ONLY

def response_finetuned_brukerstotte(prompt: str) -> str:
    device = torch.device("cuda:1")
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(device)

    with torch.no_grad():
        output = base_model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repetition_penalty=REPETITION_PENALTY
        )

    full_output = tokenizer.decode(output[0], skip_special_tokens=True)

    if "Svar:" in full_output:
        response = full_output.split("Svar:")[-1].strip()
    else: 
        response = full_output.strip()

    # Rydd opp
    response = response.replace("\\n", " ").replace("\n", " ").replace('\\"', '"')
    response = re.sub(r'\s{2,}', ' ', response)

    if not response:
        response = "Jeg klarte ikke å gi noe svar basert på dokumentasjonen."

    return response

'''