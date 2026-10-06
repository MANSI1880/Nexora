from pydantic import BaseModel, Field
from typing import List, Optional, Any

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    sources: List[str] = Field(default_factory=list)
    ticket_id: Optional[str] = None
    action: Optional[str] = None
    status: str
