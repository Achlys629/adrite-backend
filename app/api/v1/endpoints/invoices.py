from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.invoice import Invoice, InvoiceStatus
from app.models.user import User, UserRole
from app.schemas.invoice_schema import InvoiceCreate, InvoiceUpdate, InvoiceResponse

router = APIRouter()

# Admin: Create invoice
@router.post("/", response_model=InvoiceResponse)
def create_invoice(
    invoice_data: InvoiceCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    # Check if invoice number already exists
    existing = db.query(Invoice).filter(
        Invoice.invoice_number == invoice_data.invoice_number
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Invoice number already exists")

    new_invoice = Invoice(
        invoice_number=invoice_data.invoice_number,
        amount=invoice_data.amount,
        due_date=invoice_data.due_date,
        description=invoice_data.description,
        client_id=invoice_data.client_id,
        project_id=invoice_data.project_id
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice

# Admin: Get all invoices
@router.get("/", response_model=List[InvoiceResponse])
def get_all_invoices(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    invoices = db.query(Invoice).all()
    return invoices

# Client: Get my invoices
@router.get("/my-invoices", response_model=List[InvoiceResponse])
def get_my_invoices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoices = db.query(Invoice).filter(
        Invoice.client_id == current_user.id
    ).all()
    return invoices

# Get single invoice
@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Client can only see their own invoices
    if current_user.role == UserRole.client and invoice.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return invoice

# Admin: Update invoice
@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int,
    update_data: InvoiceUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    if update_data.amount:
        invoice.amount = update_data.amount
    if update_data.due_date:
        invoice.due_date = update_data.due_date
    if update_data.description:
        invoice.description = update_data.description
    if update_data.status:
        invoice.status = update_data.status

    db.commit()
    db.refresh(invoice)
    return invoice

# Admin: Delete invoice
@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted successfully"}