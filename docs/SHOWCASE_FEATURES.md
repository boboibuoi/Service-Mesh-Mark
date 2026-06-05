# MeshMart Showcase Features

Use this file as the short scoring checklist for the final presentation.

## Website Experience

- Product catalog is loaded from `product-service` through the same ingress path as backend APIs.
- Users can add multiple products to a shopping cart before checkout.
- Successful checkout decrements product stock through inventory reservation.
- Checkout supports approved, declined, and slow payment scenarios.
- Recent order history is loaded from `order-service` for the selected customer.
- Customers can submit a product review with rating, comment, and optional image URL after checkout.
- The UI shows response JSON, latency, idempotency key, and request path evidence.

## Fault Tolerance

- `POST /orders` accepts `Idempotency-Key` so client retries do not create duplicate logical orders.
- `order-service` records upstream timing for product, payment, and notification calls.
- Payment failure returns a controlled `payment_failed` order state rather than an unhandled crash.
- Inventory uses a Saga-style compensation path: reserve stock before payment, commit on success, release on payment failure.
- Slow payment can be constrained by Istio timeout policies.
- Notification failure is handled as graceful degradation: the order can remain visible with `notification: queued`.
- Kubernetes liveness/readiness probes allow unhealthy pods to be removed from traffic.
- PodDisruptionBudgets protect at least one available pod during voluntary disruptions.

## Scalability

- Each workload has CPU and memory requests/limits.
- `k8s/autoscaling.yaml` adds HorizontalPodAutoscalers for frontend and backend services.
- k6 load tests can compare 1 replica vs. multiple replicas.
- Istio sidecars expose request rate, latency, and error rate so scaling decisions are evidence-based.

## Service Mesh And Observability

- Istio Gateway and VirtualService route frontend and backend API paths.
- DestinationRules configure connection pools and outlier detection for critical services.
- Retry and timeout policies are defined for order, product, payment, and notification paths.
- Prometheus collects mesh metrics from Envoy sidecars.
- Grafana visualizes traffic, latency, and error rate.
- Jaeger shows distributed traces across order, product, payment, and notification services.
- Kiali shows the service graph and health status.

## Suggested Presentation Flow

1. Open MeshMart and add two products to the cart.
2. Checkout with approved payment and show response JSON plus recent order history.
3. Refresh the catalog and point out that stock decreased after inventory commit.
4. Submit a product review and show the product rating/review count update.
5. Checkout with declined payment and explain inventory compensation.
6. Trigger slow payment and explain Istio timeout behavior.
7. Show Kiali graph, Jaeger trace, and Prometheus `istio_requests_total`.
8. Show `k8s/autoscaling.yaml`, resource requests, and PodDisruptionBudgets.
