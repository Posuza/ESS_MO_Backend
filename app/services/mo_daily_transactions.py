from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.models.mo_daily_transaction_detail_1 import MoDailyTransactionDetail1
from app.models.mo_daily_transaction_detail_2 import MoDailyTransactionDetail2
from app.models.mo_daily_transactions import ApprovedStatusEnum, MoDailyTransaction
from app.models.positions import Position
from app.schemas.mo_daily_transactions import (
    MoDailyTransactionCreate,
    MoDailyTransactionResponse,
    MoDailyTransactionUpdate,
    SectorReportProject,
)

# ─── Field mappings ──────────────────────────────────────────────────────────
# Detail 1 fields: (key_in_detail1, field_name_in_flat_payload)
DETAIL_1_FIELDS = [
    ("1.1", "dept_guard_post_count"),
    ("1.2", "dept_current_personnel_count"),
    ("1.3", "dept_missing_regular_count"),
    ("1.4", "dept_missing_personnel_count"),
    ("1.5", "dept_supplement_count"),
    ("1.6", "dept_recruitment_count"),
    ("1.7", "dept_reserve_units_count"),
    ("1.8", "dept_reserve_personnel_count"),
    ("2.1", "leave_personal_count"),
    ("2.2", "leave_sick_count"),
    ("2.3", "leave_absent_count"),
    ("2.4", "leave_deserted_count"),
    ("2.5", "leave_resigned_count"),
    ("2.6", "leave_terminated_count"),
    ("3.1", "shift_18_count"),
    ("3.2", "shift_24_count"),
    ("3.3", "shift_36_count"),
    ("4.1", "training_shift_change_count"),
    ("4.2", "training_planned_count"),
    ("4.3", "training_duty_control_count"),
]
DETAIL_1_BY_KEY = dict(DETAIL_1_FIELDS)
DETAIL_1_BY_NAME = {name: key for key, name in DETAIL_1_FIELDS}

# Legacy field aliases: (standardized_name, legacy_name)
LEGACY_ALIASES = {
    "leave_personal_count": "leave_business_count",
    "leave_absent_count": "absent_count",
    "discipline_phone_count": "rule_use_phone_count",
    "discipline_belt_count": "rule_sleep_count",
    "discipline_badge_count": "rule_no_card_count",
}


class MoDailyTransactionService:
    """Service layer for MO Daily Transaction operations.

    All public methods follow the same pattern:
      - ``db`` is injected by the caller (FastAPI ``Depends(get_db)``)
      - ``actor_employee`` is resolved by the ``@active_employee_required`` decorator
    """

    # ─── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _as_int(value, default: int = 0) -> int:
        if value is None or value == "":
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _is_admin(actor: Employee, db: Session) -> bool:
        """Check if the actor has an admin-level role or position."""
        if actor.role_id in {1, 9, 99}:
            return True
        position = (
            db.execute(
                select(Position.position_name).where(
                    Position.position_id == actor.position_id
                )
            )
            .scalars()
            .first()
        )
        return position is not None and "admin" in position.strip().lower()

    @staticmethod
    def _enforce_same_department(
        actor: Employee, department_id: Optional[int], db: Session
    ) -> None:
        if MoDailyTransactionService._is_admin(actor, db):
            return
        if department_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Department is required",
            )
        if actor.department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access reports in your own department",
            )

    @staticmethod
    def _normalize_flat(data: dict) -> dict:
        """Resolve legacy field aliases into standardized names."""
        n = dict(data)
        for standard, legacy in LEGACY_ALIASES.items():
            if legacy in n and standard not in n:
                n[standard] = n[legacy]
        return n

    @staticmethod
    def _build_response(txn: MoDailyTransaction, db: Session) -> dict:
        """Build a flat response dict from a transaction + its detail rows."""
        data = {
            "id": txn.mo_daily_transaction_id,
            "mo_daily_transaction_id": txn.mo_daily_transaction_id,
            "department_id": txn.department_id,
            "sub_location": txn.sub_location,
            "report_date": txn.created_at.date().isoformat()
            if txn.created_at
            else None,
            "status": txn.approved_status.value if txn.approved_status else None,
            "approved_status": txn.approved_status.value
            if txn.approved_status
            else None,
            "approved_by": txn.approved_by,
            "approved_at": txn.approved_at,
            "approved_remark": txn.approved_remark,
            "created_by": txn.created_by,
            "created_at": txn.created_at,
            "updated_at": txn.updated_at,
            "updated_by": txn.updated_by,
        }

        # Default all detail1 count fields to 0
        for _, name in DETAIL_1_FIELDS:
            data[name] = 0

        # Load detail1 rows
        detail1_rows = (
            db.execute(
                select(MoDailyTransactionDetail1).where(
                    MoDailyTransactionDetail1.mo_daily_transaction_id
                    == txn.mo_daily_transaction_id
                )
            )
            .scalars()
            .all()
        )
        for row in detail1_rows:
            field_name = DETAIL_1_BY_KEY.get(row.field_key)
            if field_name:
                data[field_name] = MoDailyTransactionService._as_int(row.field_value)

        # Populate legacy aliases from standardized values
        for standard, legacy in LEGACY_ALIASES.items():
            data[legacy] = data.get(standard, 0)

        # Load detail2 → projects
        detail2_rows = (
            db.execute(
                select(MoDailyTransactionDetail2)
                .where(
                    MoDailyTransactionDetail2.mo_daily_transaction_id
                    == txn.mo_daily_transaction_id
                )
                .order_by(MoDailyTransactionDetail2.created_at)
            )
            .scalars()
            .all()
        )

        projects = []
        for row in detail2_rows:
            projects.append(
                {
                    "key": row.key,
                    "label": row.label,
                    "detail": row.detail or "",
                    "status": row.status or "normal",
                    "note": row.note or "",
                }
            )
        data["projects"] = projects

        return data

    @staticmethod
    def _replace_detail1(db: Session, txn_id: int, payload: dict) -> None:
        db.execute(
            delete(MoDailyTransactionDetail1).where(
                MoDailyTransactionDetail1.mo_daily_transaction_id == txn_id
            )
        )
        rows = []
        for sort_order, (field_key, field_name) in enumerate(DETAIL_1_FIELDS, start=1):
            rows.append(
                MoDailyTransactionDetail1(
                    mo_daily_transaction_id=txn_id,
                    field_key=field_key,
                    field_value=str(
                        MoDailyTransactionService._as_int(payload.get(field_name))
                    ),
                    sort_order=sort_order,
                )
            )
        db.add_all(rows)

    @staticmethod
    def _replace_detail2(db: Session, txn_id: int, payload: dict) -> None:
        db.execute(
            delete(MoDailyTransactionDetail2).where(
                MoDailyTransactionDetail2.mo_daily_transaction_id == txn_id
            )
        )
        rows = []
        sort_order = 1

        # Projects/meetings
        for project_data in payload.get("projects") or []:
            if hasattr(project_data, "model_dump"):
                project_data = project_data.model_dump()
            elif not isinstance(project_data, dict):
                project_data = dict(project_data)
            rows.append(
                MoDailyTransactionDetail2(
                    mo_daily_transaction_id=txn_id,
                    key=str(project_data.get("key", f"6.{sort_order}")),
                    label=project_data.get("label", ""),
                    detail=project_data.get("detail", ""),
                    status=project_data.get("status", "normal"),
                    note=project_data.get("note", ""),
                )
            )
            sort_order += 1

        db.add_all(rows)

    # ─── Public Methods ───────────────────────────────────────────────────────

    @staticmethod
    def list_reports(
        db: Session,
        actor_employee: Employee,
        department_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[ApprovedStatusEnum] = None,
        created_by: Optional[str] = None,
    ) -> List[dict]:
        if not MoDailyTransactionService._is_admin(actor_employee, db):
            if (
                department_id is not None
                and department_id != actor_employee.department_id
            ):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only list reports in your own department",
                )
            department_id = actor_employee.department_id

        stmt = select(MoDailyTransaction)
        if department_id is not None:
            stmt = stmt.where(MoDailyTransaction.department_id == department_id)
        if start_date:
            stmt = stmt.where(MoDailyTransaction.created_at >= start_date)
        if end_date:
            if end_date.hour == 0 and end_date.minute == 0 and end_date.second == 0:
                end_date = end_date.replace(
                    hour=23, minute=59, second=59, microsecond=999999
                )
            stmt = stmt.where(MoDailyTransaction.created_at <= end_date)
        if status:
            stmt = stmt.where(MoDailyTransaction.approved_status == status)
        if created_by:
            stmt = stmt.where(MoDailyTransaction.created_by == created_by)
        stmt = stmt.order_by(MoDailyTransaction.created_at.desc())

        rows = db.execute(stmt).scalars().all()
        return [MoDailyTransactionService._build_response(r, db) for r in rows]

    @staticmethod
    def create_report(
        db: Session,
        payload: MoDailyTransactionCreate,
        actor_employee: Employee,
    ) -> dict:
        data = MoDailyTransactionService._normalize_flat(payload.model_dump())
        MoDailyTransactionService._enforce_same_department(
            actor_employee, data["department_id"], db
        )

        if data.get("approved_status") in {
            ApprovedStatusEnum.APPROVED.value,
            ApprovedStatusEnum.REJECT.value,
        }:
            data["approved_by"] = (
                data.get("approved_by") or actor_employee.employee_code
            )
            data["approved_at"] = data.get("approved_at") or func.now()

        txn = MoDailyTransaction(
            department_id=data["department_id"],
            sub_location=data.get("sub_location"),
            approved_by=data.get("approved_by"),
            approved_status=data.get("approved_status") or ApprovedStatusEnum.PENDING,
            approved_at=data.get("approved_at"),
            approved_remark=data.get("approved_remark"),
            created_by=data.get("created_by") or actor_employee.employee_code,
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)

        MoDailyTransactionService._replace_detail1(
            db, txn.mo_daily_transaction_id, data
        )
        MoDailyTransactionService._replace_detail2(
            db, txn.mo_daily_transaction_id, data
        )
        db.commit()

        return MoDailyTransactionService._build_response(txn, db)

    @staticmethod
    def get_report(
        db: Session,
        mo_daily_transaction_id: int,
        actor_employee: Employee,
    ) -> dict:
        txn = (
            db.execute(
                select(MoDailyTransaction).where(
                    MoDailyTransaction.mo_daily_transaction_id
                    == mo_daily_transaction_id
                )
            )
            .scalars()
            .first()
        )
        if not txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
            )
        MoDailyTransactionService._enforce_same_department(
            actor_employee, txn.department_id, db
        )
        return MoDailyTransactionService._build_response(txn, db)

    @staticmethod
    def update_report(
        db: Session,
        mo_daily_transaction_id: int,
        payload: MoDailyTransactionUpdate,
        actor_employee: Employee,
    ) -> dict:
        data = MoDailyTransactionService._normalize_flat(
            payload.model_dump(exclude_unset=True)
        )

        txn = (
            db.execute(
                select(MoDailyTransaction).where(
                    MoDailyTransaction.mo_daily_transaction_id
                    == mo_daily_transaction_id
                )
            )
            .scalars()
            .first()
        )
        if not txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
            )
        MoDailyTransactionService._enforce_same_department(
            actor_employee, txn.department_id, db
        )

        # Update main transaction fields
        for field in ("sub_location", "approved_by", "approved_remark"):
            if field in data:
                setattr(txn, field, data[field])
        if "approved_status" in data:
            txn.approved_status = data["approved_status"]
        if data.get("approved_status") in {
            ApprovedStatusEnum.APPROVED.value,
            ApprovedStatusEnum.REJECT.value,
        }:
            if not txn.approved_by:
                txn.approved_by = actor_employee.employee_code
            if not txn.approved_at:
                txn.approved_at = func.now()
        txn.updated_by = actor_employee.employee_code
        txn.updated_at = func.now()

        db.commit()

        # Replace detail rows (only if any detail1 fields are in payload)
        has_detail_fields = any(name in data for _, name in DETAIL_1_FIELDS)
        if has_detail_fields:
            MoDailyTransactionService._replace_detail1(
                db, txn.mo_daily_transaction_id, data
            )

        if "projects" in data:
            MoDailyTransactionService._replace_detail2(
                db, txn.mo_daily_transaction_id, data
            )

        db.commit()
        db.refresh(txn)

        return MoDailyTransactionService._build_response(txn, db)

    @staticmethod
    def delete_report(
        db: Session,
        mo_daily_transaction_id: int,
        actor_employee: Employee,
    ) -> dict:
        txn = (
            db.execute(
                select(MoDailyTransaction).where(
                    MoDailyTransaction.mo_daily_transaction_id
                    == mo_daily_transaction_id
                )
            )
            .scalars()
            .first()
        )
        if not txn:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
            )
        MoDailyTransactionService._enforce_same_department(
            actor_employee, txn.department_id, db
        )

        # CASCADE should handle details, but be explicit
        db.execute(
            delete(MoDailyTransactionDetail1).where(
                MoDailyTransactionDetail1.mo_daily_transaction_id
                == mo_daily_transaction_id
            )
        )
        db.execute(
            delete(MoDailyTransactionDetail2).where(
                MoDailyTransactionDetail2.mo_daily_transaction_id
                == mo_daily_transaction_id
            )
        )
        db.delete(txn)
        db.commit()
        return {"message": "Report deleted successfully"}
