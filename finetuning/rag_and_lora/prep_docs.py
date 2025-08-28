import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from embedding_fn import ChromaCompatibleEmbeddingFunction

# === Importer konfig fra config.py ===
from config import DATAFOLDER, CHROMA_PATH, COLLECTION_NAME, EMBEDDING_MODEL_NAME


# === Initialiser ChromaDB og tekstsplitter ===
embedding_model = ChromaCompatibleEmbeddingFunction()
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME, embedding_function=embedding_model)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=850, chunk_overlap=150)

# === Finn og chunk tekstfiler ===
docs = []
metadatas = []

for root, _, files in os.walk(DATAFOLDER):
    for file in files:
        if file.endswith(".txt"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            chunks = text_splitter.split_text(content)
            for i, chunk in enumerate(chunks):
                docs.append(chunk)
                metadatas.append({
                    "source": path.replace(DATAFOLDER, "_docs/").replace("\\", "/"),
                    "page": i + 1
                })

# === Legg til i databasen ===
print(f"\n📦 Legger til {len(docs)} chunks i ChromaDB...\n")
collection.add(
    documents=docs,
    metadatas=metadatas,
    ids=[f"id_{i}" for i in range(len(docs))]
)
print("✅ Ferdig!")



