from typing import List

from fastapi import APIRouter

from app.schemas.sub_district import SubDistrictCreate, SubDistrictUpdate, SubDistrictResponse
from app.services.sub_district import SubDistrictService

router = APIRouter(prefix="/sub-districts", tags=["Sub Districts"])
service = SubDistrictService()


@router.get("/", response_model=List[SubDistrictResponse])
async def list_sub_districts():
    return service.list_sub_districts()


@router.post("/", response_model=SubDistrictResponse, status_code=201)
async def create_sub_district(request: SubDistrictCreate):
    return service.create_sub_district(request)


@router.get("/{sub_district_id}", response_model=SubDistrictResponse)
async def get_sub_district(sub_district_id: int):
    return service.get_sub_district(sub_district_id)


@router.patch("/{sub_district_id}", response_model=SubDistrictResponse)
async def update_sub_district(sub_district_id: int, request: SubDistrictUpdate):
    return service.update_sub_district(sub_district_id, request)


@router.delete("/{sub_district_id}")
async def delete_sub_district(sub_district_id: int):
    return service.delete_sub_district(sub_district_id)
