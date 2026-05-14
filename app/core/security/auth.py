"""
Security utilities: password hashing and authentication.
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plain password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


# OLD CODE BELOW - Not used with employee authentication
# def authenticate_user(db: Session, login: str, password: str) -> Optional[Customer]:
    """Authenticate user by username/email and password, only if active"""
    try:
        user = db.query(Customer).filter(
            (Customer.username == login.lower()) | (Customer.email == login.lower())
        ).first()
        
        if not user:
            return None
        
        if not user.is_active:  # <-- Only allow active users
            return None
        
        if not verify_password(password, user.password):
            return None
        
        return user
    except Exception:
        return None
