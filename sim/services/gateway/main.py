from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx
import asyncio
import time
from pydantic import BaseModel
from datetime import datetime



@asynccontextmanager
async def lifespan(app: FastAPI):
    client = httpx.AsyncClient()
    app.state.client = client
    yield
    await client.aclose()

app = FastAPI(lifespan = lifespan)

class OrderRequest(BaseModel):
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

async def get_service_health(client, service):
    start = time.monotonic()
    try:
        r = await client.get(f'http://{service}:8000/health', timeout = 3)
        latency = (time.monotonic() - start)
        r = r.json()
        return {"service": f"{service}", "status": r['status'], "latency": latency}
    except Exception as E:
        return {"service": f"{service}", "status": "unreachable", "latency": None, "Error": str(E)}

@app.get("/health")
def get_health():
    return {"status": "healthy"}

@app.get("/health/all-services")
async def all_services_health():
    catalog_service, fraud_service, inventory_service, order_service, payment_service, user_service = await asyncio.gather(
    get_service_health(app.state.client, "catalog-service"), get_service_health(app.state.client, "fraud-service"), 
    get_service_health(app.state.client, "inventory-service"), get_service_health(app.state.client, "order-service"), 
    get_service_health(app.state.client, "payment-service"), get_service_health(app.state.client, "user-service"))
    services = [catalog_service, fraud_service, inventory_service, order_service, payment_service, user_service]
    healthy = []
    unhealthy = []
    for service in services:
        if service['status'] == 'unreachable':
            unhealthy.append(service)
        else:
            healthy.append(service)
    return {"healthy_count": len(healthy), "unhealthy_count": len(unhealthy), "healthy": healthy, "unhealthy": unhealthy}

@app.get("/health/catalog-service")
async def catalog_service_health():
    return await get_service_health(app.state.client, "catalog-service")

@app.get("/health/fraud-service")
async def fraud_service_health():
    return await get_service_health(app.state.client, "fraud-service")

@app.get("/health/inventory-service")
async def inventory_service_health():
    return await get_service_health(app.state.client, "inventory-service")

@app.get("/health/order-service")
async def order_service_health():
    return await get_service_health(app.state.client, "order-service")

@app.get("/health/payment-service")
async def payment_service_health():
    return await get_service_health(app.state.client, "payment-service")

@app.get("/health/user-service")
async def user_service_health():
    return await get_service_health(app.state.client, "user-service")

@app.post("/orders", response_model = OrderResponse)
async def post_order(order: OrderRequest):
    try:
        r = await app.state.client.post(f'http://order-service:8000/orders', json = order.model_dump(), timeout = 3)
    except httpx.RequestError:
        raise HTTPException(status_code = 502, detail = "Order service unavailable")
    body = r.json()
    status_code = r.status_code
    if status_code == 201:
        validated = OrderResponse.model_validate(body)
        return JSONResponse(content = validated.model_dump(mode = "json"), status_code = status_code)
    return JSONResponse(content = body, status_code = status_code)

@app.get("/orders/{order_id}", response_model = OrderResponse)
async def get_order(order_id: int):
    try:
        r = await app.state.client.get(f'http://order-service:8000/orders/{order_id}', timeout = 3)
    except httpx.RequestError:
        raise HTTPException(status_code = 502, detail = "Order service unavailable")
    body = r.json()
    status_code = r.status_code
    if status_code == 200:
        validated = OrderResponse.model_validate(body)
        return JSONResponse(content = validated.model_dump(mode = "json"), status_code = status_code)
    return JSONResponse(content = body, status_code = status_code)
