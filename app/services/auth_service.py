from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
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
        # Check if email exists
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Create user
        new_user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Send welcome email
        try:
            EmailService.send_welcome_email(new_user.email, new_user.full_name)
        except Exception as e:
            logger.error(f"Welcome email failed: {e}")

        logger.info(f"New user registered: {new_user.email}")
        return new_user

    @staticmethod
    def login_user(email: str, password: str, db: Session) -> dict:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is deactivated")

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = create_refresh_token()

        # Save refresh token
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
        user = db.query(User).filter(User.refresh_token == token).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        return {"access_token": access_token}

    @staticmethod
    def logout_user(token: str, db: Session) -> bool:
        user = db.query(User).filter(User.refresh_token == token).first()
        if user:
            user.refresh_token = None
            db.commit()
            logger.info(f"User logged out: {user.email}")
        return True