"""Vehicle expense schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator, model_validator

EXPENSE_TYPES = ("fuel", "service_maintenance", "accident_repair")


class VehicleExpenseCreate(BaseModel):
    """Create vehicle expense. Fuel requires bill_number, odometer_reading, qty_refueled, amount, description."""

    vehicle_id: int
    expense_type: str  # fuel, service_maintenance, accident_repair
    bill_number: str
    description: Optional[str] = None
    amount: float
    odometer_reading: Optional[float] = None
    qty_refueled: Optional[float] = None

    @field_validator("expense_type")
    @classmethod
    def expense_type_valid(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if v not in EXPENSE_TYPES:
            raise ValueError("expense_type must be fuel, service_maintenance, or accident_repair")
        return v

    @field_validator("bill_number")
    @classmethod
    def bill_number_required(cls, v: str) -> str:
        if not (v or "").strip():
            raise ValueError("bill_number is required")
        return (v or "").strip()

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v: float) -> float:
        if v is None or v < 0:
            raise ValueError("amount must be >= 0")
        return v

    @model_validator(mode="after")
    def fuel_requires_fields(self):
        if self.expense_type == "fuel":
            if self.odometer_reading is None:
                raise ValueError("odometer_reading is required for fuel")
            if self.qty_refueled is None or self.qty_refueled < 0:
                raise ValueError("qty_refueled is required for fuel and must be >= 0")
            if not (self.description or "").strip():
                raise ValueError("description is required for fuel")
        else:
            if not (self.description or "").strip():
                raise ValueError("description is required for service_maintenance and accident_repair")
        return self


class VehicleExpenseResponse(BaseModel):
    """Vehicle expense response."""

    id: int
    vehicle_id: int
    expense_type: str
    bill_number: str
    description: Optional[str] = None
    amount: float
    odometer_reading: Optional[float] = None
    qty_refueled: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
