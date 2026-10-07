# 10. MVP Launcher

## Bắt buộc

- Login/logout/refresh token.
- My Products.
- Download và verify package.
- Runtime Supervisor.
- Runtime handshake và compatibility check.
- Device list từ Runtime.
- Chọn nhiều LDPlayer instance.
- Input form theo workflow schema.
- Gán input profile theo từng thiết bị.
- Request và renew execution lease.
- Gửi lease token xuống Runtime.
- Start run group.
- Reconnect vào execution đang chạy.
- Realtime execution monitor khi Launcher đang mở.
- Pause/resume/cancel execution.
- Hiển thị trạng thái `PAUSED_LICENSE`.
- Local settings.
- Run summary.
- Đóng Runtime nếu không còn execution hoạt động.

## Sau MVP

- System tray và tùy chọn chạy Launcher nền.
- Workflow scheduling.
- Auto-start LDPlayer instance.
- Bulk import account/profile.
- Remote monitoring.
- Multi-PC management.
- Automatic retry run.
- Cloud execution history chi tiết.
- Launcher self-update hoàn chỉnh.
- Device grouping.
- Run templates.
- Resource monitoring CPU/RAM.
- Resume execution sau Runtime crash.

# 11. Các quyết định nên chốt

1. Launcher là Electron + React application trên Windows.
2. Launcher không gọi ADB trực tiếp.
3. Runtime Agent là source of truth cho execution.
4. Launcher chỉ lấy device list qua Runtime Agent.
5. Package Manager thuộc Launcher, nhưng Runtime xác minh lại package trước khi chạy.
6. Mỗi device có thể được gán input profile riêng.
7. Launcher yêu cầu và renew lease khi đang mở; Runtime tự validate lease với backend.
8. Lease token chỉ được giữ tạm trong RAM của Launcher và Runtime.
9. Đóng Launcher không làm dừng execution đang chạy.
10. Runtime tiếp tục chạy độc lập đến khi execution hoàn thành hoặc lease hết hạn.
11. Nếu không có execution hoạt động, Runtime được đóng cùng Launcher.
12. Khi mở lại, Launcher reconnect vào Runtime và đọc lại trạng thái execution.
13. Một device execution lỗi không làm dừng các device khác theo mặc định.
14. Studio và Launcher dùng chung Runtime Agent codebase nhưng khác execution policy: `development` và `production`.
15. MVP không bắt buộc Launcher chạy system tray hoặc chạy nền.
