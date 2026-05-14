from __future__ import annotations

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String, Text, Enum as SQLAlchemyEnum, ForeignKey, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm import Base


class ApprovedStatusEnum(str, Enum):
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECT = 'REJECT'


class SectorReport(Base):
    __tablename__ = "sector_report"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    sector_id: Mapped[int] = mapped_column(Integer, ForeignKey("sectors.sector_id"), nullable=False)
    
    leave_sick_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    leave_business_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    leave_other_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    absent_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    shift_18_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shift_24_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    shift_36_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    rule_sleep_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rule_use_phone_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rule_no_card_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    warning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    wear_hat_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wear_shirt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wear_pant_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wear_shoe_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    other_Job: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    other_Job_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    other_training: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    other_training_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    other_extral: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    approved_by: Mapped[str] = mapped_column(String(6), nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    approved_status: Mapped[ApprovedStatusEnum] = mapped_column(
        SQLAlchemyEnum(ApprovedStatusEnum), nullable=False, default=ApprovedStatusEnum.PENDING
    )
    approved_remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
