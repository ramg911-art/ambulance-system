"""Organization model - represents a hospital or fleet operator."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Organization(Base):
    """Organization (hospital/fleet operator) model."""

    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), unique=True, index=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    drivers = relationship("Driver", back_populates="organization")
    vehicles = relationship("Vehicle", back_populates="organization")
    preset_locations = relationship("PresetLocation", back_populates="organization")
    fixed_tariffs = relationship("FixedTariff", back_populates="organization")
    trips = relationship("Trip", back_populates="organization")
