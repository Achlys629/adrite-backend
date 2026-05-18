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


# meeting_schema

class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_link: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: Optional[int] = 30

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    meeting_link: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None

class MeetingResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    meeting_link: Optional[str]
    scheduled_at: datetime
    duration_minutes: int
    status: str
    client_id: int
    created_at: datetime

    class Config:
        from_attributes = True