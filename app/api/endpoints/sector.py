from typing import Any, List, Optional

from fastapi import APIRouter, Query

from app.schemas.sector import SectorCreate, SectorUpdate, SectorResponse
from app.services.sector import SectorService

router = APIRouter(prefix="/sectors", tags=["Sectors"])
service = SectorService()


@router.get("/", response_model=List[SectorResponse])
async def list_sectors(
    field_id: Optional[int] = Query(None),
    department_id: Optional[int] = Query(None),
    division_id: Optional[int] = Query(None)
):
    return service.list_sectors(
        field_id=field_id,
        department_id=department_id,
        division_id=division_id
    )


@router.post("/", response_model=SectorResponse, status_code=201)
async def create_sector(request: SectorCreate):
    return service.create_sector(request)


@router.get("/{sector_id}", response_model=SectorResponse)
async def get_sector(sector_id: int):
    return service.get_sector(sector_id)


@router.patch("/{sector_id}", response_model=SectorResponse)
async def update_sector(sector_id: int, request: SectorUpdate):
    return service.update_sector(sector_id, request)


@router.delete("/{sector_id}")
async def delete_sector(sector_id: int):
    return service.delete_sector(sector_id)
