
Node-RED Function node cho phép JavaScript nhận và trả message, hỗ trợ nhiều output và cả tác vụ bất đồng bộ. Nó linh hoạt nhưng yêu cầu hiểu message và JavaScript. :chatgpt-content-reference{index="3"}

n8n Code node hỗ trợ chạy một lần cho toàn bộ items hoặc một lần cho từng item. n8n cũng tách các tác vụ filesystem và HTTP sang node riêng; Code node không trực tiếp thực hiện chúng trong cấu hình được kiểm soát. :chatgpt-content-reference{index="4"}

A2MaTeX Code node nên theo hướng hẹp hơn:

```ts
function run(input, context) {
  return {
    normalizedName: input.name.trim().toLowerCase()
  };
}
```

Code node chỉ được:

- đọc input JSON;
- đọc biến workflow được cấp;
- tính toán;
- xử lý array/object/string/number/date;
- trả JSON có schema;
- chọn một trong các output được định nghĩa.

Không được:

- gọi ADB;
- gọi HTTP;
- đọc/ghi file;
- tạo process;
- import npm package;
- dynamic import;
- đọc credential;
- truy cập Runtime internals;
- tạo vòng lặp vô hạn;
- chạy quá CPU/memory/time quota.

Code node nên chạy trong **sandbox process riêng hoặc WebAssembly/isolated runner**. Chạy JavaScript trong cùng process Runtime rồi chỉ xóa vài global function không phải security boundary đủ an toàn.

MVP có thể chưa cần Code node. Trước Code node, nên cung cấp:

- Set Variable;
- Compare;
- Text Template;
- Build Object;
- List Operations;
- Expression Editor.

Phần lớn nhu cầu dữ liệu đơn giản sẽ được giải quyết mà không cần code.