from decimal import Decimal
from typing import Optional
from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Product(Base):
    """Product model representing items in the inventory.
    
    Inherits 'id', 'created_at', and 'updated_at' from Base.
    The table name will automatically be set to 'product'.
    """
    __tablename__ = "products"

    # RFID unique identifier (indexed for fast scanning lookups, optional if items aren't tagged yet)
    rfid_uid: Mapped[Optional[str]] = mapped_column(
        String(64), unique=True, index=True, nullable=True
    )
    
    # Product name
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    # Price (Using Numeric/Decimal instead of Float to avoid rounding errors)
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False, default=0.00
    )
    
    # Weight (Using Float or Numeric depending on precision needed, e.g., in grams/kg)
    weight: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Category name or type
    category: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"