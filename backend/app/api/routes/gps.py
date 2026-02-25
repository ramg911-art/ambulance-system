"""GPS routes - update location and get live positions."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.schemas.gps import GPSUpdateRequest, VehicleLocationResponse
from app.services.gps_service import GPSService

router = APIRouter(prefix="/gps", tags=["gps"])


@router.post("/update")
def update_gps(data: GPSUpdateRequest, db: DbSession) -> dict:
    """Update vehicle GPS location. Stores in Redis for live tracking and in DB if trip_id provided."""
    svc = GPSService(db)
    svc.update_vehicle_location(
        vehicle_id=data.vehicle_id,
        latitude=data.latitude,
        longitude=data.longitude,
        trip_id=data.trip_id,
    )
    if data.trip_id:
        svc.store_gps_log(
            vehicle_id=data.vehicle_id,
            latitude=data.latitude,
            longitude=data.longitude,
            trip_id=data.trip_id,
        )
    return {"status": "ok"}


@router.get("/vehicles/live")
def get_live_vehicles(db: DbSession) -> list[VehicleLocationResponse]:
    """Get live vehicle locations from Redis."""
    svc = GPSService(db)
    locations = svc.get_live_vehicle_locations()
    return [
        VehicleLocationResponse(
            vehicle_id=loc["vehicle_id"],
            latitude=loc["latitude"],
            longitude=loc["longitude"],
            last_updated=loc["last_updated"],
        )
        for loc in locations
    ]
