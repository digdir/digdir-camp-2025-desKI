import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_URL = os.getenv("FINETUNED_MODEL_API", "http://localhost:8001/generate")

def ask_model(prompt):
    try:
        response = requests.post(API_URL, json={"prompt": prompt})
        response.raise_for_status()
        data = response.json()
        return data.get("response", "[No response]"), data.get("sources", [])
    except Exception as e:
        return f"[Error: {e}]", []

if __name__ == "__main__":
    while True:
        user_input = input("\nAsk the model (or type 'exit' to quit):\n> ")
        if user_input.strip().lower() in {"exit", "quit"}:
            break

        answer, sources = ask_model(user_input)

        print("\n🧠 Answer:\n", answer)
        if sources:
            print("\n📚 Sources:")
            for src in sources:
                print("-", src)
