# Service Mesh Observability Demo

Microservices demo for a distributed system course project. The app models a small shopping flow and is prepared for Docker, Kubernetes, Istio, and observability tooling.

## Architecture

```text
frontend
   |
   |--> product-service
   |--> order-service
           |--> product-service
           |--> payment-service
           |--> notification-service
```

## Repository Layout

```text
service-mesh-observability-demo/
|-- frontend/
|-- product-service/
|-- order-service/
|-- payment-service/
|-- notification-service/
|-- k8s/
|-- istio/
|-- observability/
|-- docs/
|-- scripts/
|-- docker-compose.yml
|-- README.md
```

## API List

In Docker Compose, the frontend calls `product-service` and `order-service` through host ports.
In Kubernetes, Istio routes public traffic to frontend and backend APIs.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/products` | List demo products |
| GET | `/products/{id}` | Get one product by id |
| POST | `/orders` | Create an order and trigger payment + notification |
| POST | `/payments` | Process a payment directly |
| POST | `/notifications` | Send a notification directly |
| GET | `/health` | Check service health |

More details are in [docs/API.md](docs/API.md).

`POST /orders` supports the `Idempotency-Key` header to make client retries safe during network failures or timeout retries.

## Services

| Service | Port | Main endpoints |
| --- | --- | --- |
| frontend | 8080 | Static demo UI |
| product-service | 8004 | `/products`, `/products/{id}`, `/health` |
| order-service | 8001 | `/orders`, `/health` |
| payment-service | 8002 | `/payments`, `/payment/process`, `/payment/fail`, `/payment/delay`, `/health` |
| notification-service | 8003 | `/notifications`, `/health` |

## Run Locally

```bash
docker compose up --build
```

Open the demo UI:

```text
http://localhost:8080
```

Call the services:

```bash
curl http://localhost:8004/products
```

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"demo-user\",\"product_id\":\"PROD-001\",\"quantity\":1,\"payment_mode\":\"success\"}"
```

Expected order response:

```json
{
  "order_id": "ORD-001",
  "order_status": "confirmed",
  "amount": 899.0,
  "notification": "sent"
}
```

## Demo Scenarios

1. Normal request: call `POST /orders` with `payment_mode=success`.
2. Payment delay: call `POST /orders` with `payment_mode=delayed`.
3. Payment failure: call `POST /orders` with `payment_mode=failed`.
4. Observability: inspect traffic, latency, and errors with Istio, Prometheus, Grafana, and Jaeger.
5. Scaling: run `load-test.js` before and after increasing backend replicas.

The final presentation walkthrough is in [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md).
Evidence checklist and load-test results are in [docs/DEMO_EVIDENCE.md](docs/DEMO_EVIDENCE.md).
The report outline and evaluation table are in [docs/REPORT.md](docs/REPORT.md) and [docs/EVALUATION.md](docs/EVALUATION.md).
The chaos recovery demo is in [docs/CHAOS_DEMO.md](docs/CHAOS_DEMO.md).

Direct payment demo through `POST /payments`:

```json
{
  "order_id": "ORD-001",
  "amount": 100,
  "mode": "success"
}
```

Change `mode` to `failed` or `delayed` to demo error and latency behavior.

## Kubernetes and Istio

The `k8s/` folder contains first-pass Deployment and Service manifests.

The `istio/` folder contains:

- `gateway.yaml`
- `virtual-service.yaml`
- `destination-rule.yaml`

Typical local cluster flow:

```bash
kubectl apply -f k8s/
kubectl apply -f istio/gateway.yaml
kubectl apply -f istio/virtual-service.yaml
kubectl apply -f istio/destination-rule.yaml
kubectl apply -f istio/payment-policy.yaml
kubectl apply -f istio/telemetry-tracing.yaml
```

`istio/payment-fault-injection.yaml` is optional and should be applied only during a controlled fault-injection demo.

Image names use the explicit final demo tag `service-mesh-observability-demo/*:v1.0.0-demo`. Replace them with your registry image names before deploying to a remote cluster.

Step-by-step Kubernetes and Istio commands are in [docs/KUBERNETES_ISTIO.md](docs/KUBERNETES_ISTIO.md).
Short report notes for Istio, sidecars, observability, and load testing are in [docs/ISTIO_REPORT_NOTES.md](docs/ISTIO_REPORT_NOTES.md).
The automated evidence runner is [scripts/demo.ps1](scripts/demo.ps1).

## Optional API Gateway

The project uses Istio Gateway as the primary production-style ingress for Kubernetes. The `gateway/` folder is kept as an optional FastAPI edge gateway for comparison or local experiments. It is not required for the main Kubernetes/Istio demo path.

More detail: [docs/GATEWAY.md](docs/GATEWAY.md).

## Observability

Observability setup and dashboard notes are in [observability/README.md](observability/README.md).

## Docker

Docker build and run commands are in [docs/DOCKER.md](docs/DOCKER.md).

## Team Split

- Backend APIs: product, order, payment, notification
- Platform: Docker Compose, Kubernetes manifests, Istio routing
- Observability and demo: Grafana, Prometheus, Jaeger, failure scenarios, README/docs

