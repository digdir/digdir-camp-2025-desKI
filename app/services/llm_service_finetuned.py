import requests
import os
from dotenv import load_dotenv
from app.utils.prompt_factory import PromptFactory  # legg til dette
from app.models.endpoint_enum import NamedEndpoint  # og dette

# Load environment variables
load_dotenv()
API_URL = os.getenv("FINETUNED_MODEL_API", "http://localhost:8001/generate")

def ask_model(user_query, context=""):
    
    prompt = f"{user_query}\n\n{context}"

    #prompt = PromptFactory.get_prompt(user_query, context, NamedEndpoint.CHATBOT)
    
    try:
        response = requests.post(API_URL, json={"prompt": prompt})
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[No response]"), data.get("sources", [])
    except Exception as e:
        return f"[Error: {e}]", []

if __name__ == "__main__":
    while True:
        user_input = input("\n🧠 Spør modellen (skriv 'exit' for å avslutte):\n> ")
        if user_input.strip().lower() in {"exit", "quit"}:
            break

        # Foreløpig tom kontekst – kan senere hente fra Chroma
        context = ""
        answer, sources = ask_model(user_input, context)

        print("\n🧠 Svar:\n", answer)
        if sources:
            print("\n📚 Kilder:")
            for src in sources:
                print("-", src)
