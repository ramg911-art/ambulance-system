"""Organization routes - CRUD for admin."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_current_admin
from app.models import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[OrganizationResponse])
def list_organizations(
    db: DbSession,
    active_only: bool = Query(True),
) -> list[Organization]:
    """List organizations."""
    q = db.query(Organization)
    if active_only:
        q = q.filter(Organization.active == True)
    return q.all()


@router.post("", response_model=OrganizationResponse)
def create_organization(data: OrganizationCreate, db: DbSession) -> Organization:
    """Create an organization."""
    name = (data.name or "").strip()
    code = (data.code or "").strip().upper()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required")
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    existing = db.query(Organization).filter(Organization.code == code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Organization with this code already exists")
    org = Organization(name=name, code=code, active=data.active)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@router.get("/{org_id}", response_model=OrganizationResponse)
def get_organization(org_id: int, db: DbSession) -> Organization:
    """Get organization by ID."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.patch("/{org_id}", response_model=OrganizationResponse)
def update_organization(org_id: int, data: OrganizationUpdate, db: DbSession) -> Organization:
    """Update an organization."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if data.name is not None:
        org.name = data.name.strip() or org.name
    if data.code is not None:
        new_code = data.code.strip().upper()
        if new_code:
            other = db.query(Organization).filter(Organization.code == new_code, Organization.id != org_id).first()
            if other:
                raise HTTPException(status_code=400, detail="Organization with this code already exists")
            org.code = new_code
    if data.active is not None:
        org.active = data.active
    db.commit()
    db.refresh(org)
    return org


@router.delete("/{org_id}")
def delete_organization(org_id: int, db: DbSession) -> dict:
    """Delete an organization. Fails if it has drivers, vehicles, or other linked data."""
    from app.models import Driver, Vehicle, PresetLocation, FixedTariff

    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    if db.query(Driver).filter(Driver.organization_id == org_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete: organization has drivers")
    if db.query(Vehicle).filter(Vehicle.organization_id == org_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete: organization has vehicles")
    if db.query(PresetLocation).filter(PresetLocation.organization_id == org_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete: organization has preset locations")
    if db.query(FixedTariff).filter(FixedTariff.organization_id == org_id).first():
        raise HTTPException(status_code=400, detail="Cannot delete: organization has tariffs")
    db.delete(org)
    db.commit()
    return {"status": "deleted"}
