from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List

# Loads a LoRA fine-tuned model and connects to a ChromaDB vector database.
# Retrieves relevant document chunks based on a user query, builds a prompt, and generates an answer.
# Can be run as a simple CLI chatbot to test the inference.


# === Modell og tokenizer ===
MODEL_PATH = "/home/jovyan/digdir-camp-2025-desKI/finetuning/lora/google_gemma_3_1b_it_medselvlagde"
BASE_MODEL = "google/gemma-3-1b-it"
MAX_LENGTH = 5000
MAX_NEW_TOKENS = 1024

print("Laster LoRA-finetunet modell...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_PATH, device_map="cuda:0", torch_dtype=torch.float16, local_files_only=True)



class ChromaCompatibleEmbeddingFunction:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.embed_documents(input)



# === ChromaDB-oppsett ===
CHROMA_PATH = "800-150_db"
embedding_model = ChromaCompatibleEmbeddingFunction()
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(name="dig_docs", embedding_function=embedding_model)

# Debug: Sjekk om databasen faktisk har dokumenter
def sjekk_database():
    try:
        stats = collection.count()
        print(f"\n ChromaDB inneholder {stats} dokument(er) i samlingen 'dig_docs'.\n")
    except Exception as e:
        print(f" Feil ved tilgang til databasen: {e}")


def hent_kontekst(user_query, n_results=5):
    #query_embedding = embedding_model.embed_query(user_query)
    query_embedding = embedding_model([user_query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    texts = results["documents"][0]
    print("\n🔎 Dokument-chunks hentet fra ChromaDB:\n")
    for i, t in enumerate(texts):
        print(f"--- Chunk {i+1} ---\n{t[:500]}...\n")

    texts = results["documents"][0]
    metadatas = results["metadatas"][0]

    combined_chunks = []
    used_sources = set()

    for text, meta in zip(texts, metadatas):
        source = meta.get("source", "ukjent fil").replace("\\", "/")
        page = meta.get("page", "ukjent side")
        used_sources.add(f"{source}, side {page}")
        combined = f"[Kilde: {source}, side {page}]\n{text}"
        combined_chunks.append(combined)


    return "\n\n".join(combined_chunks), used_sources

def bygg_prompt(context, query):
    return f"""

You are a helpful DigDir assistant. You answer questions based on the provided documentation, prioritise answers from database.
Respond in Norwegian if the question is in Norwegian, and in English if the question is in English.
If you don't know the answer, reply: “I am not sure, please contact servicedesk@digdir.no” or "Jeg er usikker, kontakt servicedesk@digdir.no"
Answer concisely, but include relevant details from the sources. Do not guess or add information not found in the documentation.
Use your own words, but base your answer on the documentation.

--- Dokumentasjon ---
{context}
----------------------

Spørsmål: {query}
Svar:"""

def svar_med_lora(prompt):
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=MAX_LENGTH).to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=True,
            temperature=0.5,
            top_p=0.9,
            repetition_penalty = 1.3
        )
    full_output = tokenizer.decode(output[0], skip_special_tokens=True)
    # Fjern prompten og behold bare modellens svar
    if "Svar:" in full_output:
        return full_output.split("Svar:")[-1].strip()
    else:
        return full_output.strip()


# === CLI-bruk ===
if __name__ == "__main__":
    sjekk_database()
    while True:
        query = input("\nHva trenger du hjelp til av DigDir?\n> ")
        context, kilder = hent_kontekst(query)
        prompt = bygg_prompt(context, query)
        svar = svar_med_lora(prompt)

        print("\n\n Svar:\n")
        print(svar)

        print("\n\n  Brukte kilder:\n")
        for kilde in sorted(kilder):
            print("-", kilde)
