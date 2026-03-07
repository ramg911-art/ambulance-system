"""Billing routes - invoices for trips."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import DbSession, get_current_admin
from app.models import Invoice, Trip
from app.schemas.billing import InvoiceResponse, InvoiceWithTripResponse
from app.services.billing_service import calculate_trip_cost, create_invoice

router = APIRouter(prefix="/billing", tags=["billing"], dependencies=[Depends(get_current_admin)])


@router.get("/invoices", response_model=list[InvoiceResponse])
def list_invoices(
    db: DbSession,
    trip_id: Optional[int] = Query(None),
) -> list[Invoice]:
    """List invoices, optionally filtered by trip."""
    q = db.query(Invoice)
    if trip_id:
        q = q.filter(Invoice.trip_id == trip_id)
    return q.order_by(Invoice.created_at.desc()).all()


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(invoice_id: int, db: DbSession) -> Invoice:
    """Get invoice by ID."""
    inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return inv


@router.get("/invoices/{invoice_id}/details", response_model=InvoiceWithTripResponse)
def get_invoice_with_trip(invoice_id: int, db: DbSession) -> InvoiceWithTripResponse:
    """Get invoice with full trip details for PDF generation."""
    inv = (
        db.query(Invoice)
        .options(joinedload(Invoice.trip).joinedload(Trip.driver))
        .options(joinedload(Invoice.trip).joinedload(Trip.vehicle))
        .options(joinedload(Invoice.trip).joinedload(Trip.source_preset))
        .options(joinedload(Invoice.trip).joinedload(Trip.destination_preset))
        .options(joinedload(Invoice.trip).joinedload(Trip.organization))
        .filter(Invoice.id == invoice_id)
        .first()
    )
    if not inv or not inv.trip:
        raise HTTPException(status_code=404, detail="Invoice not found")
    t = inv.trip
    pickup = t.source_preset.name if t.source_preset else None
    if not pickup and t.pickup_lat is not None and t.pickup_lng is not None:
        pickup = f"GPS: {t.pickup_lat:.4f}, {t.pickup_lng:.4f}"
    drop = t.destination_preset.name if t.destination_preset else None
    if not drop and t.drop_lat is not None and t.drop_lng is not None:
        drop = f"GPS: {t.drop_lat:.4f}, {t.drop_lng:.4f}"
    org = t.organization if hasattr(t, "organization") else None
    return InvoiceWithTripResponse(
        id=inv.id,
        trip_id=inv.trip_id,
        amount=inv.amount,
        invoice_number=inv.invoice_number,
        status=inv.status,
        created_at=inv.created_at,
        driver_name=t.driver.name if t.driver else None,
        driver_mobile=t.driver.mobile if t.driver else None,
        vehicle_registration=t.vehicle.registration_number if t.vehicle else None,
        start_time=t.start_time,
        end_time=t.end_time,
        distance_km=t.distance_km,
        total_amount=t.total_amount,
        pickup_location=pickup,
        drop_location=drop,
        organization_name=org.name if org else None,
        organization_address=org.address if org else None,
        organization_phone=org.phone if org else None,
        organization_email=org.email if org else None,
    )


@router.post("/generate/{trip_id}", response_model=InvoiceResponse)
def generate_invoice(trip_id: int, db: DbSession) -> Invoice:
    """Generate invoice for a trip. Calculates cost and creates invoice."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    amount = calculate_trip_cost(db, trip)
    invoice = create_invoice(db, trip, amount)
    trip.total_amount = amount
    db.commit()
    db.refresh(invoice)
    return invoice
