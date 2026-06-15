from pydantic import BaseModel, ConfigDict


class DivisionResponse(BaseModel):
    """Response schema for a division."""

    division_id: int
    division_name: str
    department_id: int

    model_config = ConfigDict(from_attributes=True)
