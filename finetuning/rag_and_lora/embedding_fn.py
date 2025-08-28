from typing import List

from config_rag import EMBEDDING_MODEL_NAME
from langchain_community.embeddings import HuggingFaceEmbeddings


# === Embedding-klassen ===
class ChromaCompatibleEmbeddingFunction:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.model.embed_documents(input)

    def name(self):
        return EMBEDDING_MODEL_NAME
