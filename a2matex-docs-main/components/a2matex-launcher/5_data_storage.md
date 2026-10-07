# 6. Phân chia dữ liệu giữa Launcher và Runtime

| Dữ liệu                          | Source of truth             |
| -------------------------------- | --------------------------- |
| User session                     | Launcher                    |
| Sản phẩm đã mua                  | Backend, Launcher chỉ cache |
| Package đã tải                   | Launcher Package Manager    |
| LDPlayer devices                 | Runtime Agent               |
| Device alias                     | Launcher                    |
| Run configuration trước khi chạy | Launcher                    |
| Run group                        | Runtime Agent               |
| Current node và sequence         | Runtime Agent               |
| Execution variables              | Runtime Agent               |
| Node result                      | Runtime Agent               |
| Lease record                     | Backend                     |
| Lease token tạm thời             | Launcher RAM                |
| Lease đã validate                | Runtime RAM                 |
| Execution history chi tiết       | Runtime Agent SQLite        |
| Run summary chưa đồng bộ         | Runtime Agent SQLite        |
| Run summary đã đồng bộ           | Backend                     |

Launcher không lưu `currentNode`, `sequence` hoặc execution variables làm source of truth. Sau khi reconnect, Launcher gọi Runtime để đọc lại trạng thái.

Launcher chỉ giữ `leaseToken` trong RAM trong thời gian execution hoạt động để có thể gửi lại nếu Runtime restart. Backend mới là source of truth của lease; Runtime chỉ cache kết quả validate.

# 7. Local storage

Launcher có thể dùng Electron Store cho settings đơn giản và SQLite nếu cần quản lý nhiều package/profile:

```text
launcher_settings
installed_products
installed_releases
input_profiles
device_aliases
run_presets
download_history
```

`input_profiles` chỉ lưu dữ liệu đầu vào và reference tới credential:

```json
{
  "profileId": "profile_01",
  "name": "YouTube Account 01",
  "credentialRef": "credential_youtube_01"
}
```

Không lưu trong SQLite hoặc Electron Store:

- node execution state;
- workflow variables;
- lease token;
- raw credential;
- refresh token;
- decrypted workflow;
- ADB output chi tiết.

Access token và lease token được giữ trong RAM. Refresh token và credential cần đăng nhập lâu dài được lưu bằng **Windows Credential Manager hoặc DPAPI**.

Runtime có SQLite riêng để lưu execution state, node result, event và trạng thái đồng bộ backend. Decrypted workflow chỉ tồn tại trong RAM.

# 8. Xử lý lỗi

| Tình huống                         | Launcher xử lý                                                               |
| ---------------------------------- | ---------------------------------------------------------------------------- |
| Backend mất kết nối trước Run      | Không thể tạo hoặc validate lease mới                                        |
| Backend mất kết nối khi đang chạy  | Runtime tiếp tục đến khi lease hết hạn                                       |
| Runtime chưa chạy                  | Khởi động và health check                                                    |
| Runtime incompatible               | Yêu cầu update Runtime                                                       |
| Package corrupted                  | Cách ly/xóa package lỗi và tải lại                                           |
| Device offline trước Run           | Không cho chọn device đó để chạy                                             |
| Device offline khi đang chạy       | Hiển thị trạng thái do Runtime trả về                                        |
| Runtime crash khi Launcher còn mở  | Restart Runtime và gửi lại lease token để validate                           |
| Runtime crash khi Launcher đã đóng | Run chuyển `INTERRUPTED`; mở Launcher để cấp lease lại                       |
| Lease không renew được             | Cảnh báo; Runtime tiếp tục đến hạn rồi pause                                 |
| Customer hết quyền                 | Không cho tạo hoặc renew lease                                               |
| Release bị revoke                  | Không cho tạo hoặc renew lease; execution hiện tại có thể chạy đến hết lease |
| Một device execution lỗi           | Các device khác tiếp tục theo mặc định                                       |
| Upload run summary thất bại        | Runtime lưu pending và retry khi có mạng                                     |

Release bị revoke sẽ không dừng ngay execution đang chạy, vì Runtime không kiểm tra backend ở từng node. Việc revoke có hiệu lực muộn nhất khi lease hiện tại hết hạn.
