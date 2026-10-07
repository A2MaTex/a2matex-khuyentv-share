# 05 — Audit, Jobs, Outbox, Notification, Idempotency và Key Reference

## 1. Trách nhiệm nhóm

Nhóm này hỗ trợ reliability và operation của các domain khác. Không tạo abstraction trước khi có use case thực tế; mỗi vertical slice chỉ dùng phần cần thiết.

## 2. Audit Log

### Trách nhiệm

`AuditLog` là append-only record cho mutation nhạy cảm. Audit log khác application log: nó trả lời ai đã thay đổi resource nào, từ gì sang gì, lúc nào.

```sql
CREATE TYPE "AuditActorType" AS ENUM (
    'USER',
    'SYSTEM',
    'WORKER'
);

CREATE TABLE "AuditLog" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "actorType" "AuditActorType" NOT NULL,
    "actorUserId" UUID REFERENCES "User" (id),
    action VARCHAR(255) NOT NULL,
    "resourceType" VARCHAR(255) NOT NULL,
    "resourceId" UUID,
    "correlationId" VARCHAR(255),

    -- Mock JSON: sanitized fields before mutation.
    -- {
    --   "schemaVersion": "1.0",
    --   "status": "ACTIVE"
    -- }
    "beforeData" JSONB,

    -- Mock JSON: sanitized fields after mutation.
    -- {
    --   "schemaVersion": "1.0",
    --   "status": "BLOCKED",
    --   "blockedReason": "Repeated policy violations"
    -- }
    "afterData" JSONB,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "ip": "203.0.113.10",
    --   "userAgent": "Mozilla/5.0 ...",
    --   "requestId": "req_01"
    -- }
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,

    "occurredAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "AuditLog_json_objects_check" CHECK (
        ("beforeData" IS NULL OR jsonb_typeof("beforeData") = 'object')
        AND ("afterData" IS NULL OR jsonb_typeof("afterData") = 'object')
        AND jsonb_typeof(metadata) = 'object'
    ),
    CONSTRAINT "AuditLog_actor_check" CHECK (
        "actorType" <> 'USER' OR "actorUserId" IS NOT NULL
    )
);

CREATE INDEX "AuditLog_resource_idx"
ON "AuditLog" ("resourceType", "resourceId", "occurredAt" DESC);

CREATE INDEX "AuditLog_actor_idx"
ON "AuditLog" ("actorUserId", "occurredAt" DESC)
WHERE "actorUserId" IS NOT NULL;
```

Không đưa password hash, token, credential, workflow key hoặc raw sensitive payload vào audit JSON.

## 3. Transactional Outbox

### Trách nhiệm

`OutboxEvent` được insert trong cùng database transaction với domain change. Worker publish/dispatch sau commit, tránh mất scan/build/notification job.

```sql
CREATE TYPE "OutboxEventStatus" AS ENUM (
    'PENDING',
    'PROCESSING',
    'PUBLISHED',
    'FAILED'
);

CREATE TABLE "OutboxEvent" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "eventType" VARCHAR(255) NOT NULL,
    "aggregateType" VARCHAR(255) NOT NULL,
    "aggregateId" UUID NOT NULL,
    status "OutboxEventStatus" NOT NULL DEFAULT 'PENDING',

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "submissionId": "uuid",
    --   "workflowRevisionId": "uuid"
    -- }
    payload JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "correlationId": "req_01",
    --   "causationId": "submission_01"
    -- }
    headers JSONB NOT NULL DEFAULT '{}'::JSONB,

    attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    "availableAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "lockedAt" TIMESTAMPTZ,
    "publishedAt" TIMESTAMPTZ,
    "lastError" TEXT,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT "OutboxEvent_json_objects_check" CHECK (
        jsonb_typeof(payload) = 'object'
        AND jsonb_typeof(headers) = 'object'
    )
);

CREATE INDEX "OutboxEvent_dispatch_idx"
ON "OutboxEvent" (status, "availableAt")
WHERE status IN ('PENDING', 'FAILED');
```

## 4. Background Job

### Trách nhiệm

`BackgroundJob` theo dõi công việc dài như scan, package build và cleanup. Nếu dùng external queue, table này vẫn là business/job status cho UI và retry tracking, không thay thế queue broker.

```sql
CREATE TYPE "BackgroundJobStatus" AS ENUM (
    'QUEUED',
    'RUNNING',
    'SUCCEEDED',
    'FAILED',
    'CANCELLED'
);

CREATE TABLE "BackgroundJob" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(255) NOT NULL,
    status "BackgroundJobStatus" NOT NULL DEFAULT 'QUEUED',
    "resourceType" VARCHAR(255) NOT NULL,
    "resourceId" UUID NOT NULL,
    "deduplicationKey" VARCHAR(500),

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "submissionId": "uuid",
    --   "scanAttempt": 1
    -- }
    payload JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "submissionScanId": "uuid",
    --   "status": "PASSED"
    -- }
    result JSONB,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "code": "OBJECT_STORAGE_TIMEOUT",
    --   "retryable": true,
    --   "message": "Safe diagnostic message"
    -- }
    error JSONB,

    attempt INTEGER NOT NULL DEFAULT 0 CHECK (attempt >= 0),
    "maxAttempts" INTEGER NOT NULL DEFAULT 3 CHECK ("maxAttempts" > 0),
    "availableAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "startedAt" TIMESTAMPTZ,
    "finishedAt" TIMESTAMPTZ,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,

    CONSTRAINT "BackgroundJob_json_objects_check" CHECK (
        jsonb_typeof(payload) = 'object'
        AND (result IS NULL OR jsonb_typeof(result) = 'object')
        AND (error IS NULL OR jsonb_typeof(error) = 'object')
    )
);

CREATE UNIQUE INDEX "BackgroundJob_deduplicationKey_idx"
ON "BackgroundJob" ("deduplicationKey")
WHERE "deduplicationKey" IS NOT NULL
  AND status IN ('QUEUED', 'RUNNING');

CREATE INDEX "BackgroundJob_queue_idx"
ON "BackgroundJob" (status, "availableAt")
WHERE status IN ('QUEUED', 'FAILED');
```

## 5. Idempotency Record

### Trách nhiệm

`IdempotencyRecord` chống client retry tạo duplicate cho endpoint có side effect. Scope nên gắn với actor + operation, không dùng một key global thiếu ngữ cảnh.

```sql
CREATE TYPE "IdempotencyStatus" AS ENUM (
    'PROCESSING',
    'COMPLETED',
    'FAILED'
);

CREATE TABLE "IdempotencyRecord" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scope VARCHAR(255) NOT NULL,
    key VARCHAR(255) NOT NULL,
    "actorUserId" UUID REFERENCES "User" (id),
    "requestHash" TEXT NOT NULL,
    status "IdempotencyStatus" NOT NULL DEFAULT 'PROCESSING',
    "responseStatus" INTEGER,

    -- Mock JSON: safe API response replay; must not include token/key/credential.
    -- {
    --   "schemaVersion": "1.0",
    --   "data": {"submissionId": "uuid", "status": "PENDING_SCAN"}
    -- }
    "responseBody" JSONB,

    "resourceType" VARCHAR(255),
    "resourceId" UUID,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "expiresAt" TIMESTAMPTZ NOT NULL,

    CONSTRAINT "IdempotencyRecord_scope_key" UNIQUE (scope, key),
    CONSTRAINT "IdempotencyRecord_response_object_check" CHECK (
        "responseBody" IS NULL OR jsonb_typeof("responseBody") = 'object'
    )
);

CREATE INDEX "IdempotencyRecord_expiresAt_idx"
ON "IdempotencyRecord" ("expiresAt");
```

Không lưu response chứa access token, refresh token, lease token hoặc workflow key để replay lâu dài.

## 6. Notification

### Trách nhiệm

`Notification` hỗ trợ in-app notification tối thiểu cho review result, release và entitlement. Email/push delivery có thể bổ sung sau.

```sql
CREATE TABLE "Notification" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "userId" UUID NOT NULL REFERENCES "User" (id),
    type VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,

    -- Mock JSON: routing data only.
    -- {
    --   "schemaVersion": "1.0",
    --   "submissionId": "uuid",
    --   "productId": "uuid",
    --   "targetPath": "/publisher/submissions/uuid"
    -- }
    data JSONB NOT NULL DEFAULT '{}'::JSONB,

    "readAt" TIMESTAMPTZ,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "Notification_data_object_check"
        CHECK (jsonb_typeof(data) = 'object')
);

CREATE INDEX "Notification_user_unread_idx"
ON "Notification" ("userId", "createdAt" DESC)
WHERE "readAt" IS NULL;
```

## 7. Encryption Key Reference

### Trách nhiệm

`EncryptionKeyReference` lưu reference tới KMS/secret provider. Không lưu raw key material trong PostgreSQL.

```sql
CREATE TYPE "EncryptionKeyStatus" AS ENUM (
    'ACTIVE',
    'RETIRED',
    'REVOKED'
);

CREATE TABLE "EncryptionKeyReference" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    purpose VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    "externalKeyId" TEXT NOT NULL,
    status "EncryptionKeyStatus" NOT NULL DEFAULT 'ACTIVE',

    -- Mock JSON: non-secret KMS metadata.
    -- {
    --   "schemaVersion": "1.0",
    --   "algorithm": "AES-256-GCM",
    --   "providerRegion": "ap-southeast-1",
    --   "rotationVersion": 1
    -- }
    metadata JSONB NOT NULL DEFAULT '{}'::JSONB,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "retiredAt" TIMESTAMPTZ,
    CONSTRAINT "EncryptionKeyReference_provider_external_key"
        UNIQUE (provider, "externalKeyId"),
    CONSTRAINT "EncryptionKeyReference_metadata_object_check"
        CHECK (jsonb_typeof(metadata) = 'object')
);

ALTER TABLE "ProductRelease"
ADD COLUMN "releaseKeyId" UUID REFERENCES "EncryptionKeyReference" (id);
```

Trong migration thật, `releaseKeyId` nên được thêm cùng slice Package Builder/Encryption và chuyển `NOT NULL` trước khi release đầu tiên được publish.

## 8. Không cần PostgreSQL table riêng

### Cache

Redis/cache là derived data. Source of truth vẫn là PostgreSQL. Không thiết kế `Cache` table.

### Application log, metric và trace

Đẩy sang log/metrics/tracing backend, không lưu trong business database.

### Configuration và secret

Non-secret configuration đi qua environment/config provider. Secret nằm trong secret manager hoặc protected environment, không lưu plaintext trong PostgreSQL.

### Presigned download URL

Presigned URL có thời hạn ngắn và không cần table riêng. Nếu cần audit download, ghi sanitized AuditLog hoặc tạo DownloadEvent sau khi có requirement cụ thể.
