
# 5. Mô hình Node của A2MaTeX

## 5.1. Các phần của một node instance

```ts
interface WorkflowNode {
  id: string;
  type: string;
  version: number;
  name: string;

  config: Record<string, unknown>;
  bindings: Record<string, DataBinding>;

  timeoutMs?: number;
  retryPolicy?: RetryPolicy;
  errorPolicy?: ErrorPolicy;

  editor: {
    x: number;
    y: number;
  };
}
```

Cần phân biệt:

- **Definition:** do A2MaTeX developer cung cấp.
- **Instance:** node mà publisher kéo vào graph.
- **Handler:** code trong Runtime Agent thực hiện node.
- **Execution:** một lần node instance được chạy trên một device execution.

Một node trong vòng lặp có một instance ID, nhưng có thể tạo ra nhiều node execution với sequence khác nhau.

## 5.2. Input, config và output không phải một thứ

Ví dụ node `Tap`:

- Config: phương thức xác định vị trí, timeout.
- Input: tọa độ động hoặc selector lấy từ execution.
- Context: device serial hiện tại.
- Output: thời gian thực hiện và kết quả.
- Error: thiết bị offline, target không tìm thấy, timeout.

Không nên trộn tất cả vào một JSON `params` không schema. Nếu làm vậy, sau này không thể type-check, sinh form hoặc migrate node an toàn.

## 5.3. Execution context

Mỗi handler nhận context:

```ts
interface NodeExecutionContext {
  runGroupId: string;
  executionId: string;
  deviceId: string;

  workflowInputs: Record<string, unknown>;
  variables: Record<string, unknown>;
  nodeOutputs: Record<string, unknown>;

  capabilityGrant: CapabilityGrant;
  cancellationSignal: CancellationSignal;
}
```

Publisher không được sửa trực tiếp phần hệ thống như `deviceId` hoặc capability grant.


# 6. Thiết kế Edge

Đây là phần nên giữ đơn giản cho MVP.

## 6.1. Control edge

Cho biết sau khi một node hoàn thành thì node nào được chạy.

```text
Start ──success──> Launch App ──success──> Wait
```

## 6.2. Conditional branch

Conditional branch thực chất là control edge có nhãn output:

```text
                 ┌── true ──> Tap Close
Element Exists ──┤
                 └── false ─> Continue
```

Các nhánh được định nghĩa trong node definition, không phải người dùng tự gõ tên tùy ý.

## 6.3. Error edge

Node có thể có output `error`:

```text
HTTP Request
├── success → Parse Result
└── error   → Send Telegram
```

Tuy nhiên không bắt buộc người dùng nối error edge cho từng node. Node có `errorPolicy`:

- Stop execution.
- Retry rồi stop.
- Retry rồi đi error branch.
- Continue với default output.

## 6.4. Data binding

MVP không nên bắt người dùng kéo thêm data wire riêng cho mọi field vì graph sẽ nhanh chóng trở nên rối.

Thay vào đó, người dùng chọn dữ liệu bằng expression picker:

```text
Tap.x = {{ inputs.buttonX }}
Tap.y = {{ nodes.findButton.output.centerY }}
```

Studio phải cung cấp trình chọn trực quan:

```text
Workflow Input
  └── accountName

Previous Nodes
  └── Find Button
      ├── found
      ├── centerX
      └── centerY

Variables
  └── retryCount
```

Ở Runtime IR, data binding vẫn được lưu rõ ràng và type-check. Chỉ là nó không nhất thiết được biểu diễn bằng một đường dây trên canvas.

## 6.5. Không hỗ trợ parallel branch tùy ý trong MVP

Một device execution nên chạy tuần tự: tại một thời điểm chỉ có một node điều khiển thiết bị.

Không nên cho phép:

```text
Node A
├── Node B
└── Node C
```

rồi B và C cùng tap trên một màn hình.

Multi-device parallelism đã được xử lý ở cấp device execution. Bên trong một thiết bị, workflow nên tuần tự. Nếu sau này cần parallel background task, bổ sung `Parallel` và `Join` với ngữ nghĩa rõ ràng.
