from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.orm import Base


class MoDailyTransactionDetail2(Base):
    """
    Detail table storing group3 meeting/activity data from the daily report.
    """



    __tablename__ = "mo_daily_transaction_detail_2"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, index=True
    )
    mo_daily_transaction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mo_daily_transactions.mo_daily_transaction_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Item key, e.g. '1'"
    )
    label: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Display label"
    )
    detail: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Meeting/detail description"
    )
    status: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default="normal",
        comment="'normal' | 'warning' | 'danger'",
    )
    note: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="Additional note"
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
            f"<MoDailyTransactionDetail2(id={self.id}, "
            f"txn={self.mo_daily_transaction_id}, "
            f"key={self.key!r}, label={self.label!r})>"
        )