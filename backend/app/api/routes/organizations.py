"""Organization routes - CRUD for admin."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession, get_current_admin
from app.models import Organization

router = APIRouter(prefix="/organizations", tags=["organizations"], dependencies=[Depends(get_current_admin)])


@router.get("")
def list_organizations(
    db: DbSession,
    active_only: bool = Query(True),
) -> list[dict]:
    """List organizations."""
    q = db.query(Organization)
    if active_only:
        q = q.filter(Organization.active == True)
    orgs = q.all()
    return [
        {
            "id": o.id,
            "name": o.name,
            "code": o.code,
            "active": o.active,
        }
        for o in orgs
    ]


@router.get("/{org_id}")
def get_organization(org_id: int, db: DbSession) -> dict:
    """Get organization by ID."""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return {"id": org.id, "name": org.name, "code": org.code, "active": org.active}
