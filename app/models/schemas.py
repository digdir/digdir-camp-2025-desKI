from pydantic import BaseModel

# Request model containing the input message
class ChatRequest(BaseModel):
    message: str

# Response model containing the reply
class ChatResponse(BaseModel):
    reply: str
