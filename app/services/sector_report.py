from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import func, select, update

from app.core.orm import get_session
from app.models.employee import Employee
from app.models.position import Position
from app.models.sector_report import SectorReport, ApprovedStatusEnum
from app.schemas.sector_report import (
    SectorReportCreate,
    SectorReportUpdate,
)


class SectorReportService:
    @staticmethod
    def _row_to_dict(row: SectorReport) -> dict:
        data = dict(row.__dict__)
        data.pop("_sa_instance_state", None)
        return data

    def _resolve_actor(self, actor_employee_code: str) -> dict:
        with get_session() as session:
            employee = session.execute(
                select(Employee).where(Employee.employee_code == actor_employee_code)
            ).scalars().first()
            if not employee:
                raise HTTPException(status_code=401, detail="Actor employee not found")
            if not employee.is_active:
                raise HTTPException(status_code=403, detail="Inactive employee cannot perform this action")

            position_name = session.execute(
                select(Position.position_name).where(Position.position_id == employee.position_id)
            ).scalars().first()

        return {
            "employee_code": employee.employee_code,
            "role_id": employee.role_id,
            "sector_id": employee.sector_id,
            "position_name": (position_name or "").strip().lower(),
        }

    def _is_manager_or_admin(self, actor: dict) -> bool:
        role_id = actor["role_id"]
        position_name = actor["position_name"]
        if role_id in {1, 2, 9, 99}:
            return True
        return ("manager" in position_name) or ("admin" in position_name)

    def _is_admin(self, actor: dict) -> bool:
        role_id = actor["role_id"]
        position_name = actor["position_name"]
        return (role_id in {1, 9, 99}) or ("admin" in position_name)

    def _enforce_same_sector(self, actor: dict, target_sector_id: Optional[int]) -> None:
        if self._is_admin(actor):
            return
        if target_sector_id is None:
            raise HTTPException(status_code=403, detail="Sector is required for access control")
        if actor["sector_id"] != target_sector_id:
            raise HTTPException(status_code=403, detail="You can only access reports in your own sector")

    def list_reports(
        self,
        actor_employee_code: str,
        sector_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[ApprovedStatusEnum] = None,
        created_by: Optional[str] = None,
        min_absent: Optional[int] = None,
        max_absent: Optional[int] = None
    ) -> list[dict]:
        actor = self._resolve_actor(actor_employee_code)
        if not self._is_admin(actor):
            if sector_id is not None and sector_id != actor["sector_id"]:
                raise HTTPException(status_code=403, detail="You can only list reports in your own sector")
            sector_id = actor["sector_id"]

        with get_session() as session:
            stmt = select(SectorReport)
            
            if sector_id is not None:
                stmt = stmt.where(SectorReport.sector_id == sector_id)
            if start_date:
                stmt = stmt.where(SectorReport.created_at >= start_date)
            if end_date:
                # If end_date is just a date (midnight), include the entire day
                if end_date.hour == 0 and end_date.minute == 0 and end_date.second == 0:
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                stmt = stmt.where(SectorReport.created_at <= end_date)
            if status:
                stmt = stmt.where(SectorReport.approved_status == status)
            if created_by:
                stmt = stmt.where(SectorReport.created_by == created_by)
            if min_absent is not None:
                stmt = stmt.where(SectorReport.absent_count >= min_absent)
            if max_absent is not None:
                stmt = stmt.where(SectorReport.absent_count <= max_absent)

            rows = session.execute(
                stmt.order_by(SectorReport.created_at.desc())
            ).scalars().all()
            print(f"--- list_reports: sector={sector_id}, start={start_date}, end={end_date} ---")
            print(f"Found {len(rows)} records.")
            return [self._row_to_dict(row) for row in rows]

    def create_report(self, payload: SectorReportCreate, actor_employee_code: str) -> dict:
        p = payload.model_dump()
        actor = self._resolve_actor(actor_employee_code)
        self._enforce_same_sector(actor, p["sector_id"])

        with get_session() as session:
            report = SectorReport(
                sector_id=p["sector_id"],
                leave_sick_count=p["leave_sick_count"],
                leave_business_count=p["leave_business_count"],
                leave_other_count=p["leave_other_count"],
                absent_count=p["absent_count"],
                shift_18_count=p["shift_18_count"],
                shift_24_count=p["shift_24_count"],
                shift_36_count=p["shift_36_count"],
                rule_sleep_count=p["rule_sleep_count"],
                rule_use_phone_count=p["rule_use_phone_count"],
                rule_no_card_count=p["rule_no_card_count"],
                warning=p.get("warning"),
                wear_hat_count=p["wear_hat_count"],
                wear_shirt_count=p["wear_shirt_count"],
                wear_pant_count=p["wear_pant_count"],
                wear_shoe_count=p["wear_shoe_count"],
                other_Job=p.get("other_Job"),
                other_Job_count=p["other_Job_count"],
                other_training=p.get("other_training"),
                other_training_count=p["other_training_count"],
                other_extral=p.get("other_extral"),
                # Always start in PENDING on create.
                approved_by="",
                approved_status=ApprovedStatusEnum.PENDING,
                approved_remark=None,
                created_by=p["created_by"],
                created_at=p.get("created_at") or func.now(),
                updated_by=None,
                updated_at=None,
            )
            session.add(report)
            session.commit()
            session.refresh(report)
            ret_data = self._row_to_dict(report)
            print(f"--- create_report: created ID {report.id} for sector {report.sector_id} ---")
            return ret_data

    def get_report(self, report_id: int) -> dict:
        with get_session() as session:
            row = session.execute(
                select(SectorReport).where(SectorReport.id == report_id)
            ).scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="Sector report not found")
        return self._row_to_dict(row)

    def get_report_for_actor(self, report_id: int, actor_employee_code: str) -> dict:
        actor = self._resolve_actor(actor_employee_code)
        row = self.get_report(report_id)
        row_sector_id = row.get("sector_id")
        self._enforce_same_sector(actor, row_sector_id)
        return row

    def update_report(self, report_id: int, payload: SectorReportUpdate, actor_employee_code: str) -> dict:
        actor = self._resolve_actor(actor_employee_code)
        with get_session() as session:
            existing = session.execute(select(SectorReport).where(SectorReport.id == report_id)).scalars().first()
            if not existing:
                raise HTTPException(status_code=404, detail="Sector report not found")
            self._enforce_same_sector(actor, existing.sector_id)

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        is_manager = self._is_manager_or_admin(actor)
        if not is_manager:
            forbidden_for_staff = {"approved_status", "approved_remark", "approved_by", "approved_at", "created_by"}
            passed_forbidden = forbidden_for_staff.intersection(updates.keys())
            if passed_forbidden:
                raise HTTPException(
                    status_code=403,
                    detail=f"Only manager/admin can update approval fields: {', '.join(sorted(passed_forbidden))}",
                )

        updates["updated_at"] = func.now()
        updates["updated_by"] = actor["employee_code"]

        if is_manager and "approved_status" in updates:
            approved_status = updates["approved_status"]
            if approved_status in {ApprovedStatusEnum.APPROVED, ApprovedStatusEnum.REJECT}:
                if "approved_by" not in updates:
                    updates["approved_by"] = actor["employee_code"]
                updates["approved_at"] = func.now()

        with get_session() as session:
            session.execute(update(SectorReport).where(SectorReport.id == report_id).values(**updates))
            session.commit()

        return self.get_report_for_actor(report_id, actor_employee_code=actor_employee_code)

    def delete_report(self, report_id: int, actor_employee_code: str) -> dict:
        actor = self._resolve_actor(actor_employee_code)
        with get_session() as session:
            report = session.execute(
                select(SectorReport).where(SectorReport.id == report_id)
            ).scalars().first()
            
            if not report:
                raise HTTPException(status_code=404, detail="Sector report not found")
            self._enforce_same_sector(actor, report.sector_id)
                
            session.delete(report)
            session.commit()
            
        return {"detail": "Sector report deleted successfully"}
