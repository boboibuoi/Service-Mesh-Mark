# Docker Commands

Each service has its own Dockerfile.

## Build Images

```bash
docker build -t service-mesh-observability-demo/frontend:v1.0.0-demo ./frontend
docker build -t service-mesh-observability-demo/product-service:v1.0.0-demo ./product-service
docker build -t service-mesh-observability-demo/order-service:v1.0.0-demo ./order-service
docker build -t service-mesh-observability-demo/payment-service:v1.0.0-demo ./payment-service
docker build -t service-mesh-observability-demo/notification-service:v1.0.0-demo ./notification-service
```

## Run Containers

Run backend services on the same Docker network:

```bash
docker network create service-demo
```

```bash
docker run --rm --name product-service --network service-demo -p 8004:8004 service-mesh-observability-demo/product-service:v1.0.0-demo
docker run --rm --name payment-service --network service-demo -p 8002:8002 service-mesh-observability-demo/payment-service:v1.0.0-demo
docker run --rm --name notification-service --network service-demo -p 8003:8003 service-mesh-observability-demo/notification-service:v1.0.0-demo
```

```bash
docker run --rm --name order-service --network service-demo -p 8001:8001 \
  -e PRODUCT_SERVICE_URL=http://product-service:8004 \
  -e PAYMENT_SERVICE_URL=http://payment-service:8002 \
  -e NOTIFICATION_SERVICE_URL=http://notification-service:8003 \
  service-mesh-observability-demo/order-service:v1.0.0-demo
```

```bash
docker run --rm --name frontend -p 8080:80 service-mesh-observability-demo/frontend:v1.0.0-demo
```

## Docker Compose

```bash
docker compose up --build
```
