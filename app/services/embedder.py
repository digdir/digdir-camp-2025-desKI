from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_question(text: str) -> list[float]:
    """
    Tar inn en tekststreng og returnerer en embedding-vektor som liste.
    """
    return _model.encode(text).tolist()
