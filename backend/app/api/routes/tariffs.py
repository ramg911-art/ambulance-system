"""Tariff routes - fixed tariffs CRUD and queries."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_current_admin, get_current_admin_or_driver
from app.models import FixedTariff
from app.models import DistanceTariffConfig
from app.schemas.tariff import (
    FixedTariffCreate,
    FixedTariffUpdate,
    FixedTariffResponse,
    FallbackTariffResponse,
    FallbackTariffUpdate,
)
from app.services.tariff_service import (
    get_fixed_tariff,
    calculate_distance_tariff,
    get_fallback_rate_per_km,
)

router = APIRouter(prefix="/tariffs", tags=["tariffs"])


@router.get("/fixed")
def get_fixed_tariff_endpoint(
    db: DbSession,
    _user=Depends(get_current_admin_or_driver),
    organization_id: int = Query(...),
    source_id: int = Query(...),
    destination_id: int = Query(...),
) -> dict | None:
    """Get fixed tariff for source preset location to destination preset."""
    t = get_fixed_tariff(db, organization_id, source_id, destination_id)
    if t:
        return {"amount": t.amount, "fixed_tariff_id": t.id}
    return None


@router.get("/distance")
def get_distance_tariff(
    db: DbSession,
    _user=Depends(get_current_admin_or_driver),
    distance_km: float = Query(...),
) -> dict:
    """Calculate distance-based tariff for given km."""
    amount = calculate_distance_tariff(distance_km, db)
    return {"distance_km": distance_km, "amount": amount}


@router.get("/fallback", response_model=FallbackTariffResponse)
def get_fallback_tariff(db: DbSession, _admin=Depends(get_current_admin)) -> dict:
    """Get fallback (distance) tariff rate per km."""
    rate = get_fallback_rate_per_km(db)
    return {"rate_per_km": rate}


@router.put("/fallback", response_model=FallbackTariffResponse)
def update_fallback_tariff(data: FallbackTariffUpdate, db: DbSession, _admin=Depends(get_current_admin)) -> dict:
    """Update fallback tariff rate per km."""
    row = db.query(DistanceTariffConfig).filter(DistanceTariffConfig.id == 1).first()
    if not row:
        row = DistanceTariffConfig(id=1, rate_per_km=data.rate_per_km)
        db.add(row)
    else:
        row.rate_per_km = data.rate_per_km
    db.commit()
    db.refresh(row)
    return {"rate_per_km": row.rate_per_km}


@router.get("", response_model=list[FixedTariffResponse])
def list_fixed_tariffs(
    db: DbSession,
    _admin=Depends(get_current_admin),
    organization_id: int | None = Query(None),
) -> list[FixedTariff]:
    """List fixed tariffs, optionally filtered by organization."""
    q = db.query(FixedTariff)
    if organization_id:
        q = q.filter(FixedTariff.organization_id == organization_id)
    return q.all()


@router.post("", response_model=FixedTariffResponse)
def create_fixed_tariff(data: FixedTariffCreate, db: DbSession, _admin=Depends(get_current_admin)) -> FixedTariff:
    """Create a fixed tariff."""
    t = FixedTariff(
        organization_id=data.organization_id,
        source_id=data.source_id,
        destination_id=data.destination_id,
        amount=data.amount,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("/{tariff_id}", response_model=FixedTariffResponse)
def get_fixed_tariff_by_id(tariff_id: int, db: DbSession, _admin=Depends(get_current_admin)) -> FixedTariff:
    """Get fixed tariff by ID."""
    t = db.query(FixedTariff).filter(FixedTariff.id == tariff_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Fixed tariff not found")
    return t


@router.patch("/{tariff_id}", response_model=FixedTariffResponse)
def update_fixed_tariff(
    tariff_id: int, data: FixedTariffUpdate, db: DbSession, _admin=Depends(get_current_admin)
) -> FixedTariff:
    """Update a fixed tariff."""
    t = db.query(FixedTariff).filter(FixedTariff.id == tariff_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Fixed tariff not found")
    if data.amount is not None:
        t.amount = data.amount
    db.commit()
    db.refresh(t)
    return t


@router.delete("/{tariff_id}")
def delete_fixed_tariff(tariff_id: int, db: DbSession, _admin=Depends(get_current_admin)) -> dict:
    """Delete a fixed tariff."""
    t = db.query(FixedTariff).filter(FixedTariff.id == tariff_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Fixed tariff not found")
    db.delete(t)
    db.commit()
    return {"status": "deleted"}
