# Architecture Notes

## Runtime Flow

```text
Browser/Postman
  |
frontend or direct API call
  |
  |-- GET /products ------------> product-service
  |-- POST /orders -------------> order-service
                                  |-- GET /products/{id} ---> product-service
                                  |-- POST /payments -------> payment-service
                                  |-- POST /notifications --> notification-service
```

## Observability Focus

The demo is designed to show:

- Request path across multiple services
- Latency when payment delay is enabled
- Error behavior when payment failure is enabled
- Service-to-service traffic through Istio sidecars

## Minimum Demo Checklist

- `docker compose up --build` starts all services
- `GET /products` returns product data
- `POST /orders` returns order, payment, and notification result
- `POST /orders` with `payment_mode=failed` returns a visible payment failure result
- Istio routes external traffic to frontend and backend services in Kubernetes
