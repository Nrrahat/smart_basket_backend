# models/order.py
import enum
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.product import Product  # Avoid circular imports at runtime
    from models.payment import Bill  # Avoid circular imports at runtime

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderItem(Base):
    """Association table linking Products to Orders with an explicit quantity."""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product: Mapped["Product"] = relationship()


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Modern 1-to-Many relationship mapping to items
    items: Mapped[List["OrderItem"]] = relationship(cascade="all, delete-orphan", lazy="selectin")
    
    # Modern 1-to-1 relationship mapping to the payment bill
    bill: Mapped[Optional["Bill"]] = relationship(back_populates="order", uselist=False)