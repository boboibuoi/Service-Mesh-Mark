# Observability

This project uses Istio telemetry plus the official Istio sample add-ons for the course demo.

## Dashboards

| Tool | Purpose | Local URL |
| --- | --- | --- |
| Prometheus | Metrics query and scraping verification | `http://127.0.0.1:19090` |
| Grafana | Request rate, latency, and error rate dashboards | `http://127.0.0.1:13000` |
| Jaeger | Distributed tracing for order flow | `http://127.0.0.1:16686/jaeger/` |
| Kiali | Service graph and traffic health | `http://127.0.0.1:20001/kiali/` |

## Install Add-ons

```powershell
$istioDir = "C:\Users\ASUS\AppData\Local\Microsoft\WinGet\Packages\Istio.Istio_Microsoft.Winget.Source_8wekyb3d8bbwe\istio-1.29.2"
kubectl apply -f "$istioDir\samples\addons\prometheus.yaml"
kubectl apply -f "$istioDir\samples\addons\grafana.yaml"
kubectl apply -f "$istioDir\samples\addons\jaeger.yaml"
kubectl apply -f "$istioDir\samples\addons\kiali.yaml"
kubectl apply -f istio/telemetry-tracing.yaml
```

## Port Forward

```powershell
kubectl port-forward -n istio-system svc/prometheus 19090:9090
kubectl port-forward -n istio-system svc/grafana 13000:3000
kubectl port-forward -n istio-system svc/tracing 16686:80
kubectl port-forward -n istio-system svc/kiali 20001:20001
```

## Evidence Queries

Prometheus:

```text
istio_requests_total
histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le, destination_workload))
```

Jaeger services expected after traffic:

- `frontend.shopping-demo`
- `order-service.shopping-demo`
- `product-service.shopping-demo`
- `payment-service.shopping-demo`
- `notification-service.shopping-demo`
- `istio-ingressgateway.istio-system`

Kiali graph should show:

```text
istio-ingressgateway -> frontend
frontend -> order-service
order-service -> product-service
order-service -> payment-service
order-service -> notification-service
```
