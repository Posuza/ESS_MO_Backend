from __future__ import annotations

import traceback

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.audit_logger import set_audit_context
from app.core.db.session import get_db

from app.models.employees import Employee
from app.schemas.auth import (
    ChangePasswordRequest,
    EmployeeFaceLogin,
    EmployeeLogin,
    EmployeeRegister,
    EmployeeResponse,
    ForgotPasswordRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    MessageResponse,
)
from app.schemas.face_verify import FaceVerifyRequest
from app.services.auth import employee_auth_service, password_service
from app.services.face_verify import face_verify_service

router = APIRouter()


@router.post(
    "/register", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED
)
async def employee_register(
    employee_data: EmployeeRegister, db: Session = Depends(get_db)
):
    """Register a new employee. Audit logged in service layer."""
    return employee_auth_service.register_employee(
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
        routes_id=employee_data.routes_id,
        start_date=employee_data.start_date,
        leave_date=employee_data.leave_date,
    )


@router.post("/login", response_model=LoginResponse)
async def employee_login(
    credentials: EmployeeLogin,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate and login. Audit logged in service layer."""
    employee = employee_auth_service.authenticate_employee(
        db=db,
        employee_code=credentials.employee_code,
        password=credentials.password,
        request=http_request,
    )
    return employee_auth_service.build_login_response(db=db, employee=employee)


@router.post("/face-login", response_model=LoginResponse)
async def employee_face_login(
    credentials: EmployeeFaceLogin,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Authenticate and login with a verified face image."""
    print(
        "[FaceLogin] request received "
        f"employee_code={credentials.employee_code} "
        f"image_length={len(credentials.image_data_url or '')}",
        flush=True,
    )
    try:
        verification = face_verify_service.verify_face(
            db=db,
            payload=FaceVerifyRequest(
                employee_code=credentials.employee_code,
                image_data_url=credentials.image_data_url,
                purpose="login",
            ),
        )
        print(f"[FaceLogin] verification result={verification}", flush=True)
        if not verification.get("is_match"):
            print("[FaceLogin] face did not match", flush=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=verification.get("message") or "ใบหน้าไม่ตรงกับข้อมูลพนักงาน",
            )

        employee = employee_auth_service.authenticate_face_verified_employee(
            db=db,
            employee_code=credentials.employee_code,
            request=http_request,
        )
        print("[FaceLogin] face-authenticated employee loaded", flush=True)
        response = employee_auth_service.build_login_response(db=db, employee=employee)
        print("[FaceLogin] login response built", flush=True)
        return response
    except HTTPException as exc:
        print(
            "[FaceLogin] HTTPException "
            f"status={exc.status_code} detail={exc.detail}",
            flush=True,
        )
        raise
    except Exception as exc:
        print(
            "[FaceLogin] Unexpected error "
            f"{exc.__class__.__name__}: {exc}",
            flush=True,
        )
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Face login internal error: {exc.__class__.__name__}",
        ) from exc


@router.post("/logout", response_model=LogoutResponse)
async def employee_logout(
    employee_code: str,
    http_request: Request,
    db: Session = Depends(get_db),
):
    """Logout. Accepts employee_code as query param (?employee_code=XXX). Audit logged in service layer."""
    employee = (
        db.query(Employee).filter(Employee.employee_code == employee_code).first()
    )
    employee_name = (
        employee_auth_service.get_employee_display_name(employee)
        if employee
        else employee_code
    )
    set_audit_context(
        request=http_request,
        user_name=employee_name,
        employee_code=employee_code,
    )
    return employee_auth_service.logout(employee_code=employee_code)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Send password reset email. Audit logged in service layer."""
    return password_service.forgot_password(
        db=db,
        employee_code=request.employee_code,
        send_plain_password=request.send_plain_password,
        background_tasks=background_tasks,
    )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Change password. Audit logged in service layer."""
    return password_service.change_password(
        db=db,
        employee_code=request.employee_code,
        old_password=request.old_password,
        new_password=request.new_password,
        background_tasks=background_tasks,
    )
