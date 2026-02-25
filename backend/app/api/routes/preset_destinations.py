"""Preset destination routes - CRUD and dropdown by source."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.models import FixedTariff, PresetDestination
from app.schemas.preset_destination import (
    PresetDestinationCreate,
    PresetDestinationUpdate,
    PresetDestinationResponse,
)

router = APIRouter(prefix="/preset-destinations", tags=["preset-destinations"])


@router.get("", response_model=list[PresetDestinationResponse])
def list_preset_destinations(db: DbSession) -> list[PresetDestination]:
    """List all preset destinations."""
    return db.query(PresetDestination).all()


@router.get("/by-source/{source_id}", response_model=list[PresetDestinationResponse])
def get_destinations_for_source(
    source_id: int,
    db: DbSession,
    organization_id: int | None = Query(None),
) -> list[PresetDestination]:
    """Get preset destinations that have a fixed tariff from the given source (preset location)."""
    q = (
        db.query(PresetDestination)
        .join(FixedTariff, FixedTariff.destination_id == PresetDestination.id)
        .filter(FixedTariff.source_id == source_id)
    )
    if organization_id is not None:
        q = q.filter(FixedTariff.organization_id == organization_id)
    dests = q.distinct().all()
    return [PresetDestinationResponse.model_validate(d) for d in dests]


@router.post("", response_model=PresetDestinationResponse)
def create_preset_destination(data: PresetDestinationCreate, db: DbSession) -> PresetDestination:
    """Create a preset destination."""
    dest = PresetDestination(
        name=data.name,
        latitude=data.latitude,
        longitude=data.longitude,
    )
    db.add(dest)
    db.commit()
    db.refresh(dest)
    return dest


@router.get("/{dest_id}", response_model=PresetDestinationResponse)
def get_preset_destination(dest_id: int, db: DbSession) -> PresetDestination:
    """Get preset destination by ID."""
    dest = db.query(PresetDestination).filter(PresetDestination.id == dest_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Preset destination not found")
    return dest


@router.patch("/{dest_id}", response_model=PresetDestinationResponse)
def update_preset_destination(
    dest_id: int, data: PresetDestinationUpdate, db: DbSession
) -> PresetDestination:
    """Update a preset destination."""
    dest = db.query(PresetDestination).filter(PresetDestination.id == dest_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Preset destination not found")
    if data.name is not None:
        dest.name = data.name
    if data.latitude is not None:
        dest.latitude = data.latitude
    if data.longitude is not None:
        dest.longitude = data.longitude
    db.commit()
    db.refresh(dest)
    return dest


@router.delete("/{dest_id}")
def delete_preset_destination(dest_id: int, db: DbSession) -> dict:
    """Delete a preset destination."""
    dest = db.query(PresetDestination).filter(PresetDestination.id == dest_id).first()
    if not dest:
        raise HTTPException(status_code=404, detail="Preset destination not found")
    db.delete(dest)
    db.commit()
    return {"status": "deleted"}
