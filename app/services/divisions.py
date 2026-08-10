from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.mo.config import ACCESS_DIVISION_ONLY, get_access_level
from app.models.divisions import Division
from app.models.employees import Employee


class DivisionService:
    """Service layer for Division operations."""

    @staticmethod
    def list_by_department(
        db: Session,
        department_id: Optional[int] = None,
        current_employee: Employee | None = None,
    ) -> List[Division]:
        stmt = select(Division).where(Division.is_active)
        if department_id is not None:
            stmt = stmt.where(Division.department_id == department_id)

        # Apply position-based access filtering
        if current_employee is not None:
            level = get_access_level(current_employee.position_id)
            if level == ACCESS_DIVISION_ONLY:
                stmt = stmt.where(Division.division_id == current_employee.division_id)
            # ALL_DEPT → no extra filter (sees all divisions in department)

        stmt = stmt.order_by(Division.division_name)
        rows = db.execute(stmt).scalars().all()
        return rows
