from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm import Base


class MoDailyTransactionDetail1(Base):
    """
    Detail table storing the department personnel counts from group1&2 of the daily report.
    """

    __tablename__ = "mo_daily_transaction_detail_1"

    mo_daily_transaction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mo_daily_transactions.mo_daily_transaction_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    dept_guard_post_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="จำนวนจุดตรวจ"
    )
    dept_current_personnel_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="กำลังพลปัจจุบัน"
    )
    dept_missing_regular_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ขาดประจำการ"
    )
    dept_missing_personnel_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="กำลังพลขาด"
    )
    dept_supplement_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="กำลังพลแทน"
    )
    dept_recruitment_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="กำลังพลใหม่"
    )
    dept_reserve_units_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="หน่วยทหารพราน"
    )
    dept_reserve_personnel_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="กำลังพลทหารพราน"
    )
    leave_personal_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ลากิจ"
    )
    leave_sick_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ลาป่วย"
    )
    leave_absent_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ลากิจขาด"
    )
    leave_deserted_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="หลบหนี"
    )
    leave_resigned_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ลาออก"
    )
    leave_terminated_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ถูกไล่ออก"
    )
    shift_18_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="เวร18ชม"
    )
    shift_24_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="เวร24ชม"
    )
    shift_36_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="เวร36ชม"
    )
    training_shift_change_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ฝึกปรับเวร"
    )
    training_planned_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ฝึกตามแผน"
    )
    training_duty_control_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="ฝึกควบคุมหน้าที่"
    )
    discipline_phone_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="วินัยใช้โทรศัพท์"
    )
    discipline_belt_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="วินัยเข็มขัด"
    )
    discipline_badge_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="วินัยเครื่องหมาย"
    )
    discipline_uniform_count: Mapped[str] = mapped_column(
        String(20), nullable=False, default="0", comment="วินัยเครื่องแบบ"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        server_onupdate=text("CURRENT_TIMESTAMP"),
        default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return (
            f"<MoDailyTransactionDetail1(txn={self.mo_daily_transaction_id}, "
            f"guard_post={self.dept_guard_post_count}, "
            f"personnel={self.dept_current_personnel_count})>"
        )
