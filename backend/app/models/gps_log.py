"""GPSLog model - stores GPS track points for trips."""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class GPSLog(Base):
    """GPS log entry for a vehicle during a trip."""

    __tablename__ = "gps_logs"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vehicle = relationship("Vehicle", back_populates="gps_logs")
    trip = relationship("Trip", back_populates="gps_logs")
