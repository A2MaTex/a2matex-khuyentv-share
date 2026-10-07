
# 9. Danh mục node cho MVP

Mục tiêu đúng là:

> Tạo bộ primitive node có khả năng kết hợp cao và xây một Node Definition Framework giúp thêm node mới rất nhanh.

## 9.1. Flow-control nodes — bắt buộc

| Node | Chức năng |
|---|---|
| Start | Điểm bắt đầu |
| End | Kết thúc thành công |
| Fail | Kết thúc với lỗi |
| Delay | Chờ một khoảng thời gian |
| If | Hai nhánh true/false |
| Switch | Nhiều nhánh |
| Repeat | Lặp N lần |
| While | Lặp theo điều kiện có giới hạn |
| For Each | Lặp qua danh sách |
| Merge | Hợp nhất nhánh loại trừ |
| Set Variable | Cập nhật biến |
| Log | Ghi thông tin debug |

## 9.2. Android action nodes

| Node | Chức năng |
|---|---|
| Launch App | Mở ứng dụng theo package |
| Stop App | Dừng ứng dụng |
| Tap | Bấm theo tọa độ hoặc target |
| Long Press | Nhấn giữ |
| Swipe | Vuốt |
| Scroll | Cuộn |
| Input Text | Nhập text |
| Clear Text | Xóa nội dung |
| Key Event | Back, Home, Enter… |
| Open URL/Deep Link | Mở URI được cho phép |

`Tap` có thể hỗ trợ nhiều target mode:

- tọa độ cố định;
- tọa độ theo tỷ lệ màn hình;
- output từ node nhận diện;
- UI element selector.

Không nhất thiết tạo bốn node Tap khác nhau.

## 9.3. Android observation nodes

| Node | Chức năng |
|---|---|
| Screenshot | Chụp màn hình |
| Get Current App | Đọc package/activity hiện tại |
| Element Exists | Kiểm tra UI element |
| Wait For Element | Chờ element xuất hiện |
| Get Element Text | Đọc text |
| Find Image | Tìm ảnh mẫu trong màn hình |
| Compare Screen | So sánh trạng thái màn hình |
| Read Text/OCR | Đọc text từ vùng ảnh |

Trong nhóm này, `Element Exists` và `Wait For Element` cần ưu tiên cao hơn OCR. OCR và image matching có chi phí triển khai, kiểm thử và tài nguyên lớn hơn.

## 9.4. Data nodes

| Node | Chức năng |
|---|---|
| Compare | So sánh hai giá trị |
| Text Template | Ghép chuỗi từ input |
| Parse JSON | Chuyển JSON string thành object |
| Build Object | Tạo object từ nhiều field |
| Get Property | Lấy một field |
| List Operations | Lấy, lọc hoặc đếm item |
| Date/Time | Lấy hoặc format thời gian |
| Random Value | Sinh giá trị trong giới hạn |

## 9.5. Connector nodes

MVP chỉ nên chọn một số connector có giá trị cao:

| Node | Chức năng |
|---|---|
| HTTP Request | Gọi API theo domain/capability được duyệt |
| Telegram Message | Gửi trạng thái |
| Google Sheets Append Row | Ghi kết quả |
| Send Email | Gửi thông báo |

Connector phải dùng credential reference, không lưu token trực tiếp trong graph.

## 9.6. Debug và test nodes

| Node | Chức năng |
|---|---|
| Log | In giá trị |
| Assert | Xác nhận điều kiện khi test |
| Save Artifact | Lưu screenshot/test output |
| Mock Output | Giả lập kết quả node khi test |

### Phạm vi khả thi

MVP nên nhắm khoảng:

- 10–12 flow/data nodes;
- 8–10 Android action nodes;
- 5–7 observation nodes;
- 2–4 connector nodes;
- 2–3 debug nodes.

Tức khoảng **27–35 node type**, nhưng nhiều node dùng chung handler infrastructure nên không phải 35 implementation hoàn toàn độc lập.


# 10. Cơ chế giúp tạo node mới nhanh

Đây mới là điểm quyết định tốc độ UAT.

Một node mới nên được thêm theo quy trình:

```text
1. Khai báo NodeDefinition
2. Viết Runtime Handler
3. Khai báo input/output schema
4. Khai báo capability
5. Viết contract tests
6. Registry tự động nhận node
7. Studio tự sinh form và tài liệu
```

Cần xây một `Node Development Kit` nội bộ:

```text
packages/node-sdk
├── node-definition.schema.json
├── config-field-types
├── input-output-types
├── validation-helpers
├── test-harness
├── documentation-generator
└── compatibility-checker
```

Mỗi node phải có test tối thiểu:

- config hợp lệ;
- config sai;
- input/output đúng schema;
- timeout;
- cancel;
- runtime handler error;
- capability bị từ chối;
- migration từ version trước nếu có.

Nhờ vậy, việc tạo thêm node trở thành quá trình khai báo và viết handler, thay vì sửa đồng thời palette, form, validator, Runtime và tài liệu.
