from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import HTTPBearer
from app.schemas.user_schema import GoogleLoginRequest

from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.middleware.rate_limit import limiter
from app.models.user import User
from app.services.auth_service import AuthService
from app.schemas.user_schema import (
    UserRegister, UserLogin, UserResponse, TokenResponse,
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest,
    ResendOTPRequest, OTPResponse, ResetTokenResponse
)

router = APIRouter()
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
@limiter.limit("3/minute")
def register(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    return AuthService.register_user(user_data, db)

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    result = AuthService.login_user(user_data.email, user_data.password, db)
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
        secure=False
    )
    return {
        "access_token": result["access_token"],
        "token_type": "bearer",
        "role": result["user"].role.value,
        "user": result["user"]
    }

@router.post("/refresh")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    return AuthService.refresh_access_token(token, db)

@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if token:
        AuthService.logout_user(token, db)
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/forgot-password", response_model=OTPResponse)
@limiter.limit("3/minute")
def forgot_password(request: Request, data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    AuthService.forgot_password(data.email, db)
    return {"message": "OTP sent to your email if account exists"}

@router.post("/verify-otp", response_model=ResetTokenResponse)
@limiter.limit("5/minute")
def verify_otp(request: Request, data: VerifyOTPRequest, db: Session = Depends(get_db)):
    return AuthService.verify_otp(data.email, data.otp, db)

@router.post("/reset-password", response_model=OTPResponse)
@limiter.limit("3/minute")
def reset_password(request: Request, data: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService.reset_password(data.reset_token, data.new_password, db)
    return {"message": "Password reset successfully"}

@router.post("/resend-otp", response_model=OTPResponse)
@limiter.limit("3/minute")
def resend_otp(request: Request, data: ResendOTPRequest, db: Session = Depends(get_db)):
    AuthService.resend_otp(data.email, db)
    return {"message": "OTP resent to your email"}


@router.post("/google", response_model=TokenResponse)
def google_login(
    data: GoogleLoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    result = AuthService.google_login(data.credential, db)
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
        secure=False
    )
    return {
        "access_token": result["access_token"],
        "token_type": "bearer",
        "role": result["user"].role.value,
        "user": result["user"]
    }