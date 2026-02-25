"""Vehicle routes - CRUD and live GPS."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.models import Organization, Vehicle
from app.schemas.gps import VehicleLocationResponse
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.services.gps_service import GPSService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("", response_model=list[VehicleResponse])
def list_vehicles(
    db: DbSession,
    organization_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
) -> list[Vehicle]:
    """List vehicles, optionally filtered by organization."""
    q = db.query(Vehicle)
    if organization_id:
        q = q.filter(Vehicle.organization_id == organization_id)
    if active_only:
        q = q.filter(Vehicle.active == True)
    return q.all()


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


@router.post("", response_model=VehicleResponse)
def create_vehicle(data: VehicleCreate, db: DbSession) -> Vehicle:
    """Create a vehicle."""
    org = db.query(Organization).filter(Organization.id == data.organization_id).first()
    if not org:
        raise HTTPException(status_code=400, detail=f"Organization {data.organization_id} not found. Run seed_data.py first.")
    reg = (data.registration_number or "").strip()
    if not reg:
        raise HTTPException(status_code=400, detail="Registration number is required")
    existing = db.query(Vehicle).filter(
        Vehicle.organization_id == data.organization_id,
        Vehicle.registration_number == reg,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Vehicle with this registration already exists")
    v = Vehicle(
        organization_id=data.organization_id,
        registration_number=reg,
        make_model=(data.make_model or "").strip() or None,
        active=data.active,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int, db: DbSession) -> Vehicle:
    """Get vehicle by ID."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return v


@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(vehicle_id: int, data: VehicleUpdate, db: DbSession) -> Vehicle:
    """Update a vehicle."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if data.registration_number is not None:
        v.registration_number = data.registration_number
    if data.make_model is not None:
        v.make_model = data.make_model
    if data.active is not None:
        v.active = data.active
    db.commit()
    db.refresh(v)
    return v


@router.delete("/{vehicle_id}")
def delete_vehicle(vehicle_id: int, db: DbSession) -> dict:
    """Delete a vehicle."""
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(v)
    db.commit()
    return {"status": "deleted"}


