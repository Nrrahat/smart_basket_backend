from datetime import datetime, timezone
from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column
#from models.product import Product
#from models.order import Order, OrderItem


class Base(DeclarativeBase):
    """Abstract base class for all database models."""

    # Automatically generate __tablename__ based on class name (e.g., User -> user)
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    # Common columns every table should have
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )