from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class EmployeeRegister(BaseModel):
    """Schema for employee registration - all required Employee model fields."""

    employee_code: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=6, max_length=6)
    email: Optional[EmailStr] = None
    first_name: str = Field(..., max_length=150)
    last_name: str = Field(..., max_length=150)
    phone_number: Optional[str] = Field(None, max_length=10)
    birth_date: date

    # Required foreign keys
    role_id: int
    name_prefix_id: int
    field_id: int
    department_id: int
    division_id: int
    position_id: int
    shift_id: int

    # Optional foreign keys
    address_id: Optional[int] = None
    routes_id: Optional[int] = None

    # Optional dates
    start_date: Optional[date] = None
    leave_date: Optional[date] = None


class EmployeeResponse(BaseModel):
    """Schema for employee response after registration."""

    model_config = ConfigDict(from_attributes=True)

    employee_code: str
    email: Optional[str]
    first_name: str
    last_name: str
    is_active: bool
    role_id: int
    department_id: int
    position_id: int


class EmployeeLogin(BaseModel):
    """Schema for employee login credentials."""

    employee_code: str = Field(..., min_length=6, max_length=6)
    password: str = Field(..., min_length=6, max_length=6)


class EmployeeInfo(BaseModel):
    """Schema for employee information in login response."""

    employee_code: str
    email: Optional[str]
    first_name: str
    last_name: str
    role_name: str
    name_prefix: str
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    position_name: str
    position_id: Optional[int] = None


class LoginResponse(BaseModel):
    """Schema for login response."""

    employee: EmployeeInfo
    message: str = "Login successful"


class LogoutResponse(BaseModel):
    """Schema for logout response."""

    message: str
    tokens_revoked: int


class LogoutRequest(BaseModel):
    employee_code: str = Field(..., min_length=6, max_length=6)


class ForgotPasswordRequest(BaseModel):
    employee_code: str = Field(..., min_length=6, max_length=6)
    # Legacy behavior: when true, send the current password to the user's email
    # (insecure; use only for backwards compatibility)
    send_plain_password: bool = False


class ChangePasswordRequest(BaseModel):
    employee_code: str = Field(..., min_length=6, max_length=6)
    old_password: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6, max_length=6)


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=1, max_length=6)


class MessageResponse(BaseModel):
    message: str
