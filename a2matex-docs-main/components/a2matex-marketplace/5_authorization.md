## 10. Quản lý quyền sử dụng

Trạng thái entitlement cho MVP:

| Trạng thái | Ý nghĩa                   |
| ---------- | ------------------------- |
| `ACTIVE`   | Được phép sử dụng         |
| `EXPIRED`  | Đã hết hạn                |
| `REVOKED`  | Bị thu hồi trước thời hạn |

Trước khi chạy, Launcher phải request execution lease.

Ví dụ:

```json
{
  "productId": "product_01",
  "releaseId": "release_01",
  "deviceIds": ["ldplayer_0", "ldplayer_1"]
}
```

Server kiểm tra:

- Entitlement còn hiệu lực.
- Product không bị suspend.
- Release vẫn được phép chạy.
- Customer không bị ban.
- Device không bị disable.
- Không vượt giới hạn device.
- Không vượt số execution đồng thời.

Backend trả `leaseToken`. Launcher giữ token trong RAM và chuyển xuống Runtime. Runtime gọi Backend để validate token và nhận:

- Product/release được phép chạy.
- `maxConcurrentDevices`.
- `expiresAt`.
- Workflow decryption key tạm thời.

Runtime cache kết quả trong RAM. Mạng gián đoạn ngắn không làm dừng workflow; Runtime chỉ chuyển `PAUSED_LICENSE` khi lease thực sự hết hạn và không thể renew.

## 11. Installation, revoke và suspend

Backend quản lý Windows installation, không quản lý từng LDPlayer instance.

| Hành động            | Phạm vi                                   |
| -------------------- | ----------------------------------------- |
| Disable installation | Chặn một máy Windows đăng ký với customer |
| Revoke entitlement   | Chặn một customer dùng một product        |
| Disable release      | Chặn một release cụ thể                   |
| Suspend product      | Chặn toàn bộ product                      |
| Ban user             | Chặn toàn bộ hoạt động tài khoản          |

Khi revoke hoặc suspend trong MVP:

- Không cấp lease mới.
- Không renew lease hiện tại.
- Package có thể vẫn còn trên máy customer.
- Execution hiện tại được chạy đến khi lease hết hạn.
- Runtime pause trước khi bắt đầu node tiếp theo.
- Customer vẫn xem được order history.
- Admin phải nhập lý do và hệ thống ghi audit log.

Không hỗ trợ dừng execution ngay lập tức trong MVP vì Runtime không duy trì heartbeat hoặc command channel liên tục với Backend.

## 12. Update sản phẩm

Publisher không được ghi đè release đã publish.

```text
Publisher sửa project trong Studio
→ Tạo submission mới
→ Automated scan và admin review
→ Build ProductRelease mới
→ Đặt làm current release
```

Customer có thể:

- Tiếp tục dùng release cũ nếu vẫn được hỗ trợ.
- Update sang current release.
- Bị yêu cầu update nếu release cũ bị disable.

MVP chỉ cần:

- Một current release cho mỗi product.
- Giữ release cũ.
- Admin có thể disable release lỗi.
- Launcher kiểm tra minimum version và release status trước khi tạo run.

Chưa cần thiết kế rollback tự động phức tạp.
