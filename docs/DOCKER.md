# Docker Commands

Each service has its own Dockerfile.

## Build Images

```bash
docker build -t meshmart-service-mesh/frontend:v1.0.0 ./frontend
docker build -t meshmart-service-mesh/product-service:v1.0.0 ./product-service
docker build -t meshmart-service-mesh/order-service:v1.0.0 ./order-service
docker build -t meshmart-service-mesh/payment-service:v1.0.0 ./payment-service
docker build -t meshmart-service-mesh/notification-service:v1.0.0 ./notification-service
```

## Run Containers

Run backend services on the same Docker network:

```bash
docker network create meshmart-net
```

```bash
docker run --rm --name product-service --network meshmart-net -p 8004:8004 meshmart-service-mesh/product-service:v1.0.0
docker run --rm --name payment-service --network meshmart-net -p 8002:8002 meshmart-service-mesh/payment-service:v1.0.0
docker run --rm --name notification-service --network meshmart-net -p 8003:8003 meshmart-service-mesh/notification-service:v1.0.0
```

```bash
docker run --rm --name order-service --network meshmart-net -p 8001:8001 \
  -e PRODUCT_SERVICE_URL=http://product-service:8004 \
  -e PAYMENT_SERVICE_URL=http://payment-service:8002 \
  -e NOTIFICATION_SERVICE_URL=http://notification-service:8003 \
  meshmart-service-mesh/order-service:v1.0.0
```

```bash
docker run --rm --name frontend -p 8080:80 meshmart-service-mesh/frontend:v1.0.0
```

## Docker Compose

```bash
docker compose up --build
```

Run this without `-d` when you want the stack to keep running in the terminal until you stop it manually.
The `-d` flag starts Compose in detached mode, so the command returns right away.
