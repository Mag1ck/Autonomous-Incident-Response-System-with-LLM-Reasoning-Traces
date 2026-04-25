import os
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from pydantic import BaseModel
from databases import OrderTable
from datetime import datetime, timezone


PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")

engine = create_async_engine(f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@postgres/{PG_DB}")
async_session = async_sessionmaker(engine, expire_on_commit=False)




class Order(BaseModel):
    user_id: str
    sku: str
    quantity: int

class OrderResponse(BaseModel):
    order_id: int
    user_id: str
    sku: str
    quantity: int
    order_status: str
    payment_status: str
    fraud_status: str
    created_at: datetime
    updated_at: datetime
    rejection_reason: str | None


app = FastAPI()


@app.get("/health")
def get_health():
    return {"status": "healthy"}

@app.post("/orders", status_code=201, response_model = OrderResponse)
async def post_order(order: Order):
    now = datetime.now(timezone.utc)
    new_order = OrderTable(user_id = order.user_id, sku = order.sku, quantity = order.quantity, order_status = "pending",
                           payment_status = "pending", fraud_status = "pending", created_at = now,
                            updated_at = now)
    async with async_session() as session:
        async with session.begin():
            session.add(new_order)
            await session.flush()
    
    return {"order_id": new_order.order_id, "user_id": new_order.user_id, "sku": new_order.sku,
             "quantity": new_order.quantity, "order_status": new_order.order_status,
             "payment_status": new_order.payment_status, "fraud_status": new_order.fraud_status,
             "created_at": new_order.created_at, "updated_at": new_order.updated_at,
             "rejection_reason": new_order.rejection_reason}

@app.get("/orders/{order_id}", response_model = OrderResponse)
async def get_order(order_id: int):
    async with async_session() as session:
        async with session.begin():
            response = await session.get(OrderTable, order_id)
            if response is not None:
                return response
            else:
                raise HTTPException(status_code = 404, detail = "Order not found")