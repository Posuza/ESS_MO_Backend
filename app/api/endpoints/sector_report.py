from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Query, Request

from app.core.request_actor import extract_actor_employee_code
from app.schemas.sector_report import (
    SectorReportCreate,
    SectorReportUpdate,
    SectorReportResponse,
    ApprovedStatusEnum,
)
from app.services.sector_report import SectorReportService

router = APIRouter(prefix="/sector-reports", tags=["Sector Reports"])
service = SectorReportService()


@router.get("/", response_model=List[SectorReportResponse])
async def list_reports(
    http_request: Request,
    sector_id: Optional[int] = Query(None),
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
        sector_id=sector_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        created_by=created_by,
        min_absent=min_absent,
        max_absent=max_absent
    )


@router.post("/", response_model=SectorReportResponse, status_code=201)
async def create_report(request: SectorReportCreate, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.create_report(request, actor_employee_code=actor_employee_code)


@router.get("/{report_id}", response_model=SectorReportResponse)
async def get_report(report_id: int, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.get_report_for_actor(report_id, actor_employee_code=actor_employee_code)


@router.patch("/{report_id}", response_model=SectorReportResponse)
async def update_report(report_id: int, request: SectorReportUpdate, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.update_report(report_id, request, actor_employee_code=actor_employee_code)


@router.delete("/{report_id}")
async def delete_report(report_id: int, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.delete_report(report_id, actor_employee_code=actor_employee_code)
