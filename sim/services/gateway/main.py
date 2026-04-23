from fastapi import FastAPI
import httpx
import asyncio
import time

app = FastAPI()
client = httpx.AsyncClient()

async def get_service_health(service):
    start = time.monotonic()
    try:
        r = await client.get(f'http://{service}:8000/health')
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
    get_service_health("catalog-service"), get_service_health("fraud-service"), 
    get_service_health("inventory-service"), get_service_health("order-service"), 
    get_service_health("payment-service"), get_service_health("user-service"))
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
    return await get_service_health("catalog-service")

@app.get("/health/fraud-service")
async def fraud_service_health():
    return await get_service_health("fraud-service")

@app.get("/health/inventory-service")
async def inventory_service_health():
    return await get_service_health("inventory-service")

@app.get("/health/order-service")
async def order_service_health():
    return await get_service_health("order-service")

@app.get("/health/payment-service")
async def payment_service_health():
    return await get_service_health("payment-service")

@app.get("/health/user-service")
async def user_service_health():
    return await get_service_health("user-service")

