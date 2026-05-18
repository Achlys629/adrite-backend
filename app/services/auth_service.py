from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import secrets

from app.core.config import settings
from app.models.user import User, UserRole
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)
from app.schemas.user_schema import UserRegister
from app.services.email_service import EmailService
from app.utils.logger import logger


class AuthService:

    @staticmethod
    def register_user(user_data: UserRegister, db: Session) -> User:

        existing = db.query(User).filter(User.email == user_data.email).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password)
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        try:
            EmailService.send_welcome_email(
                new_user.email,
                new_user.full_name
            )
        except Exception as e:
            logger.error(f"Welcome email failed: {e}")

        logger.info(f"New user registered: {new_user.email}")

        return new_user

    @staticmethod
    def login_user(email: str, password: str, db: Session) -> dict:

        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Account is deactivated"
            )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role.value
            }
        )

        refresh_token = create_refresh_token()

        user.refresh_token = refresh_token
        db.commit()

        logger.info(f"User logged in: {user.email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user
        }

    @staticmethod
    def refresh_access_token(token: str, db: Session) -> dict:

        user = db.query(User).filter(
            User.refresh_token == token
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role.value
            }
        )

        return {
            "access_token": access_token
        }

    @staticmethod
    def logout_user(token: str, db: Session) -> bool:

        user = db.query(User).filter(
            User.refresh_token == token
        ).first()

        if user:
            user.refresh_token = None
            db.commit()

            logger.info(f"User logged out: {user.email}")

        return True

    @staticmethod
    def forgot_password(email: str, db: Session) -> bool:

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:
            return True

        # Cooldown check
        if user.otp_last_sent_at:

            cooldown = (
                datetime.now(timezone.utc) -
                user.otp_last_sent_at
            )

            if cooldown.total_seconds() < 60:
                raise HTTPException(
                    status_code=429,
                    detail="Please wait 60 seconds before requesting another OTP"
                )

        from app.core.security import generate_otp

        otp = generate_otp()

        user.otp_code = otp
        user.otp_expires_at = (
            datetime.now(timezone.utc) +
            timedelta(minutes=10)
        )

        user.otp_last_sent_at = datetime.now(timezone.utc)

        db.commit()

        EmailService.send_email(
            to_email=user.email,
            subject="Password Reset OTP - Adrite Agency",
            html_content=f"""
            <h2>Password Reset Request</h2>

            <p>Hello {user.full_name},</p>

            <p>Your OTP for password reset is:</p>

            <h1 style="color: #333; letter-spacing: 5px;">
                {otp}
            </h1>

            <p>
                This OTP expires in <strong>10 minutes</strong>.
            </p>

            <p>
                If you did not request this, please ignore this email.
            </p>

            <br>

            <p>Best regards,</p>
            <p>Adrite Agency Team</p>
            """
        )

        logger.info(f"OTP sent to: {user.email}")

        return True

    @staticmethod
    def verify_otp(email: str, otp: str, db: Session) -> dict:

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        if not user.otp_code or user.otp_code != otp:
            raise HTTPException(
                status_code=400,
                detail="Invalid OTP"
            )

        if datetime.now(timezone.utc) > user.otp_expires_at:
            raise HTTPException(
                status_code=400,
                detail="OTP has expired"
            )

        from app.core.security import generate_reset_token

        reset_token = generate_reset_token()

        user.reset_token = reset_token

        user.reset_token_expires_at = (
            datetime.now(timezone.utc) +
            timedelta(minutes=10)
        )

        user.otp_code = None
        user.otp_expires_at = None

        db.commit()

        logger.info(f"OTP verified for: {user.email}")

        return {
            "reset_token": reset_token
        }

    @staticmethod
    def reset_password(
        reset_token: str,
        new_password: str,
        db: Session
    ) -> bool:

        user = db.query(User).filter(
            User.reset_token == reset_token
        ).first()

        if not user:
            raise HTTPException(
                status_code=400,
                detail="Invalid reset token"
            )

        if datetime.now(timezone.utc) > user.reset_token_expires_at:
            raise HTTPException(
                status_code=400,
                detail="Reset token has expired"
            )

        user.hashed_password = hash_password(new_password)

        user.reset_token = None
        user.reset_token_expires_at = None

        db.commit()

        EmailService.send_email(
            to_email=user.email,
            subject="Password Reset Successful - Adrite Agency",
            html_content=f"""
            <h2>Password Reset Successful</h2>

            <p>Hello {user.full_name},</p>

            <p>Your password has been reset successfully.</p>

            <p>
                If you did not do this, contact support immediately.
            </p>

            <br>

            <p>Best regards,</p>
            <p>Adrite Agency Team</p>
            """
        )

        logger.info(f"Password reset for: {user.email}")

        return True

    @staticmethod
    def resend_otp(email: str, db: Session) -> bool:

        return AuthService.forgot_password(email, db)

    @staticmethod
    def google_login(credential: str, db: Session) -> dict:

        try:

            google_data = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

        except Exception:

            raise HTTPException(
                status_code=401,
                detail="Invalid Google token"
            )

        email = google_data.get("email")
        full_name = google_data.get("name")
        avatar_url = google_data.get("picture")

        if not email:
            raise HTTPException(
                status_code=400,
                detail="Could not get email from Google"
            )

        user = db.query(User).filter(
            User.email == email
        ).first()

        if not user:

            user = User(
                full_name=full_name,
                email=email,
                hashed_password=hash_password(
                    secrets.token_urlsafe(32)
                ),
                avatar_url=avatar_url,
                is_verified=True,
                is_active=True,
                role=UserRole.client
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"New Google user registered: {email}")

        if not user.is_active:
            raise HTTPException(
                status_code=403,
                detail="Account is deactivated"
            )

        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role.value
            }
        )

        refresh_token = create_refresh_token()

        user.refresh_token = refresh_token

        db.commit()

        logger.info(f"Google login: {email}")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user
        }