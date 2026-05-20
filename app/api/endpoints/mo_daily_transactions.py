from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Query, Request

from app.core.request_actor import extract_actor_employee_code
from app.schemas.mo_daily_transactions import (
    MoDailyTransactionCreate,
    MoDailyTransactionUpdate,
    MoDailyTransactionResponse,
    ApprovedStatusEnum,
)
from app.services.mo_daily_transactions import MoDailyTransactionService

router = APIRouter(prefix="/mo-daily-transactions", tags=["MO Daily Transactions"])
service = MoDailyTransactionService()


@router.get("/", response_model=List[MoDailyTransactionResponse])
async def list_reports(
    http_request: Request,
    department_id: Optional[int] = Query(None),
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
        department_id=department_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        created_by=created_by,
        min_absent=min_absent,
        max_absent=max_absent
    )


@router.post("/", response_model=MoDailyTransactionResponse, status_code=201)
async def create_report(request: MoDailyTransactionCreate, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.create_report(request, actor_employee_code=actor_employee_code)


@router.get("/{mo_daily_transaction_id}", response_model=MoDailyTransactionResponse)
async def get_report(mo_daily_transaction_id: int, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.get_report_for_actor(mo_daily_transaction_id, actor_employee_code=actor_employee_code)


@router.patch("/{mo_daily_transaction_id}", response_model=MoDailyTransactionResponse)
async def update_report(mo_daily_transaction_id: int, request: MoDailyTransactionUpdate, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.update_report(mo_daily_transaction_id, request, actor_employee_code=actor_employee_code)


@router.delete("/{mo_daily_transaction_id}")
async def delete_report(mo_daily_transaction_id: int, http_request: Request):
    actor_employee_code = extract_actor_employee_code(http_request)
    return service.delete_report(mo_daily_transaction_id, actor_employee_code=actor_employee_code)
