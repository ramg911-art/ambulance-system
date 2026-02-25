"""Vehicle routes - list vehicles and live GPS."""
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.models import Vehicle
from app.schemas.gps import VehicleLocationResponse
from app.services.gps_service import GPSService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("")
def list_vehicles(
    db: DbSession,
    organization_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
) -> list[dict]:
    """List vehicles, optionally filtered by organization."""
    q = db.query(Vehicle)
    if organization_id:
        q = q.filter(Vehicle.organization_id == organization_id)
    if active_only:
        q = q.filter(Vehicle.active == True)
    vehicles = q.all()
    return [
        {
            "id": v.id,
            "registration_number": v.registration_number,
            "make_model": v.make_model,
            "organization_id": v.organization_id,
        }
        for v in vehicles
    ]


@router.get("/live")
def get_live_vehicle_locations(db: DbSession) -> list[VehicleLocationResponse]:
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
