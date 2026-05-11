from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlogCreate(BaseModel):
    title: str
    content: str
    slug: str
    is_published: Optional[bool] = False

class BlogUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None

class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    slug: str
    is_published: bool
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True