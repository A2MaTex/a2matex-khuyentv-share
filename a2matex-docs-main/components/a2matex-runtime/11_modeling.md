
# 22. Local persistence

Dùng SQLite là đủ.

Các bảng logic:

```text
run_groups
device_executions
node_executions
execution_events
execution_variables
artifacts
device_snapshots
background_jobs
```

## `run_groups`

```text
id
workflow_release_id
status
total_devices
running_devices
succeeded_devices
failed_devices
created_at
started_at
finished_at
```

## `device_executions`

```text
id
run_group_id
device_id
status
current_node_id
current_sequence
inputs_json
variables_json
error_json
started_at
finished_at
```

## `node_executions`

```text
id
device_execution_id
node_id
sequence
loop_iteration
status
input_json
output_json
error_json
started_at
finished_at
```

## `execution_events`

Dùng cho UI history và troubleshooting.

Không cần lưu mọi screenshot dưới dạng blob trong SQLite. Lưu file vào Artifact Store và DB chỉ giữ metadata/path.


# 23. Checkpoint và crash recovery

Sau mỗi node:

1. Ghi node result.
2. Cập nhật variables.
3. Cập nhật current node.
4. Tăng sequence.
5. Cập nhật device execution.
6. Tạo event.

Tất cả nên nằm trong một SQLite transaction.

Tuy nhiên không nên tự động resume mọi workflow sau crash trong MVP.

Ví dụ:

```text
Runtime gửi Telegram thành công
→ Agent crash trước khi commit node success
→ Khi restart, không biết có nên gửi lại không
```

Vì vậy MVP:

- đọc lại execution đang `RUNNING`;
- chuyển thành `INTERRUPTED`;
- hiển thị cho người dùng;
- không tự resume;
- cho phép chạy lại thủ công.

Resume an toàn chỉ thực hiện sau khi phân loại node:

- idempotent;
- retry-safe;
- side-effecting;
- non-repeatable.


# 24. State machine

## Run group

```text
CREATED
  → QUEUED
  → RUNNING
  → SUCCEEDED
  → FAILED
  → CANCELLED
  → INTERRUPTED
```

## Device execution

```text
PENDING
  → QUEUED
  → RUNNING
  → PAUSED_USER
  → PAUSED_LICENSE
  → PAUSED_DEVICE_OFFLINE
  → SUCCEEDED
  → FAILED
  → CANCELLED
  → INTERRUPTED
```

## Node execution

```text
PENDING
  → RUNNING
  → SUCCEEDED
  → RETRYING
  → FAILED
  → TIMED_OUT
  → CANCELLED
```


# 25. Pause, resume và cancel

Mỗi run group có root context:

```go
runCtx, cancel := context.WithCancel(agentCtx)
```

Mỗi node có timeout context:

```go
nodeCtx, nodeCancel := context.WithTimeout(
    runCtx,
    node.Timeout,
)
```

Quan hệ:

```text
Agent context
└── Run group context
    └── Device execution context
        └── Node execution timeout context
```

Cancel run group sẽ propagate xuống tất cả node đang chạy.

## Pause

Pause không nhất thiết giết node ngay lập tức.

Phương án MVP:

- không bắt đầu node mới;
- node hiện tại hoàn thành hoặc timeout;
- execution chuyển `PAUSED`;
- resume tiếp tục từ node kế tiếp.

Với Android action rất ngắn như Tap, cách này an toàn hơn cancel giữa subprocess.


# 26. Capability enforcement

Trước khi gọi handler:

```go
capabilityGate.Authorize(
    releaseCapabilities,
    executionLease,
    customerGrant,
    node.RequiredCapabilities,
)
```

Ví dụ Tap cần:

```text
android.device.control
```

Screenshot cần:

```text
android.screen.capture
```

Google Sheets cần:

```text
connector.google_sheets.write
```

HTTP Request cần:

```text
network.http
```

Code node không được tự gọi các adapter này. Chỉ system handler đã đăng ký mới có quyền.
