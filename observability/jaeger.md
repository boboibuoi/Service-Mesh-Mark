# Jaeger

Jaeger is installed from the Istio sample add-ons and receives traces through the Zipkin-compatible collector endpoint configured in `istio/telemetry-tracing.yaml`.

Open locally:

```powershell
kubectl port-forward -n istio-system svc/tracing 16686:80
Start-Process http://127.0.0.1:16686/jaeger/
```

Trace to show:

```text
Client -> Istio Ingress Gateway -> order-service
  -> product-service
  -> payment-service
  -> notification-service
```

Expected services:

- `order-service.meshmart`
- `product-service.meshmart`
- `payment-service.meshmart`
- `notification-service.meshmart`
- `istio-ingressgateway.istio-system`
