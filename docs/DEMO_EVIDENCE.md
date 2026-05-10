# Demo Evidence

This table is the final checklist for the end-to-end technical demo.

| Demo area | Evidence command or screen | Expected result |
| --- | --- | --- |
| Normal request | `POST /orders` with `payment_mode=success` | `order_status=confirmed`, `payment_status=success`, `notification=sent` |
| Failure request | `POST /orders` with `payment_mode=failed` | `order_status=payment_failed`, payment failure reason visible |
| Idempotent retry | `POST /orders` twice with the same `Idempotency-Key` | Both responses use the same `order_id` |
| Timeout request | `GET /payment?mode=slow` through Istio Gateway | `504 Gateway Timeout` from `istio-envoy` |
| Chaos recovery | Delete one `payment-service` pod | Deployment returns to desired replicas and order flow still works |
| Service mesh | `kubectl get pods -n shopping-demo` | Application pods show `2/2 Running` |
| Routing | Frontend opened through `http://127.0.0.1:18080` | UI loads products and Buy button works |
| Prometheus | Query `istio_requests_total` | Request metrics exist |
| Grafana | Istio dashboard | Request rate, latency, and error panels show traffic |
| Jaeger | `http://127.0.0.1:16686/jaeger/` | Services include order, product, payment, notification |
| Kiali | `http://127.0.0.1:20001/kiali/` | Graph shows service-to-service traffic |
| Scaling | k6 before and after scaling to 3 replicas | Throughput improves or latency decreases |

## Latest Local Result

The latest local Kind run showed:

| Scenario | Replicas | Result |
| --- | ---: | --- |
| Normal order | 1 | `confirmed`, payment `success`, notification `sent` |
| Failure order | 1 | `payment_failed`, failure reason visible, notification `sent` |
| Idempotent retry | 1 | same `order_id` returned for repeated `Idempotency-Key` |
| Slow payment | 1 | Istio Gateway returned `504` |
| Observability | 1 | Prometheus had 31 Istio request series; Jaeger showed 7 services |
| 10 VUs for 10s | 1 | 71 requests, 0% failed, avg 682.52 ms, p95 1220 ms |
| 10 VUs for 10s | 3 | 91 requests, 0% failed, avg 179.23 ms, p95 585.87 ms |

Notes:

- The demo ran on a single-node Kind cluster inside Docker Desktop.
- p95 can spike on local machines because app pods, Istio, add-ons, and Docker all share the same host resources.
- Use `scripts/demo.ps1` to regenerate evidence JSON before presenting.
