from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserCRUD:
    def get(self, db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username"""
        return db.query(User).filter(User.username == username).first()

    def get_by_username_or_email(self, db: Session, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        return db.query(User).filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Get multiple users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Create new user"""
        # Get default user role
        user_role = db.query(UserRole).filter(UserRole.name == "user").first()
        if not user_role:
            raise ValueError("Default user role not found")

        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            password_hash=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role_id=user_role.id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate) -> User:
        """Update user"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in update_data:
            setattr(db_obj, field, update_data[field])

        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_password(self, db: Session, user: User, new_password: str) -> User:
        """Update user password"""
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_last_login(self, db: Session, user: User) -> User:
        """Update user's last login timestamp"""
        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        user = self.get_by_username_or_email(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active"""
        return user.is_active

    def is_superuser(self, user: User) -> bool:
        """Check if user is super admin"""
        return user.role.name == "super_admin"

    def deactivate(self, db: Session, user: User) -> User:
        """Deactivate user (soft delete)"""
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def change_role(self, db: Session, user: User, role_name: str) -> User:
        """Change user role"""
        role = db.query(UserRole).filter(UserRole.name == role_name).first()
        if not role:
            raise ValueError(f"Role {role_name} not found")

        user.role_id = role.id
        user.updated_at = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def count(self, db: Session) -> int:
        """Count total users"""
        return db.query(User).count()


user_crud = UserCRUD()
