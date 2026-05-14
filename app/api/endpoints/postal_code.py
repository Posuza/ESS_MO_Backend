from typing import List

from fastapi import APIRouter

from app.schemas.postal_code import PostalCodeCreate, PostalCodeUpdate, PostalCodeResponse
from app.services.postal_code import PostalCodeService

router = APIRouter(prefix="/postal-codes", tags=["Postal Codes"])
service = PostalCodeService()


@router.get("/", response_model=List[PostalCodeResponse])
async def list_postal_codes():
    return service.list_postal_codes()


@router.post("/", response_model=PostalCodeResponse, status_code=201)
async def create_postal_code(request: PostalCodeCreate):
    return service.create_postal_code(request)


@router.get("/{postal_code_id}", response_model=PostalCodeResponse)
async def get_postal_code(postal_code_id: int):
    return service.get_postal_code(postal_code_id)


@router.patch("/{postal_code_id}", response_model=PostalCodeResponse)
async def update_postal_code(postal_code_id: int, request: PostalCodeUpdate):
    return service.update_postal_code(postal_code_id, request)


@router.delete("/{postal_code_id}")
async def delete_postal_code(postal_code_id: int):
    return service.delete_postal_code(postal_code_id)
