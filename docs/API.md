# API Reference

Docker Compose exposes services on local host ports. Istio exposes the same paths through the ingress gateway in Kubernetes.

## GET /health

Checks whether a service is running.

Response:

```json
{
  "service": "order-service",
  "status": "ok"
}
```

## GET /products

Lists demo products from `product-service`.

Response:

```json
{
  "products": [
    {
      "id": "PROD-001",
      "name": "Laptop",
      "price": 899.0,
      "stock": 20
    }
  ]
}
```

## GET /products/{id}

Returns one product from `product-service`.

Example:

```bash
curl http://localhost:8004/products/PROD-001
```

Response:

```json
{
  "id": "PROD-001",
  "name": "Laptop",
  "price": 899.0,
  "stock": 20
}
```

## POST /orders

Creates an order through `order-service`. The order flow calls `payment-service` and `notification-service`.

`user_id` and `product_id` are required. The frontend generates a demo user id and sends the selected product id from the product list.

Optional request header:

```text
Idempotency-Key: <unique-client-generated-key>
```

When the same `Idempotency-Key` is retried with the same order payload, `order-service` returns the same `order_id` instead of creating a second logical order. If the same key is reused with a different payload, the service returns `409 Conflict`.

Request:

```json
{
  "user_id": "demo-user",
  "product_id": "PROD-001",
  "quantity": 1,
  "payment_mode": "success"
}
```

Allowed `payment_mode` values:

- `success`
- `failed`
- `delayed`

Compatibility aliases are also accepted:

- `process`
- `fail`
- `delay`

Response:

```json
{
  "order_id": "ORD-001",
  "order_status": "confirmed",
  "user_id": "demo-user",
  "product": {
    "id": "PROD-001",
    "name": "Laptop",
    "unit_price": 899.0,
    "quantity": 1
  },
  "amount": 899.0,
  "payment": {
    "order_id": "ORD-001",
    "amount": 899.0,
    "payment_status": "success",
    "mode": "success"
  },
  "notification": "sent"
}
```

## POST /payments

Processes a payment directly through `payment-service`.

Request:

```json
{
  "order_id": "ORD-001",
  "amount": 100,
  "mode": "success"
}
```

Allowed `mode` values:

- `success`
- `failed`
- `delayed`

Response:

```json
{
  "order_id": "ORD-001",
  "amount": 100,
  "payment_status": "success",
  "mode": "success"
}
```

## GET /payment

Small payment demo endpoint for failure and timeout demos.

Examples:

```bash
curl http://localhost:8002/payment?mode=success
curl http://localhost:8002/payment?mode=fail
curl http://localhost:8002/payment?mode=slow
```

`order_id` is optional for this endpoint. If it is omitted, `payment-service` generates a temporary demo id.

Allowed `mode` values:

- `success`
- `fail`
- `slow`

## POST /notifications

Sends a notification directly through `notification-service`.

Request:

```json
{
  "order_id": "ORD-001",
  "user_id": "demo-user",
  "payment_status": "success"
}
```

Response:

```json
{
  "order_id": "ORD-001",
  "user_id": "demo-user",
  "payment_status": "success",
  "notification": "sent",
  "message": "Order ORD-001 payment is success",
  "sent_at": "2026-05-10T12:00:00+00:00"
}
```
