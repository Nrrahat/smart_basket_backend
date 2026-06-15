from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from models.product import Product
from schemas.product_schema import ProductCreate


class ProductService:
    """Service layer handling all business logic and database queries for Products."""

    @staticmethod
    async def get_all_products(db: AsyncSession, category: Optional[str] = None) -> List[Product]:
        """Fetch all products, optionally filtering by category."""
        query = select(Product)
        if category:
            query = query.where(Product.category == category)
            
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_product_by_rfid(db: AsyncSession, rfid_uid: str) -> Optional[Product]:
        """Fetch a single product by its unique RFID tag UID."""
        query = select(Product).where(Product.rfid_uid == rfid_uid)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
        """Validate unique business rules and insert a new product."""
        # Enforce unique constraint check for RFID UIDs safely at the service level
        if product_data.rfid_uid:
            existing_product = await ProductService.get_product_by_rfid(
                db, rfid_uid=product_data.rfid_uid
            )
            if existing_product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"A product with RFID UID '{product_data.rfid_uid}' already exists."
                )

        new_product = Product(**product_data.model_dump())
        db.add(new_product)
        await db.flush()  # Populates id and timestamps fields
        return new_product