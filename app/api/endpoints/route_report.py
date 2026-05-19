from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Query, Request

from app.core.request_actor import extract_actor_employee_code
from app.schemas.route_report import (
    RouteReportCreate,
    RouteReportUpdate,
    RouteReportResponse,
    ApprovedStatusEnum,
)
from app.services.route_report import RouteReportService

router = APIRouter(prefix="/route-reports", tags=["Route Reports"])
service = RouteReportService()


@router.get("/", response_model=List[RouteReportResponse])
async def list_reports(
    http_request: Request,
    route_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[ApprovedStatusEnum] = Query(None),
    created_by: Optional[str] = Query(None),
    min_absent: Optional[int] = Query(None),
    max_absent: Optional[int] = Query(None)
):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.list_reports(
        actor_employee_code=actor_employee_code,
        route_id=route_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        created_by=created_by,
        min_absent=min_absent,
        max_absent=max_absent
    )


@router.post("/", response_model=RouteReportResponse, status_code=201)
async def create_report(request: RouteReportCreate, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.create_report(request, actor_employee_code=actor_employee_code)


@router.get("/{route_report_id}", response_model=RouteReportResponse)
async def get_report(route_report_id: str, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.get_report_for_actor(route_report_id, actor_employee_code=actor_employee_code)


@router.patch("/{route_report_id}", response_model=RouteReportResponse)
async def update_report(route_report_id: str, request: RouteReportUpdate, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.update_report(route_report_id, request, actor_employee_code=actor_employee_code)


@router.delete("/{route_report_id}")
async def delete_report(route_report_id: str, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.delete_report(route_report_id, actor_employee_code=actor_employee_code)
