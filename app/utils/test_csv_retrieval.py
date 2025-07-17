# test_faq_retrieval.py

import logging
from dotenv import load_dotenv
from app.services.chroma_service import ChromaService

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def query_faq(chroma: ChromaService, query: str, limit: int = 5):
    chroma.switch_collection("faq_csv")
    results = chroma.get_db().similarity_search_with_relevance_scores(query, k=limit)
    return results

if __name__ == "__main__":
    chroma = ChromaService()
    test_queries = [
        "Hvordan kan vi abonnere på kommende endringer hos dere i fremtiden?",
        "Hvordan søker jeg om støtte?",
        "Hvordan kontakter jeg kundeservice?",
    ]

    for q in test_queries:
        print(f"\n🔍 Query: {q}")
        matches = query_faq(chroma, q, limit=3)

        if not matches:
            print(" → Ingen treff")
            continue

        for doc, score in matches:
            ans = doc.metadata.get("answer", "<INGEN SVAR>")
            print(f" • [{score:.3f}] Q: {doc.page_content}")
            print(f"     A: {ans}")
