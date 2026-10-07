
# 7. Conditional branch, vòng lặp và merge

## 7.1. If

`If` nhận một boolean hoặc phép so sánh:

```text
If account.isPremium == true
├── true  → Continue
└── false → Handle Additional Screen
```

Đối với người không biết code, Inspector nên hỗ trợ condition builder:

```text
[Node output] [Element Exists.found] [is equal to] [true]
```

Advanced mode mới cho phép expression.

## 7.2. Switch

Dùng khi có nhiều trường hợp:

```text
Switch currentScreen
├── HOME
├── LOGIN
├── ERROR
└── DEFAULT
```

Mỗi case có:

- giá trị;
- toán tử;
- thứ tự ưu tiên;
- output port tương ứng.

Luôn nên có `default`.

## 7.3. Domain node có branch riêng

Một số node có thể trả branch trực tiếp để giảm số node:

```text
Wait For Element
├── found
├── timeout
└── error
```

Tuy vậy không nên cho mọi node có quá nhiều output. Chỉ tạo branch khi kết quả đó thực sự thay đổi control flow.

## 7.4. Loop

Không cho phép publisher nối edge ngược tùy ý. Mọi vòng lặp phải đi qua Loop Controller:

```text
Repeat
├── body → Step A → Step B → Repeat End
└── done → Next Step
```

Loop bắt buộc có:

- `maxIterations`;
- `maxDuration`;
- condition hoặc count;
- hành vi khi đạt giới hạn.

Các dạng MVP:

- Repeat N Times.
- While Condition.
- For Each Item.

Runtime lưu:

```text
nodeId = loop_01
iteration = 7
sequence = 35
```

Sequence luôn tăng, dù execution quay lại cùng node.

## 7.5. Merge

Vì MVP không có parallel branch tổng quát, Merge chủ yếu dùng để hợp nhất các nhánh loại trừ nhau:

```text
If
├── true  → Path A ──┐
└── false → Path B ──┴──> Merge → Continue
```

Chỉ một nhánh đi tới Merge trong mỗi execution. Vì thế Merge không cần chờ nhiều input.