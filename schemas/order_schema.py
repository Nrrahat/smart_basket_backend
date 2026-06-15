from pydantic import BaseModel, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import List
from models.order import OrderStatus
from schemas.product_schema import ProductResponse


class OrderItemResponse(BaseModel):
    product_id: int
    quantity: int
    product: ProductResponse  # Includes full product details (name, price, rfid)

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    status: OrderStatus
    total_price: Decimal
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderUpdateStatus(BaseModel):
    status: OrderStatus