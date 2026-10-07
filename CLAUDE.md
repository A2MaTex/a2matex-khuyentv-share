# CLAUDE.md — Dự án A2MaTex (SEP490 - FA26 - G52)

Tài liệu này cung cấp toàn bộ tri thức nền tảng và chỉ dẫn hệ thống cho Claude Code khi làm việc với dự án **A2MaTex**. Khi khởi tạo một session mới, Claude Code sẽ tự động đọc file này để nắm bắt ngay toàn bộ bối cảnh dự án mà không cần quét lại tài liệu.

---

## 1. Tổng quan & Vai trò
- **Dự án:** A2MaTex (Android Automation Marketplace & Ecosystem) — Đồ án tốt nghiệp Kỹ sư phần mềm (SEP490, Học kỳ FA26, FPT University, Nhóm G52).
- **Vai trò chính:** Business Analyst (BA) kết hợp Software Architect.
- **Tài liệu đặc tả chi tiết:** Tham khảo file [A2MATEX_MASTER_SPECIFICATION.md](./A2MATEX_MASTER_SPECIFICATION.md) và thư mục [a2matex-docs-main](./a2matex-docs-main).

---

## 2. Bản đồ 5 Phân hệ (The 5 Platforms)

1. **A2MaTex Marketplace (Web Portal):**
   - Web phân phối kịch bản tự động hóa dành cho Guest, Customer, Publisher và Admin.
   - Quản lý danh mục, tìm kiếm, gói quyền (`Entitlement`), lịch sử mua hàng, Publisher Portal và Admin Moderation Console.
   - *Ranh giới:* Không trực tiếp chạy workflow, không gọi ADB, không điều khiển emulator.

2. **A2MaTex Launcher (Windows Desktop Client):**
   - Ứng dụng Desktop Windows (Electron + React/TypeScript) dành cho Customer.
   - Quản lý các tool đã sở hữu ("My Products"), tải gói `.a2m` đã mã hóa, kiểm tra tính toàn vẹn (SHA-256 hash).
   - Quản lý bản cài đặt (`Installation`), giám sát tiến trình nền Runtime Agent.
   - Quản lý danh sách giả lập LDPlayer, cấu hình Input Profiles (gán tài khoản/tham số cho từng máy).
   - Xin `Execution Lease` từ Backend trước khi chạy và hiển thị màn hình giám sát tiến độ thực thi.

3. **A2MaTex Visual Studio (Workflow Editor):**
   - Ứng dụng Desktop dành cho Publisher thiết kế workflow dạng kéo-thả (React Canvas / React Flow).
   - Kiến trúc metadata-driven: `NodeDefinition` tự động sinh form cấu hình (`Schema Form Renderer`).
   - Kiểm soát luồng nghiêm ngặt: Không cho phép nối vòng lặp tùy ý (bắt buộc dùng Loop Controller có giới hạn `maxIterations`), không chạy song song trên cùng 1 thiết bị.
   - Chế độ Test cục bộ (Dev Mode) kết nối trực tiếp với Runtime Agent để test single-node, run-from-node.
   - Biên dịch graph thành Runtime IR, đồng bộ Cloud Project và bàn giao sang Web Marketplace để Publisher tự review và submit.

4. **A2MaTex Runtime Agent (Execution Daemon):**
   - Tiến trình nền độc lập viết bằng Go (`a2matex-runtime-agent.exe`), chạy trên máy khách, lắng nghe Local API (`127.0.0.1:<port>`) và WebSocket/SSE.
   - Tự động nhận diện giả lập LDPlayer qua `ldconsole.exe list2` và xác nhận kết nối qua bundled `adb.exe devices -l`.
   - Điều phối chạy song song đa thiết bị: Mỗi LDPlayer chạy trong một goroutine riêng biệt, có khóa độc quyền (exclusive lock).
   - Chạy lệnh ADB an toàn bằng `exec.CommandContext` với typed commands (tuyệt đối không qua `cmd /c`).
   - Xác thực `Execution Lease` với Backend, nhận `workflowKey` tạm thời trong RAM để giải mã gói kịch bản (không lưu IR plaintext ra đĩa).
   - Lưu trạng thái thực thi và checkpoint vào SQLite cục bộ (`run_groups`, `device_executions`, `node_executions`, `artifacts`).

5. **A2MaTex Backend (Cloud Services):**
   - Hệ thống trung tâm xây dựng bằng NestJS Modular Monolith, PostgreSQL (Prisma ORM), Redis Job Queue, Object Storage (S3-compatible).
   - Module cốt lõi: Auth & RBAC, Publisher Account & Terms, Project Draft & Immutable Workflow Revisions, Product/Listing/Release, Automated Scanner, Admin Review, Entitlement & Execution Lease, Execution Reports, Moderation & Audit Log.

---

## 3. Các Thực thể & Khái niệm Cốt lõi (Core Concepts)

- **`Product` vs `ProductListing` vs `ProductRelease` vs `Submission`:**
  - `Product`: Thực thể logic định danh sản phẩm của Publisher.
  - `ProductListing`: Metadata hiển thị thương mại trên Marketplace (tên, mô tả, media, giá).
  - `ProductRelease`: Bản phát hành kỹ thuật bất biến (đã build thành gói `.a2m`, kèm hash, runtime compatibility, capabilities).
  - `Submission`: Snapshot đóng băng gửi lên để Admin thẩm định kèm kết quả scan tự động.
- **Bản quyền, Thanh toán & Ví Coin:**
  - `Entitlement`: Quyền sở hữu dài hạn của Customer (thời hạn, số máy Windows, số giả lập chạy đồng thời tối đa).
  - `Coin & Wallet Model`: Hệ thống sử dụng mô hình Ví Coin nội bộ:
    1. Customer nạp tiền (VND qua VietQR/SePay) $\rightarrow$ Hệ thống quy đổi thành Coin trong Ví Customer.
    2. Customer mua kịch bản (Tool) bằng Coin $\rightarrow$ Hệ thống thực hiện giao dịch ví nguyên tử (Atomic transaction): Trừ Coin Customer, chia % Revenue bằng Coin vào Ví Publisher, giữ lại phí sàn (Platform Fee) và cấp ngay `Entitlement`.
    3. Publisher tích lũy Coin từ doanh thu bán kịch bản và có thể gửi yêu cầu Rút tiền (Payout/Withdrawal) ra tài khoản ngân hàng (VND) dựa trên số dư Coin.
  - `Execution Lease`: Quyền thực thi ngắn hạn cấp theo từng phiên chạy. Backend cấp `leaseToken` (chỉ lưu hash trên server). Runtime xác thực token để lấy decryption key và thời gian chạy trong RAM.
  - `PAUSED_LICENSE`: Trạng thái kịch bản tự động dừng an toàn khi lease hết hạn và không thể gia hạn.
- **Nguyên tắc "Dispatched vs Confirmed":**
  - Lệnh ADB thành công chỉ có nghĩa là lệnh đã được gửi tới thiết bị (`DISPATCHED`). Muốn xác nhận nghiệp vụ thành công (`CONFIRMED`), kịch bản bắt buộc phải có bước kiểm tra màn hình (`Wait For Element`) hoặc xác nhận qua API/Notification.

---

## 4. Phạm vi MVP (Scope Guidelines)

- **Ưu tiên MVP:** Hoàn thành 2 hành trình thông suốt:
  1. *Publisher Flow:* Studio soạn thảo → Test 1 LDPlayer → Lưu Cloud → Web Submit → Admin Duyệt → Đóng gói `.a2m`.
  2. *Customer Flow:* Nhận quyền sử dụng (Free/Manual Grant) → Launcher tải gói → Quét LDPlayer → Cấp Lease → Runtime chạy song song 2-3 thiết bị → Giám sát & Báo cáo.
- **Ngoài phạm vi MVP (Không đưa vào làm nghẽn tiến độ):**
  - Cổng thanh toán trực tuyến tự động (Production Payment Gateway).
  - Node viết code JavaScript tùy ý (Arbitrary Code Node).
  - Điều khiển thiết bị từ xa qua Internet (Remote execution).
  - Chia sẻ doanh thu, mã giảm giá, đánh giá sao.

---

## 5. Nguyên tắc làm việc & Trả lời của BA
- Khi trao đổi về yêu cầu nghiệp vụ, luôn xem xét tác động trên cả 5 phân hệ (Web, Launcher, Studio, Runtime, Backend).
- Đảm bảo ranh giới phân định rõ ràng: việc gì thuộc Cloud Backend, việc gì thuộc Launcher Desktop, việc gì thuộc Runtime Agent trên máy khách.
- Mọi tài liệu hoặc giải pháp kỹ thuật phải bám sát cấu trúc hợp đồng dữ liệu (JSON schemas) và tính bất biến của các bản phát hành.
