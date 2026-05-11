from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.project import ProjectStatus

class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    budget: Optional[float] = None
    deadline: Optional[datetime] = None

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    deadline: Optional[datetime] = None
    status: Optional[ProjectStatus] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: ProjectStatus
    budget: Optional[float]
    deadline: Optional[datetime]
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True