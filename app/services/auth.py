from __future__ import annotations

from typing import Any, Optional

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.audit_logger import audit_logger
from app.core.registries import (
    AUTH_ERROR_ACCOUNT_INACTIVE,
    AUTH_ERROR_ACCOUNT_INACTIVE_FORGOT_PASSWORD,
    AUTH_ERROR_EMPLOYEE_NOT_FOUND,
    AUTH_ERROR_INVALID_CREDENTIALS,
    AUTH_ERROR_INVALID_OLD_PASSWORD,
    AUTH_ERROR_NO_EMAIL_REGISTERED,
    CHANGE_PASSWORD_ATTEMPT,
    CHANGE_PASSWORD_SUCCESS,
    CLIENT_ERROR_BAD_REQUEST,
    CLIENT_ERROR_CONFLICT,
    FORGOT_PASSWORD_ATTEMPT,
    FORGOT_PASSWORD_EMAIL_SENT,
    FORGOT_PASSWORD_FAILED,
    LOGIN_ATTEMPT,
    LOGIN_SUCCESS,
    LOGOUT_SUCCESS,
    REGISTER,
)
from app.models.departments import Department
from app.models.divisions import Division
from app.models.employees import Employee
from app.models.name_prefixs import NamePrefix
from app.models.positions import Position
from app.models.roles import Role
from app.models.routes import Route
from app.services.email import (
    send_change_password_notification_email,
    send_plain_password_email,
)

# ─────────────────────────────────────────────────────────────────────────────
# EmployeeAuthService
# ─────────────────────────────────────────────────────────────────────────────


class EmployeeAuthService:
    """Service layer for employee authentication operations.

    All business logic AND audit logging live here — endpoints only route.
    """

    @staticmethod
    def register_employee(
        db: Session,
        employee_code: str,
        password: str,
        email: Optional[str],
        first_name: str,
        last_name: str,
        phone_number: Optional[str],
        birth_date,
        role_id: int,
        name_prefix_id: int,
        field_id: int,
        department_id: int,
        division_id: int,
        position_id: int,
        shift_id: int,
        address_id: Optional[int] = None,
        routes_id: Optional[int] = None,
        start_date: Optional[Any] = None,
        leave_date: Optional[Any] = None,
        created_by: str = "SYSTEM",
    ) -> Employee:
        """
        Register a new employee.

        Audits: REGISTER on success.
        Raises:
            HTTPException: If employee_code or email already exists
        """
        # Check if employee already exists
        existing = (
            db.query(Employee).filter(Employee.employee_code == employee_code).first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=CLIENT_ERROR_CONFLICT,
            )

        # Check email uniqueness if provided
        if email:
            existing_email = (
                db.query(Employee).filter(Employee.email == email.lower()).first()
            )
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=CLIENT_ERROR_CONFLICT,
                )

        # Create employee
        db_employee = Employee(
            employee_code=employee_code,
            password=password,
            email=email.lower() if email else None,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            birth_date=birth_date,
            role_id=role_id,
            name_prefix_id=name_prefix_id,
            field_id=field_id,
            department_id=department_id,
            division_id=division_id,
            position_id=position_id,
            shift_id=shift_id,
            address_id=address_id,
            routes_id=routes_id,
            start_date=start_date,
            leave_date=leave_date,
            is_active=True,
            created_by=created_by,
        )

        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)

        # Audit registration success
        audit_logger.log(
            action=REGISTER.format(
                resource="Employee", employee_code=db_employee.employee_code
            ),
        )

        return db_employee

    @staticmethod
    def authenticate_employee(
        db: Session, employee_code: str, password: str
    ) -> Employee:
        """
        Authenticate employee by code and password.
        """
        employee = (
            db.query(Employee).filter(Employee.employee_code == employee_code).first()
        )

        # Audit login attempt
        audit_logger.log(action=LOGIN_ATTEMPT.format(resource="Employee"))

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AUTH_ERROR_EMPLOYEE_NOT_FOUND,
            )

        # Verify password (plaintext comparison - TODO: hash when security enabled)
        if employee.password != password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERROR_INVALID_CREDENTIALS,
            )

        # Check if account is active
        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AUTH_ERROR_ACCOUNT_INACTIVE,
            )

        # Audit login success
        audit_logger.log(action=LOGIN_SUCCESS.format(resource="Employee"))

        return employee

    @staticmethod
    def logout(employee_code: str) -> dict:
        """
        Record logout audit and return standard response.
        """
        audit_logger.log(action=LOGOUT_SUCCESS.format(resource="Employee"))
        return {"message": "Successfully logged out", "tokens_revoked": 0}

    @staticmethod
    def build_login_response(db: Session, employee: Employee) -> dict:
        """Build the login response dict, resolving IDs to display names."""
        db_role = db.query(Role).filter(Role.role_id == employee.role_id).first()
        db_position = (
            db.query(Position)
            .filter(Position.position_id == employee.position_id)
            .first()
        )
        db_prefix = (
            db.query(NamePrefix)
            .filter(NamePrefix.prefix_id == employee.name_prefix_id)
            .first()
        )
        db_dept = (
            db.query(Department)
            .filter(Department.department_id == employee.department_id)
            .first()
        )
        db_division = (
            db.query(Division)
            .filter(Division.division_id == employee.division_id)
            .first()
        )
        db_route = db.query(Route).filter(Route.route_id == employee.routes_id).first()

        role_name = db_role.role_name if db_role else ""
        position_name = db_position.position_name if db_position else ""
        prefix_name = db_prefix.prefix_name if db_prefix else ""
        department_name = db_dept.department_name if db_dept else ""
        division_name = db_division.division_name if db_division else ""
        route_name = db_route.route_name if db_route else ""

        return {
            "employee": {
                "employee_code": employee.employee_code,
                "email": employee.email,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "role_name": role_name,
                "name_prefix": prefix_name,
                "position_id": employee.position_id,
                "position_name": position_name,
                "department_id": employee.department_id,
                "department_name": department_name,
                "division_id": employee.division_id,
                "division_name": division_name,
                "route_id": employee.routes_id,
                "route_name": route_name,
            },
            "message": "Login successful",
        }

    @staticmethod
    def get_employee_display_name(employee: Employee) -> str:
        """Build a human-readable display name for audit logging."""
        return (
            f"{employee.first_name} {employee.last_name}".strip()
            or employee.email
            or employee.employee_code
        )


class PasswordService:
    """Service layer for password operations.

    All business logic AND audit logging live here — endpoints only route.
    """

    @staticmethod
    def forgot_password(
        db: Session,
        employee_code: str,
        send_plain_password: bool,
        background_tasks: BackgroundTasks,
    ) -> dict:
        """
        Process forgot-password request.

        Audits:
          - FORGOT_PASSWORD_ATTEMPT
          - FORGOT_PASSWORD_FAILED (with reason)
          - FORGOT_PASSWORD_EMAIL_SENT

        Raises:
            HTTPException: With appropriate auth error code
        """
        # Look up employee
        employee = db.execute(
            select(Employee).where(Employee.employee_code == employee_code)
        ).scalar_one_or_none()

        # ── Attempt audit ──────────────────────────────────────────────
        audit_logger.log(
            action=FORGOT_PASSWORD_ATTEMPT.format(resource="Employee"),
        )

        # ── Validate ──────────────────────────────────────────────────
        if not employee:
            audit_logger.log(
                action=FORGOT_PASSWORD_FAILED.format(
                    resource="Employee", reason="Employee not found"
                ),
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AUTH_ERROR_EMPLOYEE_NOT_FOUND,
            )

        employee_name = (
            f"{employee.first_name} {employee.last_name}".strip()
            or employee.employee_code
        )

        if not employee.is_active:
            audit_logger.log(
                action=FORGOT_PASSWORD_FAILED.format(
                    resource="Employee", reason="Employee account is inactive"
                ),
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AUTH_ERROR_ACCOUNT_INACTIVE_FORGOT_PASSWORD,
            )

        if not employee.email:
            audit_logger.log(
                action=FORGOT_PASSWORD_FAILED.format(
                    resource="Employee", reason="Employee has no email registered"
                ),
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AUTH_ERROR_NO_EMAIL_REGISTERED,
            )

        # ── Send email and audit based on real result ────────────────
        email_to = employee.email
        email_emp_code = employee.employee_code

        def _send_and_audit():
            success = send_plain_password_email(
                email_to, employee_name, employee.password, email_emp_code
            )
            if success:
                audit_logger.log(
                    action=FORGOT_PASSWORD_EMAIL_SENT.format(
                        resource="Employee", email=email_to
                    ),
                )
            else:
                audit_logger.log(
                    action=FORGOT_PASSWORD_FAILED.format(
                        resource="Employee", reason="Email delivery failed"
                    ),
                )

        background_tasks.add_task(_send_and_audit)

        return {
            "message": "ส่งรหัสผ่านไปยังอีเมลเรียบร้อยแล้ว กรุณาตรวจสอบอีเมลที่ลงทะเบียนไว้",
        }

    @staticmethod
    def change_password(
        db: Session,
        employee_code: str,
        old_password: str,
        new_password: str,
        background_tasks: BackgroundTasks,
    ) -> dict:
        """
        Change an employee's password after verifying the old password.

        Audits:
          - CHANGE_PASSWORD_ATTEMPT
          - CHANGE_PASSWORD_SUCCESS

        Raises:
            HTTPException: If employee not found, old password wrong,
                           account inactive, or same password reused.
        """
        # Audit attempt
        audit_logger.log(
            action=CHANGE_PASSWORD_ATTEMPT.format(resource="Employee"),
        )

        # Look up employee
        employee = db.execute(
            select(Employee).where(Employee.employee_code == employee_code)
        ).scalar_one_or_none()

        if not employee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=AUTH_ERROR_EMPLOYEE_NOT_FOUND,
            )

        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=AUTH_ERROR_ACCOUNT_INACTIVE_FORGOT_PASSWORD,
            )

        if employee.password != old_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=AUTH_ERROR_INVALID_OLD_PASSWORD,
            )

        if employee.password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=CLIENT_ERROR_BAD_REQUEST,
            )

        # Store name and email before update for the email task
        employee_name = (
            f"{employee.first_name} {employee.last_name}".strip()
            or employee.employee_code
        )
        employee_email = employee.email

        # Update password (plaintext for now)
        stmt = (
            update(Employee)
            .where(Employee.employee_code == employee_code)
            .values(password=new_password)
        )
        db.execute(stmt)
        db.commit()

        # Send notification email and audit based on real result
        def _send_and_audit():
            if employee_email:
                success = send_change_password_notification_email(
                    employee_email, employee_name, new_password, employee_code
                )
                if success:
                    audit_logger.log(
                        action=CHANGE_PASSWORD_SUCCESS.format(resource="Employee"),
                    )
                else:
                    audit_logger.log(
                        action=CHANGE_PASSWORD_ATTEMPT.format(resource="Employee"),
                    )
            else:
                # No email on file — still audit success for the password change itself
                audit_logger.log(
                    action=CHANGE_PASSWORD_SUCCESS.format(resource="Employee"),
                )

        background_tasks.add_task(_send_and_audit)

        return {"message": "เปลี่ยนรหัสผ่านสำเร็จ"}


# Singleton instances
employee_auth_service = EmployeeAuthService()
password_service = PasswordService()
