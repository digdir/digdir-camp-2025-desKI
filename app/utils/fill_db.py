"""
Script for ingesting .txt documents into ChromaDB using Digdir's custom embedding and vector store services.

Steps:
1. Loads all .txt files from the _docs directory.
2. Splits documents into manageable chunks using a text splitter.
3. Embeds and stores the chunks in ChromaDB using HuggingFace embeddings.

Dependencies:
- EmbeddingService (for generating embeddings)
- ChromaService (for storing/searching embeddings)

Run this script with `python -m app.utils.fill_db.py` after placing .txt files under the `_docs/` folder.
"""

import os

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

from app.config import DATA_PATH, CHROMA_PATH, COLLECTION_NAME
from app.services.chroma_service import ChromaService
from app.services.embedding_service import EmbeddingService


def load_txt_documents(data_path: str):
    """
    Recursively loads all .txt files from a given directory and attaches source metadata.

    Args:
        data_path (str): Path to the folder containing .txt files.

    Returns:
        list: A list of langchain Document objects with source metadata.
    """

    txt_files = []
    for root, _, files in os.walk(data_path):
        for file in files:
            if file.endswith('.txt'):
                txt_files.append(os.path.join(root, file))

    print(f" Fant {len(txt_files)} .txt-filer i '{data_path}'")

    documents = []
    for idx, filepath in enumerate(txt_files, start=1):
        print(
            f'🔄 Leser fil {idx} av {len(txt_files)}: {os.path.relpath(filepath, data_path)}'
        )
        loader = TextLoader(filepath, encoding='utf-8')
        docs = loader.load()
        for doc in docs:
            relative_path = os.path.relpath(filepath, data_path)
            doc.metadata['source'] = relative_path
        documents.extend(docs)

    print(f' Ferdig med innlasting av {len(documents)} dokumentobjekter.')
    return documents


def chunk_documents(documents: list):
    """
    Splits documents into smaller text chunks using recursive character splitting.

    Args:
        documents (list): A list of langchain Document objects.

    Returns:
        list: A list of split Document chunks.
    """

    print(' Deler opp i tekstbiter...')
    splitter = RecursiveCharacterTextSplitter(chunk_size=850, chunk_overlap=150)
    chunks = splitter.split_documents(documents)
    print(f' Delt opp i {len(chunks)} biter.')
    return chunks


def main():
    """
    Main entrypoint for the ingestion pipeline.
    Initializes services, loads documents, chunks them, and stores them in ChromaDB.
    """

    embedding_service = EmbeddingService()
    chroma_service = ChromaService(
        embedding_model=embedding_service.get_model(),
        persist_directory=CHROMA_PATH,
        collection_name=COLLECTION_NAME,
    )

    documents = load_txt_documents(DATA_PATH)
    chunks = chunk_documents(documents)

    print(' Lagrer tekstbitene til ChromaDB...')
    success = chroma_service.add_documents(chunks)

    if success:
        print(
            f'Alt ferdig! Lagt til {len(chunks)} biter fra {len(documents)} dokumenter.'
        )
    else:
        print('Noe gikk galt under lagring til ChromaDB.')


if __name__ == '__main__':
    main()
