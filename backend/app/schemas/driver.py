"""Driver schemas."""
from typing import Optional

from pydantic import BaseModel, Field


class DriverCreate(BaseModel):
    """Create driver."""

    organization_id: int
    name: str = Field(..., min_length=1, strip_whitespace=True)
    user_id: str = Field(..., min_length=1, strip_whitespace=True)
    mobile: Optional[str] = None
    password: str = Field(..., min_length=1)
    license_number: Optional[str] = None
    active: bool = True


class DriverUpdate(BaseModel):
    """Update driver."""

    name: Optional[str] = None
    user_id: Optional[str] = None
    mobile: Optional[str] = None
    password: Optional[str] = None
    license_number: Optional[str] = None
    active: Optional[bool] = None


class DriverResponse(BaseModel):
    """Driver response."""

    id: int
    organization_id: int
    name: str
    user_id: str
    mobile: Optional[str] = None
    license_number: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True
