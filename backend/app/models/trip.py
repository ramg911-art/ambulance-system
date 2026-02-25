"""Trip model - ambulance trips with both fixed and distance-based tariff support."""
from sqlalchemy import Column, Integer, Float, Boolean, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Trip(Base):
    """Trip model - supports both fixed and distance-based tariffs."""

    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)

    source_preset_id = Column(Integer, ForeignKey("preset_locations.id"), nullable=True, index=True)
    destination_preset_id = Column(Integer, ForeignKey("preset_destinations.id"), nullable=True, index=True)

    pickup_lat = Column(Float, nullable=True)
    pickup_lng = Column(Float, nullable=True)
    drop_lat = Column(Float, nullable=True)
    drop_lng = Column(Float, nullable=True)

    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    distance_km = Column(Float, nullable=True)

    is_fixed_tariff = Column(Boolean, default=False, nullable=False)
    total_amount = Column(Float, nullable=True)
    status = Column(String(50), default="pending", nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")
    vehicle = relationship("Vehicle", back_populates="trips")
    source_preset = relationship(
        "PresetLocation",
        back_populates="trips",
        foreign_keys=[source_preset_id],
    )
    destination_preset = relationship(
        "PresetDestination",
        back_populates="trips",
        foreign_keys=[destination_preset_id],
    )
    gps_logs = relationship("GPSLog", back_populates="trip")
    invoices = relationship("Invoice", back_populates="trip")
