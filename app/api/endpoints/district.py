from typing import List

from fastapi import APIRouter

from app.schemas.district import DistrictCreate, DistrictUpdate, DistrictResponse
from app.services.district import DistrictService

router = APIRouter(prefix="/districts", tags=["Districts"])
service = DistrictService()


@router.get("/", response_model=List[DistrictResponse])
async def list_districts():
    return service.list_districts()


@router.post("/", response_model=DistrictResponse, status_code=201)
async def create_district(request: DistrictCreate):
    return service.create_district(request)


@router.get("/{district_id}", response_model=DistrictResponse)
async def get_district(district_id: int):
    return service.get_district(district_id)


@router.patch("/{district_id}", response_model=DistrictResponse)
async def update_district(district_id: int, request: DistrictUpdate):
    return service.update_district(district_id, request)


@router.delete("/{district_id}")
async def delete_district(district_id: int):
    return service.delete_district(district_id)
