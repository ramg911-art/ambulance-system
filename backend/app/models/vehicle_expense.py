"""VehicleExpense model - fuel, service/maintenance, accident repair."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class VehicleExpense(Base):
    """Vehicle expense record - fuel, service_maintenance, accident_repair."""

    __tablename__ = "vehicle_expenses"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=False, index=True)
    expense_type = Column(String(50), nullable=False, index=True)  # fuel, service_maintenance, accident_repair
    bill_number = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    amount = Column(Float, nullable=False)
    odometer_reading = Column(Float, nullable=True)  # For fuel
    qty_refueled = Column(Float, nullable=True)  # For fuel - liters
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vehicle = relationship("Vehicle", back_populates="expenses")
