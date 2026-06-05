# Chaos Recovery

This recovery scenario shows that Kubernetes can recover a failed service pod and that the system remains observable through Istio/Kiali/Prometheus.

## Goal

Cause a controlled failure in `payment-service`, then show:

- Kubernetes recreates the pod.
- The order flow works after recovery.
- Kiali/Prometheus show traffic and any transient errors.

## Command

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\chaos-recovery.ps1
```

Manual version:

```powershell
kubectl get pods -n meshmart -l app=payment-service
kubectl delete pod -n meshmart -l app=payment-service
kubectl rollout status -n meshmart deployment/payment-service --timeout=300s
kubectl get pods -n meshmart -l app=payment-service
```

Then run a normal order:

```powershell
$body = @{
  user_id = "chaos-user"
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

## Presentation Talking Point

This is not a replacement for persistent storage or exactly-once processing. It shows a core distributed-systems concern: components can fail independently, so the platform must detect failure, reschedule work, and expose enough telemetry for operators to understand recovery.
