# Optional API Gateway

The main Kubernetes path uses Istio Gateway:

```text
Client -> Istio Ingress Gateway -> frontend / order-service / product-service / payment-service
```

The `gateway/` service is intentionally optional. It is a small FastAPI edge gateway that can forward API calls to backend services when running outside Istio or when comparing application-level gateway routing with service-mesh routing.

## Why It Is Not In The Main Path

Istio already provides the important distributed-system features for this project:

- ingress routing through `Gateway` and `VirtualService`
- timeout and retry policies
- circuit breaker settings through `DestinationRule`
- sidecar telemetry, tracing, and service graph

Keeping the FastAPI gateway out of the main Kubernetes path keeps the project focused on service mesh behavior.

## When To Use It

Use `gateway/` only if the presentation needs to compare:

- application gateway vs. service mesh ingress
- code-level routing vs. infrastructure-level routing
- local non-Istio development vs. Kubernetes/Istio deployment
