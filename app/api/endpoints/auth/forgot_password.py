from typing import Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, status, Request
from sqlalchemy import select, update

from app.core.orm import get_session
from app.models.employee import Employee
from app.schemas.auth.reset_password import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse,
)
from app.core.security.reset_password import create_reset_token, decode_reset_token
from app.services.auth.forgot_password import send_reset_for_employee_code
from app.core.audit_logger import audit
from app.core.registries.error_registry import ERROR_REGISTRY


router = APIRouter(prefix="/auth", tags=["auth"])


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    req: Request,
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
):
    try:
        # Look up employee first to get their name for audit log
        with get_session() as session:
            employee = session.execute(
                select(Employee).where(Employee.employee_code == request.employee_code)
            ).scalar_one_or_none()
            
            if employee:
                user_name = f"{employee.first_name} {employee.last_name}".strip() or employee.email or request.employee_code
            else:
                user_name = request.employee_code
        
        # Audit attempt with employee name
        audit.action(
            "AUTH", 
            "ACT_AUTH_007", 
            request=req, 
            user_name=user_name, 
            employee_code=request.employee_code if employee else None,
            resource="Employee"
        )
        
        # Delegate lookup + enqueue to service
        result = send_reset_for_employee_code(
            request.employee_code, 
            background_tasks, 
            send_plain_password=request.send_plain_password
        )
        
        # Log based on result
        if result["email_sent"]:
            # Success - email was sent
            audit.action(
                "AUTH",
                "ACT_AUTH_009",
                request=req,
                user_name=result["employee_name"],
                employee_code=request.employee_code,
                resource="Employee",
                email=result["email"]
            )
        else:
            # Failed - employee not found, inactive, or no email
            audit.action(
                "AUTH",
                "ACT_AUTH_008",
                request=req,
                user_name=result.get("employee_name") or request.employee_code,
                employee_code=request.employee_code if result["found"] else None,
                resource="Employee",
                reason=result["reason"]
            )
        
        # Always return generic message for security (don't reveal if employee exists)
        if request.send_plain_password:
            return MessageResponse(message="If that employee code is registered, your current password will be emailed.")
        return MessageResponse(message="If that employee code is registered, a reset link has been sent.")
        
    except Exception as e:
        audit.error("BACKEND", "ER_BACKEND_3001", request=req, user_name=request.employee_code, detail=str(e))
        entry = ERROR_REGISTRY["BACKEND"]["ER_BACKEND_3001"]
        raise HTTPException(status_code=entry["http_status"], detail=entry["message"])



