# Istio Report Notes

## Istio

Istio is a service mesh. It adds a network control layer around microservices so the team can manage traffic, security, retries, timeouts, telemetry, and failure behavior without rewriting each service.

## Envoy Sidecar Proxy

When sidecar injection is enabled, each application pod gets a second container named `istio-proxy`. This proxy is Envoy. Service-to-service traffic goes through Envoy before reaching the application container.

```text
order-service app
  -> order-service istio-proxy
  -> payment-service istio-proxy
  -> payment-service app
```

That is why each pod should have two containers:

- application container
- `istio-proxy`

## Gateway Routing

The platform uses an Istio Gateway and VirtualService:

```text
Client
  -> Istio Ingress Gateway
  -> frontend / order-service / product-service / payment-service / notification-service
```

Routes:

- `/` goes to frontend
- `/orders` goes to order-service
- `/products` goes to product-service
- `/payments` and `/payment` go to payment-service
- `/notifications` goes to notification-service

## Fault Tolerance Validation

Payment Service can simulate three states:

```text
/payment?mode=success
/payment?mode=fail
/payment?mode=slow
```

Istio config adds:

- timeout for payment routes
- retry for transient failures
- circuit breaker through DestinationRule outlier detection

## Observability Evidence

Prometheus collects metrics from Istio sidecars.

Grafana shows:

- request rate
- latency
- error rate

Jaeger shows distributed traces, especially:

```text
Order -> Product
Order -> Payment
Order -> Notification
```

Kiali shows the service graph and traffic health.

## Load Test Table Template

Example results from the local Kind run:

| Scenario | Replicas | Result |
| --- | ---: | --- |
| Normal load, 5 VUs for 10s | 1 | 40 requests, 0% failed, p95 about 387 ms |
| Higher load, 10 VUs for 10s | 1 | 60 requests, 0% failed, avg about 690 ms |
| Higher load, 10 VUs for 10s | 3 | 85 requests, 0% failed, avg about 211 ms |

The 3-replica run had better throughput and average latency on the local single-node cluster. p95 can still spike because Kind, Docker Desktop, and all pods share the same machine.

Commands:

```bash
kubectl scale deployment order-service product-service payment-service notification-service --replicas=3
k6 run -e BASE_URL=http://<INGRESS_HOST> -e VUS=10 -e DURATION=10s load-test.js
```
