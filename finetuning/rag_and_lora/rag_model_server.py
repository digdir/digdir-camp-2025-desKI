import sys

sys.path.append("/home/jovyan/digdir-camp-2025-desKI")  # Adjust if needed

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Loads a LoRA fine-tuned model and runs a simple chatbot.
# Fetches context, builds a prompt, and generates a response using the local model.


torch.set_float32_matmul_precision('high')

print("Loading LoRA fine-tuned model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_PATH,
    device_map="cuda:0",
    torch_dtype=torch.float16,
    local_files_only=True
)

def answer_with_lora(prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=TEMPERATURE,
            top_p=TOP_P
        )
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)
    return full_output.split("Answer:")[-1].strip() if "Answer:" in full_output else full_output.strip()

if __name__ == "__main__":
    while True:
        query = input("\nWhat do you need help with (Digdir)?\n> ")
        context, sources = fetch_context(query)
        prompt = build_prompt(context, query)
        answer = answer_with_lora(prompt)

        print("\n\n Answer:\n", answer)
        print("\n\n Used sources:\n", *[f"- {s}" for s in sorted(sources)], sep="\n")
