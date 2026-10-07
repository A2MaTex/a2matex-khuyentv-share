# 16. Phạm vi MVP

## Bắt buộc

- Desktop Studio.
- Project creation.
- Graph canvas.
- System node palette.
- Schema-driven node inspector.
- Control/conditional/error edges.
- If, Switch và controlled Loop.
- Workflow input schema.
- Data binding bằng expression picker.
- Node Registry có version.
- Static validation.
- Graph → Runtime IR compiler.
- Runtime Agent integration.
- Single-node và full-workflow test.
- Device selection qua ADB.
- Node execution inspector.
- Publish submission.
- Khoảng 25–30 node thiết yếu.

## Sau MVP

- Code node.
- Publisher-created subflow.
- Community node package.
- Parallel branches.
- Collaboration realtime.
- Visual version diff.
- AI workflow generation.
- Workflow auto-repair.
- Custom node SDK cho bên thứ ba.
- Advanced multi-device test laboratory.

# 17. Quyết định kiến trúc

Theo phân tích trên, mình đề xuất chốt các điểm sau:

1. Studio là desktop Visual Automation IDE dành cho publisher.
2. Runtime Agent là process riêng và được dùng chung với Launcher.
3. Studio không trực tiếp phát ADB command.
4. Node do A2MaTeX định nghĩa thông qua Node Definition Registry.
5. Form cấu hình, validation và documentation sinh từ schema.
6. Graph chạy tuần tự trong phạm vi một thiết bị.
7. Multi-device concurrency thuộc Runtime, không phải parallel edge trên canvas.
8. Conditional branch dùng output port có tên.
9. Vòng lặp chỉ đi qua Loop Controller.
10. Data binding dùng expression picker, không bắt buộc data wire.
11. Editor Graph được compile thành Runtime IR có version.
12. Code node chưa phải trọng tâm MVP và chỉ dùng để biến đổi dữ liệu.
13. Publisher không được cài arbitrary npm/custom runtime handler.
14. Studio hỗ trợ single-node testing, pinned data và screenshot inspection để UAT nhanh.
15. Giá trị MVP được đo bằng **số workflow hữu ích có thể tạo**, không chỉ bằng số node hiển thị trong palette.

Với những quyết định này, A2MaTeX Studio sẽ mang cách xây flow trực quan của Node-RED, khả năng thao tác dữ liệu có kiểm soát của n8n, nhưng được thu hẹp rõ vào bài toán **automation nhiều thiết bị Android và phát hành workflow như sản phẩm thương mại**.