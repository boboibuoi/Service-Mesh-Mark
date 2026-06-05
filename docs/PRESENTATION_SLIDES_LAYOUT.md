# MeshMart: English Slides Layout & Visual Design Guide

This guide provides a detailed, visually engaging layout for a **16-slide presentation deck** in English. Each slide is designed to be highly readable, interesting, and easy to build in Canva or PowerPoint, with specific placeholders for diagrams and UI screenshots.

---

## 🎨 Global Design Theme (For Canva Consistency)
*   **Background**: Deep Dark Space / Navy (`#0F172A`).
*   **Fonts**: Header: *Montserrat* or *League Spartan* (Bold, 36pt+). Body: *Inter* or *Segoe UI* (Clean, 14pt-16pt).
*   **Color Accents**:
    *   **Bright White** (`#FFFFFF`) for main text.
    *   **Neon Purple/Pink** (`#C084FC` / `#F472B6`) for technical keywords and Istio policies.
    *   **Mint Green** (`#34D399`) for successes and healthy nodes.
    *   **Coral Red** (`#F87171`) for rollbacks, failures, and circuit breaking.

---

## Slide 1: Cover (The Title Slide)
*   **Visual Layout**: Minimalist centered layout. Dark slate background. Add an abstract glowing network mesh graphic in the background with 30% opacity.
*   **Slide Content (English)**:
    *   **Main Title (Montserrat, 44pt)**: Service Mesh & Full-Stack Observability
    *   **Subtitle (Inter, 20pt, Light Purple)**: MeshMart: Securing, Operating, and Monitoring Distributed Microservices on Kubernetes
    *   **Presenter Info (14pt, White)**: [Your Names] | Distributed Systems Course Project
*   **Speaker Notes (Vietnamese)**:
    > *"Chào các thầy cô và các bạn. Hôm nay nhóm em xin trình bày đồ án 'Service Mesh & Full-Stack Observability'. Chúng em xây dựng một hệ thống microservices thương mại điện tử thực tế tên là MeshMart, từ đó áp dụng Istio Service Mesh và bộ công cụ Prometheus, Grafana, Jaeger, Kiali để quản lý và giám sát hệ thống phân tán."*

---

## Slide 2: The Monolith to Microservices Paradox (Problem Statement)
*   **Visual Layout**: 2-column split-screen layout.
    *   *Left Box*: **Monolith** (1 block, green in-memory call arrows - simple).
    *   *Right Box*: **Microservices** (5 blocks, chaotic red network arrows representing latencies, timeout, and connection drops).
*   **Slide Content (English)**:
    *   **The In-Memory vs. Network Hops:**
        *   Monoliths communicate safely inside RAM.
        *   Microservices talk over unstable network boundaries (HTTP/gRPC).
    *   **The Critical Pain Points:**
        *   **Cascading Latency**: One slow service freezes the entire client request.
        *   **Operational Blindspots**: Hard to pinpoint which microservice failed.
        *   **Code Pollution**: Writing retries, timeouts, and security policies inside every service clutters business logic.
*   **Speaker Notes (Vietnamese)**:
    > *"Slide này nói về lý do chúng ta cần Service Mesh. Khi chuyển từ Monolith sang Microservices, ta đổi lời gọi hàm trong RAM lấy các kết nối mạng HTTP vốn chập chập và không ổn định. Một dịch vụ phản hồi chậm có thể gây nghẽn toàn bộ hệ thống (cascading latency). Việc tự viết code retry hay timeout trong từng service khiến code nghiệp vụ rất rối."*

---

## Slide 3: MeshMart Scope & Component Boundaries
*   **Visual Layout**: Horizontal grid of 5 cards, each with an icon (Nginx server, Shopping Cart, Database, Credit Card, Mail Envelope).
*   **Image Suggestion**: Insert the architecture diagram: `docs/architecture-diagram.png` in the center.
*   **Slide Content (English)**:
    *   `frontend` (Nginx): Serves static SPA UI and proxying endpoints. Tightly integrated with the new **Observability UI Details Panel**.
    *   `product-service` (FastAPI): Manages catalog database, reviews, and stock locks.
    *   `order-service` (FastAPI): Acts as the Saga orchestrator and transaction log coordinator.
    *   `payment-service` (FastAPI): Simulates bank payments (Success, Declined, Slow modes).
    *   `notification-service` (FastAPI): Asynchronously delivers transaction dispatch alerts.
*   **Speaker Notes (Vietnamese)**:
    > *"Đây là ranh giới các dịch vụ của MeshMart. Hệ thống gồm 5 microservices độc lập viết bằng Python FastAPI và Nginx. Frontend đã được nhóm tích hợp bảng điều khiển giám sát trực quan (Saga UI). Order Service đóng vai trò là Orchestrator quản lý luồng giao dịch, kết nối tới Product để khóa kho, Payment để trả tiền và Notification để báo tin."*

---

## Slide 4: Zero-Trust Security Architecture
*   **Visual Layout**: Sleek 2-column card layout with security locks icons.
    *   *Left Card (mTLS)*: Deep Navy with a glowing green shield.
    *   *Right Card (RBAC)*: Deep Navy with a glowing purple key.
*   **Slide Content (English)**:
    *   **STRICT Mutual TLS (mTLS):**
        *   Enforced namespace-wide in `meshmart` via `PeerAuthentication`.
        *   Envoy sidecars encrypt all traffic automatically. Plain HTTP requests are dropped.
    *   **Least-Privilege Authorization (RBAC):**
        *   Each deployment has a unique, dedicated K8s `ServiceAccount`.
        *   Granular `AuthorizationPolicy` rules restrict access paths (e.g., only `order-service` is authorized to talk to backends. Unregistered pods are rejected).
*   **Speaker Notes (Vietnamese)**:
    > *"Về khía cạnh bảo mật, hệ thống áp dụng mô hình Zero-Trust thực thụ. Chúng em thiết lập chính sách STRICT mTLS trên toàn bộ namespace. Mọi kết nối không mã hóa đều bị Envoy chặn đứng. Đồng thời, chúng em gán các ServiceAccount định danh cho từng service và cấu hình các AuthorizationPolicy chặt chẽ. Nếu một pod lạ trong cluster tìm cách truy cập trái phép, Envoy sẽ trả về lỗi RBAC access denied ngay lập tức."*

---

## Slide 5: Network Interception: How Envoy Sidecars Work
*   **Visual Layout**: Centered high-contrast diagram.
*   **Image Suggestion**: Insert `docs/envoy_sidecar_work.png` on the right side.
*   **Slide Content (English)**:
    *   **Transparent Redirection (iptables):**
        *   An init-container configures iptables rules inside the pod namespace.
        *   No application code modifications are required.
    *   **Inbound Interception**: Client $\rightarrow$ Envoy (Decrypts mTLS, validates RBAC) $\rightarrow$ FastAPI app (localhost).
    *   **Outbound Interception**: FastAPI app $\rightarrow$ Envoy (Injects trace headers, evaluates timeout/retry rules) $\rightarrow$ Target pod.
*   **Speaker Notes (Vietnamese)**:
    > *"Làm thế nào Envoy sidecar can thiệp mạng mà không cần sửa code ứng dụng? Khi Pod khởi động, iptables định tuyến toàn bộ traffic đi vào và đi ra qua Envoy. Envoy sẽ giải mã, kiểm tra policy bảo mật trước khi đưa vào ứng dụng qua localhost, đồng thời tự động tiêm trace header và kiểm tra retry khi gọi dịch vụ con."*

---

## Slide 6: Distributed Transactions: The Saga Pattern
*   **Visual Layout**: Horizontal step flowchart showing the flow of request messages across services.
*   **Image Suggestion**: Insert `docs/saga_checkout_flow.png` in the center.
*   **Slide Content (English)**:
    *   **The Database Lock Problem:**
        *   ACID transactions cannot span database boundaries safely in microservices.
        *   Row-locking over network calls blocks resources and degrades scaling.
    *   **Saga Orchestration solution:**
        *   `order-service` executes local transactions sequentially.
        *   Maintains eventual consistency across databases.
        *   Triggers **Compensating Transactions** (undo actions) if a phase fails.
*   **Speaker Notes (Vietnamese)**:
    > *"Trong microservices, ta không thể dùng transaction database thông thường để khóa bảng dữ liệu vì mỗi dịch vụ dùng một database riêng. Nhóm áp dụng mẫu thiết kế Saga Orchestration. Order Service đóng vai trò là nhạc trưởng điều phối. Nó ra lệnh cho các service thực hiện giao dịch cục bộ và lưu lại vết. Nếu phát hiện bất kỳ bước nào lỗi, nhạc trưởng sẽ kích hoạt luồng bù trừ để khôi phục trạng thái hệ thống, giữ cho dữ liệu luôn nhất quán."*

---

## Slide 7: Saga Orchestration: The Success Path (Happy Path)
*   **Visual Layout**: 2-column layout.
    *   *Left Box*: Flow summary list.
    *   *Right Box*: Clean screenshot of the **Saga Accordion UI** displaying 5 green dots.
*   **Slide Content (English)**:
    *   **Sequential Success Hops:**
        1. **Check Idempotency**: Verify if `Idempotency-Key` was processed.
        2. **Reserve Inventory**: Product Service locks stock in-memory (`/inventory/reserve`).
        3. **Process Payment**: Charge card via Payment Service (`/payments` $\rightarrow$ `success`).
        4. **Commit Inventory**: Confirm permanent stock reduction (`/inventory/commit`).
        5. **Send Notification**: Deliver success alerts to client.
*   **Speaker Notes (Vietnamese)**:
    > *"Trong luồng thành công, tiến trình Saga diễn ra lần lượt: Kiểm tra trùng lặp đơn hàng, giữ kho tạm thời qua Product Service, thanh toán thành công, gửi lệnh trừ kho vĩnh viễn và thông báo hoàn tất. Storefront của chúng em thể hiện trực quan 5 dấu chấm tròn màu xanh đại diện cho các bước này."*

---

## Slide 8: Saga Orchestration: Compensation & Rollbacks (Failure Path)
*   **Visual Layout**: Contrast layout using red/orange alert tones.
    *   *Left Box*: Rollback steps list.
    *   *Right Box*: Screenshot of the **Saga Accordion UI** displaying red indicators and the rollback step.
*   **Slide Content (English)**:
    *   **The Rollback Flow:**
        *   **Problem**: Stock reserved successfully, but payment is declined (`failed`).
        *   **Compensating Step**: The orchestrator catches the failure and calls `/inventory/release`.
        *   **Outcome**: Stock is released back to the catalog. No database drift or locked items.
        *   **Visual Evidence**: Storefront timeline displays the failed payment and rollback phases in red.
*   **Speaker Notes (Vietnamese)**:
    > *"Nếu thanh toán thất bại, hệ thống không thể để sản phẩm bị khóa mãi. Nhạc trưởng Saga sẽ tự động gọi luồng bù trừ là release kho. Số lượng tồn kho ban đầu được khôi phục nguyên vẹn. Trên giao diện storefront, các bước lỗi và bù trừ được báo đỏ trực quan, chứng minh dữ liệu được giữ nhất quán tự động."*

---

## Slide 9: Saga Observability: Event Timeline & Latency UI
*   **Visual Layout**: Split layout.
    *   *Left*: Zoomed-in screenshot of the expanded order panel showing **Service Latency** grid.
    *   *Right*: Zoomed-in screenshot of the **Order Events Timeline** details.
*   **Slide Content (English)**:
    *   **Storefront Observability Integration:**
        *   No need to log in to dashboards to verify transaction steps.
        *   **Service Latency**: Renders response duration (in ms) of each microservice step.
        *   **Event Log**: Exposes millisecond-precision event status:
            *   `order_created` $\rightarrow$ `inventory_reserved` $\rightarrow$ `payment_processed`...
        *   Improves operational debugging directly from the user application.
*   **Speaker Notes (Vietnamese)**:
    > *"Đây là cải tiến lớn về UI. Chúng em thiết kế bảng Observability UI trực tiếp trên ứng dụng. Người vận hành chỉ cần bấm vào đơn hàng là xem được thời gian xử lý thực tế của từng microservice bằng mili-giây và xem được chính xác lịch sử từng bước Saga, giúp việc gỡ lỗi hệ thống phân tán trở nên vô cùng đơn giản."*

---

## Slide 10: Idempotency Guard (Preventing Double Billing)
*   **Visual Layout**: Horizontal diagram. On the left: Client double-clicks buy button. Middle: `order-service` cache check. Right: Returns cached confirmation response directly.
*   **Slide Content (English)**:
    *   **The Network Retry Risk:**
        *   Timeout happens after charging card. Client retries request, causing double charge.
    *   **Idempotency Cache Mechanism:**
        *   Require header `Idempotency-Key` on checkout.
        *   Cache key mapping to responses in memory.
        *   If key exists: Return cached response immediately without calling payment/product again.
        *   If processing: Return `409 Conflict`.
*   **Speaker Notes (Vietnamese)**:
    > *"Slide này nói về cơ chế chống trùng lặp đơn hàng. Mạng chập chờn có thể khiến client tự động gửi lại đơn hàng, hoặc khách hàng bấm đúp nút mua. Nhờ header Idempotency-Key, hệ thống kiểm tra cache. Nếu phát hiện key trùng lặp đã xử lý xong, nó trả về ngay đơn hàng cũ mà không gọi lại Payment, bảo vệ khách hàng khỏi bị trừ tiền 2 lần."*

---

## Slide 11: Istio Ingress Gateway & Path-Based Routing
*   **Visual Layout**: Two-side comparison layout.
    *   *Left Side*: Clean table of path rules.
    *   *Right Side*: Insert the traffic management diagram `docs/traffic_management.png`.
*   **Slide Content (English)**:
    *   **Unified Client Entry Point:**
        *   Public clients hit a single host port (Gateway).
    *   **Path-Based Routing Rules (VirtualService):**
        *   `/` $\rightarrow$ `frontend` (Nginx UI)
        *   `/products` $\rightarrow$ `product-service`
        *   `/orders` $\rightarrow$ `order-service`
    *   **Infrastructure Isolation**: Service ports are hidden inside the private cluster.
*   **Speaker Notes (Vietnamese)**:
    > *"Tại cổng vào cluster, Istio Ingress Gateway kết hợp VirtualService giúp định tuyến dựa trên đường dẫn URL. Khách hàng chỉ truy cập qua một cổng duy nhất. Đường dẫn `/` đi vào Frontend, `/products` vào Product Service, `/orders` vào Order Service. Các port nội bộ được ẩn hoàn toàn để bảo vệ hệ thống."*

---

## Slide 12: Traffic Control: Timeouts & Retries
*   **Visual Layout**: Side-by-side cards.
    *   *Card 1 (Timeouts)*: Glowing clock icon.
    *   *Card 2 (Retries)*: Glowing retry circle icon.
*   **Slide Content (English)**:
    *   **Proxy-Level Timeout Enforcements:**
        *   `order-service` $\rightarrow$ **8s** timeout limit.
        *   `payment-service` $\rightarrow$ **3s** Ingress timeout.
        *   Prevents hung downstream connection threads from blocking server queues.
    *   **Automatic Retries:**
        *   **2 retry attempts** configured in Envoy.
        *   Triggers on `5xx`, `connect-failure`, `refused-stream`.
        *   Envoy transparently resolves transient network glitches.
*   **Speaker Notes (Vietnamese)**:
    > *"Chúng em cấu hình Timeout và Retry ở tầng mạng. Chúng em đặt timeout 3 giây cho Payment Service. Nếu cổng thanh toán phản hồi chậm hơn 3 giây, Envoy sẽ ngắt kết nối để giải phóng luồng. Ngoài ra, Envoy tự động retry 2 lần khi kết nối lỗi chập chớp, giúp ứng dụng tự phục hồi trước các sự cố mạng chớp nhoáng."*

---

## Slide 13: Resiliency Testing: Fault Injection & Circuit Breaking
*   **Visual Layout**: 2-column grid. Left card: **Fault Injection**. Right card: **Circuit Breaking**.
*   **Slide Content (English)**:
    *   **Chaos Testing (Fault Injection):**
        *   Target: `payment-service` calls.
        *   Policy: **2s delay** applied to **30% of requests**.
        *   Purpose: Verify order-service resilience under latency.
    *   **Self-Healing (Circuit Breaking):**
        *   Outlier Detection: Monitor HTTP `5xx` errors.
        *   Ejection: If replica pod returns **3 consecutive 5xx errors**, Envoy ejects it from load-balancer pool for **30 seconds**.
*   **Speaker Notes (Vietnamese)**:
    > *"Chúng em thử nghiệm Chaos Engineering bằng cách tiêm trễ 2 giây vào 30% kết nối đến Payment Service để test độ ổn định của hệ thống. Đồng thời, cấu hình ngắt mạch Circuit Breaking bằng Outlier Detection. Nếu một pod của một service bị lỗi 3 lần liên tiếp trong 10 giây, Envoy sẽ tạm thời loại nó khỏi danh sách định tuyến trong 30 giây để nó tự phục hồi."*

---

## Slide 14: High Availability: Probes with Deep Dependency Checks
*   **Visual Layout**: Centered flow diagram showing `Kubernetes Control Plane` querying `/health/ready` of `order-service` which sends sub-checks to `product-service` and `payment-service`.
*   **Slide Content (English)**:
    *   **Liveness Probe (`/health/live`):**
        *   Simple health response checking web server execution.
    *   **Readiness Probe (`/health/ready`):**
        *   **Deep Dependency Check**: `order-service` queries downstream services before reporting ready.
        *   **Self-Healing Impact**: If a downstream service is down, `order-service` responds with **HTTP 503 Unhealthy**. Kubernetes stops sending ingress traffic to this pod.
*   **Speaker Notes (Vietnamese)**:
    > *"Để đảm bảo tính sẵn sàng cao, chúng em phát triển Readiness Probe kiểm tra sâu. Khi Kubernetes hỏi thăm `/health/ready` của Order Service, nó sẽ chủ động gửi request test kết nối tới các dịch vụ con. Nếu một dịch vụ con sập, Order Service sẽ báo Unhealthy 503 để Kubernetes ngắt traffic vào nó, tránh xảy ra lỗi đơn hàng."*

---

## Slide 15: Full-Stack Observability Pipeline
*   **Visual Layout**: Sleek grid displaying 4 tools screenshots.
*   **Image Suggestion**: Insert `docs/observability_data_flow.png` in the center.
*   **Slide Content (English)**:
    *   **Prometheus**: Scrapes application and Envoy metrics every 15s.
    *   **Grafana**: Displays auto-provisioned 16-panel business and network dashboards.
    *   **Jaeger**: Traces distributed spans to map request paths.
    *   **Kiali**: Renders real-time topology graphs of the service mesh.
    *   **Structured Logs**: JSON logs capture error contexts easily.
*   **Speaker Notes (Vietnamese)**:
    > *"Hệ thống Observability giám sát toàn diện cả hạ tầng lẫn ứng dụng. Prometheus tự động gom metrics; Grafana vẽ biểu đồ 16 panel chi tiết; Jaeger vẽ vết trace của request qua các chặng microservice; Kiali vẽ sơ đồ mạng thời gian thực; và Logs được chuẩn hóa JSON để phục vụ điều tra lỗi."*

---

## Slide 16: Achievements & Production Roadmap (Conclusion)
*   **Visual Layout**: Clean 2-column checklist layout.
    *   *Left Box*: **Completed Work** (Green icons).
    *   *Right Box*: **Production Roadmap** (Purple icons).
*   **Slide Content (English)**:
    *   **Completed Work:**
        *   STRICT mTLS encryption & Zero-Trust Authorization Policies.
        *   Saga transaction orchestrator & Storefront Timeline UI.
        *   Dynamic health check probes with dependency monitoring.
        *   JSON Structured logs & 16-panel Grafana Dashboard.
    *   **Production Roadmap:**
        *   Migrate in-memory lists to persistent databases (PostgreSQL/MySQL).
        *   Use shared Redis cluster for Idempotency Cache.
        *   Enable JSON Web Token (JWT) request authentication at Gateway.
*   **Speaker Notes (Vietnamese)**:
    > *"Tóm lại, dự án đã triển khai thành công bảo mật mTLS/RBAC, điều phối Saga với UI trực quan, đầu dò sức khỏe động và hệ thống giám sát tự động. Lộ trình phát triển tiếp theo của nhóm là đưa vào database thực tế (Postgres), dùng Redis làm shared cache cho Idempotency và xác thực JWT tại Gateway. Nhóm xin chân thành cảm ơn thầy cô và các bạn đã lắng nghe!"*
