from app.workers.celery_app import celery_app
from app.services.email_service import EmailService

@celery_app.task
def send_welcome_email_task(email: str, full_name: str):
    EmailService.send_welcome_email(email, full_name)

@celery_app.task
def send_invoice_email_task(email: str, full_name: str, invoice_number: str, amount: float):
    EmailService.send_invoice_email(email, full_name, invoice_number, amount)

@celery_app.task
def send_otp_email_task(email: str, full_name: str, otp: str):
    EmailService.send_email(
        to_email=email,
        subject="Password Reset OTP - Adrite Agency",
        html_content=f"""
        <h2>Password Reset OTP</h2>
        <p>Hello {full_name},</p>
        <p>Your OTP is: <strong>{otp}</strong></p>
        <p>Expires in 10 minutes.</p>
        """
    )