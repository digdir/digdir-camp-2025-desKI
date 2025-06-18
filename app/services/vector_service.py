import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./chroma_data"
))

collection = client.get_or_create_collection(name="docs")

def search(embedding: list[float], k: int = 1):
    return collection.query(query_embeddings=[embedding], n_results=k)

def add_doc(doc_id: str, text: str, embedding: list[float]):
    collection.add(documents=[text], ids=[doc_id], embeddings=[embedding])

