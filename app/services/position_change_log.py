from fastapi import HTTPException
from sqlalchemy import func, select, update

from app.core.orm import get_session
from app.models.position_change_log import PositionChangeLog
from app.schemas.position_change_log import PositionChangeLogCreate, PositionChangeLogUpdate


class PositionChangeLogService:
    def list_logs(self) -> list[dict]:
        with get_session() as session:
            rows = session.execute(
                select(PositionChangeLog).order_by(PositionChangeLog.log_id.desc())
            ).scalars().all()
            return [row.__dict__ for row in rows]

    def create_log(self, payload: PositionChangeLogCreate) -> dict:
        p = payload.model_dump()
        
        with get_session() as session:
            log_entry = PositionChangeLog(
                employee_code=p["employee_code"],
                from_field=p["from_field"],
                from_department=p["from_department"],
                from_division=p["from_division"],
                from_sector=p["from_sector"],
                from_zone=p["from_zone"],
                from_routes=p["from_routes"],
                from_position=p["from_position"],
                from_shift=p["from_shift"],
                to_field=p["to_field"],
                to_department=p["to_department"],
                to_division=p["to_division"],
                to_sector=p["to_sector"],
                to_zone=p["to_zone"],
                to_routes=p["to_routes"],
                to_position=p["to_position"],
                to_shift=p["to_shift"],
                transition_type=p["transition_type"],
                effective_date=p["effective_date"],
                detail=p.get("detail"),
                created_by=p["created_by"],
                created_at=func.now()
            )
            session.add(log_entry)
            session.commit()
            session.refresh(log_entry)
            return log_entry.__dict__

    def get_log(self, log_id: int) -> dict:
        with get_session() as session:
            row = session.execute(
                select(PositionChangeLog).where(PositionChangeLog.log_id == log_id)
            ).scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="Position Change Log not found")
        return row.__dict__

    def update_log(self, log_id: int, payload: PositionChangeLogUpdate) -> dict:
        with get_session() as session:
            existing = session.execute(
                select(PositionChangeLog.log_id).where(PositionChangeLog.log_id == log_id)
            ).first()
            if not existing:
                raise HTTPException(status_code=404, detail="Position Change Log not found")

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        with get_session() as session:
            session.execute(update(PositionChangeLog).where(PositionChangeLog.log_id == log_id).values(**updates))
            session.commit()

        return self.get_log(log_id)

    def delete_log(self, log_id: int) -> dict:
        with get_session() as session:
            log_entry = session.execute(
                select(PositionChangeLog).where(PositionChangeLog.log_id == log_id)
            ).scalars().first()
            
            if not log_entry:
                raise HTTPException(status_code=404, detail="Position Change Log not found")
                
            session.delete(log_entry)
            session.commit()
            
        return {"detail": "Position Change Log deleted successfully"}
