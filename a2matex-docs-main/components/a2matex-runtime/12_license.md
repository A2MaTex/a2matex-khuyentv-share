
# 27. Package và license trong Runtime Agent

Có hai giai đoạn.

## Development

Studio gửi Runtime IR trực tiếp:

```json
{
  "mode": "DEVELOPMENT",
  "workflow": {},
  "devices": [],
  "testInputs": {}
}
```

Runtime đánh dấu run là development.

## Production

Launcher cung cấp:

- encrypted release/package reference;
- execution lease;
- selected devices;
- device inputs;
- credential references.

Tốt hơn là Runtime Agent tự:

1. xác minh signature;
2. kiểm tra hash;
3. kiểm tra lease;
4. mở package;
5. giữ Runtime IR trong memory;
6. chạy;
7. xóa reference khi kết thúc.

Không nên để Launcher giải mã graph thành plaintext rồi truyền tự do cho Runtime nếu mục tiêu là tăng chi phí trích xuất. MVP có thể tạm truyền IR rõ, sau đó thêm `SecurePackageLoader`.
