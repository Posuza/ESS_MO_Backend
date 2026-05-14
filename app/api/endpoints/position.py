from typing import Any, List

from fastapi import APIRouter

from app.schemas.position import PositionCreate, PositionUpdate, PositionResponse
from app.services.position import PositionService

router = APIRouter(prefix="/positions", tags=["Positions"])
service = PositionService()


@router.get("/", response_model=List[PositionResponse])
async def list_positions():
    return service.list_positions()


@router.post("/", response_model=PositionResponse, status_code=201)
async def create_position(request: PositionCreate):
    return service.create_position(request)


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(position_id: int):
    return service.get_position(position_id)


@router.patch("/{position_id}", response_model=PositionResponse)
async def update_position(position_id: int, request: PositionUpdate):
    return service.update_position(position_id, request)


@router.delete("/{position_id}")
async def delete_position(position_id: int):
    return service.delete_position(position_id)
