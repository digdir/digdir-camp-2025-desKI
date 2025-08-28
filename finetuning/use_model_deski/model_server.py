from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from generate_response_bruker import response_finetuned_brukerstotte
from generate_response_service import response_finetuned_servicedesk

# FastAPI server that exposes endpoints for generating responses using two separate LoRA-finetuned models.
# One endpoint is for servicedesk prompts, the other for brukerstøtte.
# Can be run with: uvicorn model_server:app --host 0.0.0.0 --port 8001


app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods = ["GET", "POST"], allow_headers = ["*"])


class GenerationRequest(BaseModel):
    prompt: str


#generating response from model finetuned for servicedesk
@app.post("/generate_servicedesk")
async def generate_servicedesk(req: GenerationRequest):
    try:
        response = response_finetuned_servicedesk(req.prompt)
        return {
            "response": response
        }
    except Exception as e:
        return {"error": str(e)}

        
#generating response from model finetuned for brukerstotte
@app.post("/generate_brukerstotte")
async def generate_brukerstotte(req: GenerationRequest):
    try: 
        response = response_finetuned_brukerstotte(req.prompt)
        return {
            "response": response
        }

    except Exception as e:
        return {"error": str(e)}
  