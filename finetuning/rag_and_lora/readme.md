# 🧠 Local Inference with LoRA and ChromaDB

This folder contains scripts for testing a fine-tuned LoRA model using a local vector database (ChromaDB).  
The goal is to test inference directly inside Jupyter notebook without relying on the rest of the Git repo

## 📦 What's included
- vector db (chroma db)
- digdir docs
- config
- embedding function
- rag_model_server.py to generate answers
- A CLI interface for testing

## 🧪 What it does

1. Loads the tokenizer and model from `MODEL_PATH`
2. Loads the ChromaDB vector store 
3. Embeds the user’s query
4. Fetches matching document chunks
5. Builds a context-aware prompt
6. Sends the prompt to the model and prints the response

## 

- Adjust `MODEL_PATH` to change the model used

## ▶️ Use by running the following:

```bash
python3 rag_pipeline.py
```

You'll be asked to enter a question, and the model will return a generated answer based on retrieved documentation.


