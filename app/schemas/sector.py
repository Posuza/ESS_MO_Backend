from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SectorBase(BaseModel):
    sector_name: str = Field(..., max_length=150)
    field_id: int
    department_id: int
    division_id: int
    created_by: str = Field(..., max_length=6)


class SectorCreate(SectorBase):
    pass


class SectorUpdate(BaseModel):
    sector_name: Optional[str] = Field(None, max_length=150)
    field_id: Optional[int] = None
    department_id: Optional[int] = None
    division_id: Optional[int] = None
    updated_by: str = Field(..., max_length=6)


class SectorResponse(SectorBase):
    sector_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)
