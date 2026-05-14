from typing import Any, List

from fastapi import APIRouter

from app.schemas.zone import ZoneCreate, ZoneUpdate, ZoneResponse
from app.services.zone import ZoneService

router = APIRouter(prefix="/zones", tags=["Zones"])
service = ZoneService()


@router.get("/", response_model=List[ZoneResponse])
async def list_zones():
    return service.list_zones()


@router.post("/", response_model=ZoneResponse, status_code=201)
async def create_zone(request: ZoneCreate):
    return service.create_zone(request)


@router.get("/{zone_id}", response_model=ZoneResponse)
async def get_zone(zone_id: int):
    return service.get_zone(zone_id)


@router.patch("/{zone_id}", response_model=ZoneResponse)
async def update_zone(zone_id: int, request: ZoneUpdate):
    return service.update_zone(zone_id, request)


@router.delete("/{zone_id}")
async def delete_zone(zone_id: int):
    return service.delete_zone(zone_id)
