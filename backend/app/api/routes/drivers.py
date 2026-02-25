"""Driver routes - CRUD for admin/dispatch."""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_current_admin
from app.core.security import hash_password
from app.models import Driver, Organization
from app.schemas.driver import DriverCreate, DriverUpdate, DriverResponse

router = APIRouter(prefix="/drivers", tags=["drivers"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[DriverResponse])
def list_drivers(
    db: DbSession,
    organization_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
) -> list[Driver]:
    """List drivers, optionally filtered by organization."""
    q = db.query(Driver)
    if organization_id:
        q = q.filter(Driver.organization_id == organization_id)
    if active_only:
        q = q.filter(Driver.active == True)
    return q.all()


logger = logging.getLogger(__name__)


@router.post("", response_model=DriverResponse)
def create_driver(data: DriverCreate, db: DbSession) -> Driver:
    """Create a driver."""
    try:
        org = db.query(Organization).filter(Organization.id == data.organization_id).first()
        if not org:
            raise HTTPException(status_code=400, detail=f"Organization {data.organization_id} not found. Run seed_data.py first.")
        existing = db.query(Driver).filter(Driver.phone == data.phone).first()
        if existing:
            raise HTTPException(status_code=400, detail="Phone number already registered")
        d = Driver(
            organization_id=data.organization_id,
            name=data.name,
            phone=data.phone,
            password_hash=hash_password(data.password),
            license_number=data.license_number,
            active=data.active,
        )
        db.add(d)
        db.commit()
        db.refresh(d)
        logger.info("Created driver id=%s phone=%s org=%s", d.id, data.phone, data.organization_id)
        return d
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("create_driver failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/{driver_id}", response_model=DriverResponse)
def get_driver(driver_id: int, db: DbSession) -> Driver:
    """Get driver by ID."""
    d = db.query(Driver).filter(Driver.id == driver_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Driver not found")
    return d


@router.patch("/{driver_id}", response_model=DriverResponse)
def update_driver(driver_id: int, data: DriverUpdate, db: DbSession) -> Driver:
    """Update a driver."""
    d = db.query(Driver).filter(Driver.id == driver_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Driver not found")
    if data.name is not None:
        d.name = data.name
    if data.phone is not None:
        other = db.query(Driver).filter(Driver.phone == data.phone, Driver.id != driver_id).first()
        if other:
            raise HTTPException(status_code=400, detail="Phone number already in use")
        d.phone = data.phone
    if data.password is not None:
        d.password_hash = hash_password(data.password)
    if data.license_number is not None:
        d.license_number = data.license_number
    if data.active is not None:
        d.active = data.active
    db.commit()
    db.refresh(d)
    return d


@router.delete("/{driver_id}")
def delete_driver(driver_id: int, db: DbSession) -> dict:
    """Delete a driver."""
    d = db.query(Driver).filter(Driver.id == driver_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Driver not found")
    db.delete(d)
    db.commit()
    return {"status": "deleted"}
