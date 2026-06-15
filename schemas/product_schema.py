from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProductBase(BaseModel):
    """Shared fields for Product schemas."""
    rfid_uid: Optional[str] = Field(None, max_length=64, description="Unique RFID tag identifier")
    name: str = Field(..., min_length=1, max_length=255, description="Name of the product")
    price: Decimal = Field(..., ge=0, description="Price of the product (must be 0 or greater)")
    weight: Optional[float] = Field(None, ge=0, description="Weight of the product in grams/kg")
    category: str = Field(..., min_length=1, max_length=100, description="Product category")


class ProductCreate(ProductBase):
    """Schema for validating data when creating a new product."""
    pass  # Inherits all fields from ProductBase as required/optional payloads


class ProductResponse(ProductBase):
    """Schema for serialization when returning product data from the API."""
    id: int = Field(..., description="Database auto-incremented primary key")
    created_at: datetime
    updated_at: datetime

    # Pydantic v2 configuration to cleanly serialize data from SQLAlchemy object instances
    model_config = ConfigDict(from_attributes=True)