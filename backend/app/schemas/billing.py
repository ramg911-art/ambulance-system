"""Billing schemas."""
from datetime import datetime

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
