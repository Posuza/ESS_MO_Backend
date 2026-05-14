from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PositionBase(BaseModel):
    position_name: str = Field(..., max_length=150)
    field_id: int
    department_id: int
    division_id: int
    sector_id: int
    zone_id: int
    route_id: int
    is_active: bool = True
    position_detail: Optional[str] = Field(None, max_length=150)
    created_by: str = Field(..., max_length=6)


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    position_name: Optional[str] = Field(None, max_length=150)
    field_id: Optional[int] = None
    department_id: Optional[int] = None
    division_id: Optional[int] = None
    sector_id: Optional[int] = None
    zone_id: Optional[int] = None
    route_id: Optional[int] = None
    is_active: Optional[bool] = None
    position_detail: Optional[str] = Field(None, max_length=150)
    updated_by: str = Field(..., max_length=6)


class PositionResponse(PositionBase):
    position_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)
