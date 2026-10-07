## 13. Handler Registry

`Handler Registry` ánh xạ loại node và version sang handler Go thực thi node đó.

```go
type NodeType string

const (
    NodeTypeAndroidTap       NodeType = "android.tap"
    NodeTypeAndroidSwipe     NodeType = "android.swipe"
    NodeTypeAndroidInputText NodeType = "android.input_text"
    NodeTypeAndroidLaunchApp NodeType = "android.launch_app"

    NodeTypeFlowIf     NodeType = "flow.if"
    NodeTypeFlowSwitch NodeType = "flow.switch"
    NodeTypeFlowDelay  NodeType = "flow.delay"
    NodeTypeFlowRepeat NodeType = "flow.repeat"

    NodeTypeTelegramSend NodeType = "telegram.send_message"
    NodeTypeSheetsAppend NodeType = "google_sheets.append_row"
)

type NodeVersion int
```

Mọi handler triển khai chung interface:

```go
type NodeHandler interface {
    Execute(
        ctx context.Context,
        input NodeExecutionInput,
    ) (NodeExecutionOutput, error)
}
```

Registry:

```go
type HandlerKey struct {
    Type    NodeType
    Version NodeVersion
}

type HandlerRegistry struct {
    handlers map[HandlerKey]NodeHandler
}
```

Đăng ký và lấy handler:

```go
registry.Register(
    HandlerKey{
        Type:    NodeTypeAndroidTap,
        Version: 1,
    },
    NewTapHandler(deviceController),
)

handler, exists := registry.Get(
    HandlerKey{
        Type:    NodeType(node.Type),
        Version: NodeVersion(node.Version),
    },
)

if !exists {
    return ErrUnsupportedNodeHandler
}

output, err := handler.Execute(ctx, input)
```

Runtime IR và DB vẫn lưu string:

```json
{
  "type": "android.tap",
  "version": 1
}
```

Registry chỉ đảm nhiệm:

```text
NodeType + Version → NodeHandler
```