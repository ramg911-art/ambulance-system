"""Trip routes."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_current_admin, get_current_admin_or_driver
from app.models import Driver, Trip
from app.schemas.trip import TripCreate, TripResponse
from app.services.trip_service import create_trip, start_trip, end_trip

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("", response_model=list[TripResponse])
def list_trips(
    db: DbSession,
    _admin=Depends(get_current_admin),
    organization_id: Optional[int] = Query(None),
    driver_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
) -> list[Trip]:
    """List trips with optional filters."""
    q = db.query(Trip)
    if organization_id:
        q = q.filter(Trip.organization_id == organization_id)
    if driver_id:
        q = q.filter(Trip.driver_id == driver_id)
    if status:
        q = q.filter(Trip.status == status)
    return q.order_by(Trip.created_at.desc()).all()


@router.post("", response_model=TripResponse)
def post_trip(data: TripCreate, db: DbSession) -> Trip:
    """Create a new trip."""
    trip = create_trip(db, data)
    return trip


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: int,
    db: DbSession,
    user=Depends(get_current_admin_or_driver),
) -> Trip:
    """Get trip by ID. Admin can get any trip; driver can get only their own."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if isinstance(user, Driver) and trip.driver_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this trip")
    return trip


@router.post("/{trip_id}/start", response_model=TripResponse)
def start_trip_endpoint(trip_id: int, db: DbSession) -> Trip:
    """Start a trip."""
    trip = start_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not pending")
    return trip


@router.post("/{trip_id}/end", response_model=TripResponse)
def end_trip_endpoint(trip_id: int, db: DbSession) -> Trip:
    """End a trip - calculates distance from GPS logs, bill, creates invoice."""
    trip = end_trip(db, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found or not in progress")
    return trip
