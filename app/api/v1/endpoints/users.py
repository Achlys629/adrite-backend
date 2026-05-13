from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin
from app.models.user import User, UserRole
from app.schemas.user_schema import UserResponse, UserUpdate, UserAdminUpdate
from app.utils.pagination import PaginationParams, paginate_query


router = APIRouter()

# Get my profile
@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    return current_user

# Update my profile
@router.put("/me", response_model=UserResponse)
def update_my_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if update_data.full_name:
        current_user.full_name = update_data.full_name
    if update_data.avatar_url:
        current_user.avatar_url = update_data.avatar_url

    db.commit()
    db.refresh(current_user)
    return current_user


# Admin: Get all users with pagination
@router.get("/")
def get_all_users(
    pagination: PaginationParams = Depends(),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    if pagination.search:
        query = query.filter(User.full_name.ilike(f"%{pagination.search}%"))
    return paginate_query(query, pagination)

# Admin: Get single user
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Admin: Update user
@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    update_data: UserAdminUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if update_data.full_name:
        user.full_name = update_data.full_name
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    if update_data.role:
        user.role = UserRole[update_data.role]

    db.commit()
    db.refresh(user)
    return user

# Admin: Delete user
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}