from pydantic import BaseModel, Field


class EssProfileRequest(BaseModel):
    """ESS identity used only to bootstrap the local employee profile."""

    employee_id: str = Field(..., min_length=1, max_length=64)
