"""Vehicle schemas."""
from typing import Optional

from pydantic import BaseModel


class VehicleCreate(BaseModel):
    """Create vehicle."""

    organization_id: int
    registration_number: str
    make_model: Optional[str] = None
    active: bool = True


class VehicleUpdate(BaseModel):
    """Update vehicle."""

    registration_number: Optional[str] = None
    make_model: Optional[str] = None
    active: Optional[bool] = None


class VehicleResponse(BaseModel):
    """Vehicle response."""

    id: int
    organization_id: int
    registration_number: str
    make_model: Optional[str] = None
    active: bool

    class Config:
        from_attributes = True
