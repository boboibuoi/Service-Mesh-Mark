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

Lists catalog products from `product-service`.

Response:

```json
{
  "products": [
    {
      "id": "PROD-001",
      "name": "Ultrabook Pro 14",
      "price": 899.0,
      "stock": 20,
      "rating": 4.8,
      "review_count": 24
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
  "name": "Ultrabook Pro 14",
  "price": 899.0,
  "stock": 20,
  "rating": 4.8,
  "review_count": 24,
  "reviews": []
}
```

## POST /orders

Creates an order through `order-service`. The order flow reserves inventory in `product-service`, calls `payment-service`, commits or releases inventory, and sends a notification.

`user_id` is required. The request can use either the backward-compatible `product_id` + `quantity` fields or the richer `items` array used by the MeshMart cart.

Optional request header:

```text
Idempotency-Key: <unique-client-generated-key>
```

When the same `Idempotency-Key` is retried with the same order payload, `order-service` returns the same `order_id` instead of creating a second logical order. If the same key is reused with a different payload, the service returns `409 Conflict`.

Request:

```json
{
  "user_id": "meshmart-user",
  "items": [
    {
      "product_id": "PROD-001",
      "quantity": 1
    },
    {
      "product_id": "PROD-003",
      "quantity": 2
    }
  ],
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
  "created_at": "2026-06-04T15:30:00+00:00",
  "order_status": "confirmed",
  "user_id": "meshmart-user",
  "product": {
    "id": "PROD-001",
    "name": "Ultrabook Pro 14",
    "unit_price": 899.0,
    "quantity": 1,
    "line_total": 899.0
  },
  "items": [
    {
      "id": "PROD-001",
      "name": "Ultrabook Pro 14",
      "unit_price": 899.0,
      "quantity": 1,
      "line_total": 899.0
    },
    {
      "id": "PROD-003",
      "name": "Audio Pods Max",
      "unit_price": 89.0,
      "quantity": 2,
      "line_total": 178.0
    }
  ],
  "amount": 1077.0,
  "payment": {
    "order_id": "ORD-001",
    "amount": 1077.0,
    "payment_status": "success",
    "mode": "success"
  },
  "notification": "sent",
  "inventory": {
    "reservation_id": "ORD-001",
    "inventory_status": "committed",
    "compensated": false
  },
  "service_timings_ms": {
    "inventory_reserve_ms": 12.4,
    "payment_service_ms": 18.7,
    "inventory_commit_ms": 4.3,
    "notification_service_ms": 9.2
  },
  "resilience": {
    "idempotency_key": "order-001",
    "retry_safe": true,
    "notification_degraded": false,
    "inventory_compensated": false
  }
}
```

When payment succeeds, product stock is reduced and the inventory reservation is committed. When payment fails, the reserved stock is released and the response includes `inventory.compensated: true`.

If `notification-service` is unavailable, `order-service` keeps the checkout result visible and returns `notification: "queued"` with `resilience.notification_degraded: true`. This models graceful degradation for non-critical side effects.

## GET /orders

Lists recent orders stored by `order-service`.

Examples:

```bash
curl http://localhost:8001/orders
curl "http://localhost:8001/orders?user_id=meshmart-user&limit=5"
```

## GET /orders/{id}

Returns one stored order by id.

Example:

```bash
curl http://localhost:8001/orders/ORD-001
```

## POST /products/{id}/reviews

Adds a customer review for a product after checkout. Reviews are stored in memory by `product-service` and update the product rating shown in the catalog.

Request:

```json
{
  "user_id": "meshmart-user",
  "order_id": "ORD-001",
  "rating": 5,
  "comment": "Fast delivery and useful for dashboard work.",
  "image_url": "https://example.com/review-image.png"
}
```

Response:

```json
{
  "review": {
    "review_id": "REV-001",
    "product_id": "PROD-001",
    "rating": 5
  },
  "product": {
    "id": "PROD-001",
    "rating": 4.81,
    "review_count": 25
  }
}
```

## GET /products/{id}/reviews

Lists reviews for a product.

## Internal Inventory Endpoints

`order-service` uses these `product-service` endpoints to implement a lightweight Saga:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/inventory/reserve` | Validate stock and decrement it before payment |
| POST | `/inventory/commit` | Mark reserved stock as committed after successful payment |
| POST | `/inventory/release` | Restore reserved stock after failed payment or order failure |

Example reservation payload:

```json
{
  "reservation_id": "ORD-001",
  "items": [
    {
      "product_id": "PROD-001",
      "quantity": 1
    }
  ]
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

Small payment endpoint for failure and timeout validation.

Examples:

```bash
curl http://localhost:8002/payment?mode=success
curl http://localhost:8002/payment?mode=fail
curl http://localhost:8002/payment?mode=slow
```

`order_id` is optional for this endpoint. If it is omitted, `payment-service` generates a temporary order id.

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
  "user_id": "meshmart-user",
  "payment_status": "success"
}
```

Response:

```json
{
  "order_id": "ORD-001",
  "user_id": "meshmart-user",
  "payment_status": "success",
  "notification": "sent",
  "message": "Order ORD-001 payment is success",
  "sent_at": "2026-05-10T12:00:00+00:00"
}
```
