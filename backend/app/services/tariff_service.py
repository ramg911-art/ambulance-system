"""Tariff service - fixed and distance-based tariff calculation."""
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import FixedTariff


def get_fixed_tariff(
    db: Session,
    organization_id: int,
    source_id: int,
    destination_id: int,
) -> Optional[FixedTariff]:
    """Get fixed tariff for source preset location to destination preset."""
    return (
        db.query(FixedTariff)
        .filter(
            FixedTariff.organization_id == organization_id,
            FixedTariff.source_id == source_id,
            FixedTariff.destination_id == destination_id,
        )
        .first()
    )


def calculate_distance_tariff(distance_km: float) -> float:
    """Calculate tariff based on distance using configured rate per km."""
    return distance_km * settings.distance_tariff_per_km
