"""
Pre-configured decorators for MO (Monthly Operation) endpoints.

Usage
-----
from app.api.dependencies import active_employee_required, mo_active_required

@router.get("/")
@active_employee_required
@mo_active_required
async def api_list_reports(
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    ...

Logic (mo_active_required):
  - Director (1, 5): position + department active
  - Manager (2, 6):  position + department + division active
  - Other:           reject — not authorized for MO
"""

from __future__ import annotations

from functools import wraps

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.audit_logger import audit_logger
from app.core.registries.dependencies_message import (
    DEPARTMENT_INACTIVE,
    DEPARTMENT_NOT_FOUND,
    DIVISION_INACTIVE,
    DIVISION_NOT_FOUND,
    POSITION_INACTIVE,
    POSITION_NOT_FOUND,
)
from app.models.departments import Department
from app.models.divisions import Division
from app.models.employees import Employee
from app.models.positions import Position


# ═══════════════════════════════════════════════════════════════════════
# Position role groups
# ═══════════════════════════════════════════════════════════════════════

POSITION_DIRECTOR = {1, 5}    # ผู้อำนวยการ, รองผู้อำนวยการ
POSITION_MANAGER = {2, 6}     # ผู้จัดการเขต, รองผู้จัดการเขต
MO_ALLOWED_POSITIONS = POSITION_DIRECTOR | POSITION_MANAGER  # {1, 2, 5, 6}


# ═══════════════════════════════════════════════════════════════════════
# Active scope check — position / department / division
# ═══════════════════════════════════════════════════════════════════════

ACTIVE_CHECK_MAP = {
    "position": (Position, "position_id", "ตำแหน่ง", POSITION_NOT_FOUND, POSITION_INACTIVE),
    "department": (Department, "department_id", "หน่วยงาน", DEPARTMENT_NOT_FOUND, DEPARTMENT_INACTIVE),
    "division": (Division, "division_id", "หน่วยงานย่อย", DIVISION_NOT_FOUND, DIVISION_INACTIVE),
}


def _check_active(db: Session, employee: Employee, check_type: str) -> None:
    """Check if employee's related record (position/dept/division) is active.

    Raises 404 if not found, 403 if deactivated.
    """
    model, field, label, not_found_msg, inactive_msg = ACTIVE_CHECK_MAP[check_type]
    employee_value = getattr(employee, field, None)

    # Legacy data uses division_id == 0 for department-wide scope.
    if field == "division_id" and employee_value == 0:
        return

    if employee_value is None:
        audit_logger.log(action=f"{label}ไม่ได้กำหนด")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{label}ยังไม่ได้กำหนด ไม่สามารถดำเนินการได้ โปรดติดต่อ GutsEssCenter",
        )

    record = (
        db.execute(
            select(model).where(getattr(model, field) == employee_value)
        )
        .scalars()
        .first()
    )

    if not record:
        audit_logger.log(
            action=not_found_msg,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{label}ไม่พบในระบบ โปรดติดต่อ GutsEssCenter",
        )

    if not record.is_active:
        audit_logger.log(
            action=inactive_msg,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"{label}นี้ถูกปิดใช้งาน ไม่สามารถดำเนินการได้ โปรดติดต่อ GutsEssCenter",
        )


# ═══════════════════════════════════════════════════════════════════════
# MO scope decorator — role-aware
# ═══════════════════════════════════════════════════════════════════════


def mo_active_required(func):
    """Verify employee's scope records are active based on role.

    Must be used **below** ``@active_employee_required`` so that
    ``current_employee`` is already injected.

    Logic:
      - Director (1, 5): position + department active
      - Manager (2, 6):  position + department + division active
      - Other:           reject — not authorized for MO
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        db = None
        current_employee = kwargs.get("current_employee")

        for value in kwargs.values():
            if isinstance(value, Session):
                db = value

        if db is None or current_employee is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="MO dependency setup is invalid",
            )

        # 1. Position always checked
        _check_active(db, current_employee, "position")

        # 2. Role-based scope checks
        if current_employee.position_id in POSITION_DIRECTOR:
            _check_active(db, current_employee, "department")
        elif current_employee.position_id in POSITION_MANAGER:
            _check_active(db, current_employee, "department")
            _check_active(db, current_employee, "division")
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ตำแหน่งนี้ไม่มีสิทธิ์เข้าถึงข้อมูล MO โปรดติดต่อ GutsEssCenter",
            )

        return await func(*args, **kwargs)

    return wrapper
