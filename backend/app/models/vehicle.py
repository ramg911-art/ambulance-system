"""Vehicle model - represents ambulances."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Vehicle(Base):
    """Vehicle (ambulance) model."""

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    registration_number = Column(String(50), nullable=False, index=True)
    make_model = Column(String(255))
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="vehicles")
    trips = relationship("Trip", back_populates="vehicle")
    gps_logs = relationship("GPSLog", back_populates="vehicle")
