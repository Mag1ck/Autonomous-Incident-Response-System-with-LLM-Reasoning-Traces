from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
import httpx
from pydantic import BaseModel


PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")

engine = create_async_engine(f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@postgres/{PG_DB}")
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Sku(BaseModel):
    sku: str
    name: str
    description: str
    price: float
    currency: str
    available_quantity: int
    in_stock: bool
    attributes: dict
    estimated_delivery_days: int

app = FastAPI()

@app.get("/health")
def get_health():
    return {"status": "healthy"}


@app.get("/inventory/{sku}", response_model = Sku)
async def get_order(sku: str):
    async with async_session() as session:
        async with session.begin():
            response = await session.get(OrderTable, order_id)
            if response is not None:
                return response
            else:
                raise HTTPException(status_code = 404, detail = "Order not found")