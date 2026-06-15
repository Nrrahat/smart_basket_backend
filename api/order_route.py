from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from schemas.order_schema import OrderResponse, OrderUpdateStatus
from services.order_service import OrderService

router = APIRouter(tags=["Orders"])


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def start_order_session(db: AsyncSession = Depends(get_db_session)):
    """Initializes a new order session (e.g., when a user grabs a smart basket)."""
    return await OrderService.create_order(db)


@router.post("/orders/{order_id}/add-item", response_model=OrderResponse)
async def scan_item_into_basket(
    order_id: int, 
    rfid_uid: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Simulates scanning an RFID tag at the basket level to append an item."""
    return await OrderService.add_item_to_order(db, order_id=order_id, rfid_uid=rfid_uid)