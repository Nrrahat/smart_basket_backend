from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from database.connection import get_db_session
from schemas.product_schema import ProductCreate, ProductResponse
from services.product_service import ProductService

router = APIRouter(tags=["Products"])


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Simple API health check endpoint to verify the service status."""
    return {"status": "healthy"}


@router.get("/products", response_model=List[ProductResponse], status_code=status.HTTP_200_OK)
async def get_products(
    category: Optional[str] = None, 
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch all products, optionally filtered by a specific category."""
    return await ProductService.get_all_products(db, category=category)


@router.get("/products/{rfid_uid}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
async def get_product_by_rfid(
    rfid_uid: str, 
    db: AsyncSession = Depends(get_db_session)
):
    """Fetch a single product details using its unique RFID tag UID."""
    product = await ProductService.get_product_by_rfid(db, rfid_uid=rfid_uid)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with RFID UID '{rfid_uid}' not found."
        )
    return product


@router.post("/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate, 
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new product entry in the system."""
    return await ProductService.create_product(db, product_data)