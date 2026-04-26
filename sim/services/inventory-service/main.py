from fastapi import FastAPI, HTTPException
from databases import InventoryItems
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from pydantic import BaseModel
import os
from datetime import datetime

PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")

engine = create_async_engine(f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@postgres/{PG_DB}")
async_session = async_sessionmaker(engine, expire_on_commit=False)

app = FastAPI()

class InventoryItemsResponse(BaseModel):
    sku: str
    available_quantity: int
    in_stock: bool
    updated_at: datetime


@app.get("/health")
def get_health():
    return {"status": "healthy"}


@app.get("/inventory/{sku}", response_model = InventoryItemsResponse)
async def get_inventory_items(sku: str):
    async with async_session() as session:
        async with session.begin():
            response = await session.get(InventoryItems, sku)
            if response is not None:
                return {"sku": response.sku, "available_quantity": response.available_quantity,
                        "in_stock": response.available_quantity > 0,
                         "updated_at": response.updated_at}
            else:
                raise HTTPException(status_code = 404, detail = "Inventory item not found")