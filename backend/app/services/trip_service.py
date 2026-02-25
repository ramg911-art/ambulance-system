"""Trip service - create, start, end trips with distance and billing."""
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models import GPSLog, Trip
from app.schemas.trip import TripCreate
from app.services.billing_service import calculate_trip_cost, create_invoice
from app.services.haversine import haversine_km


def create_trip(db: Session, data: TripCreate) -> Trip:
    """Create a new trip."""
    trip = Trip(
        organization_id=data.organization_id,
        driver_id=data.driver_id,
        vehicle_id=data.vehicle_id,
        source_preset_id=data.source_preset_id,
        destination_preset_id=data.destination_preset_id,
        pickup_lat=data.pickup_lat,
        pickup_lng=data.pickup_lng,
        drop_lat=data.drop_lat,
        drop_lng=data.drop_lng,
        is_fixed_tariff=data.is_fixed_tariff,
        status="pending",
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip


def start_trip(db: Session, trip_id: int) -> Optional[Trip]:
    """Start a trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip or trip.status != "pending":
        return None
    trip.status = "in_progress"
    trip.start_time = datetime.utcnow()
    db.commit()
    db.refresh(trip)
    return trip


def _calculate_trip_distance(db: Session, trip_id: int) -> float:
    """Calculate total distance from GPS logs for a trip, in km."""
    logs = (
        db.query(GPSLog)
        .filter(GPSLog.trip_id == trip_id)
        .order_by(GPSLog.recorded_at)
        .all()
    )
    if len(logs) < 2:
        return 0.0
    total_km = 0.0
    for i in range(1, len(logs)):
        prev, curr = logs[i - 1], logs[i]
        total_km += haversine_km(
            prev.latitude, prev.longitude,
            curr.latitude, curr.longitude,
        )
    return total_km


def end_trip(db: Session, trip_id: int) -> Optional[Trip]:
    """End a trip: calculate distance from GPS logs, calculate bill, create invoice."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip or trip.status != "in_progress":
        return None
    trip.end_time = datetime.utcnow()
    trip.distance_km = _calculate_trip_distance(db, trip_id)
    trip.total_amount = calculate_trip_cost(db, trip)
    create_invoice(db, trip, trip.total_amount)
    trip.status = "completed"
    db.commit()
    db.refresh(trip)
    return trip
