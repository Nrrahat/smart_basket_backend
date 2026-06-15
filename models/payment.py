# app/models/payment.py
import enum
from datetime import datetime
from sqlalchemy import ForeignKey, Numeric, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base

class BillStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"

class Bill(Base):
    __tablename__ = "bills"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[BillStatus] = mapped_column(Enum(BillStatus), default=BillStatus.PENDING, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Bidirectional Relationship back to Order
    order: Mapped["Order"] = relationship(back_populates="bill")