from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum,    Text,ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class UserRole(enum.Enum):
    admin = "admin"
    client = "client"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.client)
    is_active = Column(Boolean, default=True)
    refresh_token = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)
    otp_last_sent_at = Column(DateTime(timezone=True), nullable=True)
    reset_token = Column(String, nullable=True)
    reset_token_expires_at = Column(DateTime(timezone=True), nullable=True)

    projects = relationship("Project", back_populates="client")
    invoices = relationship("Invoice", back_populates="client")
    tickets = relationship("Ticket", back_populates="client")
    blogs = relationship("Blog", back_populates="author")
    profile = relationship("Profile", back_populates="user", uselist=False, lazy="select")
    tasks = relationship("Task", back_populates="assignee", lazy="select")
    testimonials = relationship("Testimonial", back_populates="client", lazy="select")
    analytics_events = relationship("AnalyticsEvent", back_populates="user", lazy="select")
    chat_messages = relationship("ChatMessage", back_populates="client")


# for profile
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    bio = Column(Text, nullable=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    country = Column(String, nullable=True)
    city = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    linkedin = Column(String, nullable=True)
    twitter = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")