from typing import Optional, List
from fastapi import HTTPException
from sqlalchemy import func, select, update

from app.core.orm import get_session
from app.models.sector import Sector
from app.schemas.sector import SectorCreate, SectorUpdate


class SectorService:
    def list_sectors(
        self,
        field_id: Optional[int] = None,
        department_id: Optional[int] = None,
        division_id: Optional[int] = None
    ) -> list[dict]:
        with get_session() as session:
            stmt = select(Sector)
            
            if field_id is not None:
                stmt = stmt.where(Sector.field_id == field_id)
            if department_id is not None:
                stmt = stmt.where(Sector.department_id == department_id)
            if division_id is not None:
                stmt = stmt.where(Sector.division_id == division_id)
                
            rows = session.execute(
                stmt.order_by(Sector.sector_id.desc())
            ).scalars().all()
            return [row.__dict__ for row in rows]

    def create_sector(self, payload: SectorCreate) -> dict:
        p = payload.model_dump()
        
        with get_session() as session:
            sector_entry = Sector(
                sector_name=p["sector_name"],
                field_id=p["field_id"],
                department_id=p["department_id"],
                division_id=p["division_id"],
                created_by=p["created_by"],
                updated_by=p["created_by"],  # Mirror created_by on init
                created_at=func.now(),
                updated_at=func.now()
            )
            session.add(sector_entry)
            session.commit()
            session.refresh(sector_entry)
            return sector_entry.__dict__

    def get_sector(self, sector_id: int) -> dict:
        with get_session() as session:
            row = session.execute(
                select(Sector).where(Sector.sector_id == sector_id)
            ).scalars().first()
        if not row:
            raise HTTPException(status_code=404, detail="Sector not found")
        return row.__dict__

    def update_sector(self, sector_id: int, payload: SectorUpdate) -> dict:
        with get_session() as session:
            existing = session.execute(
                select(Sector.sector_id).where(Sector.sector_id == sector_id)
            ).first()
            if not existing:
                raise HTTPException(status_code=404, detail="Sector not found")

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        updates["updated_at"] = func.now()

        with get_session() as session:
            session.execute(update(Sector).where(Sector.sector_id == sector_id).values(**updates))
            session.commit()

        return self.get_sector(sector_id)

    def delete_sector(self, sector_id: int) -> dict:
        with get_session() as session:
            sector_entry = session.execute(
                select(Sector).where(Sector.sector_id == sector_id)
            ).scalars().first()
            
            if not sector_entry:
                raise HTTPException(status_code=404, detail="Sector not found")
                
            session.delete(sector_entry)
            session.commit()
            
        return {"detail": "Sector deleted successfully"}
