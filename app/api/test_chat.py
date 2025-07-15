from app.services.query_service import QueryService
from app.models.endpoint_enum import NamedEndpoint

if __name__ == "__main__":
    print("🧠 Starter terminal-chat med modellen. Skriv 'exit' for å avslutte.\n")

    qs = QueryService()  # Bruker .env-konfig automatisk

    # 🔍 Sjekk om ChromaDB er koblet til og inneholder dokumenter
    try:
        chroma_collection = qs.chroma_service.db._collection
        num_docs = chroma_collection.count()
        if num_docs == 0:
            print("⚠️  Vektordatabasen er tom! Ingen dokumenter funnet i ChromaDB.\n")
        else:
            print(f"✅  Vektordatabasen er klar. Antall dokumenter: {num_docs}\n")
    except Exception as e:
        print(f"❌  Klarte ikke å koble til ChromaDB: {e}\n")

    while True:
        user_input = input("Du: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        response = qs.run_query(user_input, named_endpoint=NamedEndpoint.CHATBOT)
        print("\n🔁 Modellens svar:\n", response, "\n")
