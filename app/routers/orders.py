from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.order import TestOrder
from app.models.diagnostic import Diagnostic
from app.schemas.order import OrderCreate, Order
from app.schemas.diagnostic import DiagnosticCreate
from .diagnostics import calculate_diagnostic_result

router = APIRouter(prefix="/api/orders", tags=["orders"])


def require_role(role: str):
    def checker(user: User = Depends(get_current_user)):
        if user.role != role:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return checker


@router.post("/", response_model=Order)
async def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    doctor: User = Depends(require_role("doctor"))
):
    order = TestOrder(patient_name=order_in.patient_name, doctor_id=doctor.id)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/fulfill", response_model=Order)
async def fulfill_order(
    order_id: int,
    diag_in: DiagnosticCreate,
    db: Session = Depends(get_db),
    labtech: User = Depends(require_role("labtech"))
):
    order = db.query(TestOrder).filter(TestOrder.id == order_id).first()
    if not order or order.status != "pending":
        raise HTTPException(status_code=404, detail="Order not found")

    result = calculate_diagnostic_result(diag_in.protein1, diag_in.protein2, diag_in.protein3)
    diagnostic = Diagnostic(
        identifier=diag_in.identifier,
        protein1=diag_in.protein1,
        protein2=diag_in.protein2,
        protein3=diag_in.protein3,
        result=result,
        user_id=labtech.id
    )
    db.add(diagnostic)
    db.commit()
    db.refresh(diagnostic)

    order.diagnostic_id = diagnostic.id
    order.lab_tech_id = labtech.id
    order.status = "fulfilled"
    db.commit()
    db.refresh(order)
    return order


@router.get("/", response_model=List[Order])
async def list_orders(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(TestOrder).all()
