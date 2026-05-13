from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from app.services.email_service import EmailService
from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user_schema import UserRegister, UserLogin, UserResponse, TokenResponse

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
security = HTTPBearer()

REFRESH_TOKEN_EXPIRE_DAYS = 7

@router.post("/register", response_model=UserResponse)
@limiter.limit("5/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Send welcome email
    EmailService.send_welcome_email(new_user.email, new_user.full_name)
    
    return new_user

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login(request: Request, user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    refresh_token = create_refresh_token()

    user.refresh_token = refresh_token
    db.commit()

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        samesite="lax",
        secure=False
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "user": user
    }

@router.post("/refresh")
@limiter.limit("20/minute")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")

    user = db.query(User).filter(User.refresh_token == token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if token:
        user = db.query(User).filter(User.refresh_token == token).first()
        if user:
            user.refresh_token = None
            db.commit()

    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

