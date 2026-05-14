from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ZoneBase(BaseModel):
    zone_name: str = Field(..., max_length=150)
    field_id: int
    department_id: int
    division_id: int
    sector_id: int
    is_active: bool = True
    created_by: str = Field(..., max_length=6)


class ZoneCreate(ZoneBase):
    pass


class ZoneUpdate(BaseModel):
    zone_name: Optional[str] = Field(None, max_length=150)
    field_id: Optional[int] = None
    department_id: Optional[int] = None
    division_id: Optional[int] = None
    sector_id: Optional[int] = None
    is_active: Optional[bool] = None
    updated_by: str = Field(..., max_length=6)


class ZoneResponse(ZoneBase):
    zone_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)
