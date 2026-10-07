
# 28. Hướng triển khai theo giai đoạn

## Giai đoạn 1 — Technical spike

Mục tiêu: chứng minh có thể điều khiển nhiều LDPlayer.

Làm CLI Go:

```text
agent devices
agent tap --device ldplayer:0 --x 400 --y 700
agent screenshot --device ldplayer:1
```

Chứng minh:

- `list2` phát hiện nhiều instance;
- instance 0 và 1 được điều khiển riêng;
- nhận stdout/stderr;
- chụp screenshot riêng;
- một instance lỗi không ảnh hưởng instance khác.

## Giai đoạn 2 — Device layer

Xây:

- Device model;
- LDPlayer discovery;
- ADB discovery;
- Device Registry;
- DeviceController interface;
- ADBController;
- LDPlayerController;
- device exclusive lease.

## Giai đoạn 3 — Workflow Engine một thiết bị

Hỗ trợ:

- Start
- End
- Delay
- Tap
- Swipe
- Input Text
- If
- Repeat
- Screenshot
- Log

Chạy Runtime IR trên một thiết bị.

## Giai đoạn 4 — Multi-device scheduler

Thêm:

- Run Group;
- Device Execution;
- goroutine per selected device;
- concurrency semaphore;
- result aggregation;
- one-device-one-execution lock.

## Giai đoạn 5 — State và event

Thêm:

- SQLite;
- checkpoint;
- WebSocket;
- event history;
- Studio/Launcher reconnect;
- cancel/pause.

## Giai đoạn 6 — Observation

Thêm:

- Wait For Element;
- UI hierarchy;
- current activity;
- image matching;
- screenshot artifacts.

## Giai đoạn 7 — Background connector

Thêm:

- HTTP Request;
- Telegram;
- Google Sheets;
- connector worker pool;
- credential reference;
- idempotency key.

## Giai đoạn 8 — Production security

Thêm:

- package signature;
- encrypted release;
- execution lease;
- capability grants;
- log redaction;
- runtime compatibility checking.


# 29. Test strategy

## Unit test

Dùng fake handler và fake device:

```go
type FakeDeviceController struct {
    Results map[DeviceCommandType]DeviceCommandResult
}
```

Test:

- graph transition;
- If/Switch;
- loop sequence;
- retry;
- timeout;
- cancel;
- output validation;
- capability denial;
- device lock;
- independent variables giữa devices.

## Integration test không cần LDPlayer

Tạo fake ADB executable trả output fixture:

```text
fake-adb devices -l
fake-adb -s device-1 shell input tap ...
```

Giúp CI chạy được mà không cần Windows/LDPlayer thật.

## Integration test với LDPlayer

Chạy thủ công hoặc trên Windows test machine:

- 1 instance;
- 2–5 instances;
- một instance offline;
- một instance boot chậm;
- screenshot đồng thời;
- cancel giữa workflow;
- khởi động lại Agent.

## Concurrency test

Luôn chạy:

```bash
go test -race ./...
```

Thêm soak test:

```text
10 fake devices
100 node executions/device
random timeout
random disconnect
```

Kiểm tra:

- không data race;
- không goroutine leak;
- không mất event;
- không dùng nhầm device serial;
- không trộn variables giữa devices.
