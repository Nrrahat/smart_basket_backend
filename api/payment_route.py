# app/api/payment_route.py
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session  
from schemas.payment_schema import CheckoutRequest, BillResponse
from services.payment_service import PaymentService

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/checkout", response_model=BillResponse, status_code=status.HTTP_201_CREATED)
async def checkout(payload: CheckoutRequest, db: AsyncSession = Depends(get_db_session)):
    """Executes order serialization, freezes transactions, and delivers scannable receipt invoice bills."""
    bill_data = await PaymentService.checkout_order(db=db, order_id=payload.order_id)
    return bill_data