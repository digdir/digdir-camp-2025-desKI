import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

# Stier
DATA_PATH = r"_docs"
CHROMA_PATH = r"app/db/chroma_db"

# 1. Definer embedderen
embedding_model = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-base"
)

# 2. Finn alle .txt-filer rekursivt
txt_files = []
for root, dirs, files in os.walk(DATA_PATH):
    for file in files:
        if file.endswith(".txt"):
            txt_files.append(os.path.join(root, file))

print(f" Fant {len(txt_files)} .txt-filer i '{DATA_PATH}'")

# 3. Last inn og legg til metadata
documents = []
for idx, filepath in enumerate(txt_files, start=1):
    print(f"🔄 Leser fil {idx} av {len(txt_files)}: {os.path.relpath(filepath, DATA_PATH)}")
    loader = TextLoader(filepath, encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        relative_path = os.path.relpath(filepath, DATA_PATH)
        doc.metadata["source"] = relative_path
    documents.extend(docs)

print(f" Ferdig med innlasting av {len(documents)} dokumentobjekter.")

# 4. Del opp i tekstbiter
print(" Deler opp i tekstbiter...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = text_splitter.split_documents(documents)

# 5. Lagre til ChromaDB med embedder
print(f" Lagrer {len(chunks)} tekstbiter til vektorbasen...")
vectordb = Chroma.from_documents(
    documents=chunks,
    embedding=embedding_model,
    persist_directory=CHROMA_PATH,
    collection_name="dig_docs"
)

vectordb.persist()
print(f" Alt ferdig! Lagt til {len(chunks)} biter fra {len(txt_files)} filer.")