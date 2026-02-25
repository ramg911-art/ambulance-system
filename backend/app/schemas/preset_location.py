"""Preset location schemas."""
from typing import Optional

from pydantic import BaseModel


class PresetLocationCreate(BaseModel):
    """Create preset location."""

    organization_id: int
    name: str
    latitude: float
    longitude: float
    radius_meters: float = 100.0
    active: bool = True


class PresetLocationUpdate(BaseModel):
    """Update preset location."""

    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_meters: Optional[float] = None
    active: Optional[bool] = None


class PresetLocationResponse(BaseModel):
    """Preset location response."""

    id: int
    organization_id: int
    name: str
    latitude: float
    longitude: float
    radius_meters: float
    active: bool

    class Config:
        from_attributes = True
