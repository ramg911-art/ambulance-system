"""PresetLocation model - pickup locations with geofence radius."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PresetLocation(Base):
    """Preset pickup location with latitude, longitude, and radius for auto-detection."""

    __tablename__ = "preset_locations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    radius_meters = Column(Float, nullable=False, default=100.0)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="preset_locations")
    fixed_tariffs_as_source = relationship(
        "FixedTariff",
        back_populates="source_location",
        foreign_keys="FixedTariff.source_id",
    )
    trips = relationship(
        "Trip",
        back_populates="source_preset",
        foreign_keys="Trip.source_preset_id",
    )
