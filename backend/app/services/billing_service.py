"""Billing service - trip cost calculation and invoice generation."""
import uuid

from sqlalchemy.orm import Session

from app.models import Invoice, Trip
from app.services.tariff_service import get_fixed_tariff, calculate_distance_tariff


def calculate_trip_cost(db: Session, trip: Trip) -> float:
    """Calculate trip cost based on tariff type.
    If is_fixed_tariff and source/destination presets match a FixedTariff, use it.
    Otherwise use distance-based tariff.
    """
    if trip.is_fixed_tariff and trip.source_preset_id and trip.destination_preset_id:
        fixed = get_fixed_tariff(
            db,
            trip.organization_id,
            trip.source_preset_id,
            trip.destination_preset_id,
        )
        if fixed:
            return fixed.amount
    distance = trip.distance_km or 0.0
    return calculate_distance_tariff(distance, db)


def create_invoice(db: Session, trip: Trip, amount: float) -> Invoice:
    """Create invoice for a trip."""
    inv = Invoice(
        trip_id=trip.id,
        amount=amount,
        invoice_number=f"INV-{trip.id}-{uuid.uuid4().hex[:8].upper()}",
        status="pending",
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv
