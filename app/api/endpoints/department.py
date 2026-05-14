from typing import Any, List

from fastapi import APIRouter

from app.schemas.department import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from app.services.department import DepartmentService

router = APIRouter(prefix="/departments", tags=["Departments"])
service = DepartmentService()


@router.get("/", response_model=List[DepartmentResponse])
async def list_departments():
    return service.list_departments()


@router.post("/", response_model=DepartmentResponse, status_code=201)
async def create_department(request: DepartmentCreate):
    return service.create_department(request)


@router.get("/{department_id}", response_model=DepartmentResponse)
async def get_department(department_id: int):
    return service.get_department(department_id)


@router.patch("/{department_id}", response_model=DepartmentResponse)
async def update_department(department_id: int, request: DepartmentUpdate):
    return service.update_department(department_id, request)


@router.delete("/{department_id}")
async def delete_department(department_id: int):
    return service.delete_department(department_id)
