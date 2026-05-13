import stripe
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.core.config import settings
from app.models.invoice import Invoice, InvoiceStatus

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentService:

    @staticmethod
    def create_payment_intent(invoice_id: int, currency: str, client_id: int, db: Session):
        # Get invoice
        invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        # Check ownership
        if invoice.client_id != client_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # Check if already paid
        if invoice.status == InvoiceStatus.paid:
            raise HTTPException(status_code=400, detail="Invoice already paid")

        # Create Stripe payment intent
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(invoice.amount * 100),  # Stripe uses cents
                currency=currency,
                metadata={
                    "invoice_id": invoice.id,
                    "client_id": client_id
                }
            )
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))

        return {
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": invoice.amount,
            "currency": currency,
            "invoice_id": invoice.id
        }

    @staticmethod
    def handle_webhook(payload: bytes, sig_header: str, db: Session):
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise HTTPException(status_code=400, detail="Invalid signature")

        # Handle successful payment
        if event["type"] == "payment_intent.succeeded":
            payment_intent = event["data"]["object"]
            invoice_id = payment_intent["metadata"].get("invoice_id")

            if invoice_id:
                invoice = db.query(Invoice).filter(
                    Invoice.id == int(invoice_id)
                ).first()
                if invoice:
                    invoice.status = InvoiceStatus.paid
                    db.commit()

        return {"status": "success"}

    @staticmethod
    def get_payment_status(payment_intent_id: str):
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "payment_intent_id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100
            }
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=400, detail=str(e))