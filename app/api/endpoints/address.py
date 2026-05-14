from typing import List

from fastapi import APIRouter

from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.services.address import AddressService

router = APIRouter(prefix="/addresses", tags=["Addresses"])
service = AddressService()


@router.get("/", response_model=List[AddressResponse])
async def list_addresses():
    return service.list_addresses()


@router.post("/", response_model=AddressResponse, status_code=201)
async def create_address(request: AddressCreate):
    return service.create_address(request)


@router.get("/{address_id}", response_model=AddressResponse)
async def get_address(address_id: int):
    return service.get_address(address_id)


@router.patch("/{address_id}", response_model=AddressResponse)
async def update_address(address_id: int, request: AddressUpdate):
    return service.update_address(address_id, request)


@router.delete("/{address_id}")
async def delete_address(address_id: int):
    return service.delete_address(address_id)
