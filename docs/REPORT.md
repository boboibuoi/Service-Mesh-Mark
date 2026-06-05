# Final Report Outline

## 1. Project Introduction

This project implements a resilient e-commerce microservices platform using Kubernetes, Istio service mesh, and observability tools.

Problem:

Microservice systems are vulnerable to partial failures, slow upstream services, duplicate client retries, and poor visibility across service boundaries. The project shows how a service mesh and clear API design improve reliability and debuggability.

## 2. Related Systems

- Kubernetes: container orchestration, service discovery, self-healing, scaling.
- Istio and Envoy: service mesh sidecars, ingress routing, retries, timeout, circuit breaker, telemetry.
- Prometheus and Grafana: metrics collection and dashboarding.
- Jaeger: distributed tracing.
- Kiali: service graph and mesh health visualization.

## 3. Architecture

```text
Client
  -> Istio Ingress Gateway
  -> frontend
  -> order-service
      -> product-service
      -> payment-service
      -> notification-service
```

Services:

- `product-service`: product catalog.
- `order-service`: orchestration service and idempotent order creation.
- `payment-service`: success, failure, and delay simulation.
- `notification-service`: notification side effect.
- `frontend`: frontend web experience.

## 4. Key Design Choices

### Service Mesh Instead Of Application-Only Routing

Istio Gateway and VirtualService route external traffic without adding routing logic to every service.

### Timeout, Retry, And Circuit Breaker

Payment Service can be slow or fail. Istio policies show timeout and retry behavior while DestinationRule adds basic circuit breaker settings.

### Idempotent Order Creation

`POST /orders` supports the `Idempotency-Key` header. Retrying the same request with the same key returns the same logical order id. This addresses duplicate order creation during client or infrastructure retries.

### Observability First

Metrics, traces, and service graph are part of the system, not afterthoughts. They are used to explain normal flow, failure, and scaling behavior.

## 5. Key Code To Show

Recommended code walkthrough:

- [order-service/main.py](../order-service/main.py): `create_order`, idempotency logic, service-to-service calls.
- [istio/virtual-service.yaml](../istio/virtual-service.yaml): Gateway routing, retry, timeout.
- [istio/destination-rule.yaml](../istio/destination-rule.yaml): connection pool and outlier detection.
- [scripts/evidence-run.ps1](../scripts/evidence-run.ps1): repeatable evidence generation.

## 6. Evaluation

Use [docs/EVALUATION.md](EVALUATION.md) for tables.

Summary:

- Normal order flow succeeds.
- Payment failure is visible and controlled.
- Slow payment produces Istio timeout.
- Idempotent retry returns the same order id.
- Observability tools show metrics, traces, and service graph.
- Scaling from 1 to 3 backend replicas improves average latency and throughput in local Kind tests.

## 7. Limitations And Future Work

- Replace in-memory idempotency with Redis/PostgreSQL for cross-replica durability.
- Add persistent product/order storage.
- Add mTLS authorization policy and JWT authentication.
- Add CI pipeline and image publishing to a registry.
- Add automated screenshots for report evidence.

## 8. Conclusion

The project shows a practical distributed system with service decomposition, service mesh traffic management, failure handling, observability, and scalability evaluation.
