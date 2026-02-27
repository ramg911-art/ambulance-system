"""GPS routes - update location and get live positions."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.api.deps import DbSession, get_current_admin
from app.models import Vehicle, Trip
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
def get_live_vehicles(db: DbSession, _admin=Depends(get_current_admin)) -> list[VehicleLocationResponse]:
    """Get live vehicle locations from Redis, enriched with vehicle number and trip preset names."""
    svc = GPSService(db)
    locations = svc.get_live_vehicle_locations()
    result = []
    for loc in locations:
        vehicle_id = loc["vehicle_id"]
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        reg_no = vehicle.registration_number if vehicle else str(vehicle_id)

        pickup_lat = None
        pickup_lng = None
        dest_lat = None
        dest_lng = None
        trip_id = loc.get("trip_id")
        if trip_id:
            trip = (
                db.query(Trip)
                .options(
                    joinedload(Trip.source_preset),
                    joinedload(Trip.destination_preset),
                )
                .filter(Trip.id == trip_id)
                .first()
            )
            if trip:
                if trip.source_preset:
                    pickup_lat = trip.source_preset.latitude
                    pickup_lng = trip.source_preset.longitude
                elif trip.pickup_lat is not None and trip.pickup_lng is not None:
                    pickup_lat = trip.pickup_lat
                    pickup_lng = trip.pickup_lng
                if trip.destination_preset:
                    dest_lat = trip.destination_preset.latitude
                    dest_lng = trip.destination_preset.longitude
                elif trip.drop_lat is not None and trip.drop_lng is not None:
                    dest_lat = trip.drop_lat
                    dest_lng = trip.drop_lng

        result.append(
            VehicleLocationResponse(
                vehicle_id=vehicle_id,
                registration_number=reg_no,
                latitude=loc["latitude"],
                longitude=loc["longitude"],
                last_updated=loc["last_updated"],
                trip_id=trip_id,
                pickup_location_name=None,
                pickup_lat=pickup_lat,
                pickup_lng=pickup_lng,
                destination_name=None,
                destination_lat=dest_lat,
                destination_lng=dest_lng,
                current_location_name=None,
            )
        )
    return result
