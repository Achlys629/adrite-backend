from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User, UserRole, Profile
from app.schemas.user_schema import UserUpdate, UserAdminUpdate
from app.utils.logger import logger

class UserService:

    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    @staticmethod
    def update_user_profile(user: User, update_data: UserUpdate, db: Session) -> User:
        if update_data.full_name:
            user.full_name = update_data.full_name
        if update_data.avatar_url:
            user.avatar_url = update_data.avatar_url

        db.commit()
        db.refresh(user)
        logger.info(f"User profile updated: {user.email}")
        return user

    @staticmethod
    def update_user_by_admin(user_id: int, update_data: UserAdminUpdate, db: Session) -> User:
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
        logger.info(f"User updated by admin: {user.email}")
        return user

    @staticmethod
    def delete_user(user_id: int, db: Session) -> bool:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(user)
        db.commit()
        logger.info(f"User deleted: {user.email}")
        return True

    @staticmethod
    def get_or_create_profile(user_id: int, db: Session) -> Profile:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            profile = Profile(user_id=user_id)
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile