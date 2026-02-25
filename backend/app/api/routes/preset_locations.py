"""Preset location routes - CRUD and nearby auto-detection."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_current_admin
from app.models import PresetLocation
from app.schemas.preset_location import (
    PresetLocationCreate,
    PresetLocationUpdate,
    PresetLocationResponse,
)
from app.services.preset_location_service import detect_preset_location

router = APIRouter(prefix="/preset-locations", tags=["preset-locations"])


@router.get("", response_model=list[PresetLocationResponse])
def list_preset_locations(
    db: DbSession,
    _admin=Depends(get_current_admin),
    organization_id: Optional[int] = Query(None),
) -> list[PresetLocation]:
    """List preset locations, optionally filtered by organization."""
    q = db.query(PresetLocation)
    if organization_id:
        q = q.filter(PresetLocation.organization_id == organization_id)
    return q.all()


@router.post("", response_model=PresetLocationResponse)
def create_preset_location(data: PresetLocationCreate, db: DbSession, _admin=Depends(get_current_admin)) -> PresetLocation:
    """Create a preset location."""
    loc = PresetLocation(
        organization_id=data.organization_id,
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
        radius_meters=data.radius_meters,
        active=data.active,
    )
    db.add(loc)
    db.commit()
    db.refresh(loc)
    return loc


@router.get("/nearby")
def get_nearby_preset_location(
    db: DbSession,
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    organization_id: int = Query(..., description="Organization ID"),
) -> Optional[PresetLocationResponse]:
    """Returns matching preset location if coordinates are within its radius."""
    preset = detect_preset_location(db, organization_id, lat, lng)
    if preset:
        return PresetLocationResponse.model_validate(preset)
    return None


@router.get("/{loc_id}", response_model=PresetLocationResponse)
def get_preset_location(loc_id: int, db: DbSession, _admin=Depends(get_current_admin)) -> PresetLocation:
    """Get preset location by ID."""
    loc = db.query(PresetLocation).filter(PresetLocation.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Preset location not found")
    return loc


@router.patch("/{loc_id}", response_model=PresetLocationResponse)
def update_preset_location(
    loc_id: int, data: PresetLocationUpdate, db: DbSession, _admin=Depends(get_current_admin)
) -> PresetLocation:
    """Update a preset location."""
    loc = db.query(PresetLocation).filter(PresetLocation.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Preset location not found")
    if data.name is not None:
        loc.name = data.name
    if data.latitude is not None:
        loc.latitude = data.latitude
    if data.longitude is not None:
        loc.longitude = data.longitude
    if data.radius_meters is not None:
        loc.radius_meters = data.radius_meters
    if data.active is not None:
        loc.active = data.active
    db.commit()
    db.refresh(loc)
    return loc


@router.delete("/{loc_id}")
def delete_preset_location(loc_id: int, db: DbSession, _admin=Depends(get_current_admin)) -> dict:
    """Delete a preset location."""
    loc = db.query(PresetLocation).filter(PresetLocation.id == loc_id).first()
    if not loc:
        raise HTTPException(status_code=404, detail="Preset location not found")
    db.delete(loc)
    db.commit()
    return {"status": "deleted"}
