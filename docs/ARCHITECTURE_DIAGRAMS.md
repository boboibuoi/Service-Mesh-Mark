# Updated Architecture Diagrams & Flow Analysis

This document contains the updated architecture diagrams for the **MeshMart Service Mesh Observability Platform**. The diagrams have been updated to reflect the new features in the codebase:
1. **Namespace Update**: Transitioned from `shopping-demo` to `meshmart`.
2. **Saga Transaction Pattern (Inventory Reservation)**: Integrated `/inventory/reserve`, `/inventory/commit`, and `/inventory/release` (compensation) flows between `order-service` and `product-service` to manage product stock safely during payment success/failure.
3. **Idempotency-Key Support**: Added header-based idempotency checks on checkout (`POST /orders`).
4. **Product Rating & Reviews API**: Added `/products/{id}/reviews` (GET/POST) endpoints to `product-service`.
5. **Traffic & Resilience Configurations**: Updated timeouts, retries, fault injection parameters, and DestinationRule circuit breaker settings (outlier detection and connection pooling) to match the actual configs in `istio/`.

---

## 1. System Architecture Diagram
*This diagram shows the layout of components in the `meshmart` Kubernetes namespace, their sidecar proxies, control plane, and how the observability stack collects telemetry.*

```mermaid
flowchart TB
  %% Colors & Styles
  classDef client fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a8a
  classDef mesh fill:#ecfdf5,stroke:#059669,stroke-width:2px,color:#064e3b
  classDef service fill:#f8fafc,stroke:#64748b,stroke-width:2px,color:#0f172a
  classDef proxy fill:#f472b6,stroke:#db2777,stroke-width:1px,color:#831843
  classDef control fill:#fae8ff,stroke:#c084fc,stroke-width:2px,color:#581c87
  classDef obs fill:#fff7ed,stroke:#ea580c,stroke-width:2px,color:#7c2d12
  
  %% Elements
  CLIENT["Client <br/> (Browser / Postman)"]:::client
  
  subgraph K8S["Kubernetes Cluster (Namespace: meshmart)"]
    INGRESS["Istio Ingress Gateway"]:::control
    
    subgraph DATA_PLANE["Data Plane (Envoy Sidecar Mesh)"]
      subgraph POD_FRONTEND["Frontend Pod"]
        FRONTEND["Frontend App <br/> (Nginx :80)"]:::service
        PROXY_FRONTEND["Envoy Sidecar"]:::proxy
      end
      
      subgraph POD_PRODUCT["Product Service Pod"]
        PRODUCT["Product Service <br/> (FastAPI :8004)"]:::service
        PROXY_PRODUCT["Envoy Sidecar"]:::proxy
      end
      
      subgraph POD_ORDER["Order Service Pod"]
        ORDER["Order Service <br/> (FastAPI :8001)"]:::service
        PROXY_ORDER["Envoy Sidecar"]:::proxy
      end
      
      subgraph POD_PAYMENT["Payment Service Pod"]
        PAYMENT["Payment Service <br/> (FastAPI :8002)"]:::service
        PROXY_PAYMENT["Envoy Sidecar"]:::proxy
      end
      
      subgraph POD_NOTIFY["Notification Service Pod"]
        NOTIFY["Notification Service <br/> (FastAPI :8003)"]:::service
        PROXY_NOTIFY["Envoy Sidecar"]:::proxy
      end
    end
    
    subgraph CONTROL_PLANE["Istio Control Plane"]
      ISTIOD["istiod"]:::control
    end
  end
  
  subgraph OBS_STACK["Observability Stack"]
    PROM["Prometheus <br/> (Metrics Store)"]:::obs
    GRAF["Grafana <br/> (Dashboards)"]:::obs
    JAEGER["Jaeger <br/> (Tracing)"]:::obs
    KIALI["Kiali <br/> (Service Graph)"]:::obs
  end

  %% Links
  CLIENT -->|"HTTP/HTTPS"| INGRESS
  
  %% Ingress Routing
  INGRESS -->|"/"| PROXY_FRONTEND --> FRONTEND
  INGRESS -->|"/products"| PROXY_PRODUCT --> PRODUCT
  INGRESS -->|"/orders"| PROXY_ORDER --> ORDER
  INGRESS -->|"/payments"| PROXY_PAYMENT --> PAYMENT
  INGRESS -->|"/notifications"| PROXY_NOTIFY --> NOTIFY
  
  %% Inter-service Traffic
  PROXY_ORDER ==>|"POST /inventory/reserve <br/> POST /inventory/commit <br/> POST /inventory/release"| PROXY_PRODUCT
  PROXY_ORDER ==>|"POST /payments"| PROXY_PAYMENT
  PROXY_ORDER ==>|"POST /notifications"| PROXY_NOTIFY
  
  %% Reviews Call from Browser
  PROXY_FRONTEND -.->|"GET/POST /products/{id}/reviews"| PROXY_PRODUCT
  
  %% Control Plane
  ISTIOD -.->|"Config Push (xDS)"| PROXY_FRONTEND
  ISTIOD -.->|"Config Push (xDS)"| PROXY_PRODUCT
  ISTIOD -.->|"Config Push (xDS)"| PROXY_ORDER
  ISTIOD -.->|"Config Push (xDS)"| PROXY_PAYMENT
  ISTIOD -.->|"Config Push (xDS)"| PROXY_NOTIFY

  %% Telemetry Metrics
  PROXY_FRONTEND -. "metrics" .-> PROM
  PROXY_PRODUCT -. "metrics" .-> PROM
  PROXY_ORDER -. "metrics" .-> PROM
  PROXY_PAYMENT -. "metrics" .-> PROM
  PROXY_NOTIFY -. "metrics" .-> PROM
  
  %% Telemetry Traces
  PROXY_FRONTEND -. "traces (zipkin)" .-> JAEGER
  PROXY_PRODUCT -. "traces (zipkin)" .-> JAEGER
  PROXY_ORDER -. "traces (zipkin)" .-> JAEGER
  PROXY_PAYMENT -. "traces (zipkin)" .-> JAEGER
  PROXY_NOTIFY -. "traces (zipkin)" .-> JAEGER
  
  %% Observability Internal
  PROM --> GRAF
  PROM --> KIALI
  JAEGER --> KIALI
```

### Key Highlights
- **Ingress Gateway Routing**: The Gateway routes public API endpoints based on the path prefixes defined in `istio/virtual-service.yaml` (e.g. `/orders` to `order-service`, `/products` to `product-service`).
- **Saga Network Calls**: The thick green arrows highlight the business transaction flow orchestrated by `order-service` using the Saga pattern.
- **Sidecar Instrumentation**: Each container runs alongside an `istio-proxy` (Envoy) sidecar which handles all inbound/outbound communication, trace context propagation (Zipkin/B3 headers), and metrics emission.

---

## 2. Business Request Flow (Sequence Diagram) - Saga Orchestration
*This sequence diagram captures what happens when a client calls `POST /orders`. It highlights how order placement, inventory reservation/commit/release, and notification sending are orchestrated.*

```mermaid
sequenceDiagram
  autonumber
  actor Client as Client (Browser / Postman)
  participant Gateway as Istio Ingress Gateway
  participant Order as order-service (8001)
  participant Product as product-service (8004)
  participant Payment as payment-service (8002)
  participant Notification as notification-service (8003)

  Client->>Gateway: POST /orders (with Idempotency-Key)
  Gateway->>Order: Route POST /orders
  Note over Order: Step 1: Idempotency Check & Order ID Generation
  
  %% Saga Phase 1: Reservation
  Order->>Product: POST /inventory/reserve (reservation_id=ORD-XXX, items)
  Note over Product: Lock stock in-memory <br/> (stock = stock - qty)
  Product-->>Order: 200 OK (inventory_status: reserved, items, line_totals)
  Note over Order: Calculate total amount

  %% Saga Phase 2: Payment
  Order->>Payment: POST /payments (order_id, amount, mode)
  Note over Payment: Process payment simulation <br/> (success, failed, delayed)
  Payment-->>Order: 200 OK or 402 Error (payment_status: success/failed)
  
  %% Saga Phase 3: Commit or Compensate
  alt Payment Success (payment_status: success)
    Order->>Product: POST /inventory/commit (reservation_id=ORD-XXX)
    Note over Product: Commit stock lock <br/> (inventory_status: committed)
    Product-->>Order: 200 OK (inventory_status: committed)
  else Payment Failed (payment_status: failed / error)
    Order->>Product: POST /inventory/release (reservation_id=ORD-XXX, reason: payment_failed)
    Note over Product: Release locked stock <br/> (stock = stock + qty)
    Product-->>Order: 200 OK (inventory_status: released, reason: payment_failed)
  end

  %% Saga Phase 4: Notification
  Order->>Notification: POST /notifications (order_id, user_id, status)
  Note over Notification: Send out notifications
  alt Notification Service Available
    Notification-->>Order: 200 OK (notification: sent)
  else Notification Service Fails (Graceful Degradation)
    Note over Order: Catch exception, fallback status: queued
  end

  Order-->>Gateway: Return order result JSON (order_status: confirmed/payment_failed, etc.)
  Gateway-->>Client: Return JSON response
```

### Detailed Sequence Breakdown
1. **Idempotency Key Verification**: The `order-service` checks if the `Idempotency-Key` header has been processed before. If it has succeeded, it returns the cached JSON order confirmation. If it is currently processing, it returns a `409 Conflict`.
2. **Phase 1 (Reserve)**: The `order-service` acts as the Saga orchestrator. It immediately calls `product-service` on `/inventory/reserve` to check availability and lock product stock in-memory.
3. **Phase 2 (Payment)**: If stock is reserved successfully, it initiates the payment simulation.
4. **Phase 3 (Commit / Compensate)**:
   - **Commit**: If payment succeeds, it commands `product-service` to commit the reservation (`/inventory/commit`). The stock reduction becomes permanent.
   - **Compensate (Release)**: If payment fails or returns an error, it commands `product-service` to release the reservation (`/inventory/release`). The stock is credited back to the product catalog, preserving inventory consistency.
5. **Phase 4 (Notification)**: A notification is dispatched. If the `notification-service` is down, the orchestrator catches the error, registers the notification status as `queued`, and successfully responds to the user (graceful degradation).

---

## 3. Observability & Telemetry Data Flow
*This diagram illustrates how telemetry data (metrics and traces) flows from Envoy sidecars to data repositories and how Kiali, Grafana, and Jaeger consume it.*

```mermaid
flowchart LR
  %% Style definitions
  classDef app fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1
  classDef collector fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e
  classDef ui fill:#f3e8ff,stroke:#7e22ce,stroke-width:2px,color:#6b21a8
  classDef question fill:#f0fdf4,stroke:#16a34a,stroke-width:2px,color:#14532d

  subgraph workloads["Service Pods (with Envoy Sidecars)"]
    direction TB
    frontend["frontend Pod <br/> (Envoy Sidecar)"]:::app
    product["product-service Pod <br/> (Envoy Sidecar)"]:::app
    order["order-service Pod <br/> (Envoy Sidecar)"]:::app
    payment["payment-service Pod <br/> (Envoy Sidecar)"]:::app
    notify["notification-service Pod <br/> (Envoy Sidecar)"]:::app
  end

  subgraph collection["Data Collection Layer"]
    PROM["Prometheus <br/> (Metrics Scraper)"]:::collector
    JAEGER["Jaeger Collector <br/> (Trace Receiver)"]:::collector
  end

  subgraph visualization["Visualization & Analysis"]
    GRAF["Grafana <br/> (Dashboards)"]:::ui
    KIALI["Kiali <br/> (Mesh Graph)"]:::ui
    JAEGER_UI["Jaeger UI <br/> (Distributed Traces)"]:::ui
  end

  %% Data collection links
  frontend & product & order & payment & notify -->|"metrics (scrape every 15s) <br/> - istio_requests_total <br/> - istio_request_duration_ms_bucket <br/> - CPU/Memory"| PROM
  frontend & product & order & payment & notify -->|"traces (B3 / Trace Context) <br/> - traceparent header <br/> - span data <br/> - trace correlation"| JAEGER

  %% Query & Graph links
  PROM -->|"PromQL queries"| GRAF
  PROM -->|"graph metrics & service health"| KIALI
  JAEGER -->|"trace data & service spans"| KIALI
  JAEGER -->|"trace timelines"| JAEGER_UI

  %% Questions block
  subgraph QA["Questions Answered by Observability"]
    Q1["Is the system healthy overall? <br/> ➔ Prometheus + Grafana"]:::question
    Q2["Where is the bottleneck? <br/> ➔ Jaeger Tracing"]:::question
    Q3["Which link is failing? <br/> ➔ Kiali Graph"]:::question
    Q4["What happened inside a service? <br/> ➔ Application JSON Logs"]:::question
  end
```

### Telemetry Pipeline Details
- **Metrics Scraping**: Prometheus pulls Envoy-exposed endpoints every 15 seconds, tracking metrics such as HTTP request counts (`istio_requests_total`), request latency histograms, and Kubernetes system stats (CPU/Memory).
- **Trace Propagation**: When an HTTP request enters the gateway, a unique trace identifier is assigned. The Envoy sidecars pass headers like `x-request-id` and W3C `traceparent` headers downstream. Jaeger captures the resulting span telemetry.
- **Kiali Integration**: Kiali queries both Prometheus (for traffic volume and health status) and Jaeger (for distributed trace overlays) to draw a real-time topology map of service communications.

---

## 4. Istio Traffic Management & Fault Tolerance
*This diagram explains the mechanics of sidecar proxy traffic interception and summarizes VirtualService traffic policies and DestinationRule resilience rules.*

```mermaid
flowchart TD
  %% Styles
  classDef app fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0369a1
  classDef envoy fill:#fce7f3,stroke:#db2777,stroke-width:2px,color:#9d174d
  classDef vs fill:#fef9c3,stroke:#ca8a04,stroke-width:2px,color:#854d0e
  classDef dr fill:#fae8ff,stroke:#9333ea,stroke-width:2px,color:#6b21a8

  subgraph pod["Kubernetes Pod Structure"]
    direction LR
    APP["App Container <br/> (e.g., Order Service)"]:::app
    ENVOY["Envoy Sidecar Proxy <br/> (istio-proxy)"]:::envoy
    
    INBOUND[Inbound Traffic] --> ENVOY
    ENVOY -->|"intercepted"| APP
    APP --> OUTBOUND[Outbound Traffic]
    OUTBOUND --> ENVOY
  end

  subgraph rules["Traffic Policies (VirtualService)"]
    VS_ROUTING["Routing Paths <br/> ➔ / -> frontend:80 <br/> ➔ /products -> product-service:8004 <br/> ➔ /orders -> order-service:8001 <br/> ➔ /payments -> payment-service:8002 <br/> ➔ /notifications -> notification-service:8003"]:::vs
    VS_RETRY["Retry Settings <br/> ➔ 2 attempts <br/> ➔ 1s-3s perTryTimeout <br/> ➔ retryOn: connect-failure, 5xx"]:::vs
    VS_TIMEOUT["Timeout Settings <br/> ➔ /orders: 8s <br/> ➔ /products: 4s <br/> ➔ /payments: 3s (Ingress), 8s (Mesh) <br/> ➔ /notifications: 4s"]:::vs
    VS_FAULT["Fault Injection <br/> ➔ payment-service: 30% percentage <br/> ➔ 2s fixedDelay"]:::vs
  end

  subgraph policies["DestinationRules (Resilience)"]
    DR_LB["Load Balancing <br/> ➔ ROUND_ROBIN across replica pods"]:::dr
    DR_POOL["Connection Pooling (TCP/HTTP) <br/> ➔ payment: maxConnections: 20 <br/> ➔ product: maxConnections: 50 <br/> ➔ notification: maxConnections: 30 <br/> ➔ order: maxConnections: 100"]:::dr
    DR_OUTLIER["Outlier Detection (Circuit Breaker) <br/> ➔ 3 consecutive 5xx errors <br/> ➔ 10s interval, 30s base ejection <br/> ➔ maxEjectionPercent: 50%"]:::dr
  end

  pod -.->|"Configured by VS"| rules
  pod -.->|"Enforces DR policies"| policies
```

### Explanation of Resilience Settings
- **Retries & Timeouts**: If a backend service fails temporarily (e.g. standard socket errors or 503 Service Unavailable), the Envoy sidecar retries up to 2 times. If a downstream call (like calling the payment processor) exceeds the configured timeout (e.g. 8s for orders, 3s for payments), the sidecar terminates the connection to prevent cascading latency.
- **Fault Injection**: You can apply `istio/payment-fault-injection.yaml` to test how the orchestrator handles slow dependencies. It injects a `2s` fixed delay on 30% of calls to the payment service, simulating high latency in a controlled environment.
- **Connection Pools**: Limits the maximum active connections to prevent overloading database/service ports (e.g. capping `payment-service` to 20 TCP connections).
- **Outlier Detection (Circuit Breaker)**: Envoy tracks 5xx errors. If a specific replica pod of `product-service`, `payment-service`, or `notification-service` produces 3 consecutive 5xx errors within 10 seconds, it is marked as unhealthy and ejected from the load-balancer pool for 30 seconds.
