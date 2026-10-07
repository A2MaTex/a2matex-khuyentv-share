
# 30. Kiến trúc MVP

```mermaid
flowchart TB
    CLIENT["Studio / Launcher"]
    API["Local HTTP + WebSocket"]
    SCHED["Scheduler"]
    REG["Device Registry"]
    COORD["Run Group Coordinator"]

    E1["Execution Runner A"]
    E2["Execution Runner B"]
    E3["Execution Runner C"]

    ENG["Workflow Engine"]
    HAND["Handler Registry"]

    ADB["ADB Controller"]
    LDP["LDPlayer Controller"]
    CON["Connector Executors"]

    DB["SQLite"]
    EVT["Event Bus"]

    CLIENT <--> API
    API --> SCHED
    REG --> SCHED
    SCHED --> COORD

    COORD --> E1
    COORD --> E2
    COORD --> E3

    E1 --> ENG
    E2 --> ENG
    E3 --> ENG

    ENG --> HAND
    HAND --> ADB
    HAND --> LDP
    HAND --> CON

    ENG --> DB
    ENG --> EVT
    EVT --> API
```


Runtime Agent nên được xây như một **local workflow execution daemon bằng Go**, không phải một tập script ADB.

Mô hình triển khai cốt lõi:

1. `Device Registry` phát hiện tất cả LDPlayer/ADB device.
2. Launcher cho người dùng chọn thiết bị.
3. `Scheduler` tạo một device execution cho mỗi thiết bị được chọn.
4. Mỗi device execution chạy trong một goroutine độc lập.
5. Mỗi thiết bị có exclusive lease để không bị hai workflow điều khiển cùng lúc.
6. Workflow Engine chạy node tuần tự trên từng thiết bị.
7. Android handler chuyển node thành typed `DeviceCommand`.
8. Device Adapter chuyển command thành ADB/LDPlayer CLI.
9. Background handler gọi connector mà không phụ thuộc màn hình Android.
10. SQLite lưu checkpoint; Event Bus cập nhật Studio/Launcher.
11. Command thành công chỉ xác nhận thao tác được gửi; muốn xác nhận nghiệp vụ phải có observation node hoặc external verification.

Thứ tự triển khai hợp lý nhất là: **device discovery → command adapter → single-device engine → multi-device scheduler → persistence/event → connector → license/security**. Nếu spike đầu tiên chưa điều khiển độc lập được hai LDPlayer instance và lấy screenshot riêng từ từng instance, chưa nên đi tiếp sang Marketplace hoặc mã hóa workflow.