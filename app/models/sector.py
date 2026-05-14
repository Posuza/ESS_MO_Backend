from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Integer, String, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm import Base


class Sector(Base):
    __tablename__ = "sectors"

    sector_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    sector_name: Mapped[str] = mapped_column(String(150), nullable=False)
    
    field_id: Mapped[int] = mapped_column(Integer, ForeignKey("fields.field_id"), nullable=False)
    department_id: Mapped[int] = mapped_column(Integer, ForeignKey("departments.department_id"), nullable=False)
    division_id: Mapped[int] = mapped_column(Integer, ForeignKey("divisions.division_id"), nullable=False)
    
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
