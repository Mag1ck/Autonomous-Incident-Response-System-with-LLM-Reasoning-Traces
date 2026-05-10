# Autonomous Incident Response System with LLM Reasoning Traces

In-progress local SRE simulation platform for experimenting with autonomous incident detection, root-cause analysis, and explainable LLM-assisted remediation.

The current phase focuses on building a realistic microservice simulation environment before adding full observability, statistical anomaly detection, causal inference, and local LLM reasoning.

## Current Status

Phase 1: microservice simulation environment.

The project currently includes a Docker Compose-based local service topology with FastAPI services, PostgreSQL-backed domain state for selected services, Alembic-managed migrations, gateway-level health aggregation, basic structured observation forwarding, and Toxiproxy-based network fault injection setup.

## Current Features

- Docker Compose-based local microservice environment
- FastAPI services for:
  - gateway
  - order-service
  - catalog-service
  - inventory-service
  - incident-service
  - payment-service
  - fraud-service
  - user-service
- Internal Docker bridge network with only the gateway exposed to the host
- Gateway health aggregation across downstream services
- PostgreSQL and Redis included in the simulation topology
- Toxiproxy included for controlled network fault injection
- Alembic migration containers for order, catalog, and inventory schema setup
- Seed data migrations for catalog and inventory services
- Async SQLAlchemy integration for DB-backed services
- Order creation and order lookup endpoints
- Catalog lookup endpoint enriched with inventory state
- Gateway-emitted structured observations for downstream calls and health probes
- Basic incident-service endpoint for collecting recent observations in memory

## Implemented Service Flows

### Health Aggregation

```text
client
  -> gateway
      -> catalog-service
      -> fraud-service
      -> inventory-service
      -> order-service
      -> payment-service
      -> user-service
```

### Browse Product

```text
client
  -> gateway
      -> catalog-service
          -> toxiproxy
              -> inventory-service
```

### Order API

```text
client
  -> gateway
      -> order-service
          -> postgres
```

## Public Gateway Endpoints

- `GET /health`
- `GET /health/all-services`
- `GET /health/{service}`
- `GET /catalog/{sku}`
- `POST /orders`
- `GET /orders/{order_id}`

## Internal Service Endpoints

Order service:

- `GET /health`
- `POST /orders`
- `GET /orders/{order_id}`

Catalog service:

- `GET /health`
- `GET /catalog/{sku}`

Inventory service:

- `GET /health`
- `GET /inventory/{sku}`

Incident service:

- `GET /health`
- `POST /observations`
- `GET /observations/recent`

Payment, fraud, and user services currently expose health endpoints and are placeholders for later workflow phases.


## Technology Stack

Current:

- Python
- FastAPI
- Pydantic
- SQLAlchemy async
- Alembic
- PostgreSQL
- Redis
- Docker
- Docker Compose
- Toxiproxy
- httpx

Planned:

- Prometheus
- Grafana
- OpenTelemetry
- Redis Streams
- Statistical anomaly detection
- Causal inference / root-cause analysis
- Local LLM reasoning with Ollama
- ChromaDB-backed runbook retrieval
- Automated remediation workflows
- Engineer feedback loop

## Local Development

Create a local Compose environment file:

```bash
cd sim

cat > .env <<EOF
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=incident_response
EOF
```

Start the simulation:

```bash
docker compose up --build
```

Gateway is exposed on:

```text
http://localhost:8000
```

Example checks:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/all-services
curl http://localhost:8000/catalog/SKU-NORMAL-001
```

Example order creation:

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-001","sku":"SKU-NORMAL-001","quantity":1}'
```

## Planned Next Milestones

- Add realistic traffic generator with browse, order, and order-status flows
- Implement Redis Streams-based asynchronous fraud-check workflow
- Expand order workflow to call user, inventory, and payment services
- Persist incident observations instead of storing them only in memory
- Add Prometheus metrics and structured logging conventions
- Add OpenTelemetry traces across service boundaries
- Build statistical anomaly detection over latency, error-rate, and saturation signals
- Add causal inference / root-cause analysis over service dependency graphs
- Generate local LLM reasoning traces with explicit hypotheses and confidence
- Add audited remediation actions and engineer feedback capture
