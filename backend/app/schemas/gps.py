"""GPS schemas."""
from pydantic import BaseModel


class GPSUpdateRequest(BaseModel):
    """GPS location update request."""

    vehicle_id: int
    latitude: float
    longitude: float
    trip_id: int | None = None


class VehicleLocationResponse(BaseModel):
    """Live vehicle location response."""

    vehicle_id: int
    latitude: float
    longitude: float
    last_updated: str
