"""Driver schemas."""
from typing import Optional

from pydantic import BaseModel, Field


class DriverCreate(BaseModel):
    """Create driver."""

    organization_id: int
    name: str = Field(..., min_length=1, strip_whitespace=True)
    phone: str = Field(..., min_length=1, strip_whitespace=True)
    password: str = Field(..., min_length=1)
    license_number: Optional[str] = None
    active: bool = True


class DriverUpdate(BaseModel):
    """Update driver."""

    name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    license_number: Optional[str] = None
    active: Optional[bool] = None


class DriverResponse(BaseModel):
    """Driver response."""

    id: int
    organization_id: int
    name: str
    phone: str
    license_number: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True
