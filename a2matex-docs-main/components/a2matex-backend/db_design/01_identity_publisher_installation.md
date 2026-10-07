# 01 — Identity, Publisher, Terms và Installation

## 1. Trách nhiệm nhóm

Nhóm này trả lời bốn câu hỏi:

1. User là ai và session nào đang đăng nhập?
2. User có role/permission nào?
3. User có đủ điều kiện thực hiện nghiệp vụ Publisher không?
4. Launcher installation nào thuộc user và có được phép download/request lease không?

`Device` hiện có là **Auth Device/session context**. `Installation` là một bản cài Launcher ổn định trên máy Windows. LDPlayer/ADB device thuộc Runtime Agent, không lưu trong Backend PostgreSQL.

## 2. Auth, User và RBAC — schema đã có

Source of truth hiện tại là `a2matex-be/prisma/schema.prisma` và các migration đã apply. Không tạo lại các table này trong migration mới.

| Entity | Trách nhiệm |
| --- | --- |
| `User` | Credential, username/email và trạng thái account |
| `Profile` | Thông tin cá nhân/public profile; Publisher không copy dữ liệu này |
| `VerificationCode` | OTP theo email và purpose |
| `Device` | Auth device/session metadata; một user có nhiều Device |
| `RefreshToken` | Refresh token gắn bắt buộc với User và Device |
| `Role` | Role hệ thống như `CUSTOMER`, `PUBLISHER`, `ADMIN` |
| `Permission` | HTTP route permission |
| `UserRole` | User ↔ Role |
| `RolePermission` | Role ↔ Permission |

Các constraint nền hiện tại cần được giữ:

```sql
-- Existing logical constraints; shown for design reference only.
CREATE UNIQUE INDEX "User_username_idx"
ON "User" (lower(username))
WHERE "deletedAt" IS NULL;

CREATE UNIQUE INDEX "User_email_idx"
ON "User" (lower(email))
WHERE "deletedAt" IS NULL;

CREATE UNIQUE INDEX "Profile_userId_idx"
ON "Profile" ("userId")
WHERE "deletedAt" IS NULL;

CREATE UNIQUE INDEX "RefreshToken_token_idx"
ON "RefreshToken" (token)
WHERE "deletedAt" IS NULL;

CREATE UNIQUE INDEX "RolePermission_roleId_permissionId_idx"
ON "RolePermission" ("roleId", "permissionId")
WHERE "deletedAt" IS NULL;
```

Lưu ý: token storage hiện tại thuộc Auth implementation. Khi hardening security, nên đánh giá migration từ refresh token plaintext sang token hash, nhưng không đưa thay đổi đó vào schema core MVP khi chưa thiết kế rotation/revocation đầy đủ.

## 3. Publisher Account

### Trách nhiệm

`PublisherAccount` quản lý khả năng publish của User, không phải public publisher profile. Public data đọc từ `User + Profile` theo whitelist.

```sql
CREATE TYPE "PublisherAccountStatus" AS ENUM (
    'ACTIVE',
    'BLOCKED'
);

CREATE TABLE "PublisherAccount" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "userId" UUID NOT NULL UNIQUE REFERENCES "User" (id),
    status "PublisherAccountStatus" NOT NULL DEFAULT 'ACTIVE',
    "activatedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),

    "blockedReason" TEXT,
    "blockedAt" TIMESTAMPTZ,
    "blockedById" UUID REFERENCES "User" (id),

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,

    CONSTRAINT "PublisherAccount_blocked_fields_check" CHECK (
        (status = 'ACTIVE' AND "blockedAt" IS NULL AND "blockedById" IS NULL)
        OR
        (status = 'BLOCKED' AND "blockedReason" IS NOT NULL AND "blockedAt" IS NOT NULL AND "blockedById" IS NOT NULL)
    )
);
```

Business access policy:

```text
User ACTIVE
AND PUBLISHER role ACTIVE
AND PublisherAccount ACTIVE
AND accepted current PUBLISHER_TERMS
```

## 4. Terms

### Trách nhiệm

`Term` lưu versioned legal/business terms. Chỉ `DRAFT` được sửa. `ACTIVE` và `ARCHIVED` là immutable content. Mỗi type chỉ có một bản active.

```sql
CREATE TYPE "TermType" AS ENUM (
    'PUBLISHER_TERMS',
    'CUSTOMER_TERMS',
    'PRIVACY_POLICY'
);

CREATE TYPE "TermStatus" AS ENUM (
    'DRAFT',
    'ACTIVE',
    'ARCHIVED'
);

CREATE TABLE "Term" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type "TermType" NOT NULL,
    version VARCHAR(100) NOT NULL,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    status "TermStatus" NOT NULL DEFAULT 'DRAFT',
    "publishedAt" TIMESTAMPTZ,

    "createdById" UUID NOT NULL REFERENCES "User" (id),
    "updatedById" UUID REFERENCES "User" (id),
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,

    CONSTRAINT "Term_type_version_key" UNIQUE (type, version),
    CONSTRAINT "Term_publishedAt_check" CHECK (
        (status = 'DRAFT' AND "publishedAt" IS NULL)
        OR
        (status IN ('ACTIVE', 'ARCHIVED') AND "publishedAt" IS NOT NULL)
    )
);

CREATE UNIQUE INDEX "Term_one_active_type_idx"
ON "Term" (type)
WHERE status = 'ACTIVE' AND "deletedAt" IS NULL;
```

`PublisherTermsAcceptance` là immutable evidence cho biết account đã chấp nhận đúng version nào.

```sql
CREATE TABLE "PublisherTermsAcceptance" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "publisherAccountId" UUID NOT NULL REFERENCES "PublisherAccount" (id),
    "termId" UUID NOT NULL REFERENCES "Term" (id),
    "acceptedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "ip": "203.0.113.10",
    --   "userAgent": "Mozilla/5.0 ..."
    -- }
    -- Chỉ lưu metadata audit an toàn; không lưu access token hoặc fingerprint bí mật.
    "acceptanceMetadata" JSONB NOT NULL DEFAULT '{}'::JSONB,

    CONSTRAINT "PublisherTermsAcceptance_account_term_key"
        UNIQUE ("publisherAccountId", "termId"),
    CONSTRAINT "PublisherTermsAcceptance_metadata_object_check"
        CHECK (jsonb_typeof("acceptanceMetadata") = 'object')
);
```

## 5. Windows Launcher Installation

### Trách nhiệm

`Installation` là định danh ổn định của một Launcher install. Nó là input cho download authorization, entitlement installation limit và execution lease.

```sql
CREATE TYPE "InstallationStatus" AS ENUM (
    'ACTIVE',
    'INACTIVE',
    'BLOCKED'
);

CREATE TABLE "Installation" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "userId" UUID NOT NULL REFERENCES "User" (id),
    "clientKey" UUID NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL DEFAULT 'WINDOWS',
    "osVersion" VARCHAR(255),
    "launcherVersion" VARCHAR(100) NOT NULL,
    "runtimeVersion" VARCHAR(100),
    "machineFingerprintHash" TEXT,
    status "InstallationStatus" NOT NULL DEFAULT 'ACTIVE',
    "statusReason" TEXT,
    "lastSeenAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "blockedAt" TIMESTAMPTZ,
    "blockedById" UUID REFERENCES "User" (id),

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "architecture": "x64",
    --   "runtimeMode": "production",
    --   "supportedPackageFormats": ["a2m/1.0"]
    -- }
    -- Dùng cho compatibility/risk metadata không cần query quan hệ.
    "clientMetadata" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,
    "createdById" UUID NOT NULL REFERENCES "User" (id),
    "updatedById" UUID REFERENCES "User" (id),

    CONSTRAINT "Installation_clientMetadata_object_check"
        CHECK (jsonb_typeof("clientMetadata") = 'object'),
    CONSTRAINT "Installation_blocked_fields_check" CHECK (
        status <> 'BLOCKED'
        OR ("statusReason" IS NOT NULL AND "blockedAt" IS NOT NULL AND "blockedById" IS NOT NULL)
    )
);

CREATE INDEX "Installation_userId_status_idx"
ON "Installation" ("userId", status)
WHERE "deletedAt" IS NULL;
```

`clientKey` không phải credential. Mọi request vẫn cần access token và ownership check.

## 6. Quan hệ chính

```text
User
├── Profile
├── Device[]                    # auth sessions
├── UserRole[]
├── PublisherAccount
│   └── PublisherTermsAcceptance[] → Term
└── Installation[]              # Launcher installations
```

## 7. Không lưu trong nhóm này

- LDPlayer instance hoặc ADB serial.
- Raw machine fingerprint.
- Lease token plaintext.
- Runtime node/execution state.
- Public publisher data copy tách khỏi Profile.
