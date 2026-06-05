# Observability

MeshMart exposes **two layers** of metrics:

| Layer | Source | What it measures |
|---|---|---|
| Infrastructure | Istio sidecar proxies | Request count, latency, error rate at the network level |
| Application | `prometheus-client` in each service | Business logic — orders, payments, stock, reviews |

---

## Local (Docker Compose)

When running `docker compose up`, Prometheus and Grafana start automatically alongside the microservices.

| Tool | URL | Purpose |
|---|---|---|
| **Grafana** | http://localhost:3000 | Auto-loaded MeshMart dashboard (no login needed) |
| **Prometheus** | http://localhost:9090 | Raw metric explorer and scrape status |

The MeshMart dashboard loads automatically — go to **Dashboards → MeshMart → MeshMart — Application Overview**.

---

## Kubernetes + Istio Add-ons

```powershell
$istioDir = "C:\Users\ASUS\AppData\Local\Microsoft\WinGet\Packages\Istio.Istio_Microsoft.Winget.Source_8wekyb3d8bbwe\istio-1.29.2"
kubectl apply -f "$istioDir\samples\addons\prometheus.yaml"
kubectl apply -f "$istioDir\samples\addons\grafana.yaml"
kubectl apply -f "$istioDir\samples\addons\jaeger.yaml"
kubectl apply -f "$istioDir\samples\addons\kiali.yaml"
kubectl apply -f istio/telemetry-tracing.yaml
```

Port-forward:
```powershell
kubectl port-forward -n istio-system svc/prometheus 19090:9090
kubectl port-forward -n istio-system svc/grafana 13000:3000
kubectl port-forward -n istio-system svc/tracing 16686:80
kubectl port-forward -n istio-system svc/kiali 20001:20001
```

Dashboards: http://127.0.0.1:13000 | Jaeger: http://127.0.0.1:16686/jaeger/ | Kiali: http://127.0.0.1:20001/kiali/

---

## Application Metrics Reference

### order-service `:8001/metrics`

| Metric | Type | Labels | Description |
|---|---|---|---|
| `meshmart_orders_total` | Counter | `status`, `payment_mode` | Total orders created |
| `meshmart_order_duration_seconds` | Histogram | — | End-to-end order processing latency |
| `meshmart_order_amount_usd` | Histogram | — | Cart checkout value in USD |
| `meshmart_order_items_total` | Histogram | — | Distinct products per order |
| `meshmart_order_in_flight` | Gauge | — | Orders currently being processed |
| `meshmart_idempotency_hits_total` | Counter | `outcome` | Idempotency cache hits (cached / conflict / in_progress) |

### product-service `:8004/metrics`

| Metric | Type | Labels | Description |
|---|---|---|---|
| `meshmart_product_stock_total` | Gauge | `product_id`, `product_name` | Real-time stock level per product |
| `meshmart_reviews_total` | Counter | `product_id`, `product_name` | Reviews submitted |
| `meshmart_inventory_operations_total` | Counter | `operation`, `product_id` | reserve / commit / release counts |
| `meshmart_inventory_units_per_operation` | Histogram | `operation` | Units per inventory call |

### payment-service `:8002/metrics`

| Metric | Type | Labels | Description |
|---|---|---|---|
| `meshmart_payments_total` | Counter | `status`, `mode` | Total payments processed |
| `meshmart_payment_duration_seconds` | Histogram | — | Payment latency (delayed mode shows ~5s spike) |
| `meshmart_payment_amount_usd` | Histogram | — | Payment amounts |

### notification-service `:8003/metrics`

| Metric | Type | Labels | Description |
|---|---|---|---|
| `meshmart_notifications_total` | Counter | `payment_status` | Notifications dispatched |
| `meshmart_notifications_sent_total_gauge` | Gauge | — | Running total for stat panels |

---

## Useful Prometheus Queries

```promql
# Order success rate (%)
sum(meshmart_orders_total{status="confirmed"}) / sum(meshmart_orders_total) * 100

# p95 order processing latency
histogram_quantile(0.95, rate(meshmart_order_duration_seconds_bucket[5m]))

# p95 payment latency — should spike during 'delayed' mode
histogram_quantile(0.95, rate(meshmart_payment_duration_seconds_bucket[5m]))

# Real-time stock per product
meshmart_product_stock_total

# Order throughput per minute
sum by (status) (rate(meshmart_orders_total[1m])) * 60

# Inventory compensation rate (payment failures that triggered release)
rate(meshmart_inventory_operations_total{operation="release"}[5m])

# Idempotency effectiveness — how many duplicate requests were prevented
sum(meshmart_idempotency_hits_total{outcome="cached"})

# Istio infrastructure metrics (requires Kubernetes + Istio)
istio_requests_total
histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le, destination_workload))
```

---

## Grafana Dashboard Panels

The auto-provisioned dashboard **"MeshMart — Application Overview"** contains:

| Panel | Type | Query |
|---|---|---|
| Total / Confirmed / Failed Orders | Stat | `meshmart_orders_total` |
| Payment Success Rate | Stat gauge | confirmed / total × 100 |
| Total Reviews | Stat | `meshmart_reviews_total` |
| Notifications Sent | Stat | `meshmart_notifications_total` |
| Order Rate (per minute) | Time series | `rate(meshmart_orders_total[1m])` by status |
| Order Processing Latency p50/p95/p99 | Time series | `histogram_quantile` on order duration |
| Product Stock Levels | Bar gauge | `meshmart_product_stock_total` |
| Orders by Payment Mode | Donut chart | `meshmart_orders_total` by payment_mode |
| Payment Latency p50/p95 | Time series | `histogram_quantile` on payment duration |
| Inventory Operations Rate | Time series | `meshmart_inventory_operations_total` by operation |
| Idempotency Cache Events | Time series | `meshmart_idempotency_hits_total` by outcome |
| Order Amount Distribution | Heatmap | `meshmart_order_amount_usd_bucket` |
| Reviews per Product | Time series | `meshmart_reviews_total` by product_name |
| Orders In-Flight | Stat | `meshmart_order_in_flight` |
