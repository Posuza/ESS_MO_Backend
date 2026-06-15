from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.dependencies import active_employee_required
from app.core.db.session import get_db
from app.models.employees import Employee
from app.schemas.divisions import DivisionResponse
from app.services.divisions import DivisionService

router = APIRouter()


@router.get("/", response_model=List[DivisionResponse])
@active_employee_required
async def api_list_divisions(
    request: Request,
    department_id: Optional[int] = Query(None),
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    return DivisionService.list_by_department(
        db=db,
        department_id=department_id,
        current_employee=current_employee,
    )
