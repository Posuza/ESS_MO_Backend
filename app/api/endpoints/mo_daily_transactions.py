from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.dependencies import active_employee_required
from app.core.db.session import get_db
from app.models.employees import Employee
from app.models.mo_daily_transactions import ApprovedStatusEnum
from app.schemas.mo_daily_transactions import (
    MoDailyTransactionCreate,
    MoDailyTransactionResponse,
    MoDailyTransactionUpdate,
)
from app.services.mo_daily_transactions import MoDailyTransactionService

router = APIRouter()


@router.get("/", response_model=List[MoDailyTransactionResponse])
@active_employee_required
async def api_list_reports(
    http_request: Request,
    department_id: Optional[int] = Query(None),
    division_id: Optional[int] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[ApprovedStatusEnum] = Query(None),
    created_by: Optional[str] = Query(None),
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    return MoDailyTransactionService.list_reports(
        db=db,
        actor_employee=current_employee,
        department_id=department_id,
        division_id=division_id,
        start_date=start_date,
        end_date=end_date,
        status=status,
        created_by=created_by,
    )


@router.get("/employee-position-active")
@active_employee_required
async def api_check_employee_position_active(
    http_request: Request,
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    """
    Check if the authenticated employee's position is active.
    Returns ``{"position_id": ..., "is_active": true|false}``.
    This is a fresh DB query — does NOT rely on cached login data.
    """
    return MoDailyTransactionService.check_employee_position_active(
        actor_employee=current_employee,
        db=db,
    )


@router.get("/available-report-divisions")
@active_employee_required
async def api_list_available_report_divisions(
    http_request: Request,
    department_id: int = Query(...),
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    return MoDailyTransactionService.list_available_report_divisions(
        db=db,
        actor_employee=current_employee,
        department_id=department_id,
    )


@router.post(
    "/",
    response_model=MoDailyTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
@active_employee_required
async def api_create_report(
    request: MoDailyTransactionCreate,
    http_request: Request,
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    return MoDailyTransactionService.create_report(
        db=db,
        payload=request,
        actor_employee=current_employee,
    )


@router.get(
    "/{mo_daily_transaction_id}",
    response_model=MoDailyTransactionResponse,
)
@active_employee_required
async def api_get_report(
    mo_daily_transaction_id: int,
    http_request: Request,
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    return MoDailyTransactionService.get_report(
        db=db,
        mo_daily_transaction_id=mo_daily_transaction_id,
        actor_employee=current_employee,
    )


@router.patch(
    "/{mo_daily_transaction_id}",
    response_model=MoDailyTransactionResponse,
)
@active_employee_required
async def api_update_report(
    mo_daily_transaction_id: int,
    request: MoDailyTransactionUpdate,
    http_request: Request,
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    return MoDailyTransactionService.update_report(
        db=db,
        mo_daily_transaction_id=mo_daily_transaction_id,
        payload=request,
        actor_employee=current_employee,
    )


@router.delete("/{mo_daily_transaction_id}", status_code=status.HTTP_200_OK)
@active_employee_required
async def api_delete_report(
    mo_daily_transaction_id: int,
    http_request: Request,
    current_employee: Employee = None,
    db: Session = Depends(get_db),
):
    return MoDailyTransactionService.delete_report(
        db=db,
        mo_daily_transaction_id=mo_daily_transaction_id,
        actor_employee=current_employee,
    )
