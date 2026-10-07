# A2MaTex MVP — System Checklist

Tài liệu này là bản đồ tổng quan để chia phạm vi MVP theo platform. A2MaTex hiện gồm năm platform:

| Platform                     | Trách nhiệm chính                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------------------------- |
| **Web Marketplace Frontend** | Hiển thị dữ liệu từ Backend API cho guest, customer, publisher và admin                         |
| **Backend**                  | Cung cấp toàn bộ API, business rule, authorization, persistence và integration cho các platform |
| **Studio**                   | Thiết kế, validate, test và lưu project automation lên Backend                                  |
| **Launcher**                 | Quản lý product đã sở hữu, package, cấu hình chạy và giao tiếp với Runtime Agent                |
| **Runtime Agent**            | Phát hiện device và thực thi Runtime IR trên máy customer                                       |

Các module Backend nằm trong cùng NestJS modular monolith, chưa tách thành microservice. Chi tiết database, state machine và workflow nghiệp vụ sẽ được thiết kế sau khi hoàn tất plan/checklist tổng thể.

Mục tiêu MVP đầu tiên là hoàn thành hai hành trình chính:

1. Customer kích hoạt Publisher → phát triển project trong Studio → lưu project → tự review và tạo submission trên Web → admin review → publish Product.
2. Customer nhận/mua Product trên Marketplace → mở Launcher → tải Product → chọn device → Runtime Agent chạy workflow trên máy cá nhân.

---

# 1. Backend — API và business modules

Backend là source of truth cho dữ liệu cloud và cung cấp API cho Web Marketplace, Studio, Launcher và Runtime Agent.

## 1.1. Identity, account và access

- [x] **Auth Module** — login, logout, access/refresh token và session.
- [x] **User/Profile Module** — thông tin customer, profile công khai và trạng thái tài khoản.
- [x] **RBAC Module** — role và permission; resource ownership vẫn được kiểm tra trong domain service tương ứng.
- [ ] **Publisher Module** — `PublisherAccount`, self-activation, block/unblock và shared publisher access policy.
- [ ] **Terms Module** — versioned terms, publish/archive và immutable terms acceptance.
- [ ] **Installation Module** — quản lý bản cài Launcher trên máy Windows; không quản lý LDPlayer/ADB device.

## 1.2. Studio project và workflow definition

- [ ] **Node Catalog Module** — node definition, version, config/input/output schema, capability và Runtime handler compatibility.
- [ ] **Project Module** — cloud project và mutable project draft do Studio lưu/sync lên Backend.
- [ ] **Workflow Revision Module** — tạo immutable revision từ một phiên bản project draft khi publisher submit trên Web.
- [ ] **Asset Module** — metadata và ownership của template image, OCR resource, icon, screenshot và video.
- [ ] **Storage Service** — upload lifecycle, Object Storage object key và presigned URL.
- [ ] **Workflow Validation Service** — kiểm tra Editor Graph, Runtime IR, node, edge, binding và schema.

Studio chỉ lưu và đồng bộ project. Studio không gửi Product Submission trực tiếp.

## 1.3. Product, submission và review

- [ ] **Product Module** — product identity ổn định và `PublisherAccount` ownership.
- [ ] **Product Listing Module** — name, slug, descriptions, media, visibility và current release reference.
- [ ] **Taxonomy Module** — category, tag và featured placement ở mức tối thiểu cho MVP.
- [ ] **Submission Module** — nhận project được chọn trên Web, tạo immutable Workflow Revision và tạo Submission tham chiếu revision đó.
- [ ] **Automated Scanner Service** — capability, graph/IR, node version, code node, asset và policy scan.
- [ ] **Review Module** — scan result, admin feedback, request changes, approve và reject.
- [ ] **Release Module** — version và immutable `ProductRelease`.
- [ ] **Package Builder Service** — chuẩn hóa Runtime IR, tạo manifest và đóng gói `.a2m`.
- [ ] **Encryption/Key Service** — mã hóa workflow payload và quản lý release key.
- [ ] **Artifact Integrity Service** — tạo package hash, payload hash và metadata để Launcher/Runtime verify.
- [ ] **Catalog/Search Module** — public listing, product detail, publisher page, category và tìm kiếm cơ bản.

Luồng tạo submission trên Web:

```text
Publisher mở Publisher Portal
→ chọn project đã được Studio lưu trên Backend
→ xem project summary, validation result và capability
→ tự review project theo checklist
→ nhập/chọn Product data, Listing data và Release metadata
→ xác nhận submit
→ Backend tạo immutable Workflow Revision từ đúng draft version
→ Backend tạo Submission tham chiếu revision
```

Nếu admin yêu cầu thay đổi, publisher sửa project trong Studio, lưu draft mới rồi tạo submission mới trên Web. Submission và revision cũ không bị ghi đè.

## 1.4. Distribution, entitlement và execution authorization

- [ ] **Product Offer Module** — free/paid offer, thời hạn, installation limit và concurrent device limit.
- [ ] **Entitlement Module** — quyền dài hạn của customer đối với Product.
- [ ] **Manual Grant Use Case** — admin cấp entitlement cho UAT/MVP; nằm trong Entitlement Module.
- [ ] **Download Authorization Service** — kiểm tra entitlement và cấp presigned package download URL.
- [ ] **Launcher API** — My Products, release metadata, compatibility và installation operations.
- [ ] **Execution Lease Module** — issue, validate, renew, expire và revoke lease.
- [ ] **Lease Concurrency Policy** — giới hạn installation, active lease và requested device count khi cấp/renew lease.
- [ ] **Runtime API** — validate lease, trả capability grant và workflow decryption key tạm thời.
- [ ] **Execution Report Module** — nhận idempotent run summary từ Runtime Agent.

## 1.5. Commerce — phạm vi MVP tối thiểu

- [ ] **Free Product Acquisition** — customer nhận entitlement cho Product miễn phí.
- [ ] **Order Module** — cấu trúc order cơ bản và lịch sử sở hữu; không mở rộng promotion/refund trong MVP.
- [ ] **Payment Module** — để sau UAT nếu payment gateway production chưa cần trong tháng đầu.

MVP ưu tiên free Product và manual entitlement grant. Không để payment production chặn hành trình publish/download/run.

## 1.6. Moderation và supporting capabilities — giữ đơn giản

- [ ] **Product Report/Moderation Module** — customer gửi report, admin xem và resolve với reason.
- [ ] **Audit Log Module** — ghi các mutation nhạy cảm: publisher status, review, release, entitlement, installation và moderation.
- [ ] **Job Queue** — scan, package build, cleanup và retry.
- [ ] **Transactional Outbox** — chỉ áp dụng cho transaction cần phát job/event không được phép mất.
- [ ] **Idempotency** — áp dụng cho activate publisher, save/finalize revision, submission, grant, lease và execution report khi cần.
- [ ] **Notification Module** — notification trong ứng dụng cho review result và release; email/push nâng cao có thể để sau MVP.
- [ ] **Cache** — chỉ cache catalog, node definition hoặc public data khi có nhu cầu thực tế.
- [ ] **Observability** — structured log, request correlation và lỗi job tối thiểu cho MVP.
- [ ] **Configuration/Secret** — Object Storage key, encryption key và external service secret.

---

# 2. Web Marketplace Frontend

Web Marketplace Frontend không sở hữu business rule. Frontend hiển thị Backend API response, thu thập user input và thể hiện trạng thái nghiệp vụ.

## 2.1. Public Marketplace

- [ ] Product listing và search cơ bản.
- [ ] Product detail, offer và compatibility.
- [ ] Public publisher profile.
- [ ] Category cơ bản.
- [ ] Login/register entry points.

## 2.2. Customer Portal

- [ ] My Products và entitlement status.
- [ ] Product acquisition/purchase entry.
- [ ] Order/ownership history cơ bản.
- [ ] Registered installations.
- [ ] Open Product in Launcher.
- [ ] Submit Product report.

## 2.3. Publisher Portal

- [ ] Publisher activation và current terms acceptance.
- [ ] Publisher status/blocked reason.
- [ ] Danh sách project đã được Studio lưu lên Backend.
- [ ] Project summary và self-review checklist.
- [ ] Tạo/chọn Product và nhập Listing data.
- [ ] Nhập release version, changelog và compatibility.
- [ ] Review toàn bộ submission data trước khi gửi.
- [ ] Submission history, scan result và admin feedback.
- [ ] Product listing và release history.

## 2.4. Admin Portal

- [ ] Publisher account và Terms management.
- [ ] Submission queue và review detail.
- [ ] Scan findings, feedback, request changes, approve và reject.
- [ ] Product/release suspend hoặc disable.
- [ ] Category/tag management tối thiểu.
- [ ] User và Installation management.
- [ ] Manual entitlement grant/revoke.
- [ ] Product report resolution.
- [ ] Audit log view cơ bản.

Chi tiết màn hình nằm trong `components/ui_checklist.md`.

---

# 3. Studio

Studio chịu trách nhiệm tạo project automation và lưu project lên Backend, không trực tiếp tạo Submission.

## 3.1. Project authoring

- [ ] Create/open local project.
- [ ] Project explorer, Graph Canvas và Node Palette.
- [ ] Schema-driven Node Inspector.
- [ ] Workflow input, variable, binding và asset management.
- [ ] Controlled branch, error edge và loop.
- [ ] Local autosave và crash recovery.

## 3.2. Validation và testing

- [ ] Load compatible Node Catalog từ Backend/cache.
- [ ] Validate Editor Graph trong lúc thiết kế.
- [ ] Compile Editor Graph thành versioned Runtime IR.
- [ ] Runtime Agent development-mode connection.
- [ ] Single-node, run-from-node và full-workflow test.
- [ ] Execution inspector, output, artifact và diagnostics.

## 3.3. Cloud synchronization và Web handoff

- [ ] Create/link cloud Project.
- [ ] Save/sync mutable project draft lên Backend.
- [ ] Upload assets và lưu asset references.
- [ ] Hiển thị save/sync state và conflict.
- [ ] Mở project tương ứng trong Publisher Portal để self-review và tạo Submission.
- [ ] Không có luồng submit thẳng từ Studio trong MVP.

---

# 4. Launcher

- [ ] Login/logout/refresh session.
- [ ] Register và cập nhật Installation.
- [ ] My Products từ Backend.
- [ ] Download package bằng presigned URL.
- [ ] Verify package hash, manifest và compatibility.
- [ ] Installed release management và atomic update.
- [ ] Runtime Agent supervisor và handshake.
- [ ] Device list từ Runtime Agent.
- [ ] Input profile và credential reference.
- [ ] Per-device run configuration.
- [ ] Request/renew execution lease.
- [ ] Start/reconnect/pause/resume/cancel run qua Runtime Agent.
- [ ] Execution monitor và `PAUSED_LICENSE` state.
- [ ] Run summary visibility.

Launcher không gọi ADB trực tiếp và không giữ execution state làm source of truth.

---

# 5. Runtime Agent

- [ ] Local authenticated HTTP/event API cho Studio và Launcher.
- [ ] LDPlayer và bundled ADB discovery.
- [ ] Device Registry và per-device exclusive execution lock.
- [ ] Runtime IR validator và Handler Registry.
- [ ] Single-device workflow engine.
- [ ] Multi-device scheduler và run-group coordination.
- [ ] Typed Android commands; không nhận raw shell/ADB command.
- [ ] Flow, Android action, observation và connector handlers tối thiểu.
- [ ] Timeout, retry, pause, cancel và controlled loop.
- [ ] SQLite checkpoint, node result, event và artifact metadata.
- [ ] WebSocket/SSE event stream cho Studio/Launcher.
- [ ] Production package verification, lease validation và in-memory decryption.
- [ ] Idempotent execution summary sync về Backend.

Runtime Agent quản lý LDPlayer/ADB device và execution detail trên máy customer. Backend chỉ quản lý Windows Installation, lease và execution summary cloud.

---

# 6. Hai hành trình MVP cấp cao

Phần này chỉ giữ overview. Workflow chi tiết, error branch và state transition sẽ được thiết kế sau.

## 6.1. Customer trở thành Publisher và publish Product

```text
Customer
→ activate Publisher và accept Terms trên Web
→ tạo/phát triển project trong Studio
→ Studio save/sync project và assets lên Backend
→ Publisher chọn project trên Web
→ tự review validation/capability
→ nhập Product, Listing và Release data
→ submit
→ Backend tạo immutable Workflow Revision và Submission
→ automated scan
→ admin review
→ build/package/encrypt ProductRelease
→ publish Product trên Marketplace
```

## 6.2. Customer sở hữu và chạy Product

```text
Customer xem/nhận/mua Product trên Web
→ Backend cấp Entitlement
→ customer mở Launcher
→ Launcher register Installation và tải package
→ Launcher verify package và chọn Runtime devices
→ Launcher request execution lease
→ Runtime validate lease và decrypt Runtime IR trong memory
→ Runtime chạy workflow trên từng device
→ Launcher hiển thị execution state
→ Runtime gửi run summary về Backend
```

---

# 7. Cross-platform contracts cần chốt trước implementation

- [ ] Editor Graph schema và schema version.
- [ ] Node Definition, node type/version và capability vocabulary.
- [ ] Runtime IR schema và compiler contract.
- [ ] Project draft version/conflict contract.
- [ ] Workflow Revision immutable snapshot contract.
- [ ] Submission payload và self-review checklist contract.
- [ ] Product/Listing/Release metadata contract.
- [ ] `.a2m` manifest, payload hash và package hash contract.
- [ ] Minimum Studio/Launcher/Runtime compatibility rules.
- [ ] Launcher ↔ Runtime local API contract.
- [ ] Execution lease và Runtime validation contract.
- [ ] Execution event và run summary contract.
- [ ] API error format, pagination và generic success response conventions.

Database ownership, entity relation, constraint, indexes, retention và detailed state machine sẽ được thiết kế sau khi plan/checklist tổng thể được duyệt.

---

# 8. Thứ tự thực hiện đề xuất cho MVP một tháng

1. Chốt cross-platform JSON/API contracts cần cho vertical slice.
2. Publisher Account + Terms + Web activation UI.
3. Node Catalog contract tối thiểu.
4. Project draft + Asset upload + Studio save/sync.
5. Product identity/listing tối thiểu + Web project selection/self-review.
6. Workflow Revision + Submission + scan/validation.
7. Admin Review + request changes/approve/reject.
8. ProductRelease + package/encryption + publish.
9. Free acquisition/manual Entitlement + My Products.
10. Installation + package download/verification.
11. Execution Lease + Launcher/Runtime integration.
12. Runtime execution + event monitor + execution summary.
13. Minimal moderation, audit, notification và operational hardening.

Payment production, advanced search, recommendations, rating/review, coupon, payout, publisher team, arbitrary code node và remote execution control không thuộc critical path của MVP đầu tiên.
