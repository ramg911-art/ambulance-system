"""Vehicle expense routes - CRUD for fuel, service, accident repair."""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import DbSession, get_current_admin
from app.models import Vehicle, VehicleExpense
from app.schemas.vehicle_expense import VehicleExpenseCreate, VehicleExpenseResponse

router = APIRouter(prefix="/vehicle-expenses", tags=["vehicle-expenses"], dependencies=[Depends(get_current_admin)])


@router.get("", response_model=list[VehicleExpenseResponse])
def list_expenses(
    db: DbSession,
    vehicle_id: Optional[int] = Query(None),
    expense_type: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
) -> list[VehicleExpense]:
    """List vehicle expenses with optional filters."""
    q = db.query(VehicleExpense)
    if vehicle_id:
        q = q.filter(VehicleExpense.vehicle_id == vehicle_id)
    if expense_type:
        q = q.filter(VehicleExpense.expense_type == expense_type)
    if date_from:
        q = q.filter(func.date(VehicleExpense.created_at) >= date_from)
    if date_to:
        q = q.filter(func.date(VehicleExpense.created_at) <= date_to)
    return q.order_by(VehicleExpense.created_at.desc()).all()


@router.get("/summary")
def expenses_summary(
    db: DbSession,
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
) -> dict:
    """Total expenses in period, for dashboard tile."""
    q = db.query(func.coalesce(func.sum(VehicleExpense.amount), 0).label("total"))
    if date_from:
        q = q.filter(func.date(VehicleExpense.created_at) >= date_from)
    if date_to:
        q = q.filter(func.date(VehicleExpense.created_at) <= date_to)
    row = q.first()
    return {"total_amount": float(row.total) if row else 0}


@router.post("", response_model=VehicleExpenseResponse)
def create_expense(data: VehicleExpenseCreate, db: DbSession) -> VehicleExpense:
    """Create a vehicle expense."""
    v = db.query(Vehicle).filter(Vehicle.id == data.vehicle_id).first()
    if not v:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    exp = VehicleExpense(
        vehicle_id=data.vehicle_id,
        expense_type=data.expense_type,
        bill_number=data.bill_number,
        description=(data.description or "").strip() or None,
        amount=data.amount,
        odometer_reading=data.odometer_reading,
        qty_refueled=data.qty_refueled,
    )
    db.add(exp)
    db.commit()
    db.refresh(exp)
    return exp


@router.get("/{expense_id}", response_model=VehicleExpenseResponse)
def get_expense(expense_id: int, db: DbSession) -> VehicleExpense:
    """Get expense by ID."""
    exp = db.query(VehicleExpense).filter(VehicleExpense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    return exp


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: DbSession) -> dict:
    """Delete an expense."""
    exp = db.query(VehicleExpense).filter(VehicleExpense.id == expense_id).first()
    if not exp:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(exp)
    db.commit()
    return {"status": "deleted"}
