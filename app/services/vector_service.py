import chromadb
from chromadb.config import Settings

# Create Chroma client with DuckDB storage in a local directory
client = chromadb.Client(
    Settings(chroma_db_impl='duckdb+parquet', persist_directory='./chroma_data')
)

# Get or create a collection named 'docs'
collection = client.get_or_create_collection(name='docs')

# Search the collection for the most similar embeddings
def search(embedding: list[float], k: int = 1):
    return collection.query(query_embeddings=[embedding], n_results=k)

# Add a document with its embedding to the collection
def add_doc(doc_id: str, text: str, embedding: list[float]):
    collection.add(documents=[text], ids=[doc_id], embeddings=[embedding])
