from sentence_transformers import SentenceTransformer

_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Generates an embedding vector from the input text
def embed_question(text: str) -> list[float]:
    return _model.encode(text).tolist()
