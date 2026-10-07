# 03 — Product, Submission, Review và ProductRelease

## 1. Trách nhiệm nhóm

Nhóm này quản lý hành trình publish trên Marketplace:

```text
Saved Project
→ Web self-review
→ Product + Listing data
→ immutable WorkflowRevision
→ Submission
→ automated scan
→ admin review
→ immutable ProductRelease
→ public catalog
```

`Product` là identity ổn định. `ProductListing` là metadata hiển thị có thể cập nhật. `WorkflowRevision` và technical content của `ProductRelease` là immutable.

## 2. Taxonomy

### Trách nhiệm

Category/Tag phục vụ navigation và search cơ bản. MVP chỉ cần CRUD và assignment đơn giản.

```sql
CREATE TABLE "Category" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    description TEXT,
    "sortOrder" INTEGER NOT NULL DEFAULT 0,
    "isActive" BOOLEAN NOT NULL DEFAULT TRUE,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,
    "createdById" UUID NOT NULL REFERENCES "User" (id),
    "updatedById" UUID REFERENCES "User" (id)
);

CREATE UNIQUE INDEX "Category_slug_idx"
ON "Category" (lower(slug))
WHERE "deletedAt" IS NULL;

CREATE TABLE "Tag" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ
);

CREATE UNIQUE INDEX "Tag_slug_idx"
ON "Tag" (lower(slug))
WHERE "deletedAt" IS NULL;
```

## 3. Product identity

### Trách nhiệm

`Product` thuộc một Publisher và, trong MVP, liên kết với đúng một Studio Project. Product tồn tại xuyên suốt nhiều submission/release.

```sql
CREATE TYPE "ProductStatus" AS ENUM (
    'DRAFT',
    'ACTIVE',
    'SUSPENDED',
    'ARCHIVED'
);

CREATE TABLE "Product" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "publisherAccountId" UUID NOT NULL REFERENCES "PublisherAccount" (id),
    "projectId" UUID NOT NULL UNIQUE REFERENCES "Project" (id),
    status "ProductStatus" NOT NULL DEFAULT 'DRAFT',
    "statusReason" TEXT,
    "suspendedAt" TIMESTAMPTZ,
    "suspendedById" UUID REFERENCES "User" (id),
    "currentReleaseId" UUID,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,
    "createdById" UUID NOT NULL REFERENCES "User" (id),
    "updatedById" UUID REFERENCES "User" (id),

    CONSTRAINT "Product_suspended_fields_check" CHECK (
        status <> 'SUSPENDED'
        OR ("statusReason" IS NOT NULL AND "suspendedAt" IS NOT NULL AND "suspendedById" IS NOT NULL)
    )
);

CREATE INDEX "Product_publisher_status_idx"
ON "Product" ("publisherAccountId", status)
WHERE "deletedAt" IS NULL;
```

## 4. Product Listing và media

### Trách nhiệm

`ProductListing` lưu metadata hiển thị. Thay đổi listing không sửa technical release. Policy review lại listing nhạy cảm sẽ được thiết kế ở API layer sau.

```sql
CREATE TYPE "ListingVisibility" AS ENUM (
    'PRIVATE',
    'UNLISTED',
    'PUBLIC'
);

CREATE TABLE "ProductListing" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "productId" UUID NOT NULL UNIQUE REFERENCES "Product" (id),
    "categoryId" UUID REFERENCES "Category" (id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    "shortDescription" VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    "usageInstructions" TEXT,
    visibility "ListingVisibility" NOT NULL DEFAULT 'PRIVATE',
    "isFeatured" BOOLEAN NOT NULL DEFAULT FALSE,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "supportedAndroidVersions": ["11", "12", "13"],
    --   "testedLdPlayerVersions": ["9.1"],
    --   "targetPackages": ["com.example.game"]
    -- }
    "compatibilitySummary" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,
    "createdById" UUID NOT NULL REFERENCES "User" (id),
    "updatedById" UUID REFERENCES "User" (id),

    CONSTRAINT "ProductListing_compatibility_object_check"
        CHECK (jsonb_typeof("compatibilitySummary") = 'object')
);

CREATE UNIQUE INDEX "ProductListing_slug_idx"
ON "ProductListing" (lower(slug))
WHERE "deletedAt" IS NULL;

CREATE TABLE "ProductTag" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "tagId" UUID NOT NULL REFERENCES "Tag" (id),
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "ProductTag_product_tag_key" UNIQUE ("productId", "tagId")
);

CREATE TYPE "ProductMediaType" AS ENUM (
    'ICON',
    'SCREENSHOT',
    'VIDEO'
);

CREATE TABLE "ProductMedia" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "assetId" UUID NOT NULL REFERENCES "Asset" (id),
    type "ProductMediaType" NOT NULL,
    "sortOrder" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "deletedAt" TIMESTAMPTZ
);

CREATE UNIQUE INDEX "ProductMedia_product_asset_idx"
ON "ProductMedia" ("productId", "assetId")
WHERE "deletedAt" IS NULL;
```

## 5. Submission

### Trách nhiệm

`Submission` là request review immutable về content snapshot. Status thay đổi theo review, nhưng các JSON snapshot và `workflowRevisionId` không được ghi đè.

```sql
CREATE TYPE "SubmissionStatus" AS ENUM (
    'PENDING_SCAN',
    'READY_FOR_REVIEW',
    'CHANGES_REQUESTED',
    'APPROVED',
    'REJECTED'
);

CREATE TABLE "Submission" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "workflowRevisionId" UUID NOT NULL UNIQUE REFERENCES "WorkflowRevision" (id),
    "previousSubmissionId" UUID REFERENCES "Submission" (id),
    number INTEGER NOT NULL CHECK (number > 0),
    status "SubmissionStatus" NOT NULL DEFAULT 'PENDING_SCAN',

    -- Mock JSON: Product fields exactly as publisher confirmed at submit time.
    -- {
    --   "schemaVersion": "1.0",
    --   "productId": "uuid",
    --   "publisherAccountId": "uuid",
    --   "projectId": "uuid"
    -- }
    "productSnapshot" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "name": "Daily Reward Collector",
    --   "slug": "daily-reward-collector",
    --   "shortDescription": "Collect daily rewards",
    --   "description": "...",
    --   "categoryId": "uuid",
    --   "tagIds": ["uuid"],
    --   "media": [{"assetId":"uuid","type":"ICON","sortOrder":0}]
    -- }
    "listingSnapshot" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "version": "1.0.0",
    --   "changelog": "Initial release",
    --   "minimumLauncherVersion": "1.0.0",
    --   "minimumRuntimeVersion": "1.0.0"
    -- }
    "releaseRequest" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "purpose": "Collect daily reward",
    --   "targetPackages": ["com.example.game"],
    --   "testInstructions": "Use the provided test account",
    --   "knownLimitations": ["English UI only"]
    -- }
    "reviewMetadata" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "confirmed": true,
    --   "items": [
    --     {"code":"LISTING_MATCHES_BEHAVIOR","checked":true},
    --     {"code":"NO_RAW_CREDENTIALS","checked":true}
    --   ]
    -- }
    "selfReview" JSONB NOT NULL,

    "submittedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "submittedById" UUID NOT NULL REFERENCES "User" (id),
    "updatedAt" TIMESTAMPTZ,

    CONSTRAINT "Submission_product_number_key" UNIQUE ("productId", number),
    CONSTRAINT "Submission_json_objects_check" CHECK (
        jsonb_typeof("productSnapshot") = 'object'
        AND jsonb_typeof("listingSnapshot") = 'object'
        AND jsonb_typeof("releaseRequest") = 'object'
        AND jsonb_typeof("reviewMetadata") = 'object'
        AND jsonb_typeof("selfReview") = 'object'
    )
);

CREATE INDEX "Submission_status_submittedAt_idx"
ON "Submission" (status, "submittedAt");
```

Một transaction submit nên:

1. Lock/check ProjectDraft exact version.
2. Revalidate graph/IR/assets.
3. Create WorkflowRevision immutable.
4. Create/reuse Product và snapshot listing/release request.
5. Create Submission.
6. Create outbox event cho scan job.

## 6. Automated Scan

### Trách nhiệm

`SubmissionScan` lưu một lần scanner chạy. `SubmissionScanFinding` lưu finding có thể filter/query mà không phải parse một JSON result lớn.

```sql
CREATE TYPE "ScanStatus" AS ENUM (
    'QUEUED',
    'RUNNING',
    'PASSED',
    'FAILED',
    'ERROR'
);

CREATE TYPE "FindingSeverity" AS ENUM (
    'INFO',
    'WARNING',
    'ERROR'
);

CREATE TABLE "SubmissionScan" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "submissionId" UUID NOT NULL REFERENCES "Submission" (id),
    attempt INTEGER NOT NULL DEFAULT 1 CHECK (attempt > 0),
    status "ScanStatus" NOT NULL DEFAULT 'QUEUED',
    "scannerVersion" VARCHAR(100) NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "totalRules": 20,
    --   "passed": 18,
    --   "warnings": 1,
    --   "errors": 1
    -- }
    summary JSONB NOT NULL DEFAULT '{}'::JSONB,

    "startedAt" TIMESTAMPTZ,
    "finishedAt" TIMESTAMPTZ,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "SubmissionScan_submission_attempt_key"
        UNIQUE ("submissionId", attempt),
    CONSTRAINT "SubmissionScan_summary_object_check"
        CHECK (jsonb_typeof(summary) = 'object')
);

CREATE TABLE "SubmissionScanFinding" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "submissionScanId" UUID NOT NULL REFERENCES "SubmissionScan" (id),
    code VARCHAR(255) NOT NULL,
    severity "FindingSeverity" NOT NULL,
    message TEXT NOT NULL,
    "nodeId" VARCHAR(255),
    "assetId" UUID REFERENCES "Asset" (id),

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "jsonPath": "$.nodes[3].config.timeoutMs",
    --   "expected": "<= 60000",
    --   "actual": 120000
    -- }
    details JSONB NOT NULL DEFAULT '{}'::JSONB,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "SubmissionScanFinding_details_object_check"
        CHECK (jsonb_typeof(details) = 'object')
);
```

## 7. Admin Review

### Trách nhiệm

`SubmissionReview` là append-only history của admin decisions/feedback. `Submission.status` giữ current state để query queue nhanh.

```sql
CREATE TYPE "ReviewDecision" AS ENUM (
    'REQUEST_CHANGES',
    'APPROVE',
    'REJECT'
);

CREATE TABLE "SubmissionReview" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "submissionId" UUID NOT NULL REFERENCES "Submission" (id),
    decision "ReviewDecision" NOT NULL,
    reason TEXT,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "items": [
    --     {"code":"LISTING_ACCURACY","result":"PASS","comment":null},
    --     {"code":"CAPABILITY_JUSTIFIED","result":"CHANGE_REQUIRED","comment":"Explain HTTP access"}
    --   ]
    -- }
    checklist JSONB NOT NULL DEFAULT '{}'::JSONB,

    "reviewedById" UUID NOT NULL REFERENCES "User" (id),
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "SubmissionReview_checklist_object_check"
        CHECK (jsonb_typeof(checklist) = 'object'),
    CONSTRAINT "SubmissionReview_reason_check" CHECK (
        decision = 'APPROVE' OR reason IS NOT NULL
    )
);
```

## 8. ProductRelease

### Trách nhiệm

`ProductRelease` lưu immutable technical artifact metadata. Khi `PUBLISHED`, package fields không được update; disable chỉ thay status/reason.

```sql
CREATE TYPE "ProductReleaseStatus" AS ENUM (
    'PENDING_BUILD',
    'BUILDING',
    'PUBLISHED',
    'BUILD_FAILED',
    'DISABLED'
);

CREATE TABLE "ProductRelease" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "productId" UUID NOT NULL REFERENCES "Product" (id),
    "submissionId" UUID NOT NULL UNIQUE REFERENCES "Submission" (id),
    "workflowRevisionId" UUID NOT NULL REFERENCES "WorkflowRevision" (id),
    version VARCHAR(100) NOT NULL,
    status "ProductReleaseStatus" NOT NULL DEFAULT 'PENDING_BUILD',
    changelog TEXT NOT NULL,
    "minimumLauncherVersion" VARCHAR(100) NOT NULL,
    "minimumRuntimeVersion" VARCHAR(100) NOT NULL,
    "workflowSchemaVersion" VARCHAR(100) NOT NULL,
    "packageObjectKey" TEXT UNIQUE,
    "packageSizeBytes" BIGINT CHECK ("packageSizeBytes" IS NULL OR "packageSizeBytes" >= 0),
    "packageHash" TEXT,
    "payloadHash" TEXT,

    -- Mock JSON: public package manifest; packageHash stays outside the package.
    -- {
    --   "formatVersion": "1.0",
    --   "productId": "uuid",
    --   "releaseId": "uuid",
    --   "version": "1.0.0",
    --   "entryWorkflowId": "main",
    --   "payload": {"path":"workflow.enc","hash":"sha256:..."}
    -- }
    manifest JSONB,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "algorithm": "AES-256-GCM",
    --   "keyId": "release-key-uuid",
    --   "nonceEncoding": "base64"
    -- }
    -- Không lưu plaintext encryption key.
    "encryptionMetadata" JSONB,

    -- Mock JSON:
    -- {"schemaVersion":"1.0","capabilities":["android.device.control"]}
    "requiredCapabilities" JSONB NOT NULL,

    -- Mock JSON Schema copied from approved revision for Launcher form generation.
    "inputSchema" JSONB NOT NULL,

    "publishedAt" TIMESTAMPTZ,
    "disabledAt" TIMESTAMPTZ,
    "disabledById" UUID REFERENCES "User" (id),
    "disabledReason" TEXT,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,

    CONSTRAINT "ProductRelease_product_version_key"
        UNIQUE ("productId", version),
    CONSTRAINT "ProductRelease_json_objects_check" CHECK (
        (manifest IS NULL OR jsonb_typeof(manifest) = 'object')
        AND ("encryptionMetadata" IS NULL OR jsonb_typeof("encryptionMetadata") = 'object')
        AND jsonb_typeof("requiredCapabilities") = 'object'
        AND jsonb_typeof("inputSchema") = 'object'
    ),
    CONSTRAINT "ProductRelease_published_artifact_check" CHECK (
        status <> 'PUBLISHED'
        OR (
            "packageObjectKey" IS NOT NULL
            AND "packageHash" IS NOT NULL
            AND "payloadHash" IS NOT NULL
            AND manifest IS NOT NULL
            AND "encryptionMetadata" IS NOT NULL
            AND "publishedAt" IS NOT NULL
        )
    ),
    CONSTRAINT "ProductRelease_disabled_fields_check" CHECK (
        status <> 'DISABLED'
        OR ("disabledAt" IS NOT NULL AND "disabledById" IS NOT NULL AND "disabledReason" IS NOT NULL)
    )
);

ALTER TABLE "Product"
ADD CONSTRAINT "Product_currentReleaseId_fkey"
FOREIGN KEY ("currentReleaseId") REFERENCES "ProductRelease" (id);
```

Application transaction đặt current release phải xác nhận release thuộc đúng Product và đang `PUBLISHED`; FK một mình không enforce được điều kiện đó.

## 9. Quan hệ chính

```text
PublisherAccount
└── Product ── Project
    ├── ProductListing ── Category
    ├── ProductTag[] ── Tag
    ├── ProductMedia[] ── Asset
    ├── Submission[] ── WorkflowRevision
    │   ├── SubmissionScan[]
    │   │   └── SubmissionScanFinding[]
    │   └── SubmissionReview[]
    └── ProductRelease[]
```
