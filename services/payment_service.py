# app/services/payment_service.py
import io
import base64
import qrcode
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.order import Order, OrderStatus, OrderItem
from models.payment import Bill, BillStatus

class PaymentService:

    @staticmethod
    def generate_qr_base64(data: str) -> str:
        """Generates a QR code image as a clean base64 data URL string."""
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

    @staticmethod
    async def checkout_order(db: AsyncSession, order_id: int) -> dict:
        """Finalizes order state, records billing metrics, and outputs payment graphics."""
        # 1. Fetch Order with fully pre-loaded item relationships
        result = await db.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
        )
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order session not found")
        if order.status != OrderStatus.PENDING:
            raise HTTPException(status_code=400, detail="Order is already checked out or finalized")
        if not order.items:
            raise HTTPException(status_code=400, detail="Cannot checkout an empty basket")

        # 2. Build and stage the new billing record
        new_bill = Bill(order_id=order.id, total_price=order.total_price, status=BillStatus.PENDING)
        db.add(new_bill)
        
        # 3. Secure the order status from modifications
        order.status = OrderStatus.COMPLETED  
        
        await db.commit()
        await db.refresh(new_bill)

        # 4. Generate structured items breakdown list
        formatted_items = []
        for item in order.items:
            formatted_items.append({
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": item.product.price,
                "subtotal": item.product.price * item.quantity
            })

        # 5. Compile the string metadata hidden within the visual QR array
        payment_payload = f"SMART_BASKET_PAY:BILL_ID={new_bill.id}:TOTAL={new_bill.total_price}"
        qr_code_image = PaymentService.generate_qr_base64(payment_payload)

        return {
            "bill_id": new_bill.id,
            "order_id": order.id,
            "status": new_bill.status,
            "items": formatted_items,
            "total_price": new_bill.total_price,
            "created_at": new_bill.created_at,
            "qr_code_base64": qr_code_image
        }