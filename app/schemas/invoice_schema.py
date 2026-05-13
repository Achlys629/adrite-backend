from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.invoice import InvoiceStatus

class InvoiceCreate(BaseModel):
    invoice_number: str
    amount: float
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    client_id: int
    project_id: Optional[int] = None

class InvoiceUpdate(BaseModel):
    amount: Optional[float] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    status: Optional[InvoiceStatus] = None

class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    amount: float
    status: InvoiceStatus
    due_date: Optional[datetime]
    description: Optional[str]
    client_id: int
    project_id: Optional[int]
    created_at: datetime

class PaymentIntentCreate(BaseModel):
    invoice_id: int
    currency: str = "usd"

class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str
    invoice_id: int

class PaymentStatusResponse(BaseModel):
    payment_intent_id: str
    status: str
    amount: float

    class Config:
        from_attributes = True