from fastapi import HTTPException
from sqlalchemy import func, select, update

from app.core.orm import get_session
from app.models.field import FieldModel
from app.schemas.field import FieldCreate, FieldUpdate
from app.core.registries.error_registry import ERROR_REGISTRY


class FieldService:
    def list_fields(self) -> list[dict]:
        with get_session() as session:
            rows = session.execute(
                select(FieldModel).order_by(FieldModel.field_id.desc())
            ).scalars().all()
            return [row.__dict__ for row in rows]

    def create_field(self, payload: FieldCreate) -> dict:
        p = payload.model_dump()
        
        with get_session() as session:
            field_entry = FieldModel(
                field_name=p["field_name"],
                is_active=p["is_active"],
                created_by=p["created_by"],
                updated_by=p["created_by"],  # Can mirror created_by initially
                created_at=func.now(),
                updated_at=func.now()
            )
            session.add(field_entry)
            session.commit()
            session.refresh(field_entry)
            return field_entry.__dict__

    def get_field(self, field_id: int) -> dict:
        with get_session() as session:
            row = session.execute(
                select(FieldModel).where(FieldModel.field_id == field_id)
            ).scalars().first()
        if not row:
            entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2002"]
            raise HTTPException(
                status_code=entry["http_status"],
                detail=entry["message"]  # Use registry message
            )
        return row.__dict__

    def update_field(self, field_id: int, payload: FieldUpdate) -> dict:
        with get_session() as session:
            existing = session.execute(
                select(FieldModel.field_id).where(FieldModel.field_id == field_id)
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
            session.execute(update(FieldModel).where(FieldModel.field_id == field_id).values(**updates))
            session.commit()

        return self.get_field(field_id)

    def delete_field(self, field_id: int) -> dict:
        with get_session() as session:
            field_entry = session.execute(
                select(FieldModel).where(FieldModel.field_id == field_id)
            ).scalars().first()
            
            if not field_entry:
                entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2002"]
                raise HTTPException(
                    status_code=entry["http_status"],
                    detail=entry["message"]  # Use registry message
                )
                
            session.delete(field_entry)
            session.commit()
            
        return {"detail": "Field deleted successfully"}
