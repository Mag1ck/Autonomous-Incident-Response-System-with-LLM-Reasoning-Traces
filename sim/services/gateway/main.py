from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx
import asyncio
import time
from pydantic import BaseModel
from datetime import datetime, timezone
import json
import uuid



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

class CatalogResponse(BaseModel):
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


def get_correlation_id():
    return uuid.uuid4()


async def get_service_health(request, service, correlation_id):
    start = time.monotonic()
    try:
        r = await app.state.client.get(f"http://{service}:8000/health", timeout = 3)
        latency = (time.monotonic() - start)
        output = {
        "event": "healthcheck_probe",
        "route": f"{request.method} {request.scope['route'].path}",
        "latency": latency,
        "downstream_service": service,
        "operation": "check_service_health",
        "status_code": r.status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uuid": f"{correlation_id}"
    }
        await emit_observation(output)
        r = r.json()
        return {"service": f"{service}", "status": r["status"], "latency": latency}
    except httpx.RequestError:
        output = {
        "event": "healthcheck_probe",
        "route": f"{request.method} {request.scope['route'].path}",
        "latency": (time.monotonic() - start),
        "downstream_service": service,
        "operation": "check_service_health",
        "status_code": 502,
        "error": "service_unavailable",
        "error_type": "transport_error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uuid": f"{correlation_id}"
    }
        await emit_observation(output)
        return {"service": f"{service}", "status": "unreachable", "latency": None, "error": "service_unreachable"}
    
async def emit_observation(observation: dict):
    print(json.dumps(observation))
    try:
        await app.state.client.request("POST", "http://incident-service:8000/observations", timeout=0.5, json = observation)
    except httpx.RequestError:
        pass
    

async def call_downstream(request, method, url, service, operation, correlation_id, json_body = None):
    start = time.monotonic()
    try:
        r = await app.state.client.request(method, url, timeout=3, json = json_body,  headers={'X-Correlation-ID': f"{correlation_id}"})
        output = {
        "event": "downstream_request",
        "route": f"{request.method} {request.scope['route'].path}",
        "latency": (time.monotonic() - start),
        "downstream_service": service,
        "operation": operation,
        "status_code": r.status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uuid": f"{correlation_id}"
    }
        if output["status_code"] >= 500:
            output["error"] = "downstream_http_error"
            output["error_type"] = "http_status"
        await emit_observation(output)
        return r
    except httpx.RequestError:
        output = {
        "event": "downstream_request",
        "route": f"{request.method} {request.scope['route'].path}",
        "latency": (time.monotonic() - start),
        "downstream_service": service,
        "operation": operation,
        "status_code": 502,
        "error": "service_unavailable",
        "error_type": "transport_error",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uuid": f"{correlation_id}"
    }
        await emit_observation(output)
        raise HTTPException(status_code = 502, detail = f"{service} unavailable")


@app.get("/health")
def get_health():
    return {"status": "healthy"}

@app.get("/health/all-services")
async def all_services_health(request: Request):
    correlation_id = get_correlation_id()
    catalog_service, fraud_service, inventory_service, order_service, payment_service, user_service = await asyncio.gather(
    get_service_health(request, "catalog-service", correlation_id), get_service_health(request, "fraud-service", correlation_id),
    get_service_health(request, "inventory-service", correlation_id), get_service_health(request, "order-service", correlation_id),
    get_service_health(request, "payment-service", correlation_id), get_service_health(request, "user-service", correlation_id))
    services = [catalog_service, fraud_service, inventory_service, order_service, payment_service, user_service]
    healthy = []
    unhealthy = []
    for service in services:
        if service["status"] == "unreachable":
            unhealthy.append(service)
        else:
            healthy.append(service)
    return {"healthy_count": len(healthy), "unhealthy_count": len(unhealthy), "healthy": healthy, "unhealthy": unhealthy}

@app.get("/health/catalog-service")
async def catalog_service_health(request: Request):
    correlation_id = get_correlation_id()
    return await get_service_health(request, "catalog-service", correlation_id)

@app.get("/health/fraud-service")
async def fraud_service_health(request: Request):
    correlation_id = get_correlation_id()
    return await get_service_health(request, "fraud-service", correlation_id)

@app.get("/health/inventory-service")
async def inventory_service_health(request: Request):
    correlation_id = get_correlation_id()
    return await get_service_health(request, "inventory-service", correlation_id)

@app.get("/health/order-service")
async def order_service_health(request: Request):
    correlation_id = get_correlation_id()
    return await get_service_health(request, "order-service", correlation_id)

@app.get("/health/payment-service")
async def payment_service_health(request: Request):
    correlation_id = get_correlation_id()
    return await get_service_health(request, "payment-service", correlation_id)

@app.get("/health/user-service")
async def user_service_health(request: Request):
    correlation_id = get_correlation_id()
    return await get_service_health(request, "user-service", correlation_id)

@app.post("/orders", response_model = OrderResponse)
async def post_order(request: Request, order: OrderRequest):
    correlation_id = get_correlation_id()
    r = await call_downstream(request, "POST", f"http://order-service:8000/orders", "order-service", "create_order", correlation_id,
                              json_body = order.model_dump())
    body = r.json()
    status_code = r.status_code
    if status_code == 201:
        validated = OrderResponse.model_validate(body)
        return JSONResponse(content = validated.model_dump(mode = "json"), status_code = status_code)
    return JSONResponse(content = body, status_code = status_code)

@app.get("/orders/{order_id}", response_model = OrderResponse)
async def get_order(request: Request, order_id: int):
    correlation_id = get_correlation_id()
    r = await call_downstream(request, "GET", f"http://order-service:8000/orders/{order_id}", "order-service", "get_order", 
                              correlation_id)
    body = r.json()
    status_code = r.status_code
    if status_code == 200:
        validated = OrderResponse.model_validate(body)
        return JSONResponse(content = validated.model_dump(mode = "json"), status_code = status_code)
    return JSONResponse(content = body, status_code = status_code)

@app.get("/catalog/{sku}", response_model = CatalogResponse)
async def get_product(request: Request, sku: str):
    correlation_id = get_correlation_id()
    r = await call_downstream(request, "GET", f"http://catalog-service:8000/catalog/{sku}", "catalog-service", "get_product", 
                              correlation_id)
    body = r.json()
    status_code = r.status_code
    if status_code == 200:
        validated = CatalogResponse.model_validate(body)
        return JSONResponse(content = validated.model_dump(mode = "json"), status_code = status_code)
    return JSONResponse(content = body, status_code = status_code)