from unittest.mock import patch

from app.services.embedding_service import EmbeddingService 

class EmbeddingServiceTests:
    def __init__(self):
        self.es = EmbeddingService()
        pass
    