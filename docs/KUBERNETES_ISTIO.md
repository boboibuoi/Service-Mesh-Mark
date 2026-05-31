# Kubernetes and Istio Runbook

## 20/5 - Docker Compose

Start the full local system:

```bash
docker compose up --build
```

Expected services:

- frontend: `http://localhost:8080`
- product-service: `http://localhost:8004`
- order-service: `http://localhost:8001`
- payment-service: `http://localhost:8002`
- notification-service: `http://localhost:8003`

Smoke test:

```bash
curl http://localhost:8004/products
curl -X POST http://localhost:8001/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","product_id":"PROD-001","quantity":1,"payment_mode":"success"}'
```

## 21/5 - Kubernetes

Create and label a namespace:

```bash
kubectl create namespace shopping-demo
kubectl config set-context --current --namespace=shopping-demo
```

Build images:

```bash
docker compose build
```

For Kind, load images into the cluster:

```bash
kind load docker-image service-mesh-observability-demo/frontend:v1.0.0-demo --name shopping-demo
kind load docker-image service-mesh-observability-demo/product-service:v1.0.0-demo --name shopping-demo
kind load docker-image service-mesh-observability-demo/order-service:v1.0.0-demo --name shopping-demo
kind load docker-image service-mesh-observability-demo/payment-service:v1.0.0-demo --name shopping-demo
kind load docker-image service-mesh-observability-demo/notification-service:v1.0.0-demo --name shopping-demo
```

Deploy services:

```bash
kubectl apply -f k8s/
```

Check:

```bash
kubectl get pods
kubectl get services
kubectl logs deploy/order-service
```

Port-forward local tests:

```bash
kubectl port-forward svc/frontend 8080:80
kubectl port-forward svc/order-service 8001:8001
```

## 22/5 - Istio Sidecar Injection

Install Istio, then enable namespace injection:

```bash
istioctl install \
  --set profile=demo \
  --set meshConfig.extensionProviders[0].name=zipkin \
  --set meshConfig.extensionProviders[0].zipkin.service=zipkin.istio-system.svc.cluster.local \
  --set meshConfig.extensionProviders[0].zipkin.port=9411 \
  -y
kubectl label namespace shopping-demo istio-injection=enabled
kubectl rollout restart deployment
```

Each application pod should show two containers:

```bash
kubectl get pods
kubectl get pod <pod-name> -o jsonpath="{.spec.containers[*].name}"
```

Expected container names include:

- app container
- `istio-proxy`

## 23/5 - Istio Gateway and VirtualService

Apply Istio routing:

```bash
kubectl apply -f istio/gateway.yaml
kubectl apply -f istio/virtual-service.yaml
kubectl apply -f istio/destination-rule.yaml
kubectl apply -f istio/payment-policy.yaml
kubectl apply -f istio/telemetry-tracing.yaml
```

`payment-fault-injection.yaml` is optional. Apply it only during the failure demo because it injects delay into live payment traffic.

Open access with Kind:

```bash
kubectl port-forward -n istio-system svc/istio-ingressgateway 18080:80
```

If the Docker Compose frontend is already using `18080`, use `18081:80` for the mesh port-forward instead so Kiali can see traffic in `shopping-demo`.

Open access with Minikube:

```bash
minikube tunnel
kubectl get svc istio-ingressgateway -n istio-system
```

Routes:

- `/` -> frontend
- `/orders` -> order-service
- `/products` -> product-service
- `/payments` -> payment-service
- `/payment?mode=success|fail|slow` -> payment-service
- `/notifications` -> notification-service

Final check:

```bash
curl http://<INGRESS_HOST>/products
curl -X POST http://<INGRESS_HOST>/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":"demo-user","product_id":"PROD-001","quantity":1,"payment_mode":"success"}'
```

For the Kind port-forward above, use `http://127.0.0.1:18080` as `<INGRESS_HOST>`.

## Observability Add-ons

Istio sample add-ons are useful for the course demo:

```bash
kubectl apply -f <ISTIO_DIR>/samples/addons/prometheus.yaml
kubectl apply -f <ISTIO_DIR>/samples/addons/grafana.yaml
kubectl apply -f <ISTIO_DIR>/samples/addons/jaeger.yaml
kubectl apply -f <ISTIO_DIR>/samples/addons/kiali.yaml
kubectl apply -f istio/telemetry-tracing.yaml
```

Open dashboards:

```bash
istioctl dashboard grafana
istioctl dashboard prometheus
istioctl dashboard jaeger
istioctl dashboard kiali
```

Or use local port-forwarding:

```bash
kubectl port-forward -n istio-system svc/prometheus 19090:9090
kubectl port-forward -n istio-system svc/grafana 13000:3000
kubectl port-forward -n istio-system svc/tracing 16686:80
kubectl port-forward -n istio-system svc/kiali 20001:20001
```

Dashboard URLs:

- Prometheus: `http://127.0.0.1:19090`
- Grafana: `http://127.0.0.1:13000`
- Jaeger: `http://127.0.0.1:16686/jaeger/`
- Kiali: `http://127.0.0.1:20001/kiali/`

## Failure and Load Test

Payment failure:

```bash
curl http://<INGRESS_HOST>/payment?mode=fail
```

Payment slow response:

```bash
curl http://<INGRESS_HOST>/payment?mode=slow
```

k6 load test:

```bash
k6 run -e BASE_URL=http://<INGRESS_HOST> load-test.js
```

If k6 is not installed locally, run it through Docker:

```bash
kubectl port-forward --address 0.0.0.0 -n istio-system svc/istio-ingressgateway 18081:80
docker run --rm \
  -e BASE_URL=http://host.docker.internal:18081 \
  -e VUS=10 \
  -e DURATION=10s \
  --mount type=bind,source="$PWD",target=/scripts \
  grafana/k6:latest run /scripts/load-test.js
```

