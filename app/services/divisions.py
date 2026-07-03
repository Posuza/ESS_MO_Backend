from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.divisions import Division
from app.models.employees import Employee

# ── Access levels (mirrors frontEnd/src/utils/positionAccess.ts) ──


class _AccessLevel:
    ALL_DEPT = "ALL_DEPT"
    DIVISION_ONLY = "DIVISION_ONLY"


def _get_access_level(position_id: int | None) -> str:
    if position_id in (1, 5):
        return _AccessLevel.ALL_DEPT
    return _AccessLevel.DIVISION_ONLY  # positions 2,3,4,6 + default


class DivisionService:
    """Service layer for Division operations."""

    @staticmethod
    def list_by_department(
        db: Session,
        department_id: Optional[int] = None,
        current_employee: Employee | None = None,
    ) -> List[Division]:
        print(
            "[DivisionService.list_by_department] input:",
            {
                "department_id": department_id,
                "employee_id": getattr(current_employee, "employee_id", None),
                "position_id": getattr(current_employee, "position_id", None),
                "division_id": getattr(current_employee, "division_id", None),
            },
        )
        stmt = select(Division)
        if department_id is not None:
            stmt = stmt.where(Division.department_id == department_id)

        # Apply position-based access filtering
        if current_employee is not None:
            level = _get_access_level(current_employee.position_id)
            print(
                "[DivisionService.list_by_department] access level:",
                level,
            )
            if level == _AccessLevel.DIVISION_ONLY:
                stmt = stmt.where(Division.division_id == current_employee.division_id)
            # ALL_DEPT → no extra filter (sees all divisions in department)

        stmt = stmt.order_by(Division.division_name)
        rows = db.execute(stmt).scalars().all()
        print(
            "[DivisionService.list_by_department] returned:",
            len(rows),
            [
                {
                    "division_id": row.division_id,
                    "division_name": row.division_name,
                    "department_id": row.department_id,
                }
                for row in rows
            ],
        )
        return rows
