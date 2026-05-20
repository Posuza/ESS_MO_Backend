from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.models.mo_daily_transactions import ApprovedStatusEnum


class MoDailyTransactionBase(BaseModel):
    department_id: int
    leave_sick_count: int = 0
    leave_business_count: int = 0
    leave_other_count: int = 0
    absent_count: int = 0
    shift_18_count: int = 0
    shift_24_count: int = 0
    shift_36_count: int = 0
    rule_sleep_count: int = 0
    rule_use_phone_count: int = 0
    rule_no_card_count: int = 0
    warning: Optional[str] = None
    wear_hat_count: int = 0
    wear_shirt_count: int = 0
    wear_pant_count: int = 0
    wear_shoe_count: int = 0
    other_job: Optional[str] = None
    other_job_count: int = 0
    other_training: Optional[str] = None
    other_training_count: int = 0
    other_extral: Optional[str] = None
    approved_by: Optional[str] = None
    approved_status: ApprovedStatusEnum = ApprovedStatusEnum.PENDING
    approved_remark: Optional[str] = None
    created_by: str

    model_config = ConfigDict(extra="forbid")


class MoDailyTransactionCreate(MoDailyTransactionBase):
    created_at: Optional[datetime] = None


class MoDailyTransactionUpdate(BaseModel):
    department_id: Optional[int] = None
    leave_sick_count: Optional[int] = None
    leave_business_count: Optional[int] = None
    leave_other_count: Optional[int] = None
    absent_count: Optional[int] = None
    shift_18_count: Optional[int] = None
    shift_24_count: Optional[int] = None
    shift_36_count: Optional[int] = None
    rule_sleep_count: Optional[int] = None
    rule_use_phone_count: Optional[int] = None
    rule_no_card_count: Optional[int] = None
    warning: Optional[str] = None
    wear_hat_count: Optional[int] = None
    wear_shirt_count: Optional[int] = None
    wear_pant_count: Optional[int] = None
    wear_shoe_count: Optional[int] = None
    other_job: Optional[str] = None
    other_job_count: Optional[int] = None
    other_training: Optional[str] = None
    other_training_count: Optional[int] = None
    other_extral: Optional[str] = None
    approved_status: Optional[ApprovedStatusEnum] = None
    approved_remark: Optional[str] = None
    approved_by: Optional[str] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class MoDailyTransactionResponse(MoDailyTransactionBase):
    mo_daily_transaction_id: int
    approved_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)
