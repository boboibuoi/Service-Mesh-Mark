# MeshMart: Tài liệu Thuyết trình & Hướng dẫn Chạy Demo Chi tiết (20 Slides)

Tài liệu này đồng bộ hóa hoàn toàn nội dung thuyết trình (Speaker Script tiếng Việt) của **20 slide** từ slide blueprint (`docs/PRESENTATION_CONTENT_GUIDE.md`) với **Kịch bản chạy Demo trực tiếp (Live Demo Runbook)**. 

Tài liệu giúp bạn có một buổi thuyết trình mượt mà, kết hợp nhịp nhàng giữa việc chiếu Slide và chuyển sang Terminal/Trình duyệt để biểu diễn thực tế các tính năng nâng cao đã hoàn thiện trong dự án: **Saga Timeline UI, STRICT mTLS & RBAC, JSON Structured Logging, Prometheus/Grafana, Fault Injection và Kubernetes Health Probes**.

---

## 🗺️ Bản đồ Phối hợp Slide và Demo Trực tiếp

Để buổi thuyết trình đạt hiệu quả cao nhất, hãy tham khảo bản đồ phối hợp sau:

| Giai đoạn thuyết trình | Slide hiển thị | Hành động Demo trực tiếp | Giao diện/Lệnh cần hiển thị |
| :--- | :--- | :--- | :--- |
| **Phần 1: Giới thiệu hệ thống** | Slide 1 ➔ Slide 4 | Thuyết trình lý thuyết lý do chuyển đổi Monolith sang Microservices và giới thiệu MeshMart APIs. | Slide chiếu màn hình chính. |
| **Phần 2: Kiến trúc & Bảo mật** | Slide 5 ➔ Slide 6 | Thuyết trình về Kiến trúc Mesh, STRICT mTLS và Phân quyền RBAC. | Slide và hình ảnh [architecture-diagram.png](file:///c:/Users/ADMIN/OneDrive/Documents/Service%20Mesh%20Observability/distributed-system-service-mesh-observability/docs/architecture-diagram.png). |
| **Phần 3: Saga Transaction** | Slide 7 | Giới thiệu cơ chế điều phối giao dịch phân tán Saga. | Giải thích lý thuyết. |
| **Phần 4: Demo Saga Happy Path** | Slide 8 | **Demo 1: Tạo đơn hàng thành công** | Trình duyệt `http://localhost:8080` ➔ Đặt hàng ➔ Xem **Saga Accordion UI** (5 chấm xanh). |
| **Phần 5: Demo Saga Compensation** | Slide 9 | **Demo 2: Tạo đơn hàng lỗi (Thanh toán thất bại)** | Đổi Payment sang **Failed** ➔ Xem **Saga Rollback UI** (bước release màu đỏ). |
| **Phần 6: Demo Idempotency** | Slide 10 | **Demo 3: Chống trùng lặp đơn hàng** | Gửi trùng `Idempotency-Key` qua Postman/Curl hoặc giải thích cơ chế. |
| **Phần 7: Ingress & Traffic** | Slide 11 ➔ Slide 12 | Thuyết trình cơ chế định tuyến Ingress, Timeout & Retry của Envoy. | Giải thích cấu hình YAML. |
| **Phần 8: Chaos & Faults** | Slide 13 ➔ Slide 15 | **Demo 4: Thử nghiệm Timeout/Chaos** | Kích hoạt Payment **Slow** ➔ Xem UI/Envoy trả về lỗi timeout và cơ chế bảo vệ. |
| **Phần 9: Observability** | Slide 16 ➔ Slide 17 | **Demo 5: Giám sát telemetry toàn diện** | Mở Grafana Dashboard (`:3000`), Jaeger (`:16686`), Kiali (`:20001`) và chạy lệnh log JSON của `order-service` trên Terminal. |
| **Phần 10: HA & Sẵn sàng** | Slide 18 | **Demo 6: Health Probes với Dynamic Dependency Check** | Gọi `/health/ready` của `order-service` khi tắt service con để chứng minh self-healing. |
| **Phần 11: Tổng kết** | Slide 19 ➔ Slide 20 | Tổng kết thành quả đạt được và định hướng tương lai. | Slide chiếu màn hình chính. |

---

## 🎤 Kịch bản Thuyết trình Chi tiết & Slides Content (20 Slides)

### Slide 1: Cover (Tiêu đề dự án)
*   **Nội dung Slide**:
    *   **Tiêu đề chính**: Service Mesh & Observability cho Kiến trúc Microservices
    *   **Tiêu đề phụ**: MeshMart: Quản lý lưu lượng, Thử nghiệm chịu lỗi, Bảo mật Zero-Trust và Giám sát Telemetry trên Kubernetes
    *   **Người trình bày**: [Tên của bạn/Nhóm] | Đồ án môn học Hệ thống phân tán
*   **Lời thoại của bạn**:
    > "Xin kính chào các thầy cô và các bạn. Hôm nay nhóm chúng em xin phép trình bày dự án kết thúc môn học với đề tài: 'Service Mesh và Observability cho Microservices'. Với mô hình thực nghiệm là hệ thống e-commerce mang tên MeshMart chạy trên nền tảng Kubernetes và Istio Service Mesh, dự án tập trung giải quyết các bài toán hóc búa về quản lý giao dịch phân tán, kiểm soát lưu lượng, bảo mật Zero-Trust và giám sát telemetry toàn diện."

---

### Slide 2: The Monolith to Microservices Paradox (Bất cập khi chuyển dịch Microservices)
*   **Nội dung Slide**:
    *   **Monolith**: Gọi hàm trong bộ nhớ (In-memory), dễ quản lý nhưng khó scale, dễ sập toàn bộ hệ thống.
    *   **Microservices**: Tách biệt nghiệp vụ độc lập, nhưng giới thiệu ranh giới mạng (Network Boundary).
    *   **Hệ quả mạng**: Trễ mạng (Latency), mất kết nối (Packet loss), lỗi cascade (sụp đổ dây chuyền).
    *   **Code Clutter**: Việc viết code retry, timeout thủ công trong từng ứng dụng gây trùng lặp và khó bảo trì.
*   **Lời thoại của bạn**:
    > "Khi chuyển đổi từ kiến trúc Monolith sang Microservices, chúng ta giải quyết được bài toán chia tách hệ thống để phát triển độc lập, nhưng lại vướng phải ranh giới truyền thông mạng. Các lời gọi hàm trực tiếp trong bộ nhớ giờ đây đã được thay thế bằng các request HTTP hay gRPC qua mạng. Nếu một service phản hồi chậm hoặc bị treo kết nối, nó sẽ kéo theo toàn bộ giao dịch thất bại. Nếu nhà phát triển tự viết code retry hay timeout ở ứng dụng, mã nguồn sẽ trở nên cực kỳ phức tạp và thiếu đồng bộ."

---

### Slide 3: MeshMart Project Scope & Service Boundaries (Phạm vi dự án & Ranh giới dịch vụ)
*   **Nội dung Slide**:
    *   **frontend** (Nginx, Port `8080`): Giao diện người dùng, tích hợp **Observability UI details panel** hiển thị độ trễ từng service và chuỗi tiến trình Saga.
    *   **product-service** (FastAPI, Port `8004`): Quản lý danh mục sản phẩm, đánh giá và khóa tồn kho.
    *   **order-service** (FastAPI, Port `8001`): Trọng tâm điều phối giao dịch Saga (Saga Orchestrator).
    *   **payment-service** (FastAPI, Port `8002`): Giả lập giao dịch thanh toán (Success, Failed, Slow).
    *   **notification-service** (FastAPI, Port `8003`): Gửi thông báo xác nhận giao dịch.
*   **Lời thoại của bạn**:
    > "Để chứng minh cách vận hành thực tế, nhóm xây dựng MeshMart gồm 5 dịch vụ độc lập. Trong đó, Frontend đóng vai trò giao diện SPA và đã được chúng em nâng cấp một bảng giám sát Observability UI hiển thị chi tiết thời gian phản hồi thực tế của từng service con và vẽ lại timeline của tiến trình Saga. Order Service là trung tâm điều phối giao dịch; Product Service quản lý kho; Payment Service giả lập các tình huống thanh toán thành công, thất bại hoặc trễ; còn Notification Service xử lý thông báo gửi đi."

---

### Slide 4: API Endpoints & Service Contracts (Hợp đồng API giữa các dịch vụ)
*   **Nội dung Slide**:
    *   `GET /products` ➔ Lấy danh sách sản phẩm.
    *   `POST /orders` ➔ Tạo đơn hàng mới (bắt buộc truyền header `Idempotency-Key`).
    *   `POST /inventory/reserve` ➔ Giữ kho tạm thời.
    *   `POST /payments` ➔ Thanh toán hóa đơn đơn hàng.
    *   `/health/live` & `/health/ready` ➔ Các đầu dò sức khỏe (Liveness/Readiness probes).
*   **Lời thoại của bạn**:
    > "Hợp đồng API giữa các service được quy định rõ ràng. Khi khách hàng bấm đặt hàng, client gửi POST tới `/orders` kèm theo header `Idempotency-Key` nhằm chống trùng lặp. Order Service sẽ gọi `/inventory/reserve` để giữ kho tạm thời, sau đó gọi `/payments` để xử lý tiền. Tất cả các dịch vụ đều triển khai hai endpoint `/health/live` và `/health/ready` để phục vụ cơ chế tự phục hồi của Kubernetes."

---

### Slide 5: System Deployment Architecture & Zero Trust Security (Kiến trúc hệ thống & Bảo mật Zero-Trust)
*   **Nội dung Slide**:
    *   **Istio Ingress Gateway**: Cổng tiếp nhận và định tuyến lưu lượng bên ngoài vào cluster.
    *   **Data Plane (Envoy Sidecars)**: Tự động inject proxy kế bên các ứng dụng để kiểm soát traffic.
    *   **STRICT mTLS**: Cấu hình `PeerAuthentication` buộc toàn bộ pod giao tiếp qua SSL mã hóa 2 chiều.
    *   **Zero Trust RBAC**: Định nghĩa `AuthorizationPolicy` chặt chẽ, chỉ cho phép các kết nối hợp lệ (ví dụ: chỉ cho phép `order-service` gọi đến các service backend khác).
*   **Lời thoại của bạn**:
    > "Đây là kiến trúc triển khai trên Kubernetes và Istio. Điểm đặc biệt của hệ thống nằm ở mô hình bảo mật Zero Trust. Thứ nhất, chúng em thiết lập chính sách STRICT mTLS trên toàn bộ namespace `meshmart`. Mọi kết nối không được mã hóa từ bên ngoài hoặc giữa các pod đều bị chặn đứng ở tầng mạng. Thứ hai, mỗi pod được gán một ServiceAccount định danh duy nhất và chịu sự kiểm soát của AuthorizationPolicy, chỉ cho phép các service có thẩm quyền kết nối với nhau."

---

### Slide 6: Network Interception: How Envoy Sidecars Work (Cơ chế can thiệp mạng của Envoy Sidecar)
*   **Nội dung Slide**:
    *   **iptables Redirection**: Init-container cấu hình iptables để chuyển hướng toàn bộ traffic ra/vào pod qua port của Envoy.
    *   **Inbound interception**: Envoy chặn request đến, xác thực mTLS, đối chiếu AuthorizationPolicy trước khi chuyển tới Container ứng dụng qua localhost.
    *   **Outbound interception**: Envoy chặn request đi, chèn trace header, áp dụng timeout, retry.
    *   **Zero Code Modifications**: Hoàn toàn trong suốt với ứng dụng Python FastAPI.
*   **Lời thoại của bạn**:
    > "Làm thế nào Istio có thể áp dụng các chính sách phức tạp mà không bắt lập trình viên sửa code ứng dụng? Đó là nhờ cơ chế Network Interception. Khi pod khởi động, một init-container cấu hình iptables để chuyển hướng toàn bộ kết nối ra vào pod về Envoy sidecar. Khi có request đến, Envoy giải mã SSL, kiểm tra phân quyền RBAC rồi mới đẩy qua localhost cho FastAPI. Khi ứng dụng gọi ra ngoài, Envoy sẽ tiêm trace header và áp dụng chính sách mạng như retry hay timeout."

---

### Slide 7: Business Request Flow: The Saga Transaction Pattern (Luồng nghiệp vụ & Giao dịch phân tán Saga)
*   **Nội dung Slide**:
    *   **Thách thức**: Mỗi service sở hữu database riêng, không thể dùng ACID transaction thông thường trên môi trường mạng.
    *   **Giải pháp**: Saga Pattern (Orchestration-based).
    *   **Cơ chế**: Thực hiện tuần tự các giao dịch cục bộ. Nếu một bước thất bại, điều phối viên kích hoạt các giao dịch bù trừ (Compensating Transactions) để hoàn trả trạng thái ban đầu.
*   **Lời thoại của bạn**:
    > "Trong kiến trúc microservices, mỗi service sở hữu cơ sở dữ liệu riêng. Do đó, chúng ta không thể sử dụng cơ chế khóa bảng cơ sở dữ liệu để đảm bảo nhất quán giao dịch. Giải pháp là áp dụng Saga Pattern dạng Orchestration. Order Service đóng vai trò là nhạc trưởng điều phối. Nó ra lệnh cho các service thực hiện giao dịch cục bộ và lưu lại vết. Nếu phát hiện bất kỳ bước nào lỗi, nhạc trưởng sẽ kích hoạt luồng bù trừ để khôi phục trạng thái hệ thống, giữ cho dữ liệu luôn nhất quán."

---

### Slide 8: Step-by-Step Saga Execution (Success Path) (Tiến trình Saga - Luồng thành công)
*   **Nội dung Slide**:
    *   **Luồng chạy**: `order_created` ➔ `inventory_reserved` (giữ kho) ➔ `payment_processed` (thanh toán thành công) ➔ `inventory_committed` (xác nhận trừ kho thực tế) ➔ `notification_sent` (gửi thông báo).
    *   **Trực quan hóa**: Màn hình Storefront hiển thị 5 dấu chấm tròn màu xanh thể hiện tiến trình thành công mượt mà.
*   **Lời thoại của bạn**:
    > "Trong trường hợp thành công, tiến trình Saga diễn ra như sau: Khách hàng tạo đơn ➔ Hệ thống gửi lệnh giữ kho tạm thời ➔ Chuyển qua cổng thanh toán thành công ➔ Nhạc trưởng gửi lệnh xác nhận trừ kho vĩnh viễn ➔ Gửi thông báo đến khách hàng. Giao diện storefront của chúng em hiển thị chuỗi 5 sự kiện này với các dấu chấm màu xanh lá cây, cập nhật theo thời gian thực với độ chính xác mili-giây."

---

### Slide 9: Saga Compensation & Rollbacks (Failure Path) (Bù trừ Saga & Rollback - Luồng thất bại)
*   **Nội dung Slide**:
    *   **Tình huống**: Giữ kho thành công nhưng thanh toán bị từ chối (thẻ hết tiền, lỗi thẻ).
    *   **Giao dịch bù trừ**: Gọi endpoint `/inventory/release` để giải phóng kho hàng đã khóa tạm thời.
    *   **Trực quan hóa**: Màn hình hiển thị bước thanh toán bị báo đỏ, và bước bù trừ giải phóng kho được kích hoạt có màu đỏ để cảnh báo dữ liệu đã rollback an toàn.
*   **Lời thoại của bạn**:
    > "Nếu thanh toán thất bại, kho hàng không được phép bị mất. Nhạc trưởng Saga lập tức phát hiện và kích hoạt giao dịch bù trừ: gọi tới `/inventory/release` để trả lại số lượng sản phẩm đã giữ tạm thời về kho. Trên storefront, các bước giữ kho ban đầu hiển thị màu xanh, nhưng bước thanh toán lỗi và bước giải phóng kho bù trừ sẽ hiển thị màu đỏ để chứng minh hệ thống đã rollback an toàn."

---

### Slide 10: Idempotency Guard (Cơ chế chống trùng lặp đơn hàng)
*   **Nội dung Slide**:
    *   **Nguy cơ**: Người dùng nhấn 'Thanh toán' nhiều lần hoặc mạng chập chờn khiến client gửi lại request trùng lặp.
    *   **Giải pháp**: Sử dụng `Idempotency-Key` truyền từ Client.
    *   **Nguyên lý**: `order-service` kiểm tra cache. Nếu key đã tồn tại và xử lý xong, trả ngay kết quả cũ. Nếu đang xử lý, trả lỗi `409 Conflict`.
*   **Lời thoại của bạn**:
    > "Một vấn đề kinh điển của hệ thống mạng phân tán là trùng lặp request do retry tự động hoặc người dùng nhấn đúp nút mua hàng. Chúng em giải quyết bằng cách áp dụng Idempotency Key. Khi có request gửi lên, Order Service sẽ tra cứu cache. Nếu phát hiện key trùng lặp, nó lập tức trả về kết quả đã lưu trong bộ nhớ từ trước mà không thực hiện gọi lại Payment hay Product Service, ngăn chặn hoàn toàn việc trừ tiền hai lần."

---

### Slide 11: Istio Ingress Gateway & Path-Based Routing (Định tuyến tại Ingress Gateway)
*   **Nội dung Slide**:
    *   **Single Entrypoint**: Khách hàng chỉ truy cập qua một cổng duy nhất (Port `18080` hoặc `80`).
    *   **VirtualService Path Mapping**:
        *   `/` ➔ `frontend`
        *   `/products` ➔ `product-service`
        *   `/orders` ➔ `order-service`
    *   **Bảo mật**: Ẩn giấu hoàn toàn các cổng nội bộ của các microservice phía sau cluster.
*   **Lời thoại của bạn**:
    > "Chúng em cấu hình cổng vào hệ thống sử dụng Istio Ingress Gateway kết hợp VirtualService để định tuyến dựa trên đường dẫn URL. Thay vì để lộ các port chạy dịch vụ ra ngoài, Ingress Gateway tiếp nhận toàn bộ traffic ở một cổng duy nhất: đường dẫn gốc định tuyến tới Frontend, `/products` sang Product Service và `/orders` sang Order Service. Thiết lập này giúp tăng tính bảo mật và tinh gọn kiến trúc mạng."

---

### Slide 12: Traffic Control: Timeouts & Retries (Chính sách Timeout & Retry mạng)
*   **Nội dung Slide**:
    *   **Timeout**: Cấu hình giới hạn thời gian chờ ở tầng Envoy (orders: 8s, payment: 3s). Tránh nghẽn thread pool khi dịch vụ con bị treo.
    *   **Retry**: Cấu hình tự động thử lại 2 lần khi gặp lỗi kết nối tạm thời (`5xx`, `connect-failure`).
*   **Lời thoại của bạn**:
    > "Để tăng tính chịu lỗi của hệ thống truyền thông, chúng em áp dụng chính sách Timeout và Retry của Istio tại tầng Envoy proxy. Chúng em đặt timeout 3 giây cho Payment Service. Nếu cổng thanh toán phản hồi chậm hơn 3 giây, Envoy sẽ ngắt kết nối để giải phóng tài nguyên. Ngoài ra, cơ chế tự động retry 2 lần đối với các lỗi kết nối chập chờn giúp hệ thống tự vượt qua các sự cố mạng chớp nhoáng mà không làm gián đoạn trải nghiệm người dùng."

---

### Slide 13: Fault Injection (Chaos Engineering - Tiêm lỗi mạng)
*   **Nội dung Slide**:
    *   **Chaos Engineering**: Giả lập lỗi trên hệ thống đang chạy để kiểm chứng khả năng chịu đựng.
    *   **Istio Fault Injection**: Tiêm **2 giây delay** vào **30% request** gọi tới `payment-service`.
    *   **Mục tiêu**: Kiểm tra xem `order-service` có kích hoạt timeout và xử lý lỗi đồng bộ hay không.
*   **Lời thoại của bạn**:
    > "Để kiểm chứng khả năng chịu đựng của MeshMart dưới điều kiện khắc nghiệt, chúng em áp dụng Chaos Engineering bằng tính năng Fault Injection của Istio. Chúng em cấu hình tiêm một khoảng trễ cố định 2 giây vào 30% số lượng request gọi tới dịch vụ thanh toán. Điều này giúp nhóm kiểm thử xem hệ thống có tự động kích hoạt cơ chế bảo vệ và rollback kho an toàn khi xảy ra nghẽn mạng hay không."

---

### Slide 14: DestinationRules: Connection Pools & Rate Limiting (Giới hạn tài nguyên kết nối)
*   **Nội dung Slide**:
    *   **Connection Capping**: Giới hạn số lượng kết nối TCP và HTTP đồng thời tới từng service.
    *   **Cấu hình**: `payment-service` giới hạn tối đa 20 kết nối, `product-service` tối đa 50 kết nối.
    *   **Ý nghĩa**: Đóng vai trò như một bộ ngắt mạch bảo vệ dịch vụ khỏi bị quá tải khi traffic tăng đột biến.
*   **Lời thoại của bạn**:
    > "Bên cạnh định tuyến, chúng em sử dụng DestinationRules để thiết lập Connection Pool. Bằng cách giới hạn tối đa 20 kết nối đồng thời tới Payment Service và 50 tới Product Service, Envoy proxy sẽ đóng vai trò như một hàng rào xếp hàng. Khi có lượng truy cập đột biến vượt ngưỡng, Envoy sẽ giữ các request thừa trong hàng đợi thay vì đẩy thẳng vào ứng dụng gây tràn bộ nhớ hay crash container."

---

### Slide 15: Outlier Detection (Circuit Breaking - Cơ chế ngắt mạch tự động)
*   **Nội dung Slide**:
    *   **Nguyên lý**: Phát hiện pod bị lỗi liên tục và tạm thời loại bỏ khỏi danh sách load balancing.
    *   **Chỉ số kích hoạt**: 3 lỗi 5xx liên tiếp trong vòng 10 giây.
    *   **Thời gian cách ly**: Loại bỏ pod lỗi ra khỏi pool trong 30 giây để pod tự phục hồi hoặc chờ Kubernetes restart.
*   **Lời thoại của bạn**:
    > "Circuit Breaking trong Istio được triển khai qua tính năng Outlier Detection. Nếu một pod của một dịch vụ trả về 3 lỗi 5xx liên tiếp trong vòng 10 giây, Envoy proxy sẽ đánh dấu pod này là không khỏe mạnh và loại nó ra khỏi danh sách định tuyến trong 30 giây. Lưu lượng khách hàng sẽ được tự động chuyển hướng sang các pod replica khỏe mạnh khác, ngăn chặn lỗi lan rộng."

---

### Slide 16: Observability Architecture & Telemetry Data Flow (Kiến trúc giám sát & Luồng Telemetry)
*   **Nội dung Slide**:
    *   **Prometheus**: Thu thập các chỉ số (metrics) của Envoy sidecars và custom application `/metrics` định kỳ 15 giây.
    *   **Grafana**: Trực quan hóa các chỉ số qua dashboard 16 panel được nạp tự động (RPS, Latency p50/p90/p99, tồn kho).
    *   **Jaeger**: Thu thập các trace span để theo dõi đường đi của request qua các microservice.
    *   **JSON Structured Logs**: Chuẩn hóa log ứng dụng dưới dạng JSON có cấu trúc.
*   **Lời thoại của bạn**:
    > "Hệ thống giám sát (Observability) của chúng em được xây dựng toàn diện ở cả 3 trụ cột. Prometheus định kỳ quét metrics từ ứng dụng và Envoy proxy. Grafana tự động nạp dashboard gồm 16 biểu đồ chi tiết ngay khi hệ thống khởi chạy. Chúng em cũng tích hợp Jaeger để phân tích vết trace của các request và chuẩn hóa toàn bộ log của các service sang định dạng JSON có cấu trúc để sẵn sàng cho việc phân tích tập trung."

---

### Slide 17: Observability in Action: Diagnostics & Evidence (Quy trình chẩn đoán sự cố thực tế)
*   **Nội dung Slide**:
    *   **Bước 1 (Cảnh báo)**: Grafana phát hiện biểu đồ độ trễ p99 tăng vọt hoặc tỷ lệ lỗi 5xx tăng.
    *   **Bước 2 (Khoanh vùng)**: Kiali graph hiển thị liên kết đỏ bị lỗi giữa các service.
    *   **Bước 3 (Định vị)**: Jaeger trace chỉ ra span xử lý chậm nhất nằm ở microservice nào.
    *   **Bước 4 (Chi tiết)**: Truy vết log JSON ứng dụng bằng `request_id` để đọc Exception chi tiết.
*   **Lời thoại của bạn**:
    > "Đây là quy trình chẩn đoán lỗi trong thực tế vận hành MeshMart. Khi có sự cố, đầu tiên Grafana sẽ phát hiện trễ tăng vọt. Tiếp theo, Kiali graph hiển thị đường liên kết mạng bị đỏ để khoanh vùng dịch vụ lỗi. Sau đó, chúng em mở Jaeger trace để tìm chính xác trace ID và span bị chậm. Cuối cùng, chúng em dùng request_id đó lọc log JSON của ứng dụng để tìm nguyên nhân Exception cụ thể ở dòng code nào. Quy trình này giúp cô lập lỗi chỉ trong vài giây."

---

### Slide 18: High Availability, Probes & Autoscaling (Đầu dò sức khỏe động & Tính sẵn sàng cao)
*   **Nội dung Slide**:
    *   **Liveness Probes**: Gọi endpoint `/health/live` để tự động khởi động lại container bị treo.
    *   **Readiness Probes**: Gọi `/health/ready` để kiểm tra khả năng tiếp nhận traffic.
    *   **Deep Dependency Check**: `order-service` kiểm tra xem `product`, `payment`, `notification` có online không. Nếu một service sập, nó tự báo không sẵn sàng (503) để dừng nhận traffic.
    *   **HPA & PDB**: Tự động scale số lượng pod dựa trên tải CPU và đảm bảo luôn có pod chạy trong lúc deploy.
*   **Lời thoại của bạn**:
    > "Để đảm bảo hệ thống tự phục hồi, chúng em cài đặt Kubernetes Health Probes. Liveness probe kiểm tra nhanh xem container có phản hồi không qua `/health/live`. Readiness probe kiểm tra sâu qua `/health/ready`. Điểm cải tiến là ở Order Service, khi kiểm tra ready, nó sẽ gửi request ngầm test kết nối tới các dịch vụ con. Nếu bất kỳ service con nào sập, Order Service sẽ tự động trả về lỗi 503 báo 'chưa sẵn sàng' để Kubernetes dừng định tuyến người dùng vào nó, tránh sinh đơn lỗi liên tiếp."

---

### Slide 19: Project Limitations & Production Roadmap (Thành tựu & Hạn chế dự án)
*   **Nội dung Slide**:
    *   **Thành tựu đã đạt được**:
        *   Triển khai STRICT mTLS mã hóa đường truyền toàn namespace.
        *   Phân quyền RBAC qua AuthorizationPolicy và ServiceAccount.
        *   Cơ chế Saga điều phối giao dịch phân tán kèm bảng UI giám sát.
        *   Health probes động tích hợp kiểm tra dependency.
        *   Log JSON có cấu trúc và Grafana Dashboard-as-Code.
    *   **Lộ trình tương lai**:
        *   Đưa vào cơ sở dữ liệu persistent thực tế (PostgreSQL/MySQL).
        *   Sử dụng Redis làm shared cache lưu Idempotency Key.
        *   Tích hợp xác thực JWT tại Ingress Gateway.
*   **Lời thoại của bạn**:
    > "Để đánh giá thực tế dự án, chúng em đã hoàn thiện các tính năng cốt lõi của một hệ thống cloud-native bao gồm mã hóa mTLS, phân quyền RBAC, cơ chế Saga đảm bảo dữ liệu nhất quán, log JSON và dashboard giám sát 16 panel. Hạn chế hiện tại là dữ liệu đang được lưu tạm thời trên bộ nhớ. Lộ trình phát triển tiếp theo của nhóm là tích hợp database thực tế, sử dụng Redis làm cache tập trung để lưu Idempotency key và bổ sung xác thực JWT tại cổng Gateway."

---

### Slide 20: Conclusion & Key Learnings (Kết luận & Bài học kinh nghiệm)
*   **Nội dung Slide**:
    *   **Decoupling**: Tách biệt chính sách mạng (timeout, retry, security) ra khỏi code ứng dụng và đẩy xuống hạ tầng (Istio sidecars) giúp ứng dụng nhẹ nhàng và dễ phát triển.
    *   **Observability**: Giám sát kết hợp Metrics, Traces, Logs là điều kiện bắt buộc để vận hành microservices thành công.
    *   **Design for Failure**: Luôn thiết kế hệ thống chịu lỗi cao bằng cách áp dụng Saga compensation và cơ chế Idempotency.
*   **Lời thoại của bạn**:
    > "Để kết luận, dự án MeshMart mang lại cho nhóm ba bài học lớn. Thứ nhất, việc đưa các chính sách kết nối và bảo mật xuống tầng hạ tầng giúp code ứng dụng tinh gọn, tập trung hoàn toàn vào nghiệp vụ. Thứ hai, đối với hệ thống phân tán, Observability không phải là tùy chọn mà là điều kiện sống còn để vận hành. Thứ ba, chúng ta phải luôn thiết kế hệ thống với tâm thế mạng có thể lỗi bất kỳ lúc nào bằng cách áp dụng các mẫu thiết kế như Saga bù trừ và Idempotency. Nhóm xin chân thành cảm ơn các thầy cô đã lắng nghe!"

---

## 💻 Kịch bản Chạy Demo Trực tiếp Từng Bước (Live Demo Runbook)

*Chuẩn bị trước khi chạy: Hãy mở sẵn 1 cửa sổ Terminal và 1 trình duyệt Web có sẵn các tab Grafana, Jaeger, Kiali.*

### Bước 1: Khởi động & Kiểm tra Hệ thống (Smoke Test)
*   **Thời điểm thực hiện**: Sau Slide 4 (trước khi chuyển sang slide kiến trúc bảo mật) hoặc ngay đầu buổi demo.
*   **Lệnh chạy trên Terminal**:
    ```bash
    # Khởi chạy docker compose ở thư mục root của project
    docker compose up --build -d
    ```
*   **Thao tác trình duyệt**:
    *   Mở Storefront: `http://localhost:8080`
    *   Mở Grafana: `http://localhost:3000` (đăng nhập tự động không cần pass)
*   **Lời thoại Demo**:
    > *"Đầu tiên, em xin phép khởi chạy hệ thống MeshMart trên máy cục bộ bằng Docker Compose. Như các thầy cô thấy, giao diện Storefront đã tải xong danh sách sản phẩm và dashboard Grafana đã sẵn sàng nhận metrics."*

---

### Bước 2: Tạo Đơn Hàng Thành Công (Saga Happy Path)
*   **Thời điểm thực hiện**: Khi đang thuyết trình **Slide 8 (Saga Success Flow)**.
*   **Thao tác trên giao diện Web (`http://localhost:8080`)**:
    1.  Nhập ô Customer Name: `Nguyen Van A`.
    2.  Chọn phương thức thanh toán (Payment Mode): **Success**.
    3.  Nhấn nút **Add to Cart** ở sản phẩm điện thoại hoặc laptop.
    4.  Nhấn nút **Checkout**.
    5.  Hệ thống sẽ báo mua hàng thành công. Cuộn xuống phần **Recent Orders**:
        *   Nhấp chuột vào đơn hàng vừa tạo để **mở rộng bảng chi tiết (Accordion Details)**.
        *   **Trình diễn**: Chỉ vào mục **Service Latency** hiển thị thời gian xử lý thực tế của từng service, và phần **Saga Timeline** hiển thị 5 dấu chấm tròn màu xanh từ `order_created` đến `notification_sent`.
*   **Lời thoại Demo**:
    > *"Bây giờ em sẽ tạo một đơn hàng thành công thông thường với tùy chọn Payment Mode là Success. Sau khi checkout, em mở bảng giám sát chi tiết của đơn hàng vừa tạo. Các thầy cô có thể nhìn thấy độ trễ xử lý thực tế của từng service (chỉ mất vài mili-giây) và quan trọng nhất là 5 sự kiện của tiến trình Saga hiển thị thành công bằng các dấu chấm màu xanh lá cây."*

---

### Bước 3: Giao Dịch Lỗi & Bù Trừ Kho (Saga Compensation)
*   **Thời điểm thực hiện**: Khi đang thuyết trình **Slide 9 (Saga Failure & Compensation)**.
*   **Thao tác trên giao diện Web**:
    1.  Đổi Payment Mode thành **Failed**.
    2.  Nhấn nút **Checkout**.
    3.  Đơn hàng mới tạo sẽ hiển thị trạng thái `payment_failed` màu đỏ.
    4.  Nhấp vào đơn hàng đó để xem chi tiết:
        *   **Trình diễn**: Chỉ ra bước `order_created` và `inventory_reserved` vẫn có màu xanh (vì giữ kho thành công), nhưng bước `payment_processed` báo lỗi màu đỏ, và bước bù trừ giải phóng kho `inventory_released` hiển thị màu đỏ với lý do `payment_failed`.
        *   Đồng thời, chỉ ra số lượng tồn kho sản phẩm trên màn hình chính **không bị trừ đi** (chứng minh kho đã được khôi phục an toàn).
*   **Lời thoại Demo**:
    > *"Tiếp theo, em sẽ giả lập tình huống thẻ của khách hàng bị từ chối thanh toán bằng cách chọn Payment Mode là Failed. Khi checkout, đơn hàng bị báo lỗi. Khi mở chi tiết, chúng ta thấy rõ cơ chế bù trừ hoạt động: Bước giữ kho vẫn chạy thành công, nhưng khi thanh toán lỗi, nhạc trưởng Saga lập tức kích hoạt bước giải phóng kho bù trừ màu đỏ. Nhờ đó, số lượng tồn kho của sản phẩm trên giao diện chính được bảo toàn nguyên vẹn."*

---

### Bước 4: Chống Trùng Lặp Giao Dịch (Idempotency Key)
*   **Thời điểm thực hiện**: Khi thuyết trình **Slide 10 (Idempotency Guard)**.
*   **Thao tác**:
    *   Bạn có thể giải thích cơ chế hoặc thực hiện gửi thử 2 request liên tiếp có cùng header `Idempotency-Key` thông qua Postman/Curl để chứng minh request thứ 2 nhận lại ngay kết quả của request thứ 1 mà không tạo ra đơn hàng mới trong DB.
*   **Lời thoại Demo**:
    > *"Để chống trùng lặp đơn hàng, mỗi request checkout từ client đều đính kèm một Idempotency-Key duy nhất. Nếu mạng bị rớt giữa chừng và client tự động gửi lại đơn hàng trùng key đó, hệ thống sẽ trả về ngay kết quả đã lưu trữ từ trước mà không cần chạy lại luồng thanh toán, bảo vệ khách hàng khỏi bị double-billing."*

---

### Bước 5: Kiểm Tra Log JSON Có Cấu Trúc
*   **Thời điểm thực hiện**: Khi thuyết trình **Slide 16 hoặc Slide 17 (Observability in Action)**.
*   **Lệnh chạy trên Terminal**:
    ```bash
    # Xem log của order-service
    docker compose logs order-service --tail 10
    ```
*   **Trình diễn**:
    *   Chỉ ra rằng mỗi dòng log in ra trên màn hình đều là một JSON object chuẩn hóa gồm các trường như `timestamp`, `level`, `service`, `message`, `request_id`, `duration_ms`...
*   **Lời thoại Demo**:
    > *"Toàn bộ hệ thống MeshMart đã được cấu hình ghi log dưới dạng JSON có cấu trúc. Trên terminal, các thầy cô có thể thấy mỗi dòng log của `order-service` là một đối tượng JSON sạch sẽ, chứa đầy đủ thông tin định danh như `request_id` và thời gian chạy `duration_ms`. Thiết lập này giúp chúng ta dễ dàng thu thập và lọc log tập trung bằng các công cụ như Grafana Loki."*

---

### Bước 6: Khám Phá Các Dashboard Giám Sát (Prometheus, Grafana, Jaeger, Kiali)
*   **Thời điểm thực hiện**: Khi thuyết trình **Slide 17 (Diagnostics & Evidence)**.
*   **Thao tác trên trình duyệt**:
    1.  **Grafana** (`http://localhost:3000`):
        *   Vào mục **Dashboards** ➔ **MeshMart** ➔ Chọn **MeshMart — Application Overview**.
        *   **Trình diễn**: Chỉ ra các panel hiển thị tổng lượng request, tỷ lệ lỗi, độ trễ và số lượng tồn kho thực tế của các sản phẩm biến động theo thời gian thực.
    2.  **Jaeger** (trên Kubernetes): Giải thích Jaeger thu thập vết trace của request đi xuyên từ Gateway qua các service.
    3.  **Kiali** (trên Kubernetes): Giải thích Kiali vẽ bản đồ mạng trực quan biểu diễn lưu lượng thực tế và trạng thái của các pod trong mesh.
*   **Lời thoại Demo**:
    > *"Bây giờ chúng ta cùng xem bảng điều khiển Grafana. Dashboard này được tự động nạp cấu hình khi khởi động. Nó hiển thị 16 panel giám sát toàn diện: từ tổng số đơn đặt, tỷ lệ giao dịch thành công/thất bại, thời gian phản hồi thực tế của hệ thống, cho đến số lượng hàng tồn kho của từng mặt hàng cập nhật tức thì theo các giao dịch mua bán chúng ta vừa thực hiện."*

---

### Bước 7: Thử Nghiệm Health Probes & Deep Dependency Check
*   **Thời điểm thực hiện**: Khi thuyết trình **Slide 18 (High Availability, Probes & Autoscaling)**.
*   **Thao tác trên Terminal & Trình duyệt**:
    1.  Gọi thử endpoint ready của `order-service` khi mọi thứ bình thường:
        ```bash
        curl http://localhost:8001/health/ready
        ```
        ➔ Kết quả trả về: `{"status":"ready"}` (HTTP 200).
    2.  Tạm dừng dịch vụ `product-service` để tạo sự cố giả lập:
        ```bash
        docker compose stop product-service
        ```
    3.  Gọi lại endpoint ready của `order-service`:
        ```bash
        curl http://localhost:8001/health/ready
        ```
        ➔ Kết quả trả về: `{"status":"unhealthy", ...}` với mã trạng thái **HTTP 503 Service Unavailable**.
    4.  Khởi động lại product-service để khôi phục hệ thống:
        ```bash
        docker compose start product-service
        ```
*   **Lời thoại Demo**:
    > *"Đặc biệt, chúng em đã phát triển cơ chế Deep Dependency Check cho Readiness Probe. Khi hệ thống khỏe mạnh, endpoint `/health/ready` của `order-service` trả về status 200 Ready. Bây giờ, em dừng thử `product-service`. Khi em gọi lại đầu dò ready của `order-service`, nó lập tức trả về lỗi 503 Unhealthy vì phát hiện dịch vụ phụ thuộc đã mất kết nối. Khi chạy trên Kubernetes, pod này sẽ tự động ngắt kết nối khỏi Ingress để không nhận thêm request lỗi từ khách hàng."*

---

## ❓ Câu hỏi Phản biện Thường gặp & Cách Trả lời (Q&A Tips)

1.  **Q: Tại sao phải sử dụng Service Mesh (như Istio) thay vì tự viết code retry/timeout trong ứng dụng?**
    *   *Trả lời*: Việc tự viết code retry, timeout trong ứng dụng (ví dụ dùng thư viện Python, Java) khiến logic nghiệp vụ bị lẫn lộn với logic hạ tầng mạng. Khi hệ thống có hàng chục dịch vụ viết bằng nhiều ngôn ngữ khác nhau, việc đồng bộ cấu hình retry/timeout sẽ cực kỳ khó khăn. Service Mesh giúp tách biệt hoàn toàn phần này ra tầng hạ tầng (Envoy proxy), cho phép thay đổi cấu hình nóng (hot reload) mà không cần deploy lại code.
2.  **Q: Cơ chế Idempotency Key bảo vệ hệ thống như thế nào trong trường hợp rớt mạng giữa chừng?**
    *   *Trả lời*: Khi client gửi request tạo đơn kèm key `id-001`, nếu payment thành công nhưng đường truyền phản hồi về client bị đứt, client sẽ gửi lại request tạo đơn với cùng key `id-001`. Nhờ Idempotency Key được lưu trong cache, `order-service` nhận ra đây là request trùng lặp đã xử lý thành công, nó trả ngay thông tin đơn hàng cũ về mà không gọi xuống Payment Service một lần nữa, đảm bảo khách hàng không bị tính tiền lần hai.
3.  **Q: Tại sao Readiness Probe lại cần kiểm tra trạng thái của các service phụ thuộc (dependency check)?**
    *   *Trả lời*: Nếu một service như `order-service` vẫn sống (liveness tốt) nhưng tất cả các service con phía sau (`product`, `payment`) đều chết, thì `order-service` không thể xử lý bất kỳ đơn hàng nào. Nếu chỉ kiểm tra sức khỏe của riêng nó, Kubernetes vẫn chuyển traffic người dùng tới pod này, dẫn đến hàng loạt đơn hàng bị lỗi. Bằng cách check ready chiều sâu, pod tự động ẩn mình đi khi phát hiện dependencies lỗi, giúp bảo vệ tính toàn vẹn của hệ thống.
