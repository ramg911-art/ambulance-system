"""Driver routes - list drivers for admin/dispatch."""
from typing import Optional

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.models import Driver

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("")
def list_drivers(
    db: DbSession,
    organization_id: Optional[int] = Query(None),
    active_only: bool = Query(True),
) -> list[dict]:
    """List drivers, optionally filtered by organization."""
    q = db.query(Driver)
    if organization_id:
        q = q.filter(Driver.organization_id == organization_id)
    if active_only:
        q = q.filter(Driver.active == True)
    drivers = q.all()
    return [
        {
            "id": d.id,
            "name": d.name,
            "phone": d.phone,
            "organization_id": d.organization_id,
        }
        for d in drivers
    ]
