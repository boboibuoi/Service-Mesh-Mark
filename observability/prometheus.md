# Prometheus

Prometheus is installed from the Istio sample add-ons and scrapes Istio sidecar metrics.

Useful queries:

```text
istio_requests_total
sum(rate(istio_requests_total[1m])) by (destination_workload, response_code)
histogram_quantile(0.95, sum(rate(istio_request_duration_milliseconds_bucket[1m])) by (le, destination_workload))
```

Expected result:

- Request counters increase when the frontend or `scripts/evidence-run.ps1` generates traffic.
- Error/timeout traffic appears when calling `/payment?mode=slow`.
