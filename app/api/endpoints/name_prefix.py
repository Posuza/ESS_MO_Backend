from typing import List

from fastapi import APIRouter

from app.schemas.name_prefix import NamePrefixCreate, NamePrefixUpdate, NamePrefixResponse
from app.services.name_prefix import NamePrefixService

router = APIRouter(prefix="/name-prefixes", tags=["Name Prefixes"])
service = NamePrefixService()


@router.get("/", response_model=List[NamePrefixResponse])
async def list_prefixes():
    return service.list_prefixes()


@router.post("/", response_model=NamePrefixResponse, status_code=201)
async def create_prefix(request: NamePrefixCreate):
    return service.create_prefix(request)


@router.get("/{prefix_id}", response_model=NamePrefixResponse)
async def get_prefix(prefix_id: int):
    return service.get_prefix(prefix_id)


@router.patch("/{prefix_id}", response_model=NamePrefixResponse)
async def update_prefix(prefix_id: int, request: NamePrefixUpdate):
    return service.update_prefix(prefix_id, request)


@router.delete("/{prefix_id}")
async def delete_prefix(prefix_id: int):
    return service.delete_prefix(prefix_id)
