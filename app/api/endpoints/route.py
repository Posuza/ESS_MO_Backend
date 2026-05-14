from typing import Any, List

from fastapi import APIRouter

from app.schemas.route import RouteCreate, RouteUpdate, RouteResponse
from app.services.route import RouteService

router = APIRouter(prefix="/routes", tags=["Routes"])
service = RouteService()


@router.get("/", response_model=List[RouteResponse])
async def list_routes():
    return service.list_routes()


@router.post("/", response_model=RouteResponse, status_code=201)
async def create_route(request: RouteCreate):
    return service.create_route(request)


@router.get("/{route_id}", response_model=RouteResponse)
async def get_route(route_id: int):
    return service.get_route(route_id)


@router.patch("/{route_id}", response_model=RouteResponse)
async def update_route(route_id: int, request: RouteUpdate):
    return service.update_route(route_id, request)


@router.delete("/{route_id}")
async def delete_route(route_id: int):
    return service.delete_route(route_id)
