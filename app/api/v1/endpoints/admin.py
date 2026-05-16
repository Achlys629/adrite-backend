from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_admin
from app.models.user import User
from app.models.project import Project
from app.models.invoice import Invoice, InvoiceStatus
from app.models.ticket import Ticket, TicketStatus
from app.schemas.admin_schema import DashboardStats

router = APIRouter()

# Admin: Dashboard stats
@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(User).count()
    total_projects = db.query(Project).count()
    total_invoices = db.query(Invoice).count()
    total_tickets = db.query(Ticket).count()

    paid_invoices = db.query(Invoice).filter(
        Invoice.status == InvoiceStatus.paid
    ).count()

    unpaid_invoices = db.query(Invoice).filter(
        Invoice.status == InvoiceStatus.unpaid
    ).count()

    open_tickets = db.query(Ticket).filter(
        Ticket.status == TicketStatus.open
    ).count()

    resolved_tickets = db.query(Ticket).filter(
        Ticket.status == TicketStatus.resolved
    ).count()

    # Calculate total revenue from paid invoices
    paid_invoice_list = db.query(Invoice).filter(
        Invoice.status == InvoiceStatus.paid
    ).all()
    total_revenue = sum(invoice.amount for invoice in paid_invoice_list)

    return {
        "total_users": total_users,
        "total_projects": total_projects,
        "total_invoices": total_invoices,
        "total_tickets": total_tickets,
        "paid_invoices": paid_invoices,
        "unpaid_invoices": unpaid_invoices,
        "open_tickets": open_tickets,
        "resolved_tickets": resolved_tickets,
        "total_revenue": total_revenue
    }

# Admin: Get all users overview
@router.get("/users-overview")
def get_users_overview(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total = db.query(User).count()
    active = db.query(User).filter(User.is_active == True).count()
    inactive = db.query(User).filter(User.is_active == False).count()

    return {
        "total": total,
        "active": active,
        "inactive": inactive
    }

# Admin: Get revenue overview
@router.get("/revenue-overview")
def get_revenue_overview(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    all_invoices = db.query(Invoice).all()
    paid = db.query(Invoice).filter(Invoice.status == InvoiceStatus.paid).all()
    unpaid = db.query(Invoice).filter(Invoice.status == InvoiceStatus.unpaid).all()
    overdue = db.query(Invoice).filter(Invoice.status == InvoiceStatus.overdue).all()

    return {
        "total_revenue": sum(i.amount for i in paid),
        "pending_revenue": sum(i.amount for i in unpaid),
        "overdue_revenue": sum(i.amount for i in overdue),
        "total_invoices": len(all_invoices)
    }

# Admin: Get projects overview
@router.get("/projects-overview")
def get_projects_overview(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    from app.models.project import ProjectStatus

    total = db.query(Project).count()
    pending = db.query(Project).filter(Project.status == ProjectStatus.pending).count()
    in_progress = db.query(Project).filter(Project.status == ProjectStatus.in_progress).count()
    completed = db.query(Project).filter(Project.status == ProjectStatus.completed).count()
    cancelled = db.query(Project).filter(Project.status == ProjectStatus.cancelled).count()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "cancelled": cancelled
    }

# Admin: Get tickets overview
@router.get("/tickets-overview")
def get_tickets_overview(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total = db.query(Ticket).count()
    open_tickets = db.query(Ticket).filter(Ticket.status == TicketStatus.open).count()
    in_progress = db.query(Ticket).filter(Ticket.status == TicketStatus.in_progress).count()
    resolved = db.query(Ticket).filter(Ticket.status == TicketStatus.resolved).count()
    closed = db.query(Ticket).filter(Ticket.status == TicketStatus.closed).count()

    return {
        "total": total,
        "open": open_tickets,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed
    }