# Demo Script

Use this order during the presentation. Keep one terminal open for commands and one browser open for the UI and dashboards.

## 1. Open The Application

```powershell
kubectl port-forward -n istio-system svc/istio-ingressgateway 18080:80
Start-Process http://127.0.0.1:18080
```

Expected result:

- Product list loads.
- The Buy button creates an order.
- Order Status changes to `Success` for normal payment.

## 2. Normal Request

```powershell
$body = @{
  user_id = "demo-user"
  product_id = "PROD-001"
  quantity = 1
  payment_mode = "success"
} | ConvertTo-Json -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:18080/orders `
  -ContentType "application/json" `
  -Body $body
```

Expected result:

- `order_status` is `confirmed`.
- `payment.payment_status` is `success`.
- `notification` is `sent`.

## 3. Failure Request

```powershell
$body = @{
  user_id = "demo-user"
  product_id = "PROD-001"
  quantity = 1
  payment_mode = "failed"
} | ConvertTo-Json -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:18080/orders `
  -ContentType "application/json" `
  -Body $body
```

Expected result:

- `order_status` is `payment_failed`.
- Payment response includes `reason: Simulated payment failure`.
- Notification is still sent.

## 4. Idempotency Retry

```powershell
$key = "demo-idempotency-001"
$body = @{
  user_id = "demo-user"
  product_id = "PROD-001"
  quantity = 1
  payment_mode = "success"
} | ConvertTo-Json -Compress

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:18080/orders `
  -ContentType "application/json" `
  -Headers @{ "Idempotency-Key" = $key } `
  -Body $body

Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:18080/orders `
  -ContentType "application/json" `
  -Headers @{ "Idempotency-Key" = $key } `
  -Body $body
```

Expected result:

- Both responses return the same `order_id`.
- This demonstrates retry-safe order creation.

## 5. Timeout Request

```powershell
curl.exe -i "http://127.0.0.1:18080/payment?mode=slow"
```

Expected result:

- Istio returns `504 Gateway Timeout`.
- This demonstrates timeout behavior for slow payment traffic.

## 6. Chaos Recovery

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\chaos-demo.ps1
```

Expected result:

- One `payment-service` pod is deleted.
- Kubernetes recreates it.
- A normal order still works after recovery.

## 7. Observability

Open dashboards:

```powershell
kubectl port-forward -n istio-system svc/prometheus 19090:9090
kubectl port-forward -n istio-system svc/grafana 13000:3000
kubectl port-forward -n istio-system svc/tracing 16686:80
kubectl port-forward -n istio-system svc/kiali 20001:20001
```

Dashboard URLs:

- Frontend: `http://127.0.0.1:18080`
- Prometheus: `http://127.0.0.1:19090`
- Grafana: `http://127.0.0.1:13000`
- Jaeger: `http://127.0.0.1:16686/jaeger/`
- Kiali: `http://127.0.0.1:20001/kiali/`

Evidence to show:

- Prometheus query: `istio_requests_total`
- Grafana dashboard: request rate, latency, error rate
- Jaeger services: ingress, order-service, product-service, payment-service, notification-service
- Kiali graph: service-to-service edges

## 8. Scaling

Note: `http://127.0.0.1:18080` is the Docker Compose frontend in this repo. If you need Kiali graph data for the `shopping-demo` mesh, use the Istio ingress gateway on `http://127.0.0.1:18081` so the traffic actually enters the Kubernetes mesh.

```powershell
kubectl scale -n shopping-demo deployment/order-service deployment/product-service deployment/payment-service deployment/notification-service --replicas=1
docker run --rm `
  -e BASE_URL=http://host.docker.internal:18081 `
  -e VUS=10 `
  -e DURATION=10s `
  --mount "type=bind,source=$PWD,target=/scripts" `
  grafana/k6:latest run /scripts/load-test.js

kubectl scale -n shopping-demo deployment/order-service deployment/product-service deployment/payment-service deployment/notification-service --replicas=3
docker run --rm `
  -e BASE_URL=http://host.docker.internal:18081 `
  -e VUS=10 `
  -e DURATION=10s `
  --mount "type=bind,source=$PWD,target=/scripts" `
  grafana/k6:latest run /scripts/load-test.js
```

Before running Docker-based k6, expose the gateway to Docker:

```powershell
kubectl port-forward --address 0.0.0.0 -n istio-system svc/istio-ingressgateway 18081:80
```

## One Command Evidence Run

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 -RunLoadTest -RunScalingDemo
```

The script writes JSON evidence into `demo-evidence/`.
