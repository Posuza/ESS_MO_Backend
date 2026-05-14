from fastapi import HTTPException
from sqlalchemy import func, select, update

from app.core.orm import get_session
from app.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneUpdate


class ZoneService:
    def list_zones(self) -> list[dict]:
        with get_session() as session:
            rows = session.execute(
                select(Zone).order_by(Zone.zone_id.desc())
            ).scalars().all()
            return [row.__dict__ for row in rows]

    def create_zone(self, payload: ZoneCreate) -> dict:
        p = payload.model_dump()
        
        with get_session() as session:
            zone_entry = Zone(
                zone_name=p["zone_name"],
                field_id=p["field_id"],
                department_id=p["department_id"],
                division_id=p["division_id"],
                sector_id=p["sector_id"],
                is_active=p["is_active"],
                created_by=p["created_by"],
                updated_by=p["created_by"],  # Mirror created_by on init
                created_at=func.now(),
                updated_at=func.now()
            )
            session.add(zone_entry)
            session.commit()
            session.refresh(zone_entry)
            return zone_entry.__dict__

    def get_zone(self, zone_id: int) -> dict:
        with get_session() as session:
            row = session.execute(
                select(Zone).where(Zone.zone_id == zone_id)
            ).scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="Zone not found")
        return row.__dict__

    def update_zone(self, zone_id: int, payload: ZoneUpdate) -> dict:
        with get_session() as session:
            existing = session.execute(
                select(Zone.zone_id).where(Zone.zone_id == zone_id)
            ).first()
            if not existing:
                raise HTTPException(status_code=404, detail="Zone not found")

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        updates["updated_at"] = func.now()

        with get_session() as session:
            session.execute(update(Zone).where(Zone.zone_id == zone_id).values(**updates))
            session.commit()

        return self.get_zone(zone_id)

    def delete_zone(self, zone_id: int) -> dict:
        with get_session() as session:
            zone_entry = session.execute(
                select(Zone).where(Zone.zone_id == zone_id)
            ).scalars().first()
            
            if not zone_entry:
                raise HTTPException(status_code=404, detail="Zone not found")
                
            session.delete(zone_entry)
            session.commit()
            
        return {"detail": "Zone deleted successfully"}
