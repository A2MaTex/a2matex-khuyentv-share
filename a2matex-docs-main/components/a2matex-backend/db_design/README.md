# A2MaTex Backend Database Design

Thư mục này chia PostgreSQL schema của Backend thành các nhóm domain lớn và có quan hệ gần nhau. Đây là **design proposal**, chưa phải Prisma schema hoặc executable migration.

Backend là source of truth cho dữ liệu cloud. Database local của Studio, Launcher và Runtime Agent không nằm trong các tài liệu SQL này.

## Nhóm schema

| File | Nhóm domain | Nội dung chính |
| --- | --- | --- |
| `01_identity_publisher_installation.md` | Identity và access | Auth/RBAC hiện có, Publisher, Terms, Windows Installation |
| `02_studio_project_workflow.md` | Studio cloud data | Node Catalog, Project Draft, Workflow Revision, Asset |
| `03_product_submission_release.md` | Marketplace publishing | Product, Listing, Taxonomy, Submission, Scan, Review, ProductRelease |
| `04_commerce_entitlement_execution.md` | Customer ownership và execution authorization | Offer, Order, Payment, Entitlement, Lease, Execution Report, Product Report |
| `05_operations_support.md` | Hạ tầng hỗ trợ | Audit, Notification, Outbox, Job và Idempotency |

## Quy ước chung

- PostgreSQL với UUID primary key: `UUID DEFAULT gen_random_uuid()`.
- Tên table và camelCase column được quote để khớp Prisma hiện tại.
- Timestamp dùng `TIMESTAMPTZ` và lưu UTC.
- Mutable business entity có `createdAt`, `updatedAt`, `deletedAt` khi cần soft delete.
- Immutable snapshot/evidence record không soft delete; chỉ thêm record mới hoặc thay đổi status được cho phép.
- Foreign key mặc định không cascade delete dữ liệu nghiệp vụ hoặc lịch sử.
- Partial unique index dùng `WHERE "deletedAt" IS NULL` cho soft-deleted master data.
- Tiền được lưu bằng integer minor unit (`priceMinor`), không dùng floating point.
- Secret plaintext, refresh/lease token plaintext và workflow decryption key không được lưu. Chỉ lưu hash hoặc key reference.
- Binary file không lưu trong PostgreSQL. Database chỉ lưu Object Storage key, size, media type và hash.
- JSONB chỉ dùng cho snapshot, schema có version, metadata biến đổi hoặc payload event. Quan hệ cần query/join/constraint phải dùng table/column chuẩn.
- Mọi JSONB phải được validate tại API/application boundary bằng versioned schema trước khi ghi.

## JSONB rule

Mỗi JSONB column trong tài liệu có mock shape ở SQL comment:

```sql
-- Mock JSON (schemaVersion bắt buộc):
-- {
--   "schemaVersion": "1.0",
--   "example": true
-- }
"payload" JSONB NOT NULL
```

`CHECK (jsonb_typeof(...) = 'object')` chỉ kiểm tra cấu trúc JSON cơ bản. Validation nghiệp vụ đầy đủ vẫn nằm trong Backend.

## Ranh giới MVP

Thiết kế ưu tiên hai hành trình:

1. Customer activate Publisher → Studio save Project → Web self-review/submit → admin review → publish ProductRelease.
2. Customer nhận/mua Product → Launcher download → Backend cấp lease → Runtime Agent execute → sync run summary.

Payment production, recommendation, rating/review, coupon, payout và publisher team không phải critical path của MVP đầu tiên.

## Migration workflow sau này

Khi một schema group được duyệt:

1. Viết forward migration SQL mới trong `a2matex-be/prisma/migrations`.
2. Apply migration vào database phù hợp.
3. Chạy Prisma introspection.
4. Generate Prisma client.
5. Chỉ khi đó mới triển khai repository/service/API dựa trên schema đã apply.

Không copy nguyên toàn bộ design SQL thành một migration lớn. Mỗi vertical slice chỉ lấy entity/constraint thực sự cần cho API đang triển khai.
