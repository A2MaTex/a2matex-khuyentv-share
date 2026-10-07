# TÀI LIỆU ĐẶC TẢ TỔNG QUAN HỆ THỐNG A2MATEX (A2MATEX MASTER SPECIFICATION)
**Dự án:** A2MaTex (Android Automation Marketplace & Ecosystem)  
**Nhóm đồ án:** SEP490 - G52 (Học kỳ FA26 - FPT University)  
**Tài liệu biên soạn theo góc nhìn:** Business Analyst (BA) & Software Architecture

---

## 1. TỔNG QUAN DỰ ÁN & BỐI CẢNH (EXECUTIVE SUMMARY)

### 1.1. Tuyên ngôn bài toán (Problem Statement)
- **Thực trạng:** Nhu cầu tự động hóa các tác vụ trên thiết bị Android (đặc biệt là giả lập LDPlayer phục vụ cày game, nuôi tài khoản mạng xã hội, kiểm thử ứng dụng, thu thập dữ liệu) là rất lớn. Tuy nhiên, việc tự động hóa hiện nay phụ thuộc vào việc viết mã phức tạp, script ADB rời rạc, hoặc sử dụng các tool trôi nổi tiềm ẩn mã độc, thiếu bản quyền và không có sự kiểm duyệt.
- **Rào cản cho Publisher (Người phát triển tool):** Khó đóng gói, không có giải pháp bảo vệ bản quyền/mã nguồn hiệu quả, thiếu kênh phân phối tập trung và khó kiểm soát số lượng máy/thiết bị chạy đồng thời của khách hàng.
- **Rào cản cho Customer (Khách hàng sử dụng):** Ngại cài đặt môi trường kỹ thuật phức tạp (Python, Node.js, Android SDK), khó cấu hình nhiều tài khoản/thiết bị giả lập, rủi ro bị khóa tài khoản hoặc lừa đảo.

### 1.2. Giải pháp A2MaTex (Solution Overview)
A2MaTex là một hệ sinh thái toàn diện (End-to-End Ecosystem) cung cấp:
1. **A2MaTex Studio:** Môi trường thiết kế trực quan dạng kéo-thả (No-code / Low-code Visual Workflow Editor) giúp Publisher tạo ra các kịch bản tự động hóa Android mà không cần trực tiếp viết lệnh ADB hay script phức tạp.
2. **A2MaTex Marketplace:** Sàn thương mại điện tử trực tuyến kết nối Publisher và Customer, tích hợp quy trình quét mã tự động (Automated Scanning) và kiểm duyệt thủ công bởi Admin trước khi phát hành.
3. **A2MaTex Launcher:** Ứng dụng Desktop Windows dành cho Customer để quản lý các tool đã sở hữu, tự động phát hiện giả lập LDPlayer, nạp profile tham số và điều phối thực thi.
4. **A2MaTex Runtime Agent:** Tiến trình nền (Go daemon) độc lập trên máy Windows thực thi các kịch bản workflow, trực tiếp điều khiển các phiên bản LDPlayer/thiết bị qua ADB, quản lý chạy song song đa thiết bị và đồng bộ trạng thái an toàn.
5. **A2MaTex Backend:** Hệ thống Cloud trung tâm (NestJS + PostgreSQL) quản lý định danh, bản quyền (Entitlement), cấp phát quyền thực thi tạm thời (Execution Lease), lưu trữ project/release và kiểm soát toàn bộ hệ thống.

---

## 2. CÁC ĐỐI TƯỢNG SỬ DỤNG (USER ROLES & ACTORS)

| Nhóm người dùng | Mô tả vai trò | Đặc quyền & Hành động chính |
| :--- | :--- | :--- |
| **Guest** | Khách truy cập vãng lai trên Web | - Xem danh mục sản phẩm, tìm kiếm, xem chi tiết tool, giá bán, profile publisher.<br>- Đăng ký/Đăng nhập tài khoản. Không thể mua, tải hay chạy tool. |
| **Customer** | Khách hàng sử dụng tự động hóa | - Sở hữu sản phẩm (mua/nhận miễn phí) → Nhận `Entitlement`.<br>- Tải và mở sản phẩm trên A2MaTex Launcher.<br>- Cấu hình thiết bị LDPlayer, phân bổ profile tài khoản.<br>- Theo dõi tiến độ chạy, xem lịch sử, báo cáo vi phạm (Report). |
| **Publisher** | Nhà sáng tạo kịch bản tự động hóa | - Kích hoạt tài khoản Publisher và đồng ý thỏa thuận (Terms of Service).<br>- Dùng A2MaTex Studio thiết kế workflow, test trên thiết bị thật/LDPlayer.<br>- Đồng bộ Project lên Cloud, tự kiểm tra (Self-review) và gửi yêu cầu kiểm duyệt (Submission).<br>- Theo dõi phản hồi của Admin, cập nhật phiên bản mới. |
| **Admin** | Quản trị viên hệ thống | - Kiểm duyệt Submission (Xem kết quả scan tự động, chạy thử, yêu cầu sửa đổi, Approve/Reject).<br>- Quản lý Product, tạm ẩn (Suspend) hoặc vô hiệu hóa Release vi phạm.<br>- Cấp quyền thủ công (Manual Entitlement Grant), thu hồi quyền (Revoke).<br>- Xử lý tố cáo (Reports), quản lý người dùng, bản cài đặt (Installations) và xem Audit Log. |

---

## 3. KIẾN TRÚC HỆ SINH THÁI (THE 5 PLATFORMS)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   CLOUD BACKEND                                        │
│  - NestJS Modular Monolith + PostgreSQL + Object Storage (S3-compatible)               │
│  - Auth & RBAC | Project & Revisions | Marketplace Catalog | Submissions & Releases    │
│  - Entitlements | Execution Leases | Package Encryption | Execution Reporting          │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│     WEB MARKETPLACE (FRONTEND)  │             │   A2MATEX STUDIO (DEVELOPER)    │
│ - Public Catalog & Discovery    │             │ - React/TypeScript Desktop App  │
│ - Customer "My Products" Portal │             │ - Visual Canvas (Nodes & Edges) │
│ - Publisher Portal & Submission │             │ - Schema Form Renderer          │
│ - Admin Moderation Console      │             │ - Compile Editor Graph → IR     │
└─────────────────────────────────┘             │ - Local Test via Runtime Agent  │
                                                └────────────────┬────────────────┘
                                                                 │ (Dev Mode)
                                                                 ▼
┌─────────────────────────────────┐             ┌─────────────────────────────────┐
│     A2MATEX LAUNCHER (CUSTOMER) │             │    A2MATEX RUNTIME AGENT        │
│ - Windows Desktop (Electron)    │   HTTP IPC  │ - Go Standalone Daemon (EXE)    │
│ - Sync Entitlements & Packages  ├────────────►│ - LDPlayer & Bundled ADB Engine │
│ - Device & Profile Mapping      │   WebSocket │ - Multi-Device Concurrency      │
│ - Request/Renew Execution Lease │◄────────────┤ - SQLite State & Checkpointing  │
│ - Live Execution Monitor        │             │ - In-memory Workflow Decryption │
└─────────────────────────────────┘             └────────────────┬────────────────┘
                                                                 │
                                                                 ▼
                                                ┌─────────────────────────────────┐
                                                │      LDPLAYER / ANDROID PHONES  │
                                                │ - LDPlayer 0, 1, 2... (Console) │
                                                │ - ADB Shell, Tap, Swipe, Dump   │
                                                └─────────────────────────────────┘
```

---

## 4. HAI HÀNH TRÌNH NGHIỆP VỤ CỐT LÕI (CORE BUSINESS JOURNEYS)

### Hành trình 1: Từ ý tưởng của Publisher đến Sản phẩm trên Marketplace
1. **Kích hoạt & Soạn thảo:** Customer kích hoạt tài khoản Publisher trên Web, chấp thuận Terms. Mở Studio để tạo Project, kéo thả các node hành động (Launch App, Tap, Swipe, Wait for Element, Google Sheets...).
2. **Kiểm thử cục bộ (Dev Mode):** Studio kết nối tới Runtime Agent cục bộ, chạy thử nghiệm từng node (Single node test), chạy từ một điểm (Run from here) hoặc chạy toàn bộ workflow trên thiết bị LDPlayer để tinh chỉnh tọa độ/logic.
3. **Đồng bộ Cloud:** Studio lưu mutable draft và tải asset (ảnh mẫu, icon) lên Cloud Backend.
4. **Tạo Submission trên Web:** Publisher vào Publisher Portal, chọn Project đã đồng bộ, kiểm tra kết quả validate, điền thông tin thương mại (Listing, giá, mô tả, ảnh chụp) và xác nhận gửi duyệt.
5. **Khóa bất biến (Immutable Revision):** Backend tự động đóng băng Project Draft thành một `WorkflowRevision` bất biến và gắn vào `Submission`.
6. **Kiểm duyệt 2 tầng:**
   - **Tự động (Automated Scanner):** Kiểm tra cấu trúc graph, schema, phát hiện vòng lặp vô tận, kiểm tra quyền nhạy cảm (Capabilities allowlist), cấm chèn raw ADB/shell command.
   - **Thủ công (Admin Review):** Admin kiểm tra nội dung, mục đích workflow, tính an toàn, sau đó chọn: `APPROVE`, `CHANGES_REQUESTED` (yêu cầu tạo snapshot mới), hoặc `REJECT`.
7. **Đóng gói & Phát hành (Release Build):** Khi duyệt, Backend tự động biên dịch IR, sinh Content Encryption Key, mã hóa payload, đóng gói thành file `.a2m` (chứa `manifest.json`, `workflow.enc`, `input-schema.json`, `assets/`), tính toán SHA-256 hash và upload lên Object Storage. Tạo bản ghi `ProductRelease` bất biến và công bố lên Marketplace.

### Hành trình 2: Customer sở hữu, cấu hình và thực thi trên máy cá nhân
1. **Sở hữu (Acquisition):** Customer nhận tool miễn phí hoặc mua trên Marketplace Web → Backend ghi nhận `Entitlement` (gồm ID sản phẩm, hạn dùng, số máy Windows được cài, số thiết bị giả lập chạy đồng thời tối đa).
2. **Đồng bộ Launcher:** Customer mở Launcher, đăng nhập, hệ thống tự động đăng ký `Installation` (định danh máy Windows bằng DPAPI/Hardware info) và hiển thị danh sách sản phẩm trong "My Products".
3. **Tải & Xác thực Package:** Launcher nhận presigned URL tải gói `.a2m`, kiểm tra SHA-256 hash và manifest đảm bảo tính toàn vẹn.
4. **Cấu hình chạy (Run Configuration):** Runtime Agent quét danh sách giả lập LDPlayer qua `ldconsole.exe list2` và `adb.exe devices -l`. Customer chọn các thiết bị muốn chạy (ví dụ 3 máy LDPlayer), gán Input Profile (tài khoản, dữ liệu đầu vào riêng cho từng máy).
5. **Cấp phát quyền thực thi (Execution Lease):** Khi bấm **Run**, Launcher gửi yêu cầu xin lease lên Backend (`requestedDeviceCount: 3`). Backend kiểm tra quyền và trả về `leaseToken` ngẫu nhiên trong RAM (Backend chỉ lưu sha256 hash).
6. **Xác thực Lease & Giải mã:** Launcher chuyển `leaseToken` xuống Runtime Agent. Runtime gọi thẳng lên Backend để validate token, nhận thời gian hiệu lực (`validForSeconds`) và `workflowKey` tạm thời trong RAM để giải mã gói kịch bản.
7. **Thực thi song song (Execution):** Runtime Agent tạo một goroutine độc lập cho mỗi thiết bị được chọn. Các hành động Android được thực thi tuần tự trên từng máy dưới dạng typed command an toàn (`exec.CommandContext`), không chạy qua `cmd.exe`.
8. **Giám sát & Checkpoint:** Runtime Agent ghi kết quả từng bước vào SQLite cục bộ theo sequence tăng dần, phát event realtime qua WebSocket để Launcher hiển thị thanh tiến độ, ảnh chụp màn hình và log.
9. **Khả năng chịu lỗi & Mất mạng:** Nếu mạng chập chờn ngắn hạn, workflow vẫn tiếp tục chạy đến khi lease hết hạn. Nếu lease hết hạn mà không gia hạn (renew) được, Runtime sẽ tạm dừng an toàn (`PAUSED_LICENSE`) trước khi bắt đầu node mới. Kết thúc lượt chạy, Runtime gửi run summary tổng hợp về Backend.

---

## 5. ĐẶC TẢ CHI TIẾT CÁC PHÂN HỆ

### 5.1. A2MaTex Marketplace (Web Portal)
- **Công nghệ đề xuất:** React / Next.js, TailwindCSS.
- **Phân định ranh giới:** Tuyệt đối không điều khiển giả lập, không chạy ADB, không giải mã workflow trên web.
- **Thực thể thương mại cốt lõi:**
  - `Product`: Thực thể logic định danh sản phẩm của Publisher.
  - `ProductListing`: Thông tin trưng bày (tên, slug, category, mô tả, media, giá).
  - `ProductRelease`: Phiên bản kỹ thuật đã duyệt và đóng gói (chứa version, package hash, minimum runtime version, capabilities).
  - `Submission`: Bản snapshot kèm lý do và kết quả review để Admin thẩm định.

### 5.2. A2MaTex Launcher (Windows Desktop Client)
- **Công nghệ đề xuất:** Electron + React/TypeScript.
- **Bảo mật:** Access/refresh token và credential được bảo vệ bằng Windows Credential Manager hoặc DPAPI. Không lưu token hay mã giải mã vào localStorage / SQLite file thô.
- **Giao tiếp Runtime:** Giao tiếp qua Local HTTP API (`127.0.0.1:<port>`) và WebSocket nhận event.
- **Cơ chế Preflight Check:** Trước khi cho phép chạy, Launcher bắt buộc kiểm tra: (1) Package đã cài và khớp hash; (2) License còn hiệu lực; (3) Runtime Agent tương thích; (4) Thiết bị LDPlayer online và ADB sẵn sàng; (5) Input/Profile hợp lệ; (6) Số thiết bị không vượt hạn mức của gói.

### 5.3. A2MaTex Visual Studio (Workflow Editor)
- **Công nghệ đề xuất:** React Flow / Canvas tùy biến, React/TypeScript.
- **Mô hình Node:** Sử dụng `NodeDefinition` dạng metadata-driven để tự động sinh giao diện cấu hình (Schema Form Renderer), không code thủ công từng form.
- **Kiểm soát luồng (Flow Control Rules):**
  - Không cho phép nối dây vòng lặp ngược tự do gây tràn bộ nhớ. Vòng lặp bắt buộc sử dụng controller nodes chuyên dụng (`Repeat N times`, `While Condition`, `For Each`) có giới hạn cứng `maxIterations` và `maxDuration`.
  - Không hỗ trợ parallel branches tùy ý trên cùng một thiết bị trong MVP; workflow trên một thiết bị là tuần tự. Việc song song được giải quyết ở cấp độ đa thiết bị (Multi-device concurrency).
- **Bộ Node MVP (27–35 Node Types):**
  - *Flow:* Start, End, Fail, Delay, If, Switch, Repeat, While, For Each, Merge, Set Variable, Log.
  - *Android Action:* Launch App, Stop App, Tap, Long Press, Swipe, Scroll, Input Text, Clear Text, Key Event.
  - *Android Observation:* Screenshot, Get Current App, Element Exists, Wait For Element, Get Element Text, Find Image.
  - *Data & Connectors:* Compare, Text Template, Parse JSON, Build Object, List Ops, HTTP Request, Google Sheets Append, Telegram Send.

### 5.4. A2MaTex Runtime Agent (Go Daemon)
- **Công nghệ đề xuất:** Go (Golang) compile thành file thực thi duy nhất `a2matex-runtime-agent.exe`.
- **Nhận diện LDPlayer:** Đọc cấu hình thư mục LDPlayer, chạy định kỳ `ldconsole.exe list2` để lấy thông tin index, trạng thái boot, window handle; kết hợp `adb.exe devices -l` để xác nhận kết nối ADB đã sẵn sàng.
- **Thực thi Subprocess an toàn:**
  - Tuyệt đối không ghép chuỗi gọi qua `cmd /c` tránh lỗ hổng Command Injection.
  - Dùng `exec.CommandContext` truyền tường minh mảng tham số (arguments array).
  - Tách biệt timeout cấp node và timeout cấp hạ tầng.
- **Nguyên tắc "Dispatched vs Confirmed":** Thao tác Tap/Input qua ADB trả về exit code 0 chỉ có nghĩa là lệnh đã được gửi thành công (`DISPATCHED`), không đồng nghĩa với việc ứng dụng Android đã xử lý xong nghiệp vụ. Kịch bản phải dùng node quan sát (`Wait For Element`) hoặc kiểm tra bên ngoài để chuyển sang trạng thái `CONFIRMED`.
- **Lưu trữ cục bộ:** SQLite lưu các bảng `run_groups`, `device_executions`, `node_executions`, `execution_events`, `artifacts`. Khi crash, trạng thái được đánh dấu là `INTERRUPTED`, không tự động resume mù quáng để tránh lặp lại các tác vụ có side-effect.

### 5.5. A2MaTex Backend (Cloud Services)
- **Công nghệ đề xuất:** NestJS (Modular Monolith), Prisma ORM, PostgreSQL, Redis/BullMQ (Queue xử lý scan và đóng gói), S3-compatible Object Storage.
- **Database Design (PostgreSQL Core Schemas):**
  1. *Identity & Installation:* `User`, `Profile`, `PublisherAccount`, `Installation`, `Device`.
  2. *Studio & Workflows:* `Capability`, `NodeDefinition`, `NodeDefinitionVersion`, `Project`, `ProjectDraft`, `WorkflowRevision`, `Asset`.
  3. *Marketplace Publishing:* `Product`, `ProductListing`, `ProductRelease`, `Submission`, `AutomatedScanResult`, `AdminReview`.
  4. *Commerce & Execution:* `Offer`, `Order`, `Entitlement`, `ExecutionLease`, `ExecutionReport`, `ProductReport`.
  5. *Operations & Support:* `AuditLog`, `Notification`, `OutboxMessage`, `JobQueue`.

---

## 6. MA TRẬN PHÂN CHIA TRÁCH NHIỆM & NGUỒN SỰ THẬT (SOURCE OF TRUTH)

| Loại dữ liệu | Nguồn sự thật (Source of Truth) | Nơi lưu trữ / Cơ chế bảo vệ |
| :--- | :--- | :--- |
| **Tài khoản, Quyền hạn, Bản quyền (Entitlement)** | Backend Cloud | PostgreSQL |
| **Trạng thái hợp đồng cấp quyền chạy (Lease Record)** | Backend Cloud | PostgreSQL (chỉ lưu token hash) |
| **Lease Token tạm thời** | Bộ nhớ RAM (Tạm thời) | Launcher RAM & Runtime RAM (Không ghi đĩa) |
| **Gói kịch bản đã phát hành (.a2m)** | Object Storage | Mã hóa AES-256-GCM + SHA-256 hash |
| **Decrypted Workflow IR** | Runtime Agent RAM | Bộ nhớ RAM trong khi chạy (Tuyệt đối không lưu đĩa) |
| **Danh sách thiết bị giả lập thực tế** | Runtime Agent | Quét từ Windows process & LDPlayer CLI |
| **Trạng thái thực thi hiện tại (Current Node, Sequence)** | Runtime Agent | SQLite cục bộ trên máy khách |
| **Lịch sử & Báo cáo tổng kết chạy** | Runtime Agent → Sync Backend | SQLite cục bộ đồng bộ lên Backend |

---

## 7. ĐIỀU KHOẢN VÀ KẾ HOẠCH BÀN GIAO CHO DEV TEAM (MVP SCOPE)

### 7.1. Trong phạm vi MVP (In-Scope - Bắt buộc hoàn thành)
1. Luồng hoàn chỉnh từ Publisher: Studio tạo workflow → Test 1 giả lập → Cloud Sync → Web Submit → Admin duyệt → Đóng gói `.a2m`.
2. Luồng hoàn chỉnh cho Customer: Web nhận tool miễn phí/manual grant → Launcher tải về → Quét LDPlayer → Cấp Lease → Runtime chạy song song tối thiểu 2–3 LDPlayer độc lập → Hiển thị tiến độ và log.
3. Bộ node cơ bản: Điều khiển ứng dụng (Launch/Tap/Swipe/Input), kiểm tra UI (Wait for element, Element exists), điều khiển luồng (If, Repeat) và Connector ghi Google Sheets.
4. Cơ chế bản quyền bằng Lease Token và giới hạn concurrent devices.

### 7.2. Ngoài phạm vi MVP (Out-of-Scope - Để sau UAT)
- Tích hợp cổng thanh toán trực tiếp (Payment Gateway production) – MVP dùng Free Acquisition và Manual Entitlement Grant bởi Admin.
- Tự do viết mã tùy ý (Arbitrary JavaScript Code Node) kết nối mạng hay filesystem ngoài sandbox.
- Đổi hướng điều khiển từ xa qua Internet (Remote execution via cloud websocket).
- Hệ thống chia sẻ doanh thu phức tạp (Payout, Revenue split, Coupon, Referral).
- Điều khiển thiết bị iOS hoặc giả lập Android khác ngoài LDPlayer.
