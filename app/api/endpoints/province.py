from typing import List

from fastapi import APIRouter

from app.schemas.province import ProvinceCreate, ProvinceUpdate, ProvinceResponse
from app.services.province import ProvinceService

router = APIRouter(prefix="/provinces", tags=["Provinces"])
service = ProvinceService()


@router.get("/", response_model=List[ProvinceResponse])
async def list_provinces():
    return service.list_provinces()


@router.post("/", response_model=ProvinceResponse, status_code=201)
async def create_province(request: ProvinceCreate):
    return service.create_province(request)


@router.get("/{province_id}", response_model=ProvinceResponse)
async def get_province(province_id: int):
    return service.get_province(province_id)


@router.patch("/{province_id}", response_model=ProvinceResponse)
async def update_province(province_id: int, request: ProvinceUpdate):
    return service.update_province(province_id, request)


@router.delete("/{province_id}")
async def delete_province(province_id: int):
    return service.delete_province(province_id)
