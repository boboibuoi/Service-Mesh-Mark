# Evaluation

The evaluation focuses on four distributed-system properties:

- reliability under partial failure
- retry-safe order creation
- observability across service boundaries
- scalability under load

## End-to-End Functional Results

| Scenario | Expected behavior | Latest local result |
| --- | --- | --- |
| Normal order | Order is confirmed after product, payment, and notification calls | `confirmed`, payment `success`, notification `sent` |
| Payment failure | Order returns a visible failed payment result | `payment_failed`, reason `Simulated payment failure` |
| Slow payment | Istio timeout stops a slow upstream call | HTTP `504 Gateway Timeout` |
| Idempotent retry | Same `Idempotency-Key` returns the same order id | Same `order_id` returned on retry |
| Payment pod deletion | Kubernetes recreates failed pod | `payment-service` returns to desired replicas |

## Load Test Results

Latest local Kind run:

| Scenario | Replicas | Requests | Failure rate | Avg latency | p95 latency |
| --- | ---: | ---: | ---: | ---: | ---: |
| Normal load | 1 | 71 | 0% | 682.52 ms | 1220 ms |
| Normal load | 3 | 91 | 0% | 179.23 ms | 585.87 ms |

Interpretation:

- Scaling backend services from 1 to 3 replicas improved throughput from 71 to 91 requests in the same run window.
- Average latency dropped from 682.52 ms to 179.23 ms.
- p95 latency also improved, but local single-node Kind results can fluctuate because all services, Istio, and observability add-ons share the same Docker Desktop resources.

## Observability Results

| Tool | Evidence |
| --- | --- |
| Prometheus | `istio_requests_total` returned Istio request metrics |
| Grafana | Istio dashboards showed request rate, latency, and error behavior |
| Jaeger | Trace services included frontend, ingress, order, product, payment, and notification |
| Kiali | Service graph showed traffic between microservices |

## Limitations

- The demo idempotency store is in-memory. It is enough to demonstrate retry-safe semantics in the course demo, but a production multi-replica system should move idempotency records to Redis, PostgreSQL, or another shared durable store.
- The product catalog is static in memory.
- The load test runs on a local Kind cluster, so numbers show relative behavior rather than production capacity.
