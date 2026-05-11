from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.ticket import Ticket
from app.models.user import User, UserRole
from app.schemas.ticket_schema import TicketCreate, TicketUpdate, TicketResponse

router = APIRouter()

# Client: Create ticket
@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_ticket = Ticket(
        subject=ticket_data.subject,
        description=ticket_data.description,
        priority=ticket_data.priority,
        project_id=ticket_data.project_id,
        client_id=current_user.id
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

# Admin: Get all tickets
@router.get("/", response_model=List[TicketResponse])
def get_all_tickets(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).all()
    return tickets

# Client: Get my tickets
@router.get("/my-tickets", response_model=List[TicketResponse])
def get_my_tickets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tickets = db.query(Ticket).filter(
        Ticket.client_id == current_user.id
    ).all()
    return tickets

# Get single ticket
@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Client can only see their own tickets
    if current_user.role == UserRole.client and ticket.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    return ticket

# Admin: Update ticket status
@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Client can only update their own tickets
    if current_user.role == UserRole.client and ticket.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    # Client cannot change status
    if current_user.role == UserRole.client and update_data.status:
        raise HTTPException(status_code=403, detail="Clients cannot change ticket status")

    if update_data.subject:
        ticket.subject = update_data.subject
    if update_data.description:
        ticket.description = update_data.description
    if update_data.status:
        ticket.status = update_data.status
    if update_data.priority:
        ticket.priority = update_data.priority

    db.commit()
    db.refresh(ticket)
    return ticket

# Admin: Delete ticket
@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    db.delete(ticket)
    db.commit()
    return {"message": "Ticket deleted successfully"}