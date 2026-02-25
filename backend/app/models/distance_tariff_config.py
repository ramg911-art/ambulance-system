"""Distance tariff config - fallback rate per km when no fixed tariff."""
from sqlalchemy import Column, Integer, Float, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class DistanceTariffConfig(Base):
    """Singleton config for distance-based fallback tariff (₹ per km)."""

    __tablename__ = "distance_tariff_config"

    id = Column(Integer, primary_key=True, index=True)
    rate_per_km = Column(Float, nullable=False, default=50.0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
