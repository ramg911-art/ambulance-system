"""PresetDestination model - predefined destinations."""
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class PresetDestination(Base):
    """Preset destination with latitude and longitude."""

    __tablename__ = "preset_destinations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    fixed_tariffs_as_destination = relationship(
        "FixedTariff",
        back_populates="destination",
    )
    trips = relationship(
        "Trip",
        back_populates="destination_preset",
        foreign_keys="Trip.destination_preset_id",
    )
