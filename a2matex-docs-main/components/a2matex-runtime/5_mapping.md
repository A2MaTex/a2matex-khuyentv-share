
# 8. Có cần ánh xạ LDPlayer index với ADB serial không?

Có hai cách.

## Cách 1: Điều khiển LDPlayer qua index

```powershell
dnconsole.exe adb --index 0 --command "shell input tap 500 700"
```

Ưu điểm:

- không cần biết serial;
- dễ ánh xạ với Multi-Instance Manager;
- biết chính xác instance nào được điều khiển.

Nhược điểm:

- phụ thuộc LDPlayer;
- khó dùng chung với máy Android thật.

## Cách 2: Điều khiển bằng ADB serial

```powershell
adb -s 127.0.0.1:5555 shell input tap 500 700
```

Ưu điểm:

- dùng chung cho LDPlayer và Android thật;
- ít phụ thuộc vendor;
- kiến trúc adapter đơn giản.

Nhược điểm:

- phải ánh xạ instance ↔ serial;
- ADB trên Windows có thể có trạng thái offline hoặc xung đột port; chính LDPlayer cũng thừa nhận ADB có thể offline hoặc bị chiếm port và cung cấp `ld.exe` như một lựa chọn khác.

## Phương án đề xuất

Tạo interface chung:

```go
type DeviceController interface {
    Execute(
        ctx context.Context,
        device Device,
        command DeviceCommand,
    ) (DeviceCommandResult, error)

    Probe(
        ctx context.Context,
        device Device,
    ) (DeviceInfo, error)
}
```

Có hai implementation:

```text
GenericADBController
LDPlayerController
```

MVP có thể ưu tiên:

- LDPlayer → điều khiển bằng `ldconsole --index`;
- Android thật → điều khiển bằng `adb -s serial`.

Sau này có thể cho `LDPlayerController` ưu tiên ADB serial và fallback sang `ld.exe/ldconsole`.

Workflow và node handler không biết phía dưới đang dùng ADB serial hay LDPlayer index.


# 9. Agent có tự tạo goroutine theo số LDPlayer instance không?

Không theo cách:

```go
for range numberOfLDPlayers {
    go runWorkflow()
}
```

Discovery chỉ tạo danh sách thiết bị khả dụng. Khi customer chọn thiết bị A, B và C rồi bấm Run, Scheduler mới tạo ba `DeviceExecution`.

```text
Phát hiện được: A, B, C, D, E
Customer chọn: A, C, E

Run Group
├── goroutine → DeviceExecution A
├── goroutine → DeviceExecution C
└── goroutine → DeviceExecution E
```

LDPlayer B và D vẫn nằm trong Device Registry nhưng không chạy workflow.
