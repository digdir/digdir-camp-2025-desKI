# 🛰️ Running the Model Server (FastAPI)

This server exposes two endpoints for generating responses from LoRA-finetuned language models.

## ⚙️ Endpoints

- `POST /generate_servicedesk` → uses the servicedesk fine-tuned model  
- `POST /generate_brukerstotte` → uses the brukerstøtte fine-tuned model

Each endpoint expects a JSON body with a `prompt` field:

```json
{
  "prompt": "Hvordan oppretter jeg integrasjon med Maskinporten?"
}
```

## ▶️ Start the server

To run the API:

```bash
uvicorn model_server:app --host 0.0.0.0 --port 8001
```

## 🧠 Notes

- The models are loaded from paths defined in `config.py` (`MODEL_PATH_SERVICEDESK` and `MODEL_PATH_BRUKERSTOTTE`)
- The logic for generating responses is implemented in:
  - `generate_response_service.py`
  - `generate_response_bruker.py`
