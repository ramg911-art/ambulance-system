"""Invoice model - billing invoices for trips."""
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Invoice(Base):
    """Invoice generated for a completed trip."""

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    invoice_number = Column(String(100), unique=True, index=True)
    status = Column(String(50), default="pending", nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    trip = relationship("Trip", back_populates="invoices")
