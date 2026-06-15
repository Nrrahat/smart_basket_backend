from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from typing import List, Optional

from models.order import Order, OrderItem, OrderStatus
from models.product import Product
from sqlalchemy.orm import selectinload


class OrderService:

    @staticmethod
    async def create_order(db: AsyncSession) -> Order:
        """Starts a brand new pending order session for a basket."""
        new_order = Order(status=OrderStatus.PENDING, total_price=0.00)
        db.add(new_order)
        await db.commit()
        await db.refresh(new_order)
        return new_order

    @staticmethod
    async def add_item_to_order(db: AsyncSession, order_id: int, rfid_uid: str) -> Order:
        """Finds a product by RFID tag and appends it to an active order, updating the total price."""
        # 1. Fetch the order
        order_query = await db.execute(select(Order).where(Order.id == order_id).options(selectinload(Order.items)))
        order = order_query.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order session not found")
        if order.status != OrderStatus.PENDING:
            raise HTTPException(status_code=400, detail="Cannot modify a finalized order")

        # 2. Fetch product by RFID
        prod_query = await db.execute(select(Product).where(Product.rfid_uid == rfid_uid))
        product = prod_query.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"No product linked to RFID '{rfid_uid}'")

        # 3. Check if product already exists in this order
        item_query = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id, OrderItem.product_id == product.id)
        )
        existing_item = item_query.scalar_one_or_none()

        if existing_item:
            existing_item.quantity += 1
        else:
            new_item = OrderItem(order_id=order.id, product_id=product.id, quantity=1)
            db.add(new_item)

        # FIX: Manually append the item to the order relationship list 
        # so the local cache is aware of it immediately.
            order.items.append(new_item)

        # 4. Recalculate total order price
        order.total_price += product.price
        
        await db.commit()
        # Eager load everything back for FastAPI
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items).selectinload(OrderItem.product)
            )
        )
        return result.scalar_one()