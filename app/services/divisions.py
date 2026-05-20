from fastapi import HTTPException
from sqlalchemy import func, select, update

from app.core.orm import get_session
from app.models.divisions import Division
from app.schemas.divisions import DivisionCreate, DivisionUpdate
from app.core.registries.error_registry import ERROR_REGISTRY


class DivisionService:
    def list_divisions(self) -> list[dict]:
        with get_session() as session:
            rows = session.execute(
                select(Division).order_by(Division.division_id.desc())
            ).scalars().all()
            return [row.__dict__ for row in rows]

    def create_division(self, payload: DivisionCreate) -> dict:
        p = payload.model_dump()
        
        with get_session() as session:
            division_entry = Division(
                division_name=p["division_name"],
                field_id=p["field_id"],
                department_id=p["department_id"],
                is_active=p["is_active"],
                created_by=p["created_by"],
                updated_by=p["created_by"],  # Can mirror created_by initially
                created_at=func.now(),
                updated_at=func.now()
            )
            session.add(division_entry)
            session.commit()
            session.refresh(division_entry)
            return division_entry.__dict__

    def get_division(self, division_id: int) -> dict:
        with get_session() as session:
            row = session.execute(
                select(Division).where(Division.division_id == division_id)
            ).scalars().first()
        if not row:
            entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2002"]
            raise HTTPException(
                status_code=entry["http_status"],
                detail=entry["message"]  # Use registry message
            )
        return row.__dict__

    def update_division(self, division_id: int, payload: DivisionUpdate) -> dict:
        with get_session() as session:
            existing = session.execute(
                select(Division.division_id).where(Division.division_id == division_id)
            ).first()
            if not existing:
                entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2002"]
                raise HTTPException(
                    status_code=entry["http_status"],
                    detail=entry["message"]  # Use registry message
                )

        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2001"]
            raise HTTPException(
                status_code=entry["http_status"],
                detail=entry["message"]  # Use registry message
            )

        updates["updated_at"] = func.now()

        with get_session() as session:
            session.execute(update(Division).where(Division.division_id == division_id).values(**updates))
            session.commit()

        return self.get_division(division_id)

    def delete_division(self, division_id: int) -> dict:
        with get_session() as session:
            division_entry = session.execute(
                select(Division).where(Division.division_id == division_id)
            ).scalars().first()
            
            if not division_entry:
                entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2002"]
                raise HTTPException(
                    status_code=entry["http_status"],
                    detail=entry["message"]  # Use registry message
                )
                
            session.delete(division_entry)
            session.commit()
            
        return {"detail": "Division deleted successfully"}
