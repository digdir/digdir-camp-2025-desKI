# === Vector db ====
CHROMA_PATH = 'app/db/chroma_db'
COLLECTION_NAME = 'dig_docs'
DATA_PATH = '_docs'

# ==== Azure ====
AZURE_ENDPOINT = 'https://digdircamp-resource.services.ai.azure.com/models'
# Example model, change to the one you want to use
AZURE_MODEL = 'Llama-4-Maverick-17B-128E-Instruct-FP8'

USE_AZURE = True

# ==== AIvar API ====:
FINETUNED_MODEL_API = 'https://finetunes.sandkasse.ai/generate'


# === Modellinnstillinger ===
MAX_LENGTH = 2048
MAX_NEW_TOKENS = 1024
TEMPERATURE = 0.7
TOP_P = 0.9
DO_SAMPLE = True
SIMILARITY_THRESHOLD = 0.75
