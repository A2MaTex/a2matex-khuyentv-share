# 02 — Node Catalog, Project, Workflow Revision và Asset

## 1. Trách nhiệm nhóm

Nhóm này lưu phần cloud của Studio:

- Backend công bố Node Catalog có version.
- Studio tạo/sync mutable Project Draft.
- Asset binary nằm trong Object Storage; PostgreSQL lưu metadata và ownership.
- Khi publisher submit trên Web, Backend chốt đúng draft version thành immutable Workflow Revision.
- Submission review revision đó, không review draft đang tiếp tục thay đổi.

## 2. Capability vocabulary

### Trách nhiệm

`Capability` là vocabulary ổn định dùng chung cho Node Catalog, scan, release manifest và Runtime authorization.

```sql
CREATE TABLE "Capability" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    "isSensitive" BOOLEAN NOT NULL DEFAULT FALSE,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ
);
```

Ví dụ code:

```text
android.device.control
android.screen.capture
android.ui.observe
network.http
connector.google_sheets.write
```

## 3. Node Catalog

### Trách nhiệm

`NodeDefinition` là identity ổn định của node type. `NodeDefinitionVersion` là immutable contract cho một version cụ thể.

```sql
CREATE TYPE "NodeDefinitionStatus" AS ENUM (
    'ACTIVE',
    'DEPRECATED',
    'DISABLED'
);

CREATE TABLE "NodeDefinition" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    status "NodeDefinitionStatus" NOT NULL DEFAULT 'ACTIVE',
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ
);

CREATE TABLE "NodeDefinitionVersion" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "nodeDefinitionId" UUID NOT NULL REFERENCES "NodeDefinition" (id),
    version INTEGER NOT NULL CHECK (version > 0),
    "runtimeHandler" VARCHAR(255) NOT NULL,
    "minimumRuntimeVersion" VARCHAR(100) NOT NULL,
    "defaultTimeoutMs" INTEGER NOT NULL CHECK ("defaultTimeoutMs" > 0),

    -- Mock JSON Schema:
    -- {
    --   "$schema": "https://json-schema.org/draft/2020-12/schema",
    --   "type": "object",
    --   "required": ["target"],
    --   "properties": {
    --     "target": {"$ref": "a2matex://schemas/interaction-target/1.0"}
    --   },
    --   "additionalProperties": false
    -- }
    "configSchema" JSONB NOT NULL,

    -- Mock JSON Schema:
    -- {
    --   "type": "object",
    --   "properties": {
    --     "x": {"type": "number"},
    --     "y": {"type": "number"}
    --   },
    --   "additionalProperties": false
    -- }
    "inputSchema" JSONB NOT NULL,

    -- Mock JSON Schema:
    -- {
    --   "type": "object",
    --   "required": ["dispatched"],
    --   "properties": {
    --     "dispatched": {"type": "boolean"},
    --     "durationMs": {"type": "integer"}
    --   }
    -- }
    "outputSchema" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "ports": [
    --     {"key": "success", "kind": "CONTROL"},
    --     {"key": "error", "kind": "ERROR"}
    --   ]
    -- }
    "outputPorts" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "icon": "tap",
    --   "fieldOrder": ["target", "timeoutMs"],
    --   "customEditors": {"target": "interaction-target-picker"}
    -- }
    "editorHints" JSONB NOT NULL DEFAULT '{}'::JSONB,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "supported": ["STOP", "RETRY_THEN_STOP", "ERROR_BRANCH"]
    -- }
    "supportedErrorPolicies" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "publishedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "createdById" UUID NOT NULL REFERENCES "User" (id),

    CONSTRAINT "NodeDefinitionVersion_node_version_key"
        UNIQUE ("nodeDefinitionId", version),
    CONSTRAINT "NodeDefinitionVersion_json_objects_check" CHECK (
        jsonb_typeof("configSchema") = 'object'
        AND jsonb_typeof("inputSchema") = 'object'
        AND jsonb_typeof("outputSchema") = 'object'
        AND jsonb_typeof("outputPorts") = 'object'
        AND jsonb_typeof("editorHints") = 'object'
        AND jsonb_typeof("supportedErrorPolicies") = 'object'
    )
);

CREATE TABLE "NodeDefinitionCapability" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "nodeDefinitionVersionId" UUID NOT NULL REFERENCES "NodeDefinitionVersion" (id),
    "capabilityId" UUID NOT NULL REFERENCES "Capability" (id),
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "NodeDefinitionCapability_version_capability_key"
        UNIQUE ("nodeDefinitionVersionId", "capabilityId")
);
```

Không sửa một `NodeDefinitionVersion` đã publish. Thay đổi schema/handler contract tạo version mới.

## 4. Cloud Project và mutable Draft

### Trách nhiệm

`Project` là container cloud của Studio thuộc Publisher. `ProjectDraft` giữ snapshot mutable mới nhất với optimistic version để chống ghi đè giữa nhiều Studio session.

```sql
CREATE TYPE "ProjectStatus" AS ENUM (
    'ACTIVE',
    'ARCHIVED'
);

CREATE TABLE "Project" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "publisherAccountId" UUID NOT NULL REFERENCES "PublisherAccount" (id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status "ProjectStatus" NOT NULL DEFAULT 'ACTIVE',
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,
    "createdById" UUID NOT NULL REFERENCES "User" (id),
    "updatedById" UUID REFERENCES "User" (id)
);

CREATE INDEX "Project_publisherAccountId_status_idx"
ON "Project" ("publisherAccountId", status)
WHERE "deletedAt" IS NULL;

CREATE TABLE "ProjectDraft" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "projectId" UUID NOT NULL UNIQUE REFERENCES "Project" (id),
    version BIGINT NOT NULL DEFAULT 1 CHECK (version > 0),

    -- Mock JSON: editable Studio graph, including editor-only position metadata.
    -- {
    --   "schemaVersion": "1.0",
    --   "entryNodeId": "start_01",
    --   "nodes": [
    --     {
    --       "id": "tap_01",
    --       "type": "android.tap",
    --       "version": 1,
    --       "config": {},
    --       "bindings": {},
    --       "editor": {"x": 420, "y": 180}
    --     }
    --   ],
    --   "edges": []
    -- }
    "editorGraph" JSONB NOT NULL,

    -- Mock JSON Schema:
    -- {
    --   "$schema": "https://json-schema.org/draft/2020-12/schema",
    --   "type": "object",
    --   "required": ["accountName"],
    --   "properties": {"accountName": {"type": "string"}}
    -- }
    "inputSchema" JSONB NOT NULL,

    -- Mock JSON: compiler output cached for Web self-review; Backend revalidates on finalize.
    -- {
    --   "irVersion": "1.0",
    --   "entryNodeId": "start_01",
    --   "nodes": [],
    --   "requiredCapabilities": ["android.device.control"]
    -- }
    "runtimeIr" JSONB,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "status": "VALID_WITH_WARNINGS",
    --   "errors": [],
    --   "warnings": [{"code": "UNTESTED_BRANCH", "nodeId": "if_01"}]
    -- }
    "validationSummary" JSONB NOT NULL DEFAULT '{}'::JSONB,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "runtimeVersion": "0.1.0",
    --   "lastTestedAt": "2026-10-04T10:00:00Z",
    --   "successfulRuns": 2,
    --   "failedRuns": 0
    -- }
    "testSummary" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "contentHash" TEXT,
    "savedAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "savedById" UUID NOT NULL REFERENCES "User" (id),

    CONSTRAINT "ProjectDraft_json_objects_check" CHECK (
        jsonb_typeof("editorGraph") = 'object'
        AND jsonb_typeof("inputSchema") = 'object'
        AND ("runtimeIr" IS NULL OR jsonb_typeof("runtimeIr") = 'object')
        AND jsonb_typeof("validationSummary") = 'object'
        AND jsonb_typeof("testSummary") = 'object'
    )
);
```

Save contract dùng `projectId + expectedVersion`. Update thành công tăng `version`. Web submission phải gửi exact draft version đã self-review.

## 5. Asset

### Trách nhiệm

`Asset` lưu metadata/ownership của object; binary nằm ở Object Storage. `ProjectAsset` gắn asset mutable với project. Revision sẽ snapshot asset bằng mapping riêng.

```sql
CREATE TYPE "AssetType" AS ENUM (
    'IMAGE_TEMPLATE',
    'OCR_RESOURCE',
    'ICON',
    'SCREENSHOT',
    'VIDEO',
    'OTHER'
);

CREATE TYPE "AssetStatus" AS ENUM (
    'UPLOADING',
    'READY',
    'QUARANTINED',
    'DELETED'
);

CREATE TABLE "Asset" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "ownerUserId" UUID NOT NULL REFERENCES "User" (id),
    type "AssetType" NOT NULL,
    status "AssetStatus" NOT NULL DEFAULT 'UPLOADING',
    "objectKey" TEXT NOT NULL UNIQUE,
    "originalFileName" TEXT NOT NULL,
    "contentType" VARCHAR(255) NOT NULL,
    "sizeBytes" BIGINT NOT NULL CHECK ("sizeBytes" >= 0),
    "sha256" TEXT,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "width": 1080,
    --   "height": 1920,
    --   "durationMs": null,
    --   "ocrLanguages": []
    -- }
    "mediaMetadata" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "updatedAt" TIMESTAMPTZ,
    "deletedAt" TIMESTAMPTZ,

    CONSTRAINT "Asset_mediaMetadata_object_check"
        CHECK (jsonb_typeof("mediaMetadata") = 'object')
);

CREATE TABLE "ProjectAsset" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "projectId" UUID NOT NULL REFERENCES "Project" (id),
    "assetId" UUID NOT NULL REFERENCES "Asset" (id),
    alias VARCHAR(255) NOT NULL,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "deletedAt" TIMESTAMPTZ
);

CREATE UNIQUE INDEX "ProjectAsset_project_alias_idx"
ON "ProjectAsset" ("projectId", lower(alias))
WHERE "deletedAt" IS NULL;

CREATE UNIQUE INDEX "ProjectAsset_project_asset_idx"
ON "ProjectAsset" ("projectId", "assetId")
WHERE "deletedAt" IS NULL;
```

## 6. Immutable Workflow Revision

### Trách nhiệm

`WorkflowRevision` là snapshot backend tạo từ đúng ProjectDraft version lúc submit trên Web. Record này không update content và không soft delete.

```sql
CREATE TABLE "WorkflowRevision" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "projectId" UUID NOT NULL REFERENCES "Project" (id),
    number INTEGER NOT NULL CHECK (number > 0),
    "sourceDraftVersion" BIGINT NOT NULL CHECK ("sourceDraftVersion" > 0),

    -- Mock JSON: frozen Editor Graph, giữ metadata để admin/publisher inspect.
    -- {"schemaVersion":"1.0","entryNodeId":"start_01","nodes":[],"edges":[]}
    "editorGraph" JSONB NOT NULL,

    -- Mock JSON: canonical executable representation.
    -- {
    --   "irVersion": "1.0",
    --   "entryNodeId": "start_01",
    --   "nodes": [
    --     {
    --       "id": "start_01",
    --       "handler": {"type": "flow.start", "version": 1},
    --       "bindings": {},
    --       "transitions": {"success": "end_01"}
    --     }
    --   ]
    -- }
    "runtimeIr" JSONB NOT NULL,

    -- Mock JSON Schema: same meaning as ProjectDraft.inputSchema.
    "inputSchema" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "nodes": [
    --     {"type": "android.tap", "version": 1, "definitionVersionId": "uuid"}
    --   ]
    -- }
    "nodeVersionLock" JSONB NOT NULL,

    -- Mock JSON:
    -- {
    --   "schemaVersion": "1.0",
    --   "capabilities": ["android.device.control", "android.ui.observe"]
    -- }
    "capabilityManifest" JSONB NOT NULL,

    -- Mock JSON:
    -- {"schemaVersion":"1.0","status":"VALID","errors":[],"warnings":[]}
    "validationSummary" JSONB NOT NULL,

    -- Mock JSON:
    -- {"schemaVersion":"1.0","runtimeVersion":"0.1.0","successfulRuns":2}
    "testSummary" JSONB NOT NULL DEFAULT '{}'::JSONB,

    "contentHash" TEXT NOT NULL,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    "createdById" UUID NOT NULL REFERENCES "User" (id),

    CONSTRAINT "WorkflowRevision_project_number_key"
        UNIQUE ("projectId", number),
    CONSTRAINT "WorkflowRevision_project_draftVersion_key"
        UNIQUE ("projectId", "sourceDraftVersion"),
    CONSTRAINT "WorkflowRevision_json_objects_check" CHECK (
        jsonb_typeof("editorGraph") = 'object'
        AND jsonb_typeof("runtimeIr") = 'object'
        AND jsonb_typeof("inputSchema") = 'object'
        AND jsonb_typeof("nodeVersionLock") = 'object'
        AND jsonb_typeof("capabilityManifest") = 'object'
        AND jsonb_typeof("validationSummary") = 'object'
        AND jsonb_typeof("testSummary") = 'object'
    )
);

CREATE TABLE "WorkflowRevisionAsset" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    "workflowRevisionId" UUID NOT NULL REFERENCES "WorkflowRevision" (id),
    "assetId" UUID NOT NULL REFERENCES "Asset" (id),
    alias VARCHAR(255) NOT NULL,
    "assetHash" TEXT NOT NULL,
    "createdAt" TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT "WorkflowRevisionAsset_revision_alias_key"
        UNIQUE ("workflowRevisionId", alias),
    CONSTRAINT "WorkflowRevisionAsset_revision_asset_key"
        UNIQUE ("workflowRevisionId", "assetId")
);
```

`WorkflowRevisionAsset.assetHash` đóng băng expected content. Asset object không được overwrite; thay đổi asset tạo object/Asset mới.

## 7. Quan hệ chính

```text
Capability
└── NodeDefinitionCapability
    └── NodeDefinitionVersion
        └── NodeDefinition

PublisherAccount
└── Project
    ├── ProjectDraft                 # mutable, one current row
    ├── ProjectAsset[] → Asset
    └── WorkflowRevision[]           # immutable
        └── WorkflowRevisionAsset[] → Asset
```

## 8. Không lưu trong Backend DB

- Studio viewport history, undo stack hoặc local crash-recovery files.
- Test credentials và raw secrets.
- Asset binary/blob.
- Runtime development execution detail; Runtime Agent giữ local execution state.
