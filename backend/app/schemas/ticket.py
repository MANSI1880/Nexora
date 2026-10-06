from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TicketBase(BaseModel):
    title: str
    description: str
    priority: Optional[str] = "MEDIUM"

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None

class TicketResponse(TicketBase):
    id: int
    status: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
