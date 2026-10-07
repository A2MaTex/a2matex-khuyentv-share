
# 1. Trách nhiệm của Runtime Agent

## Runtime Agent chịu trách nhiệm

- Phát hiện LDPlayer instance và thiết bị Android qua ADB.
- Chuẩn hóa chúng thành một `Device` model chung.
- Nhận Runtime IR từ Studio hoặc Launcher.
- Kiểm tra Runtime có hỗ trợ toàn bộ node hay không.
- Tạo run group và device execution.
- Diễn giải graph cho từng device execution.
- Resolve workflow input, variable và node output.
- Gọi đúng node handler.
- Chuyển Android node thành lệnh ADB/LDPlayer.
- Chuyển connector node thành background job.
- Xử lý timeout, retry, cancel và conditional branch.
- Giới hạn số thiết bị và tác vụ chạy đồng thời.
- Ghi checkpoint, log và artifact.
- Phát event realtime cho Studio/Launcher.
- Tiếp tục giữ trạng thái nếu UI tạm đóng.
- Kiểm tra capability trước khi thực thi node.
- Trong production: kiểm tra release và execution lease.

## Runtime Agent không chịu trách nhiệm

- Hiển thị canvas graph.
- Cho người dùng chỉnh sửa node.
- Quản lý sản phẩm Marketplace.
- Xử lý thanh toán.
- Quyết định license thương mại.
- Lưu editor graph.
- Review workflow của publisher.
- Tự sinh thêm node chưa được đăng ký.
- Cho workflow chạy arbitrary shell command.
