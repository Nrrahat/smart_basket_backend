# app/schemas/payment.py
from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal
from datetime import datetime

class CheckoutRequest(BaseModel):
    order_id: int = Field(..., description="The ID of the order session to check out")

class BillItemResponse(BaseModel):
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = {
        "from_attributes": True  # Modern Pydantic v2 style
    }

class BillResponse(BaseModel):
    bill_id: int
    order_id: int
    status: str
    items: List[BillItemResponse]
    total_price: Decimal
    created_at: datetime
    qr_code_base64: str = Field(..., description="Base64 encoded PNG string of the payment QR code")

    model_config = {
        "from_attributes": True  # Modern Pydantic v2 style
    }