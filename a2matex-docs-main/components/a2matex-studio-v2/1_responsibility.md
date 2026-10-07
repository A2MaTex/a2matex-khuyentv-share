# 1. Mục tiêu của A2MaTeX Studio

A2MaTeX Studio giúp người dùng xây dựng sản phẩm automation Android mà không cần trực tiếp viết ADB command hoặc code.

Publisher sẽ:

1. Tạo project automation.
2. Khai báo input mà customer cần cung cấp.
3. Kéo các node hệ thống vào canvas.
4. Nối node bằng các nhánh điều khiển.
5. Cấu hình hành động Android, điều kiện, vòng lặp và connector.
6. Kết nối thiết bị Android hoặc LDPlayer để chạy thử.
7. Quan sát input/output và lỗi của từng node.
8. Kiểm tra quyền mà workflow yêu cầu.
9. Gửi một revision lên Marketplace để review.
10. Sửa lỗi và phát hành version tiếp theo.

Studio không chỉ dành cho lập trình viên. Đối tượng chính là người:

- hiểu quy trình automation mình muốn tạo;
- biết màn hình Android cần thao tác;
- có thể cấu hình tọa độ, text, ảnh mẫu, thời gian chờ;
- không nhất thiết biết JavaScript, ADB hay kiến trúc workflow engine.

Do đó hướng chính vẫn là **system node first**. Code node chỉ là công cụ bổ sung cho trường hợp node hệ thống chưa giải quyết được việc biến đổi dữ liệu.

---

# 2. Ranh giới trách nhiệm của Studio

## Studio chịu trách nhiệm

- Quản lý project và draft.
- Hiển thị graph editor.
- Cung cấp node palette.
- Sinh form cấu hình từ node definition.
- Kiểm tra graph trong lúc thiết kế.
- Quản lý input schema và test data.
- Kết nối Runtime Agent để chạy thử.
- Hiển thị trạng thái, input, output và lỗi từng node.
- Quản lý asset phát triển như ảnh mẫu.
- Tính toán danh sách capability mà workflow yêu cầu.
- Chuẩn hóa editor graph thành Runtime IR.
- Gửi workflow revision lên backend.
- Hiển thị kết quả automated validation và review.

## Studio không chịu trách nhiệm

- Quản lý license của customer.
- Mã hóa workflow để phân phối.
- Quyết định customer có quyền chạy hay không.
- Tự thực thi ADB trực tiếp từ giao diện.
- Quản lý số lượng thiết bị customer được phép sử dụng.
- Chạy workflow production dài hạn.
- Cho publisher nạp npm package hoặc native executable tùy ý.
- Cho code node gọi trực tiếp ADB, filesystem, process hoặc Internet.

Những việc đó thuộc Backend, Marketplace, Launcher hoặc Runtime Agent.
