# MeshMart Service Mesh Observability Platform

MeshMart is an online shopping microservices platform built to show service-to-service communication, traffic control, fault handling, and observability in a distributed system.

The application is intentionally small, but it is structured like a real production system: independent services, container packaging, Kubernetes manifests, Istio traffic policies, retry-safe checkout, and telemetry evidence through metrics, traces, logs, and service topology.

## Architecture

```text
Browser / Postman
  -> Istio Ingress Gateway
  -> frontend
  -> order-service
      -> product-service
      -> payment-service
      -> notification-service
```

## Repository Layout

```text
meshmart-service-mesh/
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

## Services

| Service | Port | Responsibility |
| --- | --- | --- |
| frontend | 8080 | MeshMart storefront and operational checkout panel |
| product-service | 8004 | Product catalog, inventory reservation, customer reviews, pricing, stock, and product metadata |
| order-service | 8001 | Cart checkout orchestration, order history, idempotency, and service-to-service calls |
| payment-service | 8002 | Payment approval, decline, and slow-processor behavior |
| notification-service | 8003 | Checkout notification result |

## API List

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/products` | List product catalog |
| GET | `/products/{id}` | Get one product by id |
| GET | `/products/{id}/reviews` | List customer reviews for one product |
| POST | `/products/{id}/reviews` | Submit rating, comment, and optional image URL |
| POST | `/orders` | Create an order and trigger payment + notification |
| GET | `/orders` | List recent orders, optionally filtered by `user_id` |
| GET | `/orders/{id}` | Get one stored order by id |
| POST | `/payments` | Process a payment directly |
| POST | `/notifications` | Send a notification directly |
| GET | `/health` | Check service health |

`POST /orders` supports the `Idempotency-Key` header. Retrying the same checkout payload with the same key returns the same logical order id instead of creating duplicate orders.

## Run Locally

```bash
docker compose up --build
```

Open the storefront:

```text
http://localhost:8080
```

Call the catalog service:

```bash
curl http://localhost:8004/products
```

Create an order:

```bash
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: order-local-001" \
  -H "X-Request-Id: req-local-001" \
  -d "{\"user_id\":\"customer-001\",\"items\":[{\"product_id\":\"PROD-001\",\"quantity\":1},{\"product_id\":\"PROD-003\",\"quantity\":2}],\"payment_mode\":\"success\"}"
```

Expected response:

```json
{
  "order_status": "confirmed",
  "amount": 1077.0,
  "inventory": {
    "inventory_status": "committed"
  },
  "payment": {
    "payment_status": "success"
  },
  "notification": "sent"
}
```

## Operational Scenarios

1. Normal checkout: `payment_mode=success`.
2. Payment decline: `payment_mode=failed`.
3. Inventory compensation: declined payment releases reserved stock.
4. Product review: submit rating, comment, and image URL after checkout.
5. Slow payment processor: `payment_mode=delayed`.
6. Retry-safe checkout: send the same `Idempotency-Key` twice.
7. Timeout/retry policy: inspect Istio `VirtualService` and payment policy behavior.
8. Scaling: run `load-test.js` before and after increasing backend replicas or enabling HPA.
9. Observability: inspect metrics, traces, logs, and service graph.

## Kubernetes And Istio

The `k8s/` folder contains Deployment, Service, HorizontalPodAutoscaler, and PodDisruptionBudget manifests. The `istio/` folder contains Gateway, VirtualService, DestinationRule, telemetry, and payment policy configuration.

Typical local cluster flow:

```bash
kubectl create namespace meshmart
kubectl label namespace meshmart istio-injection=enabled
kubectl apply -n meshmart -f k8s/
kubectl apply -n meshmart -f istio/gateway.yaml
kubectl apply -n meshmart -f istio/virtual-service.yaml
kubectl apply -n meshmart -f istio/destination-rule.yaml
kubectl apply -n meshmart -f istio/payment-policy.yaml
kubectl apply -n meshmart -f istio/security.yaml
kubectl apply -f istio/telemetry-tracing.yaml
```

Images use the project tag `meshmart-service-mesh/*:v1.0.0`. Replace this with your registry path before deploying to a remote cluster.

## Observability

The platform is designed to answer practical distributed-system questions:

| Question | Evidence |
| --- | --- |
| Is the system healthy overall? | Prometheus metrics and Grafana dashboards |
| Where did one request spend time? | Jaeger distributed trace spans |
| Which services communicate? | Kiali service mesh topology |
| What happened inside a service? | Structured request logs with `request_id`, status, and duration |

Useful files:

- [docs/PRESENTATION_ARCHITECTURE_SCRIPT.md](docs/PRESENTATION_ARCHITECTURE_SCRIPT.md)
- [docs/REPORT.md](docs/REPORT.md)
- [docs/EVALUATION.md](docs/EVALUATION.md)
- [docs/KUBERNETES_ISTIO.md](docs/KUBERNETES_ISTIO.md)
- [observability/README.md](observability/README.md)

## Project Strengths

- Clear microservice boundaries.
- Real cart checkout flow with multi-item orders and recent order history.
- Inventory reservation with stock decrement and compensation on payment failure.
- Customer product reviews with rating, comment, and optional image URL.
- Istio Gateway and VirtualService routing.
- Retry, timeout, outlier detection, and fault behavior around service traffic.
- Idempotent order creation for client retries.
- Graceful degradation when notification delivery is unavailable.
- Resource requests, limits, HPA, and PodDisruptionBudgets for scalability and availability.
- Request-id logging across services.
- Productive storefront UI plus operational evidence panel.

## Future Work

- Persist product/order/idempotency data in PostgreSQL or Redis.
- Add authentication and authorization policy.
- Add mTLS policy documentation and screenshots.
- Add alert rules for high latency and payment failure rate.
- Publish images to a container registry and deploy to a remote cluster.
