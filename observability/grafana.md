# Grafana

Grafana is installed from the Istio sample add-ons.

Open locally:

```powershell
kubectl port-forward -n istio-system svc/grafana 13000:3000
Start-Process http://127.0.0.1:13000
```

Screenshots to capture for the report:

- Request volume while k6 is running.
- Request duration or p95 latency.
- Error rate during the slow payment timeout scenario.

Recommended dashboard:

- Istio Service Dashboard
- Istio Workload Dashboard
