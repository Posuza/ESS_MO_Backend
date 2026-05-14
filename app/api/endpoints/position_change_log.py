from typing import Any, List

from fastapi import APIRouter

from app.schemas.position_change_log import PositionChangeLogCreate, PositionChangeLogUpdate, PositionChangeLogResponse
from app.services.position_change_log import PositionChangeLogService

router = APIRouter(prefix="/position-change-logs", tags=["Position Change Logs"])
service = PositionChangeLogService()


@router.get("/", response_model=List[PositionChangeLogResponse])
async def list_logs():
    return service.list_logs()


@router.post("/", response_model=PositionChangeLogResponse, status_code=201)
async def create_log(request: PositionChangeLogCreate):
    return service.create_log(request)


@router.get("/{log_id}", response_model=PositionChangeLogResponse)
async def get_log(log_id: int):
    return service.get_log(log_id)


@router.patch("/{log_id}", response_model=PositionChangeLogResponse)
async def update_log(log_id: int, request: PositionChangeLogUpdate):
    return service.update_log(log_id, request)


@router.delete("/{log_id}")
async def delete_log(log_id: int):
    return service.delete_log(log_id)
