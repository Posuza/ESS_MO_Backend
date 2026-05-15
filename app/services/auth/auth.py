from typing import Optional, Any
from datetime import datetime

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.employee import Employee
# from app.core.security import get_password_hash  # TODO: Enable when ready for hashing
from app.core.registries.error_registry import ERROR_REGISTRY


class EmployeeAuthService:
    """Service layer for employee authentication operations."""

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
        sector_id: Optional[int] = None,
        zone_id: Optional[int] = None,
        routes_id: Optional[int] = None,
        start_date: Optional[Any] = None,
        leave_date: Optional[Any] = None,
        created_by: str = "SYSTEM"
    ) -> Employee:
        """
        Register a new employee.
        
        Raises:
            HTTPException: If employee_code or email already exists
        """
        # Check if employee already exists
        existing = db.query(Employee).filter(
            Employee.employee_code == employee_code
        ).first()

        if existing:
            entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2004"]
            raise HTTPException(
                status_code=entry["http_status"],
                detail=entry["message"]  # Use registry message
            )

        # Check email uniqueness if provided
        if email:
            existing_email = db.query(Employee).filter(
                Employee.email == email.lower()
            ).first()
            if existing_email:
                entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2004"]
                raise HTTPException(
                    status_code=entry["http_status"],
                    detail=entry["message"]  # Use registry message
                )

        # Store plaintext password (TODO: Hash when security enabled)
        # hashed_password = get_password_hash(password)
        
        # Create employee
        db_employee = Employee(
            employee_code=employee_code,
            password=password,  # Plaintext for now
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
            sector_id=sector_id,
            zone_id=zone_id,
            routes_id=routes_id,
            start_date=start_date,
            leave_date=leave_date,
            is_active=True,
            created_by=created_by,
        )
        
        db.add(db_employee)
        db.commit()
        db.refresh(db_employee)
        
        return db_employee

    @staticmethod
    def authenticate_employee(
        db: Session,
        employee_code: str,
        password: str
    ) -> Employee:
        """
        Authenticate employee by code and password.
        
        Returns:
            Employee object if authentication successful
            
        Raises:
            HTTPException: If authentication fails
        """
        # Find employee
        employee = db.query(Employee).filter(
            Employee.employee_code == employee_code
        ).first()
        
        # Use specific auth error for invalid credentials
        if not employee:
            # Employee not found -> return explicit 404 with registry message and contacts
            entry = ERROR_REGISTRY["AUTH"]["ER_AUTH_1009"]
            raise HTTPException(
                status_code=entry["http_status"],
                detail={
                    "error": entry["error"],
                    "message": entry["message"], 
                    "contacts": entry.get("contacts")
                }
            )

        # Verify password (plaintext comparison - TODO: use verify_password() when hashing enabled)
        if employee.password != password:
            # Wrong password: keep generic invalid credentials (401)
            entry = ERROR_REGISTRY["AUTH"]["ER_AUTH_1006"]
            raise HTTPException(
                status_code=entry["http_status"],
                detail={
                    "error": entry["error"],
                    "message": entry["message"], 
                    "contacts": entry.get("contacts")
                }
            )

        # Check if account is active - use specific inactive error
        if not employee.is_active:
            entry = ERROR_REGISTRY["AUTH"]["ER_AUTH_1007"]
            raise HTTPException(
                status_code=entry["http_status"],
                detail={
                    "error": entry["error"],
                    "message": entry["message"], 
                    "contacts": entry.get("contacts")
                }
            )

        return employee


# Singleton instance
employee_auth_service = EmployeeAuthService()
