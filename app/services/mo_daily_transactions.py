from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.employees import Employee
from app.models.mo_daily_transaction_details import MoDailyTransactionDetail1
from app.models.mo_daily_transaction_project import MoDailyTransactionProject
from app.models.mo_daily_transactions import ApprovedStatusEnum, MoDailyTransaction
from app.models.mo_transaction_discipline_warning import MoTransactionDisciplineWarning
from app.models.positions import Position
from app.schemas.mo_daily_transactions import (
    MoDailyTransactionCreate,
    MoDailyTransactionResponse,
    MoDailyTransactionUpdate,
    SectorReportDiscipline,
    SectorReportProject,
)

# ─── All Detail 1 column names (map directly to model columns) ────────────
DETAIL_1_COLUMNS = [
    # dept
    "dept_guard_post_count",
    "dept_current_personnel_count",
    "dept_missing_regular_count",
    "dept_missing_personnel_count",
    "dept_supplement_count",
    "dept_recruitment_count",
    "dept_reserve_units_count",
    "dept_reserve_personnel_count",
    "dept_extra_1",
    "dept_extra_2",
    "dept_extra_3",
    "dept_extra_4",
    "dept_extra_5",
    # leave
    "leave_personal_count",
    "leave_sick_count",
    "leave_absent_count",
    "leave_deserted_count",
    "leave_resigned_count",
    "leave_terminated_count",
    "leave_extra_1",
    "leave_extra_2",
    "leave_extra_3",
    "leave_extra_4",
    "leave_extra_5",
    # shift
    "shift_18_count",
    "shift_24_count",
    "shift_36_count",
    "shift_extra_1",
    "shift_extra_2",
    "shift_extra_3",
    "shift_extra_4",
    "shift_extra_5",
    # training
    "training_shift_change_count",
    "training_planned_count",
    "training_duty_control_count",
    "training_extra_1",
    "training_extra_2",
    "training_extra_3",
    "training_extra_4",
    "training_extra_5",
]
DETAIL_1_SET = set(DETAIL_1_COLUMNS)


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
        """Return a mutable copy of data."""
        return dict(data)

    @staticmethod
    def _build_response(txn: MoDailyTransaction, db: Session) -> dict:
        """Build a flat response dict from a transaction + its detail rows."""
        data = {
            "id": txn.mo_daily_transaction_id,
            "mo_daily_transaction_id": txn.mo_daily_transaction_id,
            "department_id": txn.department_id,
            "department_name": txn.department_name,
            "division_id": txn.division_id,
            "division_name": txn.division_name,
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

        # Default all detail1 fields to 0
        for col in DETAIL_1_COLUMNS:
            data[col] = 0

        # Load the single detail1 row (1:1 with transaction)
        d1 = (
            db.execute(
                select(MoDailyTransactionDetail1).where(
                    MoDailyTransactionDetail1.mo_daily_transaction_id
                    == txn.mo_daily_transaction_id
                )
            )
            .scalars()
            .first()
        )
        if d1:
            for col in DETAIL_1_COLUMNS:
                data[col] = MoDailyTransactionService._as_int(getattr(d1, col, "0"))

        # Load disciplines
        discipline_rows = (
            db.execute(
                select(MoTransactionDisciplineWarning)
                .where(
                    MoTransactionDisciplineWarning.mo_daily_transaction_id
                    == txn.mo_daily_transaction_id
                )
                .order_by(MoTransactionDisciplineWarning.created_at)
            )
            .scalars()
            .all()
        )

        disciplines = []
        for row in discipline_rows:
            disciplines.append(
                {
                    "key": row.key,
                    "label": row.label,
                    "value": MoDailyTransactionService._as_int(row.value),
                }
            )
        data["disciplines"] = disciplines

        # Load projects
        project_rows = (
            db.execute(
                select(MoDailyTransactionProject)
                .where(
                    MoDailyTransactionProject.mo_daily_transaction_id
                    == txn.mo_daily_transaction_id
                )
                .order_by(MoDailyTransactionProject.created_at)
            )
            .scalars()
            .all()
        )

        projects = []
        for row in project_rows:
            projects.append(
                {
                    "name": row.project_name,
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
        values = {"mo_daily_transaction_id": txn_id}
        for col in DETAIL_1_COLUMNS:
            values[col] = MoDailyTransactionService._as_int(payload.get(col))
        db.add(MoDailyTransactionDetail1(**values))

    @staticmethod
    def _get_next_discipline_custom_id(db: Session) -> int:
        """Find the biggest numeric suffix from discipline_custom_N keys."""
        rows = (
            db.execute(
                select(MoTransactionDisciplineWarning.key).where(
                    MoTransactionDisciplineWarning.key.like("discipline_custom_%")
                )
            )
            .scalars()
            .all()
        )
        max_num = 0
        for key in rows:
            parts = key.rsplit("_", 1)
            if len(parts) == 2:
                try:
                    num = int(parts[1])
                    if num > max_num:
                        max_num = num
                except ValueError:
                    pass
        return max_num

    @staticmethod
    def _replace_disciplines(db: Session, txn_id: int, payload: dict) -> None:
        db.execute(
            delete(MoTransactionDisciplineWarning).where(
                MoTransactionDisciplineWarning.mo_daily_transaction_id == txn_id
            )
        )
        rows = []
        next_custom_id = MoDailyTransactionService._get_next_discipline_custom_id(db)
        for disc_data in payload.get("disciplines") or []:
            if hasattr(disc_data, "model_dump"):
                disc_data = disc_data.model_dump()
            elif not isinstance(disc_data, dict):
                disc_data = dict(disc_data)

            # Auto-generate key if null, empty, or starts with "discipline_custom_" or "auto_gen"
            raw_key = str(disc_data.get("key", "") or "")
            if not raw_key or raw_key.startswith(("discipline_custom_", "auto_gen")):
                next_custom_id += 1
                raw_key = f"discipline_custom_{next_custom_id}"

            rows.append(
                MoTransactionDisciplineWarning(
                    mo_daily_transaction_id=txn_id,
                    key=raw_key,
                    label=disc_data.get("label", ""),
                    value=MoDailyTransactionService._as_int(disc_data.get("value")),
                )
            )
        db.add_all(rows)

    @staticmethod
    def _replace_detail2(db: Session, txn_id: int, payload: dict) -> None:
        db.execute(
            delete(MoDailyTransactionProject).where(
                MoDailyTransactionProject.mo_daily_transaction_id == txn_id
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
                MoDailyTransactionProject(
                    mo_daily_transaction_id=txn_id,
                    project_name=project_data.get("name", ""),
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
            ApprovedStatusEnum.REJECTED.value,
        }:
            data["approved_by"] = (
                data.get("approved_by") or actor_employee.employee_code
            )
            data["approved_at"] = data.get("approved_at") or func.now()

        txn = MoDailyTransaction(
            department_id=data["department_id"],
            department_name=data.get("department_name", ""),
            division_id=data.get("division_id"),
            division_name=data.get("division_name"),
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
        MoDailyTransactionService._replace_disciplines(
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
        for field in ("division_id", "division_name", "approved_by", "approved_remark"):
            if field in data:
                setattr(txn, field, data[field])
        if "approved_status" in data:
            txn.approved_status = data["approved_status"]
        if data.get("approved_status") in {
            ApprovedStatusEnum.APPROVED.value,
            ApprovedStatusEnum.REJECTED.value,
        }:
            if not txn.approved_by:
                txn.approved_by = actor_employee.employee_code
            if not txn.approved_at:
                txn.approved_at = func.now()
        txn.updated_by = actor_employee.employee_code
        txn.updated_at = func.now()

        db.commit()

        # Replace detail rows (only if any detail1 fields are in payload)
        has_detail_fields = any(name in data for name in DETAIL_1_COLUMNS)
        if has_detail_fields:
            MoDailyTransactionService._replace_detail1(
                db, txn.mo_daily_transaction_id, data
            )

        if "disciplines" in data:
            MoDailyTransactionService._replace_disciplines(
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
            delete(MoTransactionDisciplineWarning).where(
                MoTransactionDisciplineWarning.mo_daily_transaction_id
                == mo_daily_transaction_id
            )
        )
        db.execute(
            delete(MoDailyTransactionProject).where(
                MoDailyTransactionProject.mo_daily_transaction_id
                == mo_daily_transaction_id
            )
        )
        db.delete(txn)
        db.commit()
        return {"message": "Report deleted successfully"}
