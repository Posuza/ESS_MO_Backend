from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import Date, DateTime, Integer, String, Text, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm import Base


class PositionChangeLog(Base):
    __tablename__ = "position_change_logs"

    position_log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    
    employee_code: Mapped[str] = mapped_column(String(6), ForeignKey("employees.employee_code"), nullable=False)
    
    from_field: Mapped[str] = mapped_column(String(50), nullable=False)
    from_department: Mapped[str] = mapped_column(String(50), nullable=False)
    from_division: Mapped[str] = mapped_column(String(50), nullable=False)
    from_routes: Mapped[str] = mapped_column(String(50), nullable=False)
    from_position: Mapped[str] = mapped_column(String(50), nullable=False)
    from_shift: Mapped[str] = mapped_column(String(50), nullable=False)
    
    to_field: Mapped[str] = mapped_column(String(50), nullable=False)
    to_department: Mapped[str] = mapped_column(String(50), nullable=False)
    to_division: Mapped[str] = mapped_column(String(50), nullable=False)
    to_routes: Mapped[str] = mapped_column(String(50), nullable=False)
    to_position: Mapped[str] = mapped_column(String(50), nullable=False)
    to_shift: Mapped[str] = mapped_column(String(50), nullable=False)
    
    transition_type: Mapped[str] = mapped_column(String(50), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP(6)'),
        default=func.now(),
    )
    created_by: Mapped[str] = mapped_column(String(6), ForeignKey("employees.employee_code"), nullable=False)
