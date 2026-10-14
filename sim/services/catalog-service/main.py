from fastapi import FastAPI, HTTPException, Request
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from pydantic import BaseModel
import os
from databases import Product
import httpx
from datetime import datetime, timezone
import json
import time


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

async def emit_observation(observation: dict):
    observation["source"] = "catalog-service"
    print(json.dumps(observation))
    try:
        await app.state.client.request("POST", "http://incident-service:8000/observations", timeout=0.5, json = observation)
    except httpx.RequestError:
        pass

async def get_inventory(sku: str, correlation_id: str):
    headers = {'X-Correlation-ID': correlation_id}
    start = time.monotonic()
    try:
        r = await app.state.client.get(f"http://toxiproxy:20000/inventory/{sku}", headers=headers, timeout = 1)
        observ_output = {
            "event": "downstream_request",
            "route": "GET /inventory/{sku}",
            "latency": (time.monotonic() - start),
            "downstream_service": "inventory-service",
            "operation": "get_inventory",
            "status_code": r.status_code,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uuid": f"{correlation_id}"
        }
        await emit_observation(observ_output)
    except httpx.RequestError:
        observ_output = {
            "event": "downstream_request",
            "route": "GET /inventory/{sku}",
            "latency": (time.monotonic() - start),
            "downstream_service": "inventory-service",
            "operation": "get_inventory",
            "status_code": 502,
            "error": "service_unavailable",
            "error_type": "transport_error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uuid": f"{correlation_id}"
        }
        await emit_observation(observ_output)
        raise HTTPException(status_code = 502, detail = "Inventory service unavailable")
    body = r.json()
    status_code = r.status_code
    if status_code == 200:
        validated = InventoryResponse.model_validate(body)
        return validated
    else:
        observ_output = {
            "event": "downstream_request",
            "route": "GET /inventory/{sku}",
            "latency": (time.monotonic() - start),
            "downstream_service": "inventory-service",
            "operation": "get_inventory",
            "status_code": status_code,
            "error": "service_unavailable",
            "error_type": "transport_error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uuid": f"{correlation_id}"
        }
        await emit_observation(observ_output)
        raise HTTPException(status_code = 502, detail = "Inventory service unavailable")


@app.get("/catalog/{sku}", response_model = ProductResponse)
async def get_product(sku: str, request: Request):
    correlation_id = request.headers.get("X-Correlation-ID")
    if correlation_id is None:
        correlation_id = "unknown"
    async with async_session() as session:
        async with session.begin():
            response = await session.get(Product, sku)
            if response is not None:
                response_inventory = await get_inventory(sku, correlation_id)
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