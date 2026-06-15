from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from database.base import Base
from database.connection import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events."""
    # Automatically create database tables on startup if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown logic (closing connections, etc.) can go here if needed


# Initialize the FastAPI Application instance
app = FastAPI(
    title="Smart Basket IoT Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Register your product API routes
from api.product_route import router as product_router
from api.order_route import router as order_router
from api.payment_route import router as payment_router

app.include_router(product_router)
app.include_router(order_router)
app.include_router(payment_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Smart Basket IoT Backend API"}


if __name__ == "__main__":
    # Allows you to run the app by executing: python main.py
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)