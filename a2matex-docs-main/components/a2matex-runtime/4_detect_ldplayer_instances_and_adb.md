Đúng, mình đã sửa nhầm nội dung mục 7. Đây là hai mục thay thế chính xác:

## 6. Phát hiện LDPlayer instance

MVP sử dụng trực tiếp toolchain trong thư mục cài đặt LDPlayer:

```text
C:\LDPlayer\LDPlayer14
├── ldconsole.exe
├── ld.exe
└── adb.exe
```

Người dùng chỉ cần cấu hình thư mục cài đặt:

```json
{
  "providers": {
    "ldplayer": {
      "enabled": true,
      "installDir": "C:\\LDPlayer\\LDPlayer14",
      "discoveryIntervalMs": 2000
    }
  }
}
```

Runtime tự suy ra đường dẫn tới các executable, không yêu cầu cài Android Platform Tools riêng.

Agent dùng:

```powershell
.\ldconsole.exe list2
```

để lấy danh sách instance:

```text
0,LDPlayer,2032678,1704928,1,7456,3500
1,LDPlayer-1,852422,590830,1,3772,3180
```

Mỗi dòng gồm:

```text
index, name, topWindowHandle, bindWindowHandle,
androidStarted, processId, vmProcessId
```

Agent chuẩn hóa thành:

```go
type LDPlayerInstance struct {
    Index            int
    Name             string
    AndroidStarted   bool
    ProcessID        int
    VMProcessID      int
    TopWindowHandle  int64
    BindWindowHandle int64
}
```

Một goroutine refresh định kỳ:

```go
func (d *LDPlayerDiscovery) Watch(ctx context.Context) {
    ticker := time.NewTicker(2 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            d.Refresh(ctx)
        }
    }
}
```

Mỗi lần refresh:

1. Chạy `ldconsole list2`.
2. Parse danh sách instance.
3. Cập nhật `Device Registry`.
4. Đánh dấu instance đang boot, online hoặc stopped.
5. Phát event khi thiết bị thay đổi.

---

## 7. Phát hiện thiết bị ADB

Runtime sử dụng `adb.exe` có sẵn trong thư mục LDPlayer:

```text
C:\LDPlayer\LDPlayer14\adb.exe
```

Không sử dụng thêm ADB từ Android Platform Tools trong MVP để tránh xung đột phiên bản hoặc restart ADB server.

Agent chạy:

```powershell
.\adb.exe devices -l
```

Ví dụ:

```text
List of devices attached
emulator-5554    device product:leidian model:LDPlayer device:ldplayer
emulator-5556    device product:leidian model:LDPlayer device:ldplayer
```

Parser tạo ADB endpoint:

```go
type ADBEndpoint struct {
    Serial string
    State  ADBDeviceState
    Model  string
    Product string
}
```

Các trạng thái cần xử lý:

```go
const (
    ADBDeviceOnline       = "device"
    ADBDeviceOffline      = "offline"
    ADBDeviceUnauthorized = "unauthorized"
)
```

Agent kết hợp kết quả của hai nguồn:

```text
ldconsole list2
        +
bundled adb devices -l
        ↓
Device Registry
```

`ldconsole list2` là nguồn chính để biết LDPlayer instance nào tồn tại. `adb devices -l` cho biết instance nào đã sẵn sàng nhận ADB command.

Device cuối cùng:

```go
type Device struct {
    ID             string
    Provider       string
    Name           string

    LDPlayerIndex  int
    ADBSerial      string

    State          DeviceState
    AndroidStarted bool
    ADBReady       bool

    LastSeenAt     time.Time
}
```

Ví dụ sau khi ánh xạ:

```json
{
  "id": "ldplayer:0",
  "name": "LDPlayer",
  "ldPlayerIndex": 0,
  "adbSerial": "emulator-5554",
  "androidStarted": true,
  "adbReady": true,
  "state": "ONLINE"
}
```

Nếu instance xuất hiện trong `list2` nhưng chưa có trong `adb devices`:

```json
{
  "id": "ldplayer:0",
  "ldPlayerIndex": 0,
  "adbSerial": "",
  "androidStarted": true,
  "adbReady": false,
  "state": "BOOTING"
}
```

Trong trường hợp đó, Agent chưa tạo execution cho thiết bị và tiếp tục probe ở chu kỳ refresh tiếp theo. Nếu ADB vẫn không nhận diện được, Runtime có thể fallback sang:

```powershell
.\ld.exe -s <index> ...
```

hoặc:

```powershell
.\ldconsole.exe adb --index <index> --command "shell ..."
```

Như vậy, `ldconsole` chịu trách nhiệm phát hiện instance, còn bundled `adb.exe` xác nhận instance đã sẵn sàng nhận Android command.