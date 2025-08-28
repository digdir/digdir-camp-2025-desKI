from config import MODEL_PATH_SERVICEDESK, BASE_MODEL_NAME, REPETITION_PENALTY, MAX_LENGTH, MAX_NEW_TOKENS, TEMPERATURE, TOP_P, DO_SAMPLE
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
import torch
from peft import PeftModel

# Generates a cleaned response from the servicedesk fine-tuned model.
# Loads the model and tokenizer, runs inference, and removes formatting artifacts from the output.


torch.set_float32_matmul_precision('high')


#loading tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH_SERVICEDESK, local_files_only=True)

model = AutoModelForCausalLM.from_pretrained(MODEL_PATH_SERVICEDESK,
                                             device_map="cuda:0",
                                             torch_dtype=torch.float16,
                                             local_files_only=True
                                            )



def response_finetuned_servicedesk(prompt: str) -> str:
    #load finetuned model servicedesk
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(model.device)
    
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=DO_SAMPLE,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            repetition_penalty = REPETITION_PENALTY
        )
        
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)

    if "Svar:" in full_output:
        response = full_output.split("Svar:")[-1]

    else: 
        response = full_output

     # === Rydd opp output ===
    response = response.strip()
    response = response.replace("\\n", " ").replace("\n", " ").replace('\\"', '"')
    response = re.sub(r'\s{2,}', ' ', response)
    return response
