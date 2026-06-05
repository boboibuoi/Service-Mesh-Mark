# 🏆 MeshMart: Final Presentation Slides Layout & Visual Design Guide

This document is the master layout blueprint and script guide for your final project presentation on **Service Mesh & Observability**. It is designed to be highly informative, visually structured, and engaging for professors. 

It translates complex infrastructure concepts into **visual grids**, **real-world analogies**, **precise English slide text**, and **Vietnamese speaker scripts**.

---

## 🎨 Design System for Canva / PowerPoint
To ensure your presentation looks premium and state-of-the-art:
*   **Background**: Deep Slate Black/Navy (`#0F172A`).
*   **Fonts**: Header: *Montserrat* or *League Spartan* (Bold, 36pt+). Body: *Inter* or *Segoe UI* (Clean, 14pt-16pt).
*   **Visual Elements**: Use glowing borders, glassmorphism cards, and high-contrast colors:
    *   `#FFFFFF` (White) - Primary Text.
    *   `#C084FC` (Neon Purple) - Service Mesh / Policies / Control Plane.
    *   `#34D399` (Mint Green) - Success / Data Plane / Healthy States.
    *   `#F87171` (Coral Red) - Rollback / Failures / Circuit Breaking.

---

## 📽️ Slide-by-Slide Layout & Speaker Scripts

---

### Slide 1: Cover (The Title Slide)
*   **Core Message**: Introducing the enterprise-grade service mesh platform.
*   **Canva Layout**: Minimalist centered layout. Dark slate background. Place an abstract glowing geometric network vector in the background (opacity 30%).
*   **On-Slide Content (English)**:
    *   **Main Title (Montserrat, 44pt)**: Service Mesh & Full-Stack Observability
    *   **Subtitle (Inter, 20pt, Light Purple)**: MeshMart: Traffic Control, Resiliency, Zero-Trust Security, and Telemetry in a Kubernetes Cluster
    *   **Presenter Info (14pt, White)**: [Group Members] | Distributed Systems Course Project
*   **Speaker Notes (Vietnamese)**:
    > "Kính chào các thầy cô và các bạn. Hôm nay nhóm chúng em xin phép trình bày đồ án cuối kỳ môn học Hệ thống phân tán với đề tài: 'Service Mesh và Observability cho Microservices'. Lấy mô hình thực tế là ứng dụng thương mại điện tử mang tên MeshMart chạy trên nền tảng Kubernetes và Istio Service Mesh, chúng em sẽ giải quyết các bài toán về: Kiểm soát lưu lượng, Khả năng chịu lỗi, Bảo mật Zero-Trust và Giám sát Telemetry toàn diện."
*   **Interactive Tip**: Stand confidently, make eye contact, and briefly introduce the group members before clicking to the next slide.

---

### Slide 2: The Monolith to Microservices Paradox (Problem Statement)
*   **Core Message**: Microservices solve deployment bottlenecks but introduce network complexity and failures.
*   **Vivid Analogy**: **The "Broken Telephone" Game.** Inside a monolith, functions talk directly in memory. In microservices, they talk over the network. If one person lags, the whole line drops.
*   **Canva Layout**: 2-column comparison.
    *   *Left Card (Monolith)*: Clean green box containing a single block (simple, in-memory calls).
    *   *Right Card (Microservices)*: Chaotic web of 5 cards with tangled orange arrows (network hops, packet drops, latencies).
*   **On-Slide Content (English)**:
    *   **In-Memory vs. Network Hops:**
        *   Monoliths communicate safely inside RAM.
        *   Microservices cross network boundaries (HTTP/gRPC) subject to network instability.
    *   **The Operational Chaos:**
        *   **Cascading Failures**: A single slow dependency freezes thread pools upstream.
        *   **Telemetry Blindspots**: Disconnected logs make it impossible to isolate issues.
        *   **Code Pollution**: Duplicating retries, timeouts, and logging in business code slows down development.
*   **Speaker Notes (Vietnamese)**:
    > "Khi chia nhỏ hệ thống thành microservices, chúng ta đổi lấy sự độc lập về phát triển nhưng phải gánh chịu sự bất ổn của truyền thông mạng. Mọi lời gọi hàm trong RAM giờ thành request HTTP qua dây cáp. Nếu một dịch vụ con như Payment bị chậm, nó sẽ gây tắc nghẽn toàn bộ hệ thống phía trên. Việc viết đè code xử lý mạng thủ công trong từng service làm phình mã nguồn ứng dụng."
*   **Interactive Tip**: Point at the tangled web on the right to emphasize the operational chaos that developers face without a service mesh.

---

### Slide 3: MeshMart Scope & Service Boundaries
*   **Core Message**: Understanding the five business boundaries of the e-commerce system.
*   **Canva Layout**: Horizontal grid of 5 cards, each containing a minimal vector icon (Nginx server, Shopping Cart, Database, Credit Card, Mail Envelope).
*   **Image Placement**: Insert the generated architecture diagram: [architecture-diagram.png](file:///c:/Users/ADMIN/OneDrive/Documents/Service%20Mesh%20Observability/distributed-system-service-mesh-observability/docs/architecture-diagram.png) in the lower half or right pane.
*   **On-Slide Content (English)**:
    *   `frontend` (Nginx, Port `8080`): Storefront UI, client routing, and the new **Observability UI Details Panel**.
    *   `product-service` (FastAPI, Port `8004`): Handles catalog data, reviews, and stock locks.
    *   `order-service` (FastAPI, Port `8001`): The Saga transaction orchestrator and event logger.
    *   `payment-service` (FastAPI, Port `8002`): Simulates payment approvals, declines, and processor delays.
    *   `notification-service` (FastAPI, Port `8003`): Delivers transaction dispatch alerts.
*   **Speaker Notes (Vietnamese)**:
    > "Để thực nghiệm, nhóm xây dựng MeshMart gồm 5 dịch vụ độc lập. Giao diện Frontend (Nginx) hiển thị sản phẩm và tích hợp bảng giám sát UI. Product Service quản lý danh mục và khóa kho; Order Service là đầu mối điều phối giao dịch; Payment Service giả lập thanh toán; và Notification Service gửi tin nhắn thông báo. Sự phân tách này tạo nên một luồng giao dịch phân tán thực tế."

---

### Slide 4: API Service Contracts & Lifecycle Probes
*   **Core Message**: Strong API contracts and Kubernetes health hooks are essential.
*   **Canva Layout**: Split-screen. Left: Stylized code editor block (Dark Gray) showing a JSON payload. Right: Clean HTTP endpoint mapping table.
*   **On-Slide Content (English)**:
    *   **API Service Contracts:**
        *   `GET /products` $\rightarrow$ List catalog & reviews.
        *   `POST /orders` $\rightarrow$ Submit checkout (requires `Idempotency-Key` header).
        *   `POST /inventory/reserve` $\rightarrow$ Lock product stock.
    *   **Self-Healing Lifecycle Probes:**
        *   `/health/live` $\rightarrow$ Liveness check (checks web server running status).
        *   `/health/ready` $\rightarrow$ Readiness check (evaluates traffic ready state).
*   **Speaker Notes (Vietnamese)**:
    > "Mọi giao tiếp đều tuân thủ hợp đồng API chặt chẽ. Đơn hàng gửi lên `/orders` bắt buộc đính kèm header Idempotency-Key. Mỗi microservice đều công khai endpoint `/health/live` để Kubernetes biết khi nào cần restart pod bị đơ, và `/health/ready` để kiểm soát xem pod đã sẵn sàng tiếp nhận người dùng hay chưa."

---

### Slide 5: System Deployment Architecture & Zero-Trust Security
*   **Core Message**: Moving encryption and security rules to the network layer (Envoy).
*   **Vivid Analogy**: **The "Secure Embassy" Protocol.** You don't verify IDs inside the office; security guards check them at the outer gates.
*   **Canva Layout**: Large display frame containing the system diagram: [system_architecture.png](file:///c:/Users/ADMIN/OneDrive/Documents/Service%20Mesh%20Observability/distributed-system-service-mesh-observability/docs/system_architecture.png) on the right. Left side contains security cards.
*   **On-Slide Content (English)**:
    *   **Unified Access**: Istio Ingress Gateway manages SSL termination and path routing.
    *   **STRICT mTLS**: Enforced namespace-wide in `meshmart`. All network packets are encrypted via Envoy sidecars.
    *   **Zero-Trust RBAC**:
        *   Unique `ServiceAccount` assigned to each microservice deployment.
        *   Granular `AuthorizationPolicy` blocks unauthorized cross-pod traffic.
*   **Speaker Notes (Vietnamese)**:
    > "Đây là kiến trúc triển khai thực tế trên Kubernetes. Điểm cốt lõi là mô hình bảo mật Zero Trust. Chúng em thiết lập chính sách STRICT mTLS mã hóa SSL 2 chiều toàn bộ kết nối giữa các pod. Đồng thời, gán các ServiceAccount riêng biệt và áp dụng AuthorizationPolicy để chỉ cho phép các cuộc gọi hợp lệ. Bất kỳ pod lạ nào gọi trực tiếp đều bị chặn đứng ở tầng proxy."

---

### Slide 6: Network Interception: The Envoy Sidecar Engine
*   **Core Message**: Transparent traffic interception without modifying application code.
*   **Canva Layout**: Diagram on the right showing inbound and outbound paths passing through the Envoy Proxy.
*   **Image Placement**: Insert the Envoy interception diagram: [envoy_sidecar_work.png](file:///c:/Users/ADMIN/OneDrive/Documents/Service%20Mesh%20Observability/distributed-system-service-mesh-observability/docs/envoy_sidecar_work.png).
*   **On-Slide Content (English)**:
    *   **iptables Redirection:**
        *   Init-container configures networking tables at startup.
        *   Redirects all inbound/outbound packets to Envoy local ports.
    *   **Inbound Flow**: Inbound $\rightarrow$ Envoy (Decrypts mTLS, checks RBAC) $\rightarrow$ App Container (localhost).
    *   **Outbound Flow**: App Container $\rightarrow$ Envoy (Injects tracing headers, applies timeouts/retries) $\rightarrow$ Outbound.
    *   **No Code Intrusion**: FastAPI application is completely unaware of Envoy's existence.
*   **Speaker Notes (Vietnamese)**:
    > "Làm thế nào Istio can thiệp mạng mà không sửa code ứng dụng? Khi khởi động, init-container thiết lập iptables để định tuyến toàn bộ lưu lượng mạng ra vào qua Envoy proxy. Khi có request tới, Envoy sẽ kiểm tra mTLS, chính sách RBAC rồi mới đẩy về ứng dụng qua localhost. Tương tự, khi ứng dụng gọi ra ngoài, Envoy sẽ tự động tiêm trace header và kiểm tra retry."

---

### Slide 7: Distributed Transactions: The Saga Orchestration Pattern
*   **Core Message**: Ensuring eventual data consistency across isolated microservice databases.
*   **Canva Layout**: Horizontal flowchart display. Top: Success flow blocks. Bottom: Compensating rollback blocks (colored in Coral Red).
*   **On-Slide Content (English)**:
    *   **The Isolation Problem**: Each microservice has an isolated database; row locks cannot cross network boundaries.
    *   **Saga Orchestration**: `order-service` coordinates sequential local transactions.
    *   **Local Transactions**: Each service commits its local database records and returns the status.
    *   **Compensating Transactions**: If a phase fails, the orchestrator triggers reverse operations to restore consistency.
*   **Speaker Notes (Vietnamese)**:
    > "Vì mỗi microservice sở hữu cơ sở dữ liệu riêng, chúng em không thể dùng database lock truyền thống để giữ tính nhất quán. Giải pháp là Saga Orchestration. Order Service đóng vai trò làm nhạc trưởng điều phối các giao dịch cục bộ tuần tự. Nếu một chặng xảy ra lỗi, nhạc trưởng sẽ phát lệnh chạy các giao dịch bù trừ để hoàn lại trạng thái cũ."

---

### Slide 8: Saga Execution: The Happy Path (Success Flow)
*   **Core Message**: Visualizing order creation and stock commit step-by-step.
*   **Canva Layout**: 2-column layout. Left: Technical sequence summary. Right: Sequence diagram: [saga_checkout_flow.png](file:///c:/Users/ADMIN/OneDrive/Documents/Service%20Mesh%20Observability/distributed-system-service-mesh-observability/docs/saga_checkout_flow.png).
*   **On-Slide Content (English)**:
    *   **Checkout Sequence:**
        1. **Idempotency Key Check**: Ensure request is not a duplicate.
        2. **Reserve Inventory**: Call `/inventory/reserve` to deduct temporary stock.
        3. **Process Payment**: Authorize credit card charge via `payment-service`.
        4. **Commit Inventory**: Permanently decrement stock via `/inventory/commit`.
        5. **Send Notification**: Trigger user alerts via `notification-service`.
*   **Speaker Notes (Vietnamese)**:
    > "Trong luồng thành công, tiến trình diễn ra lần lượt: kiểm tra tính trùng lặp đơn hàng, gửi yêu cầu khóa kho tạm thời, thanh toán thành công, gửi yêu cầu trừ kho vĩnh viễn và thông báo. Màn hình storefront hiển thị trực quan 5 chấm xanh tương ứng với 5 bước này chạy trơn tru."
*   **Interactive Tip**: **[DEMO TRIGGER 1]** Switch to the storefront UI at `http://localhost:8080`. Put an order with Payment Mode set to **Success** and expand the **Saga Accordion details** to show the 5 green dots and service latencies.

---

### Slide 9: Saga Compensation: The Rollback Path (Failure Flow)
*   **Core Message**: Recovering from payment failures to avoid inventory leakage.
*   **Canva Layout**: Red-themed alert layout. Left: Bullet points explaining rollback logic. Right: Screenshot of the storefront UI showing the red rollback timeline.
*   **On-Slide Content (English)**:
    *   **The Consistency Challenge:**
        *   Stock was locked, but card was declined. Catalog must not leak items.
    *   **Automatic Rollback Execution:**
        *   Orchestrator catches `payment_failed` status.
        *   Triggers compensation call to `/inventory/release`.
        *   Product Service credits stock back to the catalog.
        *   **Saga UI Alert**: Timeline step turns red, showing `inventory_released`.
*   **Speaker Notes (Vietnamese)**:
    > "Nếu thanh toán thất bại, hệ thống không thể khóa hàng vô lý. Nhạc trưởng Saga lập tức kích hoạt luồng bù trừ là gọi `/inventory/release` để hoàn lại số lượng hàng đã giữ. Trên storefront, các bước giữ kho ban đầu hiển thị màu xanh, nhưng bước thanh toán lỗi và bước giải phóng kho sẽ hiển thị màu đỏ để chứng minh hệ thống đã rollback an toàn."
*   **Interactive Tip**: **[DEMO TRIGGER 2]** On the storefront UI, set Payment Mode to **Failed** and click Checkout. Expand the newly created failed order to show the red dots indicating the rollback step.

---

### Slide 10: Transaction Protection: Idempotency Key Guard
*   **Core Message**: Preventing double-billing and duplicate order creation.
*   **Canva Layout**: Infographic style. Top: Client clicks buy button twice due to connection drop. Middle: Cache verification grid. Bottom: Returns cached order log.
*   **On-Slide Content (English)**:
    *   **The Network Timeout Hazard:**
        *   Payment succeeds but network drops before client receives confirmation.
        *   Client retries payment request $\rightarrow$ causes double-billing.
    *   **Idempotency Engine (`_idempotency_store`):**
        *   Stores `Idempotency-Key` headers mapped to cached responses.
        *   **Payload Fingerprinting**: Verifies retry payload matches the original.
        *   **Conflict Prevention**: Returns `409 Conflict` if request is currently processing.
*   **Speaker Notes (Vietnamese)**:
    > "Khi mạng bị rớt giữa chừng, client sẽ tự động gửi lại đơn hàng. Để tránh việc trừ tiền hai lần, chúng em bắt buộc header Idempotency-Key. Order Service lưu cache trạng thái đơn hàng. Nếu nhận request trùng key, nó sẽ trả về ngay kết quả trong cache mà không gọi xuống Payment hay Product Service, bảo vệ giao dịch của khách hàng tuyệt đối."

---

### Slide 11: Edge Traffic Control: Ingress Gateway & Path Routing
*   **Core Message**: Single public interface routing traffic dynamically to cluster services.
*   **Canva Layout**: Insert the traffic diagram: [traffic_management.png](file:///c:/Users/ADMIN/OneDrive/Documents/Service%20Mesh%20Observability/distributed-system-service-mesh-observability/docs/traffic_management.png) on the right. Left side lists prefix mappings.
*   **On-Slide Content (English)**:
    *   **unified Cổng vào**: Single public port avoids exposing internal microservice ports.
    *   **VirtualService Route Mapping:**
        *   `/` $\rightarrow$ Route to `frontend` (Nginx UI)
        *   `/products` $\rightarrow$ Route to `product-service`
        *   `/orders` $\rightarrow$ Route to `order-service`
    *   **Security & Decoupling**: Hides structural architecture from the public internet.
*   **Speaker Notes (Vietnamese)**:
    > "Tại cổng vào hệ thống, Istio Ingress Gateway chịu trách nhiệm tiếp nhận lưu lượng và định tuyến dựa trên đường dẫn URL: `/` đi vào Frontend, `/products` sang Product Service, `/orders` sang Order Service. Điều này giúp ẩn đi cấu trúc port phức tạp bên trong cluster, cung cấp một cổng giao tiếp duy nhất an toàn."

---

### Slide 12: Network Resiliency: Retries & Timeouts
*   **Core Message**: Utilizing sidecars to handle timeouts and retries at the network layer.
*   **Canva Layout**: 2-column layout. Column 1: **Timeout Settings**. Column 2: **Retry settings**.
*   **On-Slide Content (English)**:
    *   **Timeout Limits (Fail Fast):**
        *   `order-service` $\rightarrow$ **8s** timeout limit.
        *   `product-service` $\rightarrow$ **4s** timeout limit.
        *   `payment-service` $\rightarrow$ **3s** Ingress timeout.
        *   Protects server threads from getting locked up by slow dependencies.
    *   **Automatic Retries (Self-Healing):**
        *   **2 retry attempts** configured in VirtualService.
        *   Triggers on `connect-failure`, `5xx` errors.
*   **Speaker Notes (Vietnamese)**:
    > "Thời gian phản hồi chậm có thể gây nghẽn luồng. Chúng em cấu hình timeout 8 giây cho Order Service và 3 giây cho Payment Service tại tầng Envoy proxy. Ngoài ra, thiết lập cơ chế 2 lần retry cho các lỗi kết nối tạm thời. Điều này giúp ứng dụng tự phục hồi trước các sự cố mạng chớp nhoáng mà không làm sập luồng nghiệp vụ."

---

### Slide 13: Chaos Engineering: Fault Injection
*   **Core Message**: Intentionally injecting faults in staging to verify timeout resilience.
*   **Canva Layout**: Neon design style featuring a lightning bolt. Shows a sample YAML configuration of the fault injection policy.
*   **On-Slide Content (English)**:
    *   **Istio Fault Injection Policy:**
        *   Configured in `istio/payment-fault-injection.yaml`.
        *   Target: `payment-service` traffic.
        *   Fault Type: **Delay**
        *   Percentage: **30% of requests**
        *   Delay Value: **2s fixed delay**
    *   **Validation Goal**: Confirms that orchestrator timeout triggers and Saga rollbacks execute gracefully when network links degrade.
*   **Speaker Notes (Vietnamese)**:
    > "Để kiểm chứng khả năng chịu tải, chúng em áp dụng Chaos Engineering bằng cách cấu hình Fault Injection của Istio: trì hoãn kết nối 2 giây cho 30% request đến Payment Service. Điều này giúp chúng em kiểm chứng xem hệ thống Order Service có kích hoạt timeout và rollback kho đúng như thiết kế hay không."
*   **Interactive Tip**: **[DEMO TRIGGER 3]** Open browser at `http://localhost:8080`, click Checkout with payment mode set to **Success** multiple times. Due to chaos, some requests will take longer, proving the 2s injected delay.

---

### Slide 14: Resource Protection: Connection Pools & Circuit Breaking
*   **Core Message**: Protecting services from traffic surges and cascading replica crashes.
*   **Vivid Analogy**: **The "Safety Fuse" Grid.** If an appliance short-circuits, the fuse blows, shutting down power to that appliance to protect the whole house.
*   **Canva Layout**: Split-screen. Left Card: **Connection Pooling**. Right Card: **Outlier Detection (Circuit Breaking)**.
*   **On-Slide Content (English)**:
    *   **DestinationRule Connection Pools (Rate Capping):**
        *   `payment-service`: Max **20** TCP connections.
        *   `product-service`: Max **50** TCP connections.
        *   Envoy queues overflow traffic to prevent server memory saturation.
    *   **Outlier Detection (Circuit Breaking):**
        *   Monitor consecutive errors.
        *   Ejection: If replica pod returns **3 consecutive 5xx errors in 10s**, it is ejected from the load-balancer pool for **30s**.
*   **Speaker Notes (Vietnamese)**:
    > "DestinationRules giúp chúng em giới hạn TCP connection pool. Ví dụ, giới hạn tối đa 20 kết nối đồng thời cho Payment Service, các request vượt ngưỡng sẽ được xếp hàng thay vì làm sập ứng dụng. Circuit Breaking được triển khai qua Outlier Detection: tự động loại bỏ các pod replica bị lỗi 3 lần liên tiếp ra khỏi pool trong 30 giây để pod tự phục hồi."

---

### Slide 15: Full-Stack Observability Pipeline
*   **Core Message**: Correlating metrics, traces, and structured logs to isolate failures.
*   **Canva Layout**: Large central diagram: [observability_data_flow.png](file:///c:/Users/ADMIN/OneDrive/Documents/Service Mesh Observability/distributed-system-service-mesh-observability/docs/observability_data_flow.png) on the right. Left lists the telemetry stack.
*   **On-Slide Content (English)**:
    *   **Prometheus**: Polls Envoy sidecars and custom Python endpoints (`/metrics`) every 15s.
    *   **Grafana Dashboard**: Auto-provisions our custom **16-panel MeshMart dashboard** on startup (RPS, Latency p50/p95/p99, Stock levels).
    *   **Jaeger**: Captures span spans propagating W3C trace headers.
    *   **JSON Structured Logs**: Structures Python application logs for easy querying by `request_id` or `duration_ms`.
*   **Speaker Notes (Vietnamese)**:
    > "Hệ thống giám sát (Observability) của chúng em được tối ưu ở cả 3 trụ cột: Prometheus gom metrics; Grafana nạp sẵn dashboard 16 panel chi tiết; Jaeger vẽ vết trace của request; và toàn bộ log ứng dụng đã được chuẩn hóa sang định dạng JSON có cấu trúc. Quy trình chẩn đoán lỗi khi có sự cố rất mạch lạc: Grafana báo động -> Kiali khoanh vùng -> Jaeger định vị -> Log JSON tìm nguyên nhân."
*   **Interactive Tip**: **[DEMO TRIGGER 4]** Switch to terminal and run `docker compose logs order-service --tail 10` to show the JSON logging. Then switch to Grafana dashboard (`:3000`) and Jaeger UI (`:16686`) to show the metrics and traces.

---

### Slide 16: Completed Achievements, Project Boundaries, and Key Learnings
*   **Core Message**: Core features are successfully implemented and ready for cloud operations.
*   **Canva Layout**: 2-column checklist. Left: **Completed Achievements**. Right: **Production Roadmap (Future Work)**.
*   **On-Slide Content (English)**:
    *   **Completed Achievements:**
        *   STRICT mTLS encryption & Zero-Trust Authorization Policies.
        *   Saga transaction orchestrator & Storefront Timeline UI.
        *   Dynamic health check probes with dependency monitoring.
        *   JSON Structured logs & 16-panel Grafana Dashboard.
    *   **Production Roadmap (Future Work):**
        *   Migrate in-memory lists to persistent databases (PostgreSQL/MySQL).
        *   Use shared Redis cluster for Idempotency Cache.
        *   Enable JSON Web Token (JWT) request authentication at Gateway.
*   **Speaker Notes (Vietnamese)**:
    > "Tóm lại, dự án đã triển khai thành công bảo mật mTLS/RBAC, điều phối Saga với UI trực quan, đầu dò sức khỏe động và hệ thống giám sát tự động. Lộ trình phát triển tiếp theo của nhóm là đưa vào database thực tế (Postgres), dùng Redis làm shared cache cho Idempotency và xác thực JWT tại Gateway. Nhóm xin chân thành cảm ơn thầy cô và các bạn đã lắng nghe!"
*   **Interactive Tip**: **[DEMO TRIGGER 5]** Show the dynamic readiness check: run `curl http://localhost:8001/health/ready` (returns ready), then stop product service `docker compose stop product-service`, run the curl again (returns unhealthy 503), then restart it. This provides a strong visual ending to your demo.

---

## 💡 Quick Tips for a Flawless Presentation
1.  **Browser Setup**: Have three tabs open before you start:
    *   Tab 1: `http://localhost:8080` (Storefront UI)
    *   Tab 2: `http://localhost:3000` (Grafana Dashboard)
    *   Tab 3: `http://localhost:16686` (Jaeger UI - if running K8s/Istio env)
2.  **Terminal Setup**: Keep a terminal window open in the background pre-typed with the logs command:
    `docker compose logs order-service --tail 10`
3.  **Timing**: Allocate about 30-40 seconds per slide. Keep the transitions between slides and demo screens quick and smooth.
