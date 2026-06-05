# MeshMart 20-Slide Presentation Blueprint & Script

This document provides a highly detailed, 20-slide presentation guide designed to wow your professors. It expands on your codebase features (API contracts, Envoy network interception, Saga details, and idempotency) and includes specific **Canva Visual Layout Guides** (colors, grids, card shapes, and typography) and **Speaker Scripts**.

---

## 🎨 Design System for Canva (Consistency Guide)
To make your slide deck look highly premium, apply this design language across your Canva project:
*   **Background**: Deep Dark Slate/Navy (`#0F172A`).
*   **Typography**: Header: *Montserrat* or *League Spartan* (Bold, 36pt+). Body: *Inter* or *Segoe UI* (Clean, 14-16pt).
*   **Colors**:
    *   **White** (`#FFFFFF`): Main text.
    *   **Light Gray** (`#E2E8F0`): Body text.
    *   **Purple/Neon Pink** (`#C084FC` / `#F472B6`): Technical keywords, endpoints, and Control Plane references.
    *   **Green** (`#34D399`): Success states, Data Plane, and healthy nodes.
    *   **Orange/Red** (`#F87171`): Failure states, timeouts, and ejected pods.

---

## Slide 1: Cover (The Title Slide)
*   **Canva Layout**: Minimalist centered grid. Dark slate background. Add a large, glowing, abstract geometric network-mesh vector in the center (opacity 40%).
*   **On-Slide Text**:
    *   **Main Title (Montserrat, 44pt, White)**: Service Mesh & Observability for Microservices
    *   **Subtitle (Inter, 20pt, Light Purple)**: MeshMart: Resiliency, Traffic Control, and Telemetry in a Kubernetes Cluster
    *   **Presenter Info (14pt, Light Gray)**: [Group Members] | Distributed Systems Course Project
*   **Speaker Script**:
    > "Good morning, professors and peers. Welcome to our project presentation: Service Mesh and Observability for Microservices. Using an e-commerce platform called MeshMart as our case study, we will explain how to move complex networking policies like timeouts, retries, and circuit breaking from the application code to the infrastructure layer using Istio service mesh, and how to verify cluster health using Prometheus, Grafana, Jaeger, and Kiali."

---

## Slide 2: The Monolith to Microservices Paradox (Problem Statement)
*   **Canva Layout**: 2-column comparison layout.
    *   *Left Column*: "The Monolithic Way" (One neat card with internal green arrows).
    *   *Right Column*: "The Microservices Way" (A web of 5 cards with tangled orange network arrows).
*   **Real-World Analogy**: **The "Broken Telephone" Game.** In a monolith, functions communicate directly in memory. In a microservices system, services talk over the network. If one service drops the call or takes too long, the whole system freezes, and isolating the failure is like finding a needle in a haystack.
*   **On-Slide Text**:
    *   **Monolith**: Clean, in-memory function calls. Single point of failure, scaling limits.
    *   **Microservices**: Agility and independence, but introduces network boundaries (HTTP/gRPC).
    *   **The Operational Chaos**: Lack of central visibility, cascading failures, and duplicated routing code inside each service.
*   **Speaker Script**:
    > "Let’s analyze the problem. While dividing a monolith into microservices lets teams build and deploy features independently, it introduces network boundaries. Every local function call becomes an HTTP request. If a database query becomes slow or a network socket drops, the entire user transaction fails. If we try to write retry and timeout logic inside every single microservice, we clutter our codebase. We need a way to manage these policies centrally."

---

## Slide 3: MeshMart Project Scope & Service Boundaries
*   **Canva Layout**: A horizontal timeline grid featuring 5 card blocks, each colored with a thin border corresponding to their operational domain. Add service icons (static page, catalog database, orchestrator engine, card swipe, envelope).
*   **On-Slide Text**:
    *   **frontend** (Nginx, Port `80`): Storefront UI, client routing, and the new **Observability UI details panel** showing microservice latency and Saga timeline.
    *   **product-service** (FastAPI, Port `8004`): Handles catalog, ratings/reviews, and stock locking.
    *   **order-service** (FastAPI, Port `8001`): The Saga transaction orchestrator.
    *   **payment-service** (FastAPI, Port `8002`): Simulates payment processing (success, declined, delayed/slow modes).
    *   **notification-service** (FastAPI, Port `8003`): Simulates delivering dispatch alerts to users.
*   **Speaker Script**:
    > "To demonstrate this, we built a realistic microservices application named MeshMart. It consists of five containerized services: the Frontend serves static files and has been upgraded with an interactive **Observability UI details panel** showing ordered items, microservice timings, and Saga timeline. The Product Service manages catalog data and reviews; the Order Service acts as the transaction orchestrator; the Payment Service simulates credit authorizations; and the Notification Service handles customer alerts. This gives us a realistic distributed system to operate."

---

## Slide 4: API Endpoints & Service Contracts
*   **Canva Layout**: A clean, technical 2-column layout. 
    *   *Left Column*: A stylized code editor block (Dark Gray background) displaying a JSON request payload.
    *   *Right Column*: A table listing HTTP Methods, Endpoints, and Responsibilities.
*   **On-Slide Text**:
    *   `GET /products` ➔ List product catalog & details
    *   `POST /orders` ➔ Create order (accepts `Idempotency-Key` header)
    *   `POST /payments` ➔ Simulates payment billing
    *   `/health/live` & `/health/ready` ➔ Service health probes (Liveness/Readiness checks)
*   **Speaker Script**:
    > "To show coding rigor, here is our service contract. The client fetches products and submits orders to the order-service. The order-service then coordinates calls to the payment, inventory, and notification endpoints. Our checkout API supports the 'Idempotency-Key' header. Additionally, we've exposed `/health/live` and `/health/ready` endpoints on all microservices to hook directly into Kubernetes health probes, validating backend and database readiness dynamically."

---

## Slide 5: System Deployment Architecture & Zero Trust Security
*   **Canva Layout**: Large, central display frame showing the generated `system_architecture.png` diagram. Add subtle glowing highlights around the "Data Plane" and "Observability Stack" boxes to draw the viewer's eyes.
*   **On-Slide Text**:
    *   **Istio Ingress Gateway**: Entry point directing HTTP paths to Kubernetes Services.
    *   **Data Plane (Envoy Sidecars)**: Each pod runs an `istio-proxy` sidecar alongside the application.
    *   **STRICT mTLS**: Enforces mutual TLS encryption namespace-wide in the `meshmart` namespace.
    *   **Zero Trust RBAC**: Granular `AuthorizationPolicy` objects restrict service access using dedicated `ServiceAccounts`.
*   **Speaker Script**:
    > "This is our System Deployment Architecture inside the 'meshmart' namespace. Public traffic enters through the Istio Ingress Gateway. Crucially, we enforce Zero Trust Security. First, `PeerAuthentication` requires STRICT mTLS namespace-wide, encrypting all service communications. Second, we created dedicated `ServiceAccounts` for each microservice and defined granular `AuthorizationPolicy` rules. For instance, `order-service` is explicitly authorized to query backends, while unauthorized access from external workloads is blocked automatically by Envoy."

---

## Slide 6: Network Interception: How Envoy Sidecars Work
*   **Canva Layout**: A detailed diagram on the right showing inbound and outbound traffic arrows passing through `Envoy Sidecar Proxy` before reaching `App Container`. Use a glowing green circle around Envoy.
*   **On-Slide Text**:
    *   **iptables Redirection**: All traffic entering or leaving the container is transparently routed to Envoy.
    *   **Inbound Traffic**: Client ➔ Envoy (decrypts mTLS, checks policies) ➔ App (Port localhost).
    *   **Outbound Traffic**: App ➔ Envoy (injects tracing headers, checks retries/timeouts) ➔ Downstream Service.
    *   **Zero App Modification**: The FastAPI application does not know Envoy exists.
*   **Speaker Script**:
    > "How does Istio intercept traffic without code changes? When a pod starts, an init-container configures iptables rules inside the pod network namespace. This ensures that any inbound or outbound network packet is redirected to the Envoy sidecar. When the order-service calls the product-service, the packet goes to the local Envoy, which adds trace headers and checks retry rules, then sends it to the destination Envoy, which verifies access policies before passing it to the product app."

---

## Slide 7: Business Request Flow: The Saga Transaction Pattern
*   **Canva Layout**: A horizontal flowchart displaying the 4-phase transaction chain: 
    `1. POST /orders` ➔ `2. Reserve Stock` ➔ `3. Charge Card` ➔ `4. Commit or Release Stock` ➔ `5. Notify`.
*   **On-Slide Text**:
    *   **Distributed Transactions**: Databases are isolated in microservices; standard database locks cannot span network boundaries.
    *   **Saga Orchestration**: The orchestrator (`order-service`) executes sequential API transactions.
    *   **Loose Coupling**: Each service performs its local transaction and returns a result.
    *   **State Alignment**: The final status is determined by the success or failure of the payment phase.
*   **Speaker Script**:
    > "In a monolith, we can lock database rows during checkout to prevent double-selling. But in microservices, databases are isolated. We use the Saga Pattern to manage this. The order-service acts as the orchestrator. Instead of locking database tables, it executes local transactions sequentially across services. It coordinates stock locking, credit card billing, and notifications, ensuring eventual consistency without holding active database locks."

---

## Slide 8: Step-by-Step Saga Execution (Success Path)
*   **Canva Layout**: Split-pane layout.
    *   *Left Column*: Bullet points detailing the success path.
    *   *Right Column*: The `saga_checkout_flow.png` diagram, focusing on the green "payment success" branch.
*   **On-Slide Text**:
    *   **Check Idempotency**: Verify if the `Idempotency-Key` exists.
    *   **Reserve Inventory**: Call `/inventory/reserve` to lock stock.
    *   **Process Payment**: Verify payment status is `"success"`.
    *   **Commit Inventory**: Call `/inventory/commit` to confirm stock reduction.
    *   **Storefront Timeline**: Renders 5 green dots (`order_created` $\rightarrow$ `notification_sent`) representing success.
*   **Speaker Script**:
    > "Let’s look at the success path. When a client places an order, the order-service verifies the idempotency key and reserves stock. Once the payment service returns success, the order-service commits the inventory, locking the stock reduction permanently, and sends a notification. We have integrated an **Observability UI details panel** on the storefront that visualizes these exact 5 Saga steps with green checkmarks, showing the transaction lifecycle transparently."

---

## Slide 9: Saga Compensation & Rollbacks (Failure Path)
*   **Canva Layout**: Use a bright red/orange theme. Right side: `saga_checkout_flow.png` focusing on the red "payment failed" branch. Left side: Bold cards explaining "The Rollback Step".
*   **On-Slide Text**:
    *   **The Problem**: Payment fails, but stock has already been decremented during the reserve phase.
    *   **The Compensation**: Trigger an undo transaction to restore data consistency.
    *   **Rollback Steps**: payment fails $\rightarrow$ call `/inventory/release` $\rightarrow$ restore reserved stock.
    *   **Storefront Timeline**: Visualizes the compensation step (`inventory_released`) in red, proving rollback execution.
*   **Speaker Script**:
    > "What happens if a payment is declined? Since the stock was already decremented, we must trigger compensation to restore data consistency. The order-service immediately sends a rollback command to `/inventory/release`. The product-service restores the reserved stock back to the catalog. Our storefront details panel displays this rollback in real-time, showing the initial green steps turn red at the failed payment and rollback phases."

---

## Slide 10: Idempotency Guard (Preventing Double Billing)
*   **Canva Layout**: Centered infographic. On top: Client clicks Buy button twice. Middle: `order-service` with a lock icon. Bottom: Cached Order details returned without charging card twice.
*   **On-Slide Text**:
    *   **The Risk**: Network timeouts occur; the client retries `POST /orders`, creating duplicate orders.
    *   **Idempotency Store**: In-memory cache (`_idempotency_store`) mapping `Idempotency-Key` to responses.
    *   **Fingerprint Check**: Validates that retry payloads match the original request.
    *   **Response**: Returns the cached response for successful keys, or `409 Conflict` if the transaction is still processing.
*   **Speaker Script**:
    > "In distributed systems, networks drop. If a client submits a payment, the payment succeeds, but the network drops before the client gets the response, the client will retry. Without idempotency, this results in double-billing. We prevent this by requiring an Idempotency-Key header. If the key exists in our cache, we return the cached response immediately without invoking the payment or product services again."

---

## Slide 11: Istio Ingress Gateway & Path-Based Routing
*   **Canva Layout**: Display path routing rules as colored code cards:
    *   `/products` ➔ `product-service` (cyan)
    *   `/orders` ➔ `order-service` (green)
    *   `/payments` ➔ `payment-service` (purple)
    *   `/` ➔ `frontend` (blue)
*   **On-Slide Text**:
    *   **Unified Access**: Clients hit a single host/port (Ingress Gateway).
    *   **Decoupled Paths**: Path prefix matching maps URLs to internal cluster services.
    *   **Resiliency Layer**: Gateway handles SSL termination and routing policies.
    *   **Configuration**: Set up in `istio/virtual-service.yaml` and `gateway.yaml`.
*   **Speaker Script**:
    > "In Kubernetes, we use the Istio Ingress Gateway to route traffic. Instead of exposing five different ports to the public, the client sends all requests to the gateway on a single port. The gateway reads the URL path: requests starting with `/products` go to product-service, `/orders` go to order-service, and the root `/` goes to the frontend. This decouples service ports from public URLs."

---

## Slide 12: Traffic Control: Timeouts & Retries
*   **Canva Layout**: Two side-by-side columns: **Timeouts** (glowing orange clock) and **Retries** (glowing purple retry arrows).
*   **On-Slide Text**:
    *   **Timeouts**:
        *   `order-service` ➔ **8s timeout** (stops cascading delays).
        *   `product-service` ➔ **4s timeout**.
        *   `payment-service` ➔ **3s timeout** (Ingress routing).
    *   **Retries**:
        *   **2 attempts** configured.
        *   Triggered on `connect-failure`, `refused-stream`, `unavailable`, and `5xx` errors.
        *   Enforced automatically by the Envoy proxy.
*   **Speaker Script**:
    > "Service mesh allows us to control timeouts and retries at the network layer. We set an 8-second timeout for the order-service and 3 seconds for payment. If a payment transaction takes longer, Envoy aborts the connection to protect system threads. We also configured 2 retries on temporary connection errors. This means Envoy handles transient failures automatically, and the application never sees them."

---

## Slide 13: Fault Injection (Chaos Engineering)
*   **Canva Layout**: Neon design showing a lightning bolt striking a payment terminal. High contrast colors.
*   **On-Slide Text**:
    *   **Simulating Chaos**: Test system stability under load without crashing real infrastructure.
    *   **Istio Fault Injection**:
        *   Target: `payment-service`
        *   Fault Type: **Delay**
        *   Percentage: **30% of requests**
        *   Delay Value: **2s fixed delay**
    *   **Saga Response**: System remains stable; timeout policies terminate slow calls safely.
*   **Speaker Script**:
    > "To test our system’s resilience, we use Chaos Engineering. Istio allows us to inject faults directly into network traffic. We applied a policy that delays 30% of calls to the payment service by 2 seconds. This lets us verify how the order-service behaves when dependencies are slow. We can confirm that the system handles the latency safely without crashing or leaking inventory locks."

---

## Slide 14: DestinationRules: Connection Pools & Rate Limiting
*   **Canva Layout**: Infographic displaying 4 pipelines of different widths (representing max connection capacities: 20, 30, 50, 100).
*   **On-Slide Text**:
    *   **Traffic Policies**: Configured in `istio/destination-rule.yaml`.
    *   **Connection Limits**:
        *   `payment-service`: Max **20** TCP connections.
        *   `product-service`: Max **50** TCP connections.
        *   `notification-service`: Max **30** TCP connections.
        *   `order-service`: Max **100** TCP connections.
    *   **Impact**: Limits resource usage to protect services from being overloaded during traffic spikes.
*   **Speaker Script**:
    > "We also use DestinationRules to limit connection pools. This acts as a rate-limiting mechanism. We cap payment-service to 20 concurrent connections and product-service to 50. If a surge of traffic hits MeshMart, Envoy queues requests exceeding these limits rather than overloading the application containers, protecting our services from crashing under high load."

---

## Slide 15: Outlier Detection (Circuit Breaking)
*   **Canva Layout**: Stylized "Ejection seat" infographic. A replica pod is ejected from a group of pods because it turned red (errors).
*   **On-Slide Text**:
    *   **Outlier Detection Settings**:
        *   Consecutive Errors: **3 consecutive 5xx errors**
        *   Evaluation Interval: **10 seconds**
        *   Base Ejection Time: **30 seconds**
        *   Max Ejection Percent: **50% of replica pool**
    *   **Self-Healing**: Unhealthy pods are automatically bypassed, allowing the system to heal.
*   **Speaker Script**:
    > "Circuit breaking is implemented through Outlier Detection. If a pod replica returns 3 consecutive 5xx errors within 10 seconds, Envoy marks it as unhealthy and ejects it from the active load-balancer pool for 30 seconds. Up to 50% of the replicas can be ejected. This protects our traffic by automatically bypassing failing pods while they recover or are restarted by Kubernetes."

---

## Slide 16: Observability Architecture & Telemetry Data Flow
*   **Canva Layout**: Display the `observability_data_flow.png` diagram in a sleek frame, with glowing arrows showing metrics and trace pipelines.
*   **On-Slide Text**:
    *   **Data Scraper**: Prometheus polls Envoy sidecars & custom Python endpoints (/metrics) every 15s.
    *   **Dashboard Visualizer**: Grafana automatically provisions our custom 16-panel MeshMart dashboard on startup.
    *   **Centralized Logs**: Custom Python `JSONFormatter` structures all application logs into single-line JSONs.
    *   **Traces & Graph**: Jaeger captures spans, and Kiali visualizes topology.
*   **Speaker Script**:
    > "Our observability stack operates at both the infrastructure and application layers. Prometheus polls Envoy sidecars and custom Python metrics. Grafana automatically provisions our custom 16-panel dashboard on startup, showing order throughput, latencies, and inventory levels. Additionally, we implemented JSON Structured Logging across all services, formatting log messages into structured JSON lines ready for Loki or Elasticsearch querying."

---

## Slide 17: Observability in Action: Diagnostics & Evidence
*   **Canva Layout**: Split-screen layout.
    *   *Left Side*: Grafana latency graph showing a spike.
    *   *Right Side*: Jaeger trace view highlighting a slow payment span.
*   **On-Slide Text**:
    *   **The Diagnostic Path**:
        1. **Grafana**: Alerts on aggregate latency or error rate spikes.
        2. **Kiali / Storefront UI**: Visualizes the failing connection or Saga rollback in red.
        3. **Jaeger**: Trace details pinpoint the exact slow service and span.
        4. **JSON Structured Logs**: Query centralized logs by `request_id` to read structured errors instantly.
*   **Speaker Script**:
    > "Here is our diagnostic path during an outage. First, Grafana alerts us to a latency spike. Second, Kiali or our storefront details panel highlights the failing connection or Saga rollback step in red. Third, we inspect the Jaeger trace to pinpoint the exact slow microservice span. Finally, because we use JSON structured logging, we can search logs using the unique `request_id` to inspect the exact exception payload. This demonstrates complete telemetry correlation."

---

## Slide 18: High Availability, Probes & Autoscaling
*   **Canva Layout**: 3-column layout. Column 1: **Health Probes** (Liveness/Readiness). Column 2: **Autoscaling** (HPA). Column 3: **Disruption Budgets** (PDB).
*   **On-Slide Text**:
    *   **Liveness & Readiness**: Probes check `/health/live` and `/health/ready`.
    *   **Deep Dependency Checks**: `order-service` checks if product, payment, and notification services are reachable before reporting ready.
    *   **HPA & PDB**: Scales pod replicas based on CPU, and guarantees at least 1 pod is active during rolling updates.
*   **Speaker Script**:
    > "For high availability, we implemented advanced Kubernetes health probes. Liveness probes check `/health/live` to restart dead pods. Readiness probes check `/health/ready` to block traffic. Importantly, our `order-service` readiness probe executes dynamic dependency checks on product, payment, and notification services. If any go offline, `order-service` reports degraded with a 503, preventing client requests from hitting broken paths."

---

## Slide 19: Project Limitations & Production Roadmap
*   **Canva Layout**: 2-column checklist layout. Left column: **Completed Achievements**. Right column: **Production Roadmap (Future Work)**.
*   **On-Slide Text**:
    *   **Completed Achievements**:
        *   STRICT mTLS encryption & Zero-Trust Authorization Policies.
        *   JSON Structured Logging & Custom App metrics dashboard.
        *   Liveness/Readiness health probes with dependency checks.
    *   **Production Roadmap (Future Work)**:
        *   Add persistent databases (PostgreSQL, Redis) and shared idempotency cache.
        *   Enable JSON Web Token (JWT) request authentication at the gateway.
*   **Speaker Script**:
    > "To reflect our current progress, we have successfully implemented STRICT mTLS encryption and Zero-Trust Authorization Policies in Kubernetes. We also completed JSON structured logging and dynamic health checks. Our future production roadmap is now focused on adding persistent SQL databases, utilizing Redis as a shared idempotency cache, and enabling JWT token authentication at the Ingress Gateway."

---

## Slide 20: Conclusion & Key Learnings
*   **Canva Layout**: A strong, minimalist closing slide. Use 3 large highlight text blocks with glowing icons.
*   **On-Slide Text**:
    *   **Policy Decoupling**: Traffic routing, retries, timeouts, and circuit breaking belong in the infrastructure layer (Istio), not application code.
    *   **Observability is Mandatory**: You cannot manage what you do not measure. Combined metrics, traces, and logs are operational requirements.
    *   **Design for Failure**: Resiliency patterns like Saga transactions and graceful degradation are crucial for building reliable distributed systems.
*   **Speaker Script**:
    > "To conclude, our project demonstrates three main takeaways. First, decoupling communication policies from code makes applications lighter and easier to maintain. Second, in a distributed system, observability is not a luxury—it is mandatory. The combination of metrics, traces, and graphs is the only way to operate microservices. Finally, we must design for failure. By using Saga compensation and idempotency, we build systems that remain consistent, reliable, and user-friendly even when the network fails. Thank you, and we are open to any questions."
