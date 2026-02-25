"""Preset destination schemas."""
from typing import Optional

from pydantic import BaseModel


class PresetDestinationCreate(BaseModel):
    """Create preset destination."""

    name: str
    latitude: float
    longitude: float


class PresetDestinationUpdate(BaseModel):
    """Update preset destination."""

    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PresetDestinationResponse(BaseModel):
    """Preset destination response."""

    id: int
    name: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True
