# 04 — Offer, Order, Entitlement và Execution Authorization

## 1. Trách nhiệm nhóm

Nhóm này quản lý quyền sử dụng Product của customer:

```text
ProductOffer
→ free acquisition hoặc Order/Payment
→ Entitlement
→ Installation assignment
→ ExecutionLease
→ Runtime validation
→ ExecutionReport
```

MVP ưu tiên free acquisition và admin manual grant. Schema Order/Payment được giữ ở mức cơ bản để không chặn việc bổ sung payment gateway sau UAT.

## 2. Product Offer

### Trách nhiệm

`ProductOffer` mô tả cách customer nhận quyền sử dụng và snapshot limit sẽ cấp cho Entitlement.

```sql
CREATE TYPE "ProductOfferType" AS ENUM (
    'FREE',
    'ONE_TIME',
    'SUBSCRIPTION'
);

CREATE TYPE "ProductOfferStatus" AS ENUM (
    'DRAFT',
    'ACTIVE',
    'INACTIVE'
);

CREATE TABLE "ProductOffer" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    type "ProductOfferType" NOT NULL,
    status "ProductOfferStatus" NOT NULL DEFAULT 'DRAFT',
    currency CHAR(3),
    "priceMinor" BIGINT CHECK ("priceMinor" IS NULL OR "priceMinor" >= 0),
    "durationDays" INTEGER CHECK ("durationDays" IS NULL OR "durationDays" > 0),
    "maxInstallations" INTEGER NOT NULL DEFAULT 1 CHECK ("maxInstallations" > 0),
    "maxConcurrentDevices" INTEGER NOT NULL DEFAULT 1 CHECK ("maxConcurrentDevices" > 0),

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "releaseAccess": "CURRENT_AND_SUPPORTED",
    --   "allowUpdates": true
    -- }
    "usagePolicy" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,
    "createdById" UUID NOT NULL REFERENCES "User" (id),
    "updatedById" UUID REFERENCES "User" (id),

    CONSTRAINT "ProductOffer_usagePolicy_object_check"
        CHECK (jsonb_typeof("usagePolicy") = 'object'),
    CONSTRAINT "ProductOffer_price_check" CHECK (
        (type = 'FREE' AND COALESCE("priceMinor", 0) = 0)
        OR
        (type <> 'FREE' AND "priceMinor" IS NOT NULL AND currency IS NOT NULL)
    )
);

CREATE INDEX "ProductOffer_product_status_idx"
ON "ProductOffer" ("productId", status)
WHERE "deletedAt" IS NULL;
```

## 3. Order và Payment

### Trách nhiệm

`Order` lưu commercial transaction. `OrderItem` snapshot Offer để lịch sử không thay đổi khi publisher sửa giá/limit. `PaymentTransaction` lưu normalized payment attempt, không lưu secret/payment credential.

```sql
CREATE TYPE "OrderStatus" AS ENUM (
    'PENDING',
    'PAID',
    'CANCELLED',
    'FAILED'
);

CREATE TABLE "Order" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "customerId" UUID NOT NULL REFERENCES "User" (id),
    status "OrderStatus" NOT NULL DEFAULT 'PENDING',
    currency CHAR(3) NOT NULL,
    "totalMinor" BIGINT NOT NULL CHECK ("totalMinor" >= 0),
    "paidAt" TIMESTAMPTZ,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    CONSTRAINT "Order_paidAt_check" CHECK (
        status <> 'PAID' OR "paidAt" IS NOT NULL
    )
);

CREATE TABLE "OrderItem" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "orderId" UUID NOT NULL REFERENCES "Order" (id),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "productOfferId" UUID NOT NULL REFERENCES "ProductOffer" (id),
    "unitPriceMinor" BIGINT NOT NULL CHECK ("unitPriceMinor" >= 0),

    -- Mock JSON: immutable commercial snapshot.
    -- {
    --   "schemaVersion": "1.0",
    --   "offerType": "ONE_TIME",
    --   "currency": "USD",
    --   "priceMinor": 999,
    --   "durationDays": 30,
    --   "maxInstallations": 1,
    --   "maxConcurrentDevices": 3
    -- }
    "offerSnapshot" JSONB NOT NULL,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "OrderItem_order_product_key" UNIQUE ("orderId", "productId"),
    CONSTRAINT "OrderItem_offerSnapshot_object_check"
        CHECK (jsonb_typeof("offerSnapshot") = 'object')
);

CREATE TYPE "PaymentStatus" AS ENUM (
    'PENDING',
    'SUCCEEDED',
    'FAILED',
    'CANCELLED'
);

CREATE TABLE "PaymentTransaction" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "orderId" UUID NOT NULL REFERENCES "Order" (id),
    provider VARCHAR(100) NOT NULL,
    "providerTransactionId" VARCHAR(255),
    status "PaymentStatus" NOT NULL DEFAULT 'PENDING',
    currency CHAR(3) NOT NULL,
    "amountMinor" BIGINT NOT NULL CHECK ("amountMinor" >= 0),

    -- Mock JSON: sanitized provider result only.
    -- {
    --   "schemaVersion": "1.0",
    --   "providerStatus": "captured",
    --   "failureCode": null
    -- }
    -- Không lưu card number, secret, raw authorization header hoặc full webhook chứa PII.
    "providerResult" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    CONSTRAINT "PaymentTransaction_providerResult_object_check"
        CHECK (jsonb_typeof("providerResult") = 'object')
);

CREATE UNIQUE INDEX "PaymentTransaction_provider_id_idx"
ON "PaymentTransaction" (provider, "providerTransactionId")
WHERE "providerTransactionId" IS NOT NULL;
```

Free acquisition không bắt buộc tạo PaymentTransaction. Có thể tạo Order zero-value để thống nhất history, hoặc cấp Entitlement trực tiếp với `grantSource = FREE_ACQUISITION`; quyết định API sẽ được chốt khi làm commerce slice.

## 4. Entitlement

### Trách nhiệm

`Entitlement` là quyền dài hạn của một User đối với một Product. Limit được snapshot khi grant để Offer thay đổi không âm thầm thay đổi quyền đã cấp.

```sql
CREATE TYPE "EntitlementStatus" AS ENUM (
    'ACTIVE',
    'EXPIRED',
    'REVOKED'
);

CREATE TYPE "EntitlementGrantSource" AS ENUM (
    'FREE_ACQUISITION',
    'ORDER',
    'ADMIN_GRANT'
);

CREATE TABLE "Entitlement" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "customerId" UUID NOT NULL REFERENCES "User" (id),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "productOfferId" UUID REFERENCES "ProductOffer" (id),
    "orderItemId" UUID REFERENCES "OrderItem" (id),
    status "EntitlementStatus" NOT NULL DEFAULT 'ACTIVE',
    "grantSource" "EntitlementGrantSource" NOT NULL,
    "startsAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "expiresAt" TIMESTAMPTZ,
    "maxInstallations" INTEGER NOT NULL CHECK ("maxInstallations" > 0),
    "maxConcurrentDevices" INTEGER NOT NULL CHECK ("maxConcurrentDevices" > 0),

    -- Mock JSON: immutable snapshot of effective usage rights.
    -- {
    --   "schemaVersion": "1.0",
    --   "releaseAccess": "CURRENT_AND_SUPPORTED",
    --   "allowUpdates": true,
    --   "sourceOfferVersion": 1
    -- }
    "grantSnapshot" JSONB NOT NULL,

    "grantedById" UUID REFERENCES "User" (id),
    "revokedAt" TIMESTAMPTZ,
    "revokedById" UUID REFERENCES "User" (id),
    "revokedReason" TEXT,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,

    CONSTRAINT "Entitlement_period_check"
        CHECK ("expiresAt" IS NULL OR "expiresAt" > "startsAt"),
    CONSTRAINT "Entitlement_grantSnapshot_object_check"
        CHECK (jsonb_typeof("grantSnapshot") = 'object'),
    CONSTRAINT "Entitlement_revoke_fields_check" CHECK (
        status <> 'REVOKED'
        OR ("revokedAt" IS NOT NULL AND "revokedById" IS NOT NULL AND "revokedReason" IS NOT NULL)
    )
);

CREATE UNIQUE INDEX "Entitlement_active_customer_product_idx"
ON "Entitlement" ("customerId", "productId")
WHERE status = 'ACTIVE';
```

Expiration time vẫn phải được kiểm tra bằng `expiresAt > now()`; partial index không thể tự chuyển status theo thời gian. Worker/lazy update có thể chuyển record sang `EXPIRED`.

## 5. Entitlement Installation assignment

### Trách nhiệm

`EntitlementInstallation` cho biết Product entitlement được dùng trên Windows Installation nào. Đây là nơi enforce `maxInstallations` trong transaction/application policy.

```sql
CREATE TABLE "EntitlementInstallation" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "entitlementId" UUID NOT NULL REFERENCES "Entitlement" (id),
    "installationId" UUID NOT NULL REFERENCES "Installation" (id),
    "assignedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "releasedAt" TIMESTAMPTZ,
    "createdById" UUID NOT NULL REFERENCES "User" (id)
);

CREATE UNIQUE INDEX "EntitlementInstallation_active_pair_idx"
ON "EntitlementInstallation" ("entitlementId", "installationId")
WHERE "releasedAt" IS NULL;

CREATE INDEX "EntitlementInstallation_installation_active_idx"
ON "EntitlementInstallation" ("installationId")
WHERE "releasedAt" IS NULL;
```

DB unique index chống mapping trùng; transaction phải lock Entitlement và count active assignments trước khi insert.

## 6. Execution Lease

### Trách nhiệm

`ExecutionLease` là authorization tạm thời cho một production execution trên một Installation. Backend chỉ lưu token hash.

```sql
CREATE TYPE "ExecutionLeaseStatus" AS ENUM (
    'ACTIVE',
    'EXPIRED',
    'REVOKED',
    'COMPLETED'
);

CREATE TABLE "ExecutionLease" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "executionId" UUID NOT NULL UNIQUE,
    "entitlementId" UUID NOT NULL REFERENCES "Entitlement" (id),
    "customerId" UUID NOT NULL REFERENCES "User" (id),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "productReleaseId" UUID NOT NULL REFERENCES "ProductRelease" (id),
    "installationId" UUID NOT NULL REFERENCES "Installation" (id),
    "tokenHash" TEXT NOT NULL UNIQUE,
    status "ExecutionLeaseStatus" NOT NULL DEFAULT 'ACTIVE',
    "requestedDeviceCount" INTEGER NOT NULL CHECK ("requestedDeviceCount" > 0),
    "maxConcurrentDevices" INTEGER NOT NULL CHECK ("maxConcurrentDevices" > 0),

    -- Mock JSON: snapshot of authorization decision, never contains workflow key.
    -- {
    --   "schemaVersion": "1.0",
    --   "entitlementStatus": "ACTIVE",
    --   "installationStatus": "ACTIVE",
    --   "productStatus": "ACTIVE",
    --   "releaseStatus": "PUBLISHED",
    --   "capabilities": ["android.device.control"]
    -- }
    "grantSnapshot" JSONB NOT NULL,

    "issuedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "expiresAt" TIMESTAMPTZ NOT NULL,
    "lastValidatedAt" TIMESTAMPTZ,
    "renewedAt" TIMESTAMPTZ,
    "rotationCount" INTEGER NOT NULL DEFAULT 0 CHECK ("rotationCount" >= 0),
    "revokedAt" TIMESTAMPTZ,
    "revokedReason" TEXT,
    "completedAt" TIMESTAMPTZ,
    "updatedAt" TIMESTAMPTZ,

    CONSTRAINT "ExecutionLease_period_check" CHECK ("expiresAt" > "issuedAt"),
    CONSTRAINT "ExecutionLease_device_limit_check"
        CHECK ("requestedDeviceCount" <= "maxConcurrentDevices"),
    CONSTRAINT "ExecutionLease_grantSnapshot_object_check"
        CHECK (jsonb_typeof("grantSnapshot") = 'object'),
    CONSTRAINT "ExecutionLease_revoked_fields_check" CHECK (
        status <> 'REVOKED'
        OR ("revokedAt" IS NOT NULL AND "revokedReason" IS NOT NULL)
    )
);

CREATE INDEX "ExecutionLease_active_entitlement_idx"
ON "ExecutionLease" ("entitlementId", "expiresAt")
WHERE status = 'ACTIVE';

CREATE INDEX "ExecutionLease_active_installation_idx"
ON "ExecutionLease" ("installationId", "expiresAt")
WHERE status = 'ACTIVE';
```

Issue/renew lease phải serialize concurrency decision bằng transaction lock hoặc distributed lock. Runtime receives plaintext lease token and workflow key only in memory; neither plaintext value is stored here.

## 7. Execution Report

### Trách nhiệm

Backend chỉ nhận cloud run summary. Detailed node state/history thuộc Runtime Agent SQLite.

```sql
CREATE TYPE "ExecutionOutcome" AS ENUM (
    'SUCCEEDED',
    'FAILED',
    'CANCELLED',
    'INTERRUPTED'
);

CREATE TABLE "ExecutionReport" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "executionId" UUID NOT NULL UNIQUE,
    "executionLeaseId" UUID NOT NULL REFERENCES "ExecutionLease" (id),
    "runGroupId" VARCHAR(255) NOT NULL,
    outcome "ExecutionOutcome" NOT NULL,

    -- Mock JSON: aggregate only, no raw credential, ADB output or decrypted graph.
    -- {
    --   "schemaVersion": "1.0",
    --   "totalDevices": 3,
    --   "succeededDevices": 2,
    --   "failedDevices": 1,
    --   "cancelledDevices": 0,
    --   "durationMs": 125000,
    --   "failureCodes": ["DEVICE_OFFLINE"]
    -- }
    summary JSONB NOT NULL,

    "startedAt" TIMESTAMPTZ NOT NULL,
    "finishedAt" TIMESTAMPTZ NOT NULL,
    "receivedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "ExecutionReport_time_check" CHECK ("finishedAt" >= "startedAt"),
    CONSTRAINT "ExecutionReport_summary_object_check"
        CHECK (jsonb_typeof(summary) = 'object')
);
```

Unique `executionId` giúp endpoint report idempotent.

## 8. Product Report và moderation

### Trách nhiệm

MVP chỉ cần customer gửi report và admin resolve với reason.

```sql
CREATE TYPE "ProductReportStatus" AS ENUM (
    'OPEN',
    'RESOLVED',
    'DISMISSED'
);

CREATE TABLE "ProductReport" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "reporterUserId" UUID NOT NULL REFERENCES "User" (id),
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status "ProductReportStatus" NOT NULL DEFAULT 'OPEN',

    -- Mock JSON: references only to already uploaded evidence assets.
    -- {
    --   "schemaVersion": "1.0",
    --   "assetIds": ["uuid"],
    --   "releaseId": "uuid"
    -- }
    evidence JSONB NOT NULL DEFAULT '{}'::JSONB,

    "resolutionReason" TEXT,
    "resolvedAt" TIMESTAMPTZ,
    "resolvedById" UUID REFERENCES "User" (id),
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,

    CONSTRAINT "ProductReport_evidence_object_check"
        CHECK (jsonb_typeof(evidence) = 'object'),
    CONSTRAINT "ProductReport_resolution_check" CHECK (
        status = 'OPEN'
        OR ("resolutionReason" IS NOT NULL AND "resolvedAt" IS NOT NULL AND "resolvedById" IS NOT NULL)
    )
);

CREATE INDEX "ProductReport_status_createdAt_idx"
ON "ProductReport" (status, "createdAt");
```

## 9. Quan hệ chính

```text
Product
├── ProductOffer[]
├── OrderItem[] ── Order ── PaymentTransaction[]
├── Entitlement[]
│   ├── EntitlementInstallation[] ── Installation
│   └── ExecutionLease[] ── ProductRelease
│       └── ExecutionReport
└── ProductReport[]
```
