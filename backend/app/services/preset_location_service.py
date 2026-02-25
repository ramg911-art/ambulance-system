"""Preset location auto-detection service."""
from typing import Optional

from sqlalchemy.orm import Session

from app.models import PresetLocation
from app.services.haversine import haversine_meters


def detect_preset_location(
    db: Session,
    organization_id: int,
    lat: float,
    lng: float,
) -> Optional[PresetLocation]:
    """Detect if given coordinates fall within any preset location's radius."""
    presets = (
        db.query(PresetLocation)
        .filter(
            PresetLocation.organization_id == organization_id,
            PresetLocation.active == True,
        )
        .all()
    )
    for preset in presets:
        dist_m = haversine_meters(lat, lng, preset.latitude, preset.longitude)
        if dist_m <= preset.radius_meters:
            return preset
    return None
