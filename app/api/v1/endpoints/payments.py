from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.invoice_schema import PaymentIntentCreate, PaymentIntentResponse, PaymentStatusResponse
from app.services.payment_service import PaymentService

router = APIRouter()

# Client: Create payment intent
@router.post("/create-payment-intent", response_model=PaymentIntentResponse)
def create_payment_intent(
    payment_data: PaymentIntentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return PaymentService.create_payment_intent(
        invoice_id=payment_data.invoice_id,
        currency=payment_data.currency,
        client_id=current_user.id,
        db=db
    )

# Stripe webhook
@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    return PaymentService.handle_webhook(payload, sig_header, db)

# Get payment status
@router.get("/status/{payment_intent_id}", response_model=PaymentStatusResponse)
def get_payment_status(
    payment_intent_id: str,
    current_user: User = Depends(get_current_user)
):
    return PaymentService.get_payment_status(payment_intent_id)