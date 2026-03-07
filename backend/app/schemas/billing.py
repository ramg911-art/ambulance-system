"""Billing schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InvoiceResponse(BaseModel):
    """Invoice response."""

    id: int
    trip_id: int
    amount: float
    invoice_number: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceWithTripResponse(BaseModel):
    """Invoice with full trip details for PDF generation."""

    id: int
    trip_id: int
    amount: float
    invoice_number: str
    status: str
    created_at: datetime
    driver_name: Optional[str] = None
    driver_mobile: Optional[str] = None
    vehicle_registration: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    distance_km: Optional[float] = None
    total_amount: Optional[float] = None
    pickup_location: Optional[str] = None
    drop_location: Optional[str] = None
    organization_name: Optional[str] = None
    organization_address: Optional[str] = None
    organization_phone: Optional[str] = None
    organization_email: Optional[str] = None
