# 3. Cấu trúc sản phẩm nhìn từ người dùng

Giao diện Studio nên gồm sáu khu vực chính:

```text
┌──────────────────────────────────────────────────────────────┐
│ Project | Save | Validate | Test | Publish | Device profile │
├──────────────┬────────────────────────────┬──────────────────┤
│ Project      │                            │ Node Inspector   │
│ Explorer     │       Graph Canvas         │                  │
│              │                            │ Configuration    │
│ Node Palette │                            │ Input Mapping    │
│              │                            │ Retry / Error    │
├──────────────┴────────────────────────────┴──────────────────┤
│ Execution | Node output | Variables | Logs | Diagnostics    │
└──────────────────────────────────────────────────────────────┘
```

## 3.1. Project Explorer

Quản lý các thành phần của một automation product:

```text
My Automation Product
├── Workflow
│   └── main.graph.json
├── Inputs
│   └── input.schema.json
├── Assets
│   ├── buttons/
│   └── screenshots/
├── Test Profiles
│   ├── account-a.json
│   └── account-b.json
├── Permissions
├── Product Metadata
└── Publish History
```

MVP chưa cần cho một product có nhiều workflow phức tạp. Có thể giới hạn:

- một main workflow;
- một tập asset;
- nhiều test profile;
- một input schema.

Sau này mới bổ sung subworkflow hoặc reusable workflow.

## 3.2. Node Palette

Node palette chia node theo nhóm, hỗ trợ:

- tìm kiếm theo tên;
- lọc theo nhóm;
- hiển thị mô tả ngắn;
- đánh dấu node cần quyền nhạy cảm;
- hiển thị node version;
- gợi ý node thường dùng tiếp theo.

## 3.3. Graph Canvas

Canvas hỗ trợ:

- kéo và thả node;
- nối node;
- zoom, pan;
- sao chép node;
- nhóm node để dễ nhìn;
- undo/redo;
- auto-layout;
- hiển thị lỗi ngay trên node;
- đánh dấu node đang chạy;
- hiển thị nhánh đã được chọn khi test.

## 3.4. Node Inspector

Khi người dùng chọn node, Inspector hiển thị:

- cấu hình chính;
- input mapping;
- output schema;
- retry;
- timeout;
- error handling;
- capability cần dùng;
- hướng dẫn sử dụng;
- dữ liệu test gần nhất.

Inspector phải được sinh tự động từ `NodeDefinition`, không viết riêng một form React cho từng node. Đây là điểm quan trọng để có thể phát triển nhiều node nhanh.

## 3.5. Execution Inspector

Sau khi test, người dùng có thể chọn một node và xem:

- input thực tế;
- output;
- thời gian thực thi;
- số lần retry;
- ảnh chụp màn hình trước/sau;
- biến đã thay đổi;
- lỗi ADB hoặc connector;
- node tiếp theo được chọn;
- sequence và loop iteration.

## 3.6. Diagnostics và Publish

Trước khi publish, Studio hiển thị:

- lỗi bắt buộc sửa;
- cảnh báo;
- quyền workflow yêu cầu;
- node không tương thích Runtime;
- vòng lặp có nguy cơ quá dài;
- asset còn thiếu;
- input chưa được khai báo;
- node chưa được nối;
- test case đã chạy/chưa chạy.
