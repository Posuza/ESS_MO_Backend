from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, String, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm import Base


class Position(Base):
    __tablename__ = "positions"

    position_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    position_name: Mapped[str] = mapped_column(String(150), nullable=False)
    
    field_id: Mapped[int] = mapped_column(Integer, ForeignKey("fields.field_id"), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.department_id"), nullable=False)
    division_id: Mapped[int] = mapped_column(Integer, ForeignKey("divisions.division_id"), nullable=False)
    sector_id: Mapped[int] = mapped_column(Integer, ForeignKey("sectors.sector_id"), nullable=True)
    zone_id: Mapped[int] = mapped_column(Integer, ForeignKey("zones.zone_id"), nullable=True)
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("routes.route_id"), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('1'))
    position_detail: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(6)'),
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(6)'),
        server_onupdate=text('CURRENT_TIMESTAMP(6)'),
        default=func.now(),
        onupdate=func.now(),
    )
    
    created_by: Mapped[str] = mapped_column(String(6), ForeignKey("employees.employee_code"), nullable=False)
    updated_by: Mapped[Optional[str]] = mapped_column(String(6), ForeignKey("employees.employee_code"), nullable=True)
