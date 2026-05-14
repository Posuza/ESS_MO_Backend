"""
Password Reset Token Management — JWT token creation and validation.

This module handles the security aspects of password reset:
- Creating secure reset tokens
- Validating and decoding reset tokens

Email sending functionality is in app.services.email
"""
from datetime import datetime, timedelta

from jose import jwt, JWTError

from app.core.config import settings


def create_reset_token(employee_code: str) -> str:
    """
    Create a JWT token for password reset.
    
    Args:
        employee_code: Employee code to encode in token
        
    Returns:
        JWT token string valid for RESET_EXPIRE_MINUTES
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.RESET_EXPIRE_MINUTES)
    payload = {"sub": employee_code, "exp": expire, "type": "password_reset"}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_reset_token(token: str) -> str | None:
    """
    Decode and validate a password reset token.
    
    Args:
        token: JWT token string
        
    Returns:
        Employee code if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "password_reset":
            return None
        return payload.get("sub")
    except JWTError:
        return None
