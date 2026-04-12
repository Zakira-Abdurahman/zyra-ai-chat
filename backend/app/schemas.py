from pydantic import BaseModel
from typing import List, Dict

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class WebSocketMessage(BaseModel):
    type: str  # "message", "typing", "history"
    role: str | None = None
    content: str | None = None