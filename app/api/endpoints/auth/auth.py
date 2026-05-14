from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session

from app.schemas.auth.auth import (
    EmployeeRegister,
    EmployeeResponse,
    EmployeeLogin,
    LoginResponse,
    LogoutResponse
)
from app.models.employee import Employee
from app.core.orm import get_db
from app.core.audit_logger import audit, _extract_request_context
from app.core.registries.error_registry import ERROR_REGISTRY
from app.services.auth.auth import employee_auth_service



router = APIRouter(prefix="/auth", tags=["auth"])


# Employee registration
@router.post("/register", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
async def employee_register(
    request: Request,
    employee_data: EmployeeRegister,
    db: Session = Depends(get_db)
):
    try:
        # Delegate to service layer
        db_employee = employee_auth_service.register_employee(
            db=db,
            employee_code=employee_data.employee_code,
            password=employee_data.password,
            email=employee_data.email,
            first_name=employee_data.first_name,
            last_name=employee_data.last_name,
            phone_number=employee_data.phone_number,
            birth_date=employee_data.birth_date,
            role_id=employee_data.role_id,
            name_prefix_id=employee_data.name_prefix_id,
            field_id=employee_data.field_id,
            department_id=employee_data.department_id,
            division_id=employee_data.division_id,
            position_id=employee_data.position_id,
            shift_id=employee_data.shift_id,
            address_id=employee_data.address_id,
            sector_id=employee_data.sector_id,
            zone_id=employee_data.zone_id,
            routes_id=employee_data.routes_id,
            start_date=employee_data.start_date,
            leave_date=employee_data.leave_date,
        )
        
        # Audit registration success with employee name
        employee_full_name = f"{db_employee.first_name} {db_employee.last_name}".strip() or db_employee.email or db_employee.employee_code
        audit.log(
            action=f"[AUTH_REGISTER] Employee registered: {db_employee.employee_code}",
            user_name=employee_full_name,
            employee_code=db_employee.employee_code,
            **_extract_request_context(request),
        )
        return db_employee

    except HTTPException as e:
        # Audit registration failure with detailed error info
        error_category = "CLIENT" if e.status_code in [400, 409] else "AUTH"
        error_key = "ER_CLIENT_2004" if e.status_code == 409 else "ER_CLIENT_2001"
        
        # Use employee name from registration data
        user_name = f"{employee_data.first_name} {employee_data.last_name}".strip() or employee_data.email or employee_data.employee_code
        
        audit.action_with_error(
            "AUTH", "ACT_AUTH_005",
            request=request,
            user_name=user_name,
            employee_code=None,
            error_category=error_category,
            error_key=error_key,
            resource="Employee"
        )
        raise
    except Exception as e:
        db.rollback()
        # Use employee name from registration data
        user_name = f"{employee_data.first_name} {employee_data.last_name}".strip() or employee_data.email or employee_data.employee_code
        audit.error("BACKEND", "ER_BACKEND_3001", request=request, user_name=user_name, detail=str(e))
        entry = ERROR_REGISTRY["BACKEND"]["ER_BACKEND_3001"]
        raise HTTPException(status_code=entry["http_status"], detail=entry["message"])


# Employee login
@router.post("/login", response_model=LoginResponse)
async def employee_login(
    request: Request,
    credentials: EmployeeLogin,
    db: Session = Depends(get_db)
):
    try:
        # Look up employee for audit log name
        employee_lookup = db.query(Employee).filter(
            Employee.employee_code == credentials.employee_code
        ).first()
        
        if employee_lookup:
            user_name = f"{employee_lookup.first_name} {employee_lookup.last_name}".strip() or employee_lookup.email or credentials.employee_code
        else:
            user_name = credentials.employee_code
        
        # Audit login attempt
        audit.action(
            "AUTH", "ACT_AUTH_001", 
            request=request, 
            user_name=user_name,
            employee_code=credentials.employee_code if employee_lookup else None,
            resource="Employee"
        )

        # Authenticate via service
        employee = employee_auth_service.authenticate_employee(
            db=db,
            employee_code=credentials.employee_code,
            password=credentials.password
        )

        # Audit login success with employee name
        employee_full_name = f"{employee.first_name} {employee.last_name}".strip() or employee.email or employee.employee_code
        audit.action(
            "AUTH", "ACT_AUTH_003",
            request=request,
            user_name=employee_full_name,
            employee_code=employee.employee_code,
            resource="Employee"
        )
        
        # Return employee info only (no tokens)
        return {
            "employee": {
                "employee_code": employee.employee_code,
                "email": employee.email,
                "first_name": employee.first_name,
                "last_name": employee.last_name,
                "role_id": employee.role_id,
                "is_active": employee.is_active
            },
            "message": "Login successful"
        }

    except HTTPException as e:
        # Audit login failure with detailed error info
        # Determine error category and key from status code
        error_category = "CLIENT" if e.status_code == 400 else "AUTH"
        error_key = "ER_CLIENT_2001" if e.status_code == 400 else "ER_AUTH_1002"
        
        audit.action_with_error(
            "AUTH", "ACT_AUTH_002",
            request=request,
            user_name=user_name,
            employee_code=credentials.employee_code if employee_lookup else None,
            error_category=error_category,
            error_key=error_key,
            resource="Employee"
        )
        raise
    except Exception as e:
        # Log to audit and return generic backend error
        audit.error("BACKEND", "ER_BACKEND_3001", request=request, user_name=user_name, detail=str(e))
        entry = ERROR_REGISTRY["BACKEND"]["ER_BACKEND_3001"]
        raise HTTPException(status_code=entry["http_status"], detail=entry["message"])


# Employee logout (no token revocation, just audit logging)
@router.post("/logout", response_model=LogoutResponse)
async def employee_logout(
    request: Request,
    employee_code: str = Query(..., description="Employee code for logout tracking"),
    db: Session = Depends(get_db)
):
    try:
        # Look up employee for audit log name
        employee = db.query(Employee).filter(
            Employee.employee_code == employee_code
        ).first()
        
        if employee:
            user_name = f"{employee.first_name} {employee.last_name}".strip() or employee.email or employee_code
        else:
            user_name = employee_code
        
        # Audit logout attempt
        audit.action(
            "AUTH", "ACT_AUTH_004", 
            request=request, 
            user_name=user_name,
            employee_code=employee_code if employee else None,
            resource="Employee"
        )

        # Audit logout success
        audit.action(
            "AUTH", "ACT_AUTH_006",
            request=request,
            user_name=user_name,
            employee_code=employee_code,
            resource="Employee"
        )

        return {"message": "Successfully logged out", "tokens_revoked": 0}
        
    except Exception as e:
        # Audit logout failure with detailed error info
        audit.action_with_error(
            "AUTH", "ACT_AUTH_005",
            request=request,
            user_name=user_name if 'user_name' in locals() else employee_code,
            employee_code=employee_code if 'employee' in locals() and employee else None,
            error_category="BACKEND",
            error_key="ER_BACKEND_3001",
            resource="Employee"
        )
        entry = ERROR_REGISTRY["BACKEND"]["ER_BACKEND_3001"]
        raise HTTPException(status_code=entry["http_status"], detail=entry["message"])

