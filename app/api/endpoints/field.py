from typing import Any, List

from fastapi import APIRouter

from app.schemas.field import FieldCreate, FieldUpdate, FieldResponse
from app.services.field import FieldService

router = APIRouter(prefix="/fields", tags=["Fields"])
service = FieldService()


@router.get("/", response_model=List[FieldResponse])
async def list_fields():
    return service.list_fields()


@router.post("/", response_model=FieldResponse, status_code=201)
async def create_field(request: FieldCreate):
    return service.create_field(request)


@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(field_id: int):
    return service.get_field(field_id)


@router.patch("/{field_id}", response_model=FieldResponse)
async def update_field(field_id: int, request: FieldUpdate):
    return service.update_field(field_id, request)


@router.delete("/{field_id}")
async def delete_field(field_id: int):
    return service.delete_field(field_id)
