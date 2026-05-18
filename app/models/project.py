from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ProjectStatus(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProjectStatus), default=ProjectStatus.pending)
    budget = Column(Float, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    tasks = relationship("Task", back_populates="project", lazy="select")
    client = relationship("User", back_populates="projects")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="todo")
    deadline = Column(Date, nullable=True)
    submission_link = Column(Text, nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)

    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")


    #meeting 
class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    meeting_link = Column(String, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=30)
    status = Column(String, default="scheduled")
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    client = relationship("User", back_populates="meetings")