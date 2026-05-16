from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import stripe
from app.core.database import get_db
from app.core.config import settings
from app.models.invoice import Invoice, InvoiceStatus
from app.services.email_service import EmailService
from app.models.user import User

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Payment succeeded
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        invoice_id = payment_intent["metadata"].get("invoice_id")
        client_id = payment_intent["metadata"].get("client_id")

        if invoice_id:
            invoice = db.query(Invoice).filter(
                Invoice.id == int(invoice_id)
            ).first()

            if invoice:
                # Update invoice status to paid
                invoice.status = InvoiceStatus.paid
                db.commit()

                # Send confirmation email to client
                client = db.query(User).filter(
                    User.id == int(client_id)
                ).first()

                if client:
                    EmailService.send_email(
                        to_email=client.email,
                        subject=f"Payment Confirmed - Invoice {invoice.invoice_number}",
                        html_content=f"""
                        <h2>Payment Confirmed!</h2>
                        <p>Hello {client.full_name},</p>
                        <p>Your payment for invoice <strong>{invoice.invoice_number}</strong>
                        of <strong>${invoice.amount}</strong> has been received.</p>
                        <p>Thank you for your payment!</p>
                        <br>
                        <p>Best regards,</p>
                        <p>Adrite Agency Team</p>
                        """
                    )

    # Payment failed
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        invoice_id = payment_intent["metadata"].get("invoice_id")
        client_id = payment_intent["metadata"].get("client_id")

        if invoice_id and client_id:
            client = db.query(User).filter(
                User.id == int(client_id)
            ).first()

            invoice = db.query(Invoice).filter(
                Invoice.id == int(invoice_id)
            ).first()

            if client and invoice:
                EmailService.send_email(
                    to_email=client.email,
                    subject=f"Payment Failed - Invoice {invoice.invoice_number}",
                    html_content=f"""
                    <h2>Payment Failed</h2>
                    <p>Hello {client.full_name},</p>
                    <p>Your payment for invoice <strong>{invoice.invoice_number}</strong>
                    could not be processed.</p>
                    <p>Please try again or contact support.</p>
                    <br>
                    <p>Best regards,</p>
                    <p>Adrite Agency Team</p>
                    """
                )

    return {"status": "success"}