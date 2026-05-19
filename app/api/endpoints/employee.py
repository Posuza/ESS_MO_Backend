from typing import Any, List, Optional

from fastapi import APIRouter, Query

from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee import EmployeeService

router = APIRouter(prefix="/employees", tags=["Employees"])
service = EmployeeService()


@router.get("/", response_model=List[EmployeeResponse])
async def list_employees(
    department_id: Optional[int] = Query(None),
    division_id: Optional[int] = Query(None),
    field_id: Optional[int] = Query(None),
    role_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    return service.list_employees(
        department_id=department_id,
        division_id=division_id,
        field_id=field_id,
        role_id=role_id,
        is_active=is_active
    )


@router.post("/", response_model=EmployeeResponse, status_code=201)
async def create_employee(request: EmployeeCreate):
    return service.create_employee(request)


@router.get("/{employee_code}", response_model=EmployeeResponse)
async def get_employee(employee_code: str):
    return service.get_employee(employee_code)


@router.patch("/{employee_code}", response_model=EmployeeResponse)
async def update_employee(employee_code: str, request: EmployeeUpdate):
    return service.update_employee(employee_code, request)


@router.delete("/{employee_code}")
async def delete_employee(employee_code: str):
    return service.delete_employee(employee_code)
