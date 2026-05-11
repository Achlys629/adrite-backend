from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ChatMessageCreate(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    message: str
    response: Optional[str]
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True