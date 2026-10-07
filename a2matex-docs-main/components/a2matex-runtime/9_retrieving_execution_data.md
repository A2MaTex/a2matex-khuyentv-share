# 20. Agent nhận dữ liệu từ LDPlayer được không?

Có, nhưng phải hiểu rằng LDPlayer không tự động “gửi toàn bộ trạng thái app” cho Agent.

Agent có thể lấy dữ liệu qua những cơ chế sau:

| Dữ liệu | Cách lấy |
|---|---|
| Command result | stdout, stderr, exit code |
| Screenshot | `screencap` |
| UI hierarchy | `uiautomator dump` |
| Current package/activity | `dumpsys activity` |
| Device properties | `getprop` |
| File trong thiết bị | `adb pull` hoặc shell cat |
| System/app logs | `logcat`, nếu có quyền và phù hợp |
| Installed packages | package manager |
| Screen size/DPI | `wm size`, `wm density` |
| Custom structured event | Cần app-side bridge riêng |

Ví dụ result:

```go
type DeviceCommandResult struct {
    ExitCode int
    Stdout   []byte
    Stderr   []byte

    StartedAt  time.Time
    FinishedAt time.Time

    ArtifactIDs []string
}
```

Node handler chuyển raw result thành output có kiểu:

```json
{
  "success": true,
  "durationMs": 182
}
```

## Không có push event mặc định

ADB chủ yếu hoạt động theo request/response:

```text
Agent gửi command
→ thiết bị thực hiện
→ Agent nhận output
```

Nếu muốn thiết bị chủ động gửi event realtime, cần một trong các cơ chế:

- theo dõi `logcat`;
- polling UI/state;
- socket/port forwarding;
- cài một Android companion agent do A2MaTeX kiểm soát.

MVP chưa cần Android companion agent. Có thể dùng:

- command result;
- screenshot;
- UI hierarchy;
- polling có timeout.

# 21. Event và kết quả trả về Studio/Launcher

Runtime Agent không nên chỉ giữ kết quả trong goroutine. Mỗi thay đổi trạng thái phải tạo event:

```go
type ExecutionEvent struct {
    ID          string
    RunGroupID  string
    ExecutionID string
    DeviceID    string

    Type       EventType
    NodeID     string
    Sequence   int
    Iteration  int

    Payload    map[string]any
    OccurredAt time.Time
}
```

Ví dụ:

```json
{
  "type": "NODE_SUCCEEDED",
  "runGroupId": "run_01",
  "executionId": "exec_device_a",
  "deviceId": "ldplayer:0",
  "nodeId": "tap_login",
  "sequence": 8,
  "payload": {
    "durationMs": 130
  }
}
```

Event flow:

```text
Execution Runner
→ lưu state SQLite
→ publish Event Bus
→ WebSocket
→ Launcher/Studio
```

Quan trọng: **lưu trước hoặc cùng transaction với state rồi mới broadcast**. Nếu UI đang đóng, event vẫn tồn tại trong SQLite và có thể đọc lại.
