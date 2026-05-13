from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings

class EmailService:

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str):
        try:
            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                html_content=html_content
            )
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            sg.send(message)
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False

    @staticmethod
    def send_welcome_email(to_email: str, full_name: str):
        subject = "Welcome to Adrite Agency"
        html_content = f"""
        <h2>Welcome {full_name}!</h2>
        <p>Your account has been created successfully.</p>
        <p>You can now login to your dashboard and track your projects, invoices and support tickets.</p>
        <br>
        <p>Best regards,</p>
        <p>Adrite Agency Team</p>
        """
        return EmailService.send_email(to_email, subject, html_content)

    @staticmethod
    def send_invoice_email(to_email: str, full_name: str, invoice_number: str, amount: float):
        subject = f"Invoice {invoice_number} - Adrite Agency"
        html_content = f"""
        <h2>Hello {full_name},</h2>
        <p>A new invoice has been created for you.</p>
        <p><strong>Invoice Number:</strong> {invoice_number}</p>
        <p><strong>Amount:</strong> ${amount}</p>
        <p>Please login to your dashboard to view and pay the invoice.</p>
        <br>
        <p>Best regards,</p>
        <p>Adrite Agency Team</p>
        """
        return EmailService.send_email(to_email, subject, html_content)

    @staticmethod
    def send_ticket_update_email(to_email: str, full_name: str, subject: str, status: str):
        email_subject = f"Ticket Update - {subject}"
        html_content = f"""
        <h2>Hello {full_name},</h2>
        <p>Your support ticket has been updated.</p>
        <p><strong>Ticket:</strong> {subject}</p>
        <p><strong>New Status:</strong> {status}</p>
        <p>Please login to your dashboard to view the update.</p>
        <br>
        <p>Best regards,</p>
        <p>Adrite Agency Team</p>
        """
        return EmailService.send_email(to_email, subject, html_content)

    @staticmethod
    def send_password_reset_email(to_email: str, full_name: str, reset_link: str):
        subject = "Password Reset - Adrite Agency"
        html_content = f"""
        <h2>Hello {full_name},</h2>
        <p>You requested a password reset.</p>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_link}">Reset Password</a>
        <p>This link will expire in 30 minutes.</p>
        <p>If you did not request this, please ignore this email.</p>
        <br>
        <p>Best regards,</p>
        <p>Adrite Agency Team</p>
        """
        return EmailService.send_email(to_email, subject, html_content)