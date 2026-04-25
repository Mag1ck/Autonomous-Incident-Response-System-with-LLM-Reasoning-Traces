import os
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from pydantic import BaseModel
from contextlib import asynccontextmanager


PG_USER = os.getenv("POSTGRES_USER")
PG_PASS = os.getenv("POSTGRES_PASSWORD")
PG_DB = os.getenv("POSTGRES_DB")

engine = create_async_engine(f"postgresql+asyncpg://{PG_USER}:{PG_PASS}@postgres/{PG_DB}")
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass

class OrderTable(Base):
    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    order_status: Mapped[str] = mapped_column(String, nullable=False)
    payment_status: Mapped[str] = mapped_column(String, nullable=False)
    fraud_status: Mapped[str] = mapped_column(String, nullable=False)

class Order(BaseModel):
    user_id: str
    sku: str
    quantity: int

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan = lifespan)


@app.get("/health")
def get_health():
    return {"status": "healthy"}

@app.post("/orders")
async def post_order(order: Order):
    new_order = OrderTable(user_id = order.user_id, sku = order.sku, quantity = order.quantity, order_status = "pending",
                           payment_status = "pending", fraud_status = "pending")
    async with async_session() as session:
        async with session.begin():
            session.add(new_order)
            await session.flush()
    
    return {"status": "success", "order_id": new_order.order_id, "user_id": new_order.user_id, "sku": new_order.sku,
             "quantity": new_order.quantity}