"""Trip schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TripCreate(BaseModel):
    """Create a new trip."""

    organization_id: int
    driver_id: int
    vehicle_id: int
    source_preset_id: Optional[int] = None
    destination_preset_id: Optional[int] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    drop_lat: Optional[float] = None
    drop_lng: Optional[float] = None
    is_fixed_tariff: bool = False


class TripResponse(BaseModel):
    """Trip response."""

    id: int
    organization_id: int
    driver_id: int
    vehicle_id: int
    source_preset_id: Optional[int] = None
    destination_preset_id: Optional[int] = None
    pickup_lat: Optional[float] = None
    pickup_lng: Optional[float] = None
    drop_lat: Optional[float] = None
    drop_lng: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    distance_km: Optional[float] = None
    is_fixed_tariff: bool
    total_amount: Optional[float] = None
    status: str

    class Config:
        from_attributes = True
