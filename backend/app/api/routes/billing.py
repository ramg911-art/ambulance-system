"""Billing routes - invoices for trips."""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import DbSession
from app.models import Invoice, Trip
from app.schemas.billing import InvoiceResponse
from app.services.billing_service import calculate_trip_cost, create_invoice

router = APIRouter(prefix="/billing", tags=["billing"])


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
