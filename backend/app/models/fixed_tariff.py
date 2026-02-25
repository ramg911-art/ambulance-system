"""FixedTariff model - preset source/destination pricing."""
from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class FixedTariff(Base):
    """Fixed tariff for preset source location to preset destination."""

    __tablename__ = "fixed_tariffs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("preset_locations.id"), nullable=False, index=True)
    destination_id = Column(Integer, ForeignKey("preset_destinations.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)

    organization = relationship("Organization", back_populates="fixed_tariffs")
    source_location = relationship(
        "PresetLocation",
        back_populates="fixed_tariffs_as_source",
        foreign_keys=[source_id],
    )
    destination = relationship(
        "PresetDestination",
        back_populates="fixed_tariffs_as_destination",
    )
