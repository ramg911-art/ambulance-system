"""GPS schemas."""
from pydantic import BaseModel


class GPSUpdateRequest(BaseModel):
    """GPS location update request."""

    vehicle_id: int
    latitude: float
    longitude: float
    trip_id: int | None = None


class VehicleLocationResponse(BaseModel):
    """Live vehicle location response with vehicle info and trip presets."""

    vehicle_id: int
    registration_number: str
    driver_name: str | None = None
    latitude: float
    longitude: float
    last_updated: str
    trip_id: int | None = None
    pickup_location_name: str | None = None
    pickup_lat: float | None = None
    pickup_lng: float | None = None
    destination_name: str | None = None
    destination_lat: float | None = None
    destination_lng: float | None = None
    current_location_name: str | None = None
