from typing import Any, List

from fastapi import APIRouter

from app.schemas.division import DivisionCreate, DivisionUpdate, DivisionResponse
from app.services.division import DivisionService

router = APIRouter(prefix="/divisions", tags=["Divisions"])
service = DivisionService()


@router.get("/", response_model=List[DivisionResponse])
async def list_divisions():
    return service.list_divisions()


@router.post("/", response_model=DivisionResponse, status_code=201)
async def create_division(request: DivisionCreate):
    return service.create_division(request)


@router.get("/{division_id}", response_model=DivisionResponse)
async def get_division(division_id: int):
    return service.get_division(division_id)


@router.patch("/{division_id}", response_model=DivisionResponse)
async def update_division(division_id: int, request: DivisionUpdate):
    return service.update_division(division_id, request)


@router.delete("/{division_id}")
async def delete_division(division_id: int):
    return service.delete_division(division_id)
