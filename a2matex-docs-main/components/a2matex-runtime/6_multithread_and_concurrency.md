# 15. Chạy subprocess ADB an toàn

## Subprocess là gì?

Runtime Agent là process chính:

```text
a2matex-runtime-agent.exe
```

Khi cần chạy một Android action, Agent tạo một process con:

```text
a2matex-runtime-agent.exe
└── adb.exe -s emulator-5554 shell input tap 500 700
```

`adb.exe` là subprocess. Nó kết nối với ADB server, gửi command tới Android rồi trả kết quả cho Runtime Agent.

```text
Node Handler
→ exec.CommandContext
→ tạo adb.exe subprocess
→ ADB server
→ LDPlayer instance
→ stdout/stderr/exit code
→ Node Handler
```

## Tại sao dùng `exec.CommandContext`?

```go
cmd := exec.CommandContext(
    ctx,
    a.binaryPath,
    "-s",
    serial,
    "shell",
    "input",
    "tap",
    "500",
    "700",
)
```

Hàm này:

- chạy đúng executable `adb.exe`;
- truyền từng argument riêng biệt;
- không mở `cmd.exe`;
- chờ subprocess kết thúc;
- có thể kill subprocess khi timeout hoặc cancel;
- nhận stdout, stderr và exit code.

Nó chỉ block goroutine đang thực thi node, không block toàn bộ Runtime Agent. Các device execution khác vẫn tiếp tục chạy.

## Vòng đời một command

```go
func (a *ADBExecutor) Execute(
    ctx context.Context,
    serial string,
    args ...string,
) (CommandResult, error) {
    commandArgs := append(
        []string{"-s", serial},
        args...,
    )

    cmd := exec.CommandContext(
        ctx,
        a.binaryPath,
        commandArgs...,
    )

    var stdout bytes.Buffer
    var stderr bytes.Buffer

    cmd.Stdout = &stdout
    cmd.Stderr = &stderr

    startedAt := time.Now()
    err := cmd.Run()
    finishedAt := time.Now()

    result := CommandResult{
        Stdout:     stdout.Bytes(),
        Stderr:     stderr.Bytes(),
        StartedAt:  startedAt,
        FinishedAt: finishedAt,
    }

    if err != nil {
        return result, NewADBError(err, result)
    }

    return result, nil
}
```

Các bước thực tế:

1. `exec.CommandContext` tạo cấu hình command.
2. `cmd.Run()` khởi động `adb.exe`.
3. Windows tạo process con.
4. `adb.exe` gửi lệnh tới ADB server.
5. ADB server gửi lệnh tới đúng device serial.
6. Output được ghi vào `stdout` hoặc `stderr`.
7. `adb.exe` kết thúc.
8. Runtime nhận kết quả và trả cho handler.

## Timeout và cancel

Node handler tạo context có timeout:

```go
nodeCtx, cancel := context.WithTimeout(
    executionCtx,
    10*time.Second,
)
defer cancel()

result, err := adbExecutor.Execute(
    nodeCtx,
    device.ADBSerial,
    "shell",
    "input",
    "tap",
    "500",
    "700",
)
```

Nếu quá 10 giây:

```text
Context hết hạn
→ exec.CommandContext kill adb.exe
→ Execute trả context deadline exceeded
→ node chuyển TIMED_OUT
```

Lưu ý: kill `adb.exe` không bảo đảm hủy một thao tác đã được gửi tới Android. Ví dụ lệnh Tap có thể đã được thực hiện trước khi subprocess bị kill. Vì vậy retry các action có side effect phải được cân nhắc.

## Không gọi thông qua `cmd /c`

Không dùng:

```go
exec.Command(
    "cmd",
    "/c",
    "adb -s " + serial + " shell " + userInput,
)
```

Vì toàn bộ command trở thành một chuỗi để Windows shell phân tích:

```text
adb ... & del file
adb ... | another-command
```

Nếu `userInput` chứa shell metacharacter, có thể chạy thêm command ngoài ý muốn.

Thay vào đó, truyền từng argument:

```go
exec.CommandContext(
    ctx,
    adbPath,
    "-s",
    serial,
    "shell",
    "input",
    "tap",
    strconv.Itoa(x),
    strconv.Itoa(y),
)
```

## Handler không truyền raw command

Không nên cho handler nhận:

```json
{
  "command": "shell input tap 500 700"
}
```

Nên dùng typed command:

```go
type TapCommand struct {
    X int
    Y int
}
```

Adapter chuyển typed command thành arguments:

```go
func buildTapArgs(command TapCommand) []string {
    return []string{
        "shell",
        "input",
        "tap",
        strconv.Itoa(command.X),
        strconv.Itoa(command.Y),
    }
}
```

Nhờ đó publisher chỉ cung cấp tọa độ, không thể chèn thêm shell command.

## Nhiều thiết bị chạy đồng thời

Mỗi `DeviceExecution` chạy trong goroutine riêng:

```text
Goroutine A → adb.exe -s emulator-5554 ...
Goroutine B → adb.exe -s emulator-5556 ...
Goroutine C → adb.exe -s emulator-5558 ...
```

Các subprocess kết nối tới cùng ADB server nhưng luôn chỉ định serial riêng. Runtime cần semaphore để không tạo quá nhiều `adb.exe` cùng lúc.

Với MVP, tạo một subprocess cho mỗi command là đủ đơn giản và dễ kiểm soát. Chưa cần duy trì interactive ADB shell lâu dài.

## Xử lý node timeout và tiếp tục workflow

Timeout của một node không làm dừng toàn bộ `DeviceExecution`. Mỗi node sử dụng một child context riêng:

```go
nodeCtx, cancel := context.WithTimeout(
    executionCtx,
    node.Timeout,
)

output, err := handler.Execute(nodeCtx, input)
cancel()
```

Khi node timeout, Workflow Engine ghi trạng thái `TIMED_OUT` rồi đi theo `timeout edge`:

```text
Wait For Element
├── found   → Continue
└── timeout → Tap Close → Continue
```

Node Tap tiếp theo được tạo bằng context mới từ `executionCtx`, không tái sử dụng context đã timeout:

```go
if errors.Is(err, context.DeadlineExceeded) {
    execution.CurrentNodeID = node.Outputs["timeout"]
    execution.Sequence++
}
```

Cần phân biệt:

- **Timeout nghiệp vụ:** chờ element hoặc điều kiện không thành công; có thể đi thẳng sang nhánh recovery.
- **Timeout hạ tầng:** ADB hoặc thiết bị không phản hồi; Runtime phải probe lại thiết bị trước khi chạy node tiếp theo.

```text
ADB timeout
→ kill subprocess hiện tại
→ probe thiết bị
    ├── healthy → chạy timeout/error branch
    └── offline → pause hoặc fail DeviceExecution
```

Ví dụ kết quả:

```text
Sequence 10: WaitForElement → TIMED_OUT
Sequence 11: TapClose       → SUCCEEDED
Sequence 12: Continue       → RUNNING
```

Result đến muộn của sequence 10 phải bị bỏ qua vì execution đã chuyển sang sequence 11.