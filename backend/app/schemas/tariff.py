"""Tariff schemas."""
from typing import Optional

from pydantic import BaseModel


class FixedTariffCreate(BaseModel):
    """Create fixed tariff."""

    organization_id: int
    source_id: int
    destination_id: int
    amount: float


class FixedTariffUpdate(BaseModel):
    """Update fixed tariff."""

    amount: Optional[float] = None


class FallbackTariffResponse(BaseModel):
    """Fallback (distance) tariff config."""

    rate_per_km: float


class FallbackTariffUpdate(BaseModel):
    """Update fallback tariff."""

    rate_per_km: float


class FixedTariffResponse(BaseModel):
    """Fixed tariff response."""

    id: int
    organization_id: int
    source_id: int
    destination_id: int
    amount: float

    class Config:
        from_attributes = True
