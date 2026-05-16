from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DashboardStats(BaseModel):
    total_users: int
    total_projects: int
    total_invoices: int
    total_tickets: int
    paid_invoices: int
    unpaid_invoices: int
    open_tickets: int
    resolved_tickets: int
    total_revenue: float

class UserActivityLog(BaseModel):
    id: int
    user_id: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True