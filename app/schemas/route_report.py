from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict
from app.models.route_report import ApprovedStatusEnum


class RouteReportBase(BaseModel):
    route_id: Optional[int] = None
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
    other_Job: Optional[str] = None
    other_Job_count: int = 0
    other_training: Optional[str] = None
    other_training_count: int = 0
    other_extral: Optional[str] = None
    approved_by: Optional[str] = None
    approved_status: ApprovedStatusEnum = ApprovedStatusEnum.PENDING
    approved_remark: Optional[str] = None
    created_by: str

    model_config = ConfigDict(extra="forbid")


class RouteReportCreate(RouteReportBase):
    route_report_id: str
    created_at: Optional[datetime] = None


class RouteReportUpdate(BaseModel):
    route_id: Optional[int] = None
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
    other_Job: Optional[str] = None
    other_Job_count: Optional[int] = None
    other_training: Optional[str] = None
    other_training_count: Optional[int] = None
    other_extral: Optional[str] = None
    approved_status: Optional[ApprovedStatusEnum] = None
    approved_remark: Optional[str] = None
    approved_by: Optional[str] = None
    created_by: Optional[str] = None

    model_config = ConfigDict(extra="forbid")


class RouteReportResponse(RouteReportBase):
    route_report_id: str
    approved_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    updated_by: Optional[str]

    model_config = ConfigDict(from_attributes=True)
