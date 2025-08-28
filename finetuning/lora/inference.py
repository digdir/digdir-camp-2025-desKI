from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel, PeftConfig
import torch

# A simple way to test inference with a LoRA-finetuned model.
# Loads the model, sends a prompt, and prints the generated response.
# Make sure `lora_model_path` points to the correct trained model.

torch.set_float32_matmul_precision('high')

# === Konfigurasjon ===
lora_model_path = "/home/jovyan/digdir-camp-2025-desKI/finetuning/lora/google_gemma_3n_e4b"


# === Last inn tokenizer og modeller ===
peft_config = PeftConfig.from_pretrained(lora_model_path, local_files_only = True)

tokenizer = AutoTokenizer.from_pretrained(peft_config.base_model_name_or_path)

base_model = AutoModelForCausalLM.from_pretrained(
    peft_config.base_model_name_or_path,
    device_map = "cuda:0",
    #device_map="auto",
    torch_dtype=torch.bfloat16
)

model = PeftModel.from_pretrained(base_model, lora_model_path).to("cuda:0")
#model = PeftModel.from_pretrained(base_model, lora_model_path)
model = torch.compile(model)  
model.eval()


# === Prompt / spørsmål ===
question = "Det står at jeg ikke har rettigheter til å logge inn i selvbetjeningen, kan dere gi meg tilgang? \nSvar:"
#question = "eSignering: Vil ikke at fødselsnummer skal vise i signert dokument.\nSvar:"
#question = "eSignering: Hei, er det nødvendig at fødselsnummer vises i signert dokument?.\nSvar:"
#question = "ID-porten: Hei! Trenger bistand til å opprette ein ID-porten integrasjon.\nSvar:"
#question = "Selvbetjening: Jeg forsøker å logge meg inn på deres systemer som administrator for vårt selskap, AS Financiering, orgnr 911629283. Men jeg får melding om at jeg ikke har tilgang til selvbetjeningsløsningen. Er dette noe dere kan bistå meg med?.\nSvar:"
#question = "Maskinporten: Finner ikkje scopet eg treng når eg skal opprette Maskinporten\nSvar:"
#question = "Vil opprette ein ny SAML integrasjon. Kvar skal eg sende inn metadata? \nSvar:"
#question = "Hva er digidr? .\nsvar:"
#question = "Kan du hjelpe oss med eSignering? .\nsvar:" 
    

# === Tokenisering ===
inputs = tokenizer(question, return_tensors="pt").to(model.device)

# === Generering ===
with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=200,
        pad_token_id=tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.7,
        top_p=0.9,
        repetition_penalty=1.3,
    )

# === Dekoding ===
full_output = tokenizer.decode(output[0], skip_special_tokens=True)
generated_answer = full_output[len(question):].strip()

# === Print resultat ===
print("Svar:", generated_answer)
