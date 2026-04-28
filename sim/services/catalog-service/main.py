from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from pydantic import BaseModel
import os
from databases import Product
import httpx
from datetime import datetime


PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")

engine = create_async_engine(f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@postgres/{PG_DB}")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class ProductResponse(BaseModel):
    sku: str
    name: str
    description: str
    price_in_cents: int
    currency: str
    attributes: dict
    estimated_delivery_days: int | None
    available_quantity: int
    in_stock: bool
    inventory_updated_at: datetime

class InventoryResponse(BaseModel):
    sku: str
    available_quantity: int
    in_stock: bool
    updated_at: datetime


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = httpx.AsyncClient()
    app.state.client = client
    yield
    await client.aclose()

app = FastAPI(lifespan = lifespan)

@app.get("/health")
def get_health():
    return {"status": "healthy"}

async def get_inventory(sku: str):
    try:
        r = await app.state.client.get(f'http://inventory-service:8000/inventory/{sku}', timeout = 3)
    except httpx.RequestError:
        raise HTTPException(status_code = 502, detail = "Inventory service unavailable")
    body = r.json()
    status_code = r.status_code
    if status_code == 200:
        validated = InventoryResponse.model_validate(body)
        return validated
    else:
        raise HTTPException(status_code = 502, detail = "Inventory service unavailable")


@app.get("/catalog/{sku}", response_model = ProductResponse)
async def get_product(sku: str):
    async with async_session() as session:
        async with session.begin():
            response = await session.get(Product, sku)
            if response is not None:
                response_inventory = await get_inventory(sku)
                if response_inventory is not None:
                    return {"sku": response_inventory.sku,
                            "name": response.name,
                            "description": response.description,
                            "price_in_cents": response.price_in_cents,
                            "currency": response.currency,
                            "attributes": response.attributes,
                            "estimated_delivery_days": response.estimated_delivery_days,
                            "available_quantity": response_inventory.available_quantity,
                            "in_stock": response_inventory.in_stock,
                            "inventory_updated_at": response_inventory.updated_at}
                raise HTTPException(status_code = 502, detail = "Inventory service unavailable")
            else:
                raise HTTPException(status_code = 404, detail = "Product not found")