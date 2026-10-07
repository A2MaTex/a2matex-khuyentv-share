# 14. Chuyển node thành Android action

Mỗi handler tạo một `DeviceCommand` có kiểu rõ ràng, không ghép shell command tùy ý.

```go
type DeviceCommand struct {
    Type DeviceCommandType

    Tap        *TapCommand
    LongPress  *LongPressCommand
    Swipe      *SwipeCommand
    InputText  *InputTextCommand
    LaunchApp  *LaunchAppCommand
    Screenshot *ScreenshotCommand
}
```

## Target

Tap và Long Press hỗ trợ ba cách xác định vị trí:

```go
type TargetMode string

const (
    TargetCoordinates TargetMode = "coordinates"
    TargetNormalized  TargetMode = "normalized"
    TargetSelector    TargetMode = "selector"
)

type SelectorStrategy string

const (
    SelectorResourceID         SelectorStrategy = "resource_id"
    SelectorText               SelectorStrategy = "text"
    SelectorContentDescription SelectorStrategy = "content_description"
    SelectorClassName          SelectorStrategy = "class_name"
)

type InteractionTarget struct {
    Mode TargetMode

    X float64
    Y float64

    Selector *ElementSelector
}
```

## Tap theo tọa độ

```json
{
  "type": "android.tap",
  "config": {
    "target": {
      "mode": "normalized",
      "x": 0.5,
      "y": 0.75
    }
  }
}
```

Handler chuyển tọa độ tương đối thành pixel rồi gọi:

```powershell
adb -s <serial> shell input tap 540 1440
```

## Tap theo selector

```json
{
  "type": "android.tap",
  "config": {
    "target": {
      "mode": "selector",
      "selector": {
        "strategy": "resource_id",
        "value": "com.example.app:id/login_button",
        "matchIndex": 0
      }
    },
    "waitTimeoutMs": 5000
  }
}
```

ADB không tap trực tiếp bằng selector. Runtime phải lấy UI hierarchy:

```powershell
adb -s <serial> shell uiautomator dump /sdcard/window.xml
adb -s <serial> exec-out cat /sdcard/window.xml
```

Sau đó:

1. Tìm element theo `resource-id`, text hoặc content description.
2. Đọc `bounds`, ví dụ `[120,650][520,750]`.
3. Tính tọa độ tâm `(320,700)`.
4. Gọi `input tap 320 700`.

Logic tìm element được tách thành:

```go
type ElementLocator interface {
    Find(
        ctx context.Context,
        device Device,
        selector ElementSelector,
    ) (Element, error)
}
```

## Long Press

Long Press dùng cùng target với Tap:

```json
{
  "type": "android.long_press",
  "config": {
    "target": {
      "mode": "selector",
      "selector": {
        "strategy": "text",
        "value": "Delete"
      }
    },
    "durationMs": 1000
  }
}
```

Sau khi resolve tọa độ:

```powershell
adb -s <serial> shell input swipe 320 700 320 700 1000
```

## Swipe

```powershell
adb -s <serial> shell input swipe 500 1500 500 400 500
```

## Input Text

```powershell
adb -s <serial> shell input text <escaped-text>
```

Adapter phải xử lý khoảng trắng, Unicode và ký tự đặc biệt. Không chạy chuỗi do người dùng nhập qua `cmd /c`.

## Launch App

```powershell
adb -s <serial> shell am start ...
```

Handler nhận package/activity đã validate rồi tạo command tương ứng.

## Screenshot

```powershell
adb -s <serial> exec-out screencap -p
```

PNG bytes được lưu vào Artifact Store:

```json
{
  "artifactId": "artifact_01",
  "width": 1080,
  "height": 1920
}
```

Selector chỉ hoạt động nếu ứng dụng expose UI element qua Android Accessibility/UIAutomator. Với game, Canvas, Unity hoặc một số WebView, Runtime phải sử dụng tọa độ, tọa độ tương đối, tìm ảnh hoặc OCR.