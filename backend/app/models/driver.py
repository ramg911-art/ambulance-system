"""Driver model - represents ambulance drivers."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Driver(Base):
    """Driver model - can log in with phone and password."""

    __tablename__ = "drivers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    license_number = Column(String(100))
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="drivers")
    trips = relationship("Trip", back_populates="driver")
