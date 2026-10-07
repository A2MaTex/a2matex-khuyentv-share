import xml.etree.ElementTree as ET

def build_drawio():
    mxfile = ET.Element("mxfile", host="app.diagrams.net", pages="4", type="device")

    # Helper function for adding pages
    def create_page(diag_name, diag_id):
        diag = ET.SubElement(mxfile, "diagram", name=diag_name, id=diag_id)
        model = ET.SubElement(diag, "mxGraphModel", dx="1600", dy="900", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1920", pageHeight="1080", math="0", shadow="0")
        root = ET.SubElement(model, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")
        return root

    def add_lane(root, lane_id, name, y, height, width=1750, fill_color="#f8fafc", stroke_color="#94a3b8", title_fill="#3b82f6", title_color="#ffffff"):
        # Lane parent
        lane = ET.SubElement(root, "mxCell", id=lane_id, parent="1",
            style=f"swimlane;horizontal=0;fillColor={fill_color};strokeColor={stroke_color};swimlaneFillColor={fill_color};startSize=40;fontStyle=1;align=center;verticalAlign=middle;fontColor={title_color};swimlaneHeadColor={title_fill};fontSize=12;rounded=0;shadow=0;",
            value=name, vertex="1")
        g = ET.SubElement(lane, "mxGeometry", x="40", y=str(y), width=str(width), height=str(height))
        g.set("as", "geometry")
        return lane

    def add_node(root, node_id, parent_id, val, x, y, w, h, style):
        n = ET.SubElement(root, "mxCell", id=node_id, parent=parent_id, style=style, value=val, vertex="1")
        g = ET.SubElement(n, "mxGeometry", x=str(x), y=str(y), width=str(w), height=str(h))
        g.set("as", "geometry")
        return n

    def add_start(root, node_id, parent_id, x, y, label="Start"):
        style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dcfce7;strokeColor=#16a34a;strokeWidth=2;fontStyle=1;fontColor=#15803d;fontSize=11;align=center;verticalAlign=middle;"
        return add_node(root, node_id, parent_id, label, x, y, 40, 40, style)

    def add_end(root, node_id, parent_id, x, y, label="End"):
        style = "ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fee2e2;strokeColor=#dc2626;strokeWidth=3;fontStyle=1;fontColor=#b91c1c;fontSize=11;align=center;verticalAlign=middle;"
        return add_node(root, node_id, parent_id, label, x, y, 40, 40, style)

    def add_task(root, node_id, parent_id, val, x, y, w=130, h=55, fill="#ffffff", stroke="#475569", color="#1e293b"):
        style = f"rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor={fill};strokeColor={stroke};strokeWidth=1.5;fontStyle=1;fontColor={color};fontSize=11;align=center;verticalAlign=middle;spacing=2;"
        return add_node(root, node_id, parent_id, val, x, y, w, h, style)

    def add_gateway(root, node_id, parent_id, val, x, y, w=100, h=70):
        style = "rhombus;whiteSpace=wrap;html=1;fillColor=#ffedd5;strokeColor=#ea580c;strokeWidth=1.5;fontStyle=1;fontColor=#9a3412;fontSize=10;align=center;verticalAlign=middle;spacing=1;"
        return add_node(root, node_id, parent_id, val, x, y, w, h, style)

    def add_data(root, node_id, parent_id, val, x, y, w=110, h=50):
        style = "shape=note;whiteSpace=wrap;html=1;size=14;verticalAlign=middle;align=center;fillColor=#f1f5f9;strokeColor=#64748b;fontStyle=2;fontColor=#334155;fontSize=10;"
        return add_node(root, node_id, parent_id, val, x, y, w, h, style)

    def add_edge(root, sid, tid, val="", dashed=False, color="#334155", exitX=None, exitY=None, entryX=None, entryY=None):
        style = f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor={color};strokeWidth=1.5;endArrow=classic;fontSize=10;fontColor={color};fontStyle=1;labelBackgroundColor=#ffffff;"
        if dashed:
            style += "dashed=1;"
        if exitX is not None and exitY is not None:
            style += f"exitX={exitX};exitY={exitY};exitDx=0;exitDy=0;"
        if entryX is not None and entryY is not None:
            style += f"entryX={entryX};entryY={entryY};entryDx=0;entryDy=0;"
        e = ET.SubElement(root, "mxCell", edge="1", parent="1", source=sid, target=tid, style=style, value=val)
        g = ET.SubElement(e, "mxGeometry", relative="1")
        g.set("as", "geometry")
        return e

    # =========================================================================
    # PAGE 1: BF-01 Workflow Authoring, Testing, Moderation & Publishing
    # =========================================================================
    r1 = create_page("BF-01 Authoring & Publishing", "bf01_authoring")

    # 5 Lanes: Total height: 850
    # Lane 1: Publisher (Studio & Web) -> y: 50, h: 180
    # Lane 2: Runtime Agent (Dev Mode Daemon) -> y: 230, h: 140
    # Lane 3: LDPlayer Test Instance -> y: 370, h: 120
    # Lane 4: A2MaTex Cloud Backend & Storage -> y: 490, h: 190
    # Lane 5: Admin Moderation Console -> y: 680, h: 160

    l1_pub = add_lane(r1, "l1_pub", "Publisher (Studio / Web)", 50, 180, 1800, "#f8fafc", "#94a3b8", "#2563eb", "#ffffff")
    l1_run = add_lane(r1, "l1_run", "Runtime Agent (Dev Mode)", 230, 140, 1800, "#ffffff", "#94a3b8", "#0284c7", "#ffffff")
    l1_ldp = add_lane(r1, "l1_ldp", "LDPlayer Test Instance", 370, 120, 1800, "#f8fafc", "#94a3b8", "#059669", "#ffffff")
    l1_back = add_lane(r1, "l1_back", "Cloud Backend & S3 Storage", 490, 190, 1800, "#ffffff", "#94a3b8", "#d97706", "#ffffff")
    l1_adm = add_lane(r1, "l1_adm", "Admin Moderation Console", 680, 160, 1800, "#f8fafc", "#94a3b8", "#7c3aed", "#ffffff")

    # Nodes for BF-01
    add_start(r1, "bf01_start", "l1_pub", 60, 65)
    add_task(r1, "bf01_p1", "l1_pub", "Tạo Project &\nThiết kế Workflow Canvas\n(React Flow / Schema Form)", 130, 55, 140, 60)
    add_gateway(r1, "bf01_gw_test", "l1_pub", "Test cục bộ\ntrên LDPlayer?", 310, 50, 100, 70)
    add_task(r1, "bf01_p2", "l1_pub", "Chọn Thiết bị Test &\nKích hoạt Test Run\n(Single-Node / Full Flow)", 450, 55, 140, 60)

    # Runtime dev execution
    add_task(r1, "bf01_r1", "l1_run", "Khởi tạo Dev Execution,\nNhận lệnh qua Local API\n& Điều phối ADB", 450, 40, 140, 60, "#e0f2fe", "#0284c7", "#0369a1")
    add_task(r1, "bf01_ld1", "l1_ldp", "Thực thi Action trên App\n(Launch, Tap, Swipe, Dump UI)\n& Trả kết quả / Screenshot", 450, 30, 140, 60, "#d1fae5", "#059669", "#065f46")
    add_gateway(r1, "bf01_gw_tresult", "l1_pub", "Kết quả Test\nĐạt yêu cầu?", 630, 50, 100, 70)

    # Cloud Sync
    add_task(r1, "bf01_p3", "l1_pub", "Đồng bộ ProjectDraft\n& Assets lên Cloud", 760, 55, 130, 60)
    add_task(r1, "bf01_b1", "l1_back", "Lưu trữ ProjectDraft (DB)\n& Assets mẫu vào S3 Storage", 760, 45, 130, 60, "#fef3c7", "#d97706", "#92400e")

    # Metadata & Self-Review
    add_task(r1, "bf01_p4", "l1_pub", "Kiểm tra Self-Review,\nNhập Metadata Listing,\nGiá bán (Coin) & Demo", 920, 55, 140, 60)
    add_task(r1, "bf01_p5", "l1_pub", "Xác nhận gửi duyệt\n(Submit for Review)", 1090, 55, 130, 60)

    # Freeze & Scanner
    add_task(r1, "bf01_b2", "l1_back", "Khóa bất biến:\nĐóng băng WorkflowRevision\n& Tạo Submission Record", 1090, 45, 140, 60, "#fef3c7", "#d97706", "#92400e")
    add_task(r1, "bf01_b3", "l1_back", "Chạy Automated Scanner:\nKiểm tra AST, Graph Cycles,\nCapabilities & Cấm Raw Shell", 1260, 45, 140, 60, "#fef3c7", "#d97706", "#92400e")
    add_gateway(r1, "bf01_gw_scan", "l1_back", "Automated\nScan Pass?", 1430, 40, 95, 70)

    # Admin review
    add_task(r1, "bf01_b4", "l1_back", "Enqueue Submission vào\nHàng đợi Admin Review", 1410, 125, 135, 50, "#fef3c7", "#d97706", "#92400e")
    add_task(r1, "bf01_adm1", "l1_adm", "Thẩm định nội dung,\nXem kết quả Scan, chạy thử\ntrên môi trường Sandbox", 1410, 45, 140, 65, "#f3e8ff", "#7c3aed", "#5b21b6")
    add_gateway(r1, "bf01_gw_adm", "l1_adm", "Admin\nPhê duyệt?", 1580, 42, 95, 70)

    # Packaging & Release
    add_task(r1, "bf01_b5", "l1_back", "Biên dịch Runtime IR, Mã hóa\nAES-256-GCM, Đóng gói .a2m,\nTính SHA-256 & Publish Listing", 1560, 45, 145, 65, "#dcfce7", "#16a34a", "#15803d")
    add_task(r1, "bf01_p6", "l1_pub", "Nhận Thông báo Phát hành,\nTheo dõi Doanh thu Tool", 1730, 55, 120, 60)
    add_end(r1, "bf01_end", "l1_pub", 1770, 130, "Hoàn tất")

    # Connectors for BF-01
    add_edge(r1, "bf01_start", "bf01_p1")
    add_edge(r1, "bf01_p1", "bf01_gw_test")
    add_edge(r1, "bf01_gw_test", "bf01_p2", "Có")
    add_edge(r1, "bf01_gw_test", "bf01_p3", "Bỏ qua", exitX=1, exitY=0.5, entryX=0, entryY=0.5)
    add_edge(r1, "bf01_p2", "bf01_r1", "Gửi lệnh IPC", dashed=True, color="#0284c7")
    add_edge(r1, "bf01_r1", "bf01_ld1", "ADB exec", dashed=True, color="#059669")
    add_edge(r1, "bf01_ld1", "bf01_r1", "Screen / Log", dashed=True, color="#059669")
    add_edge(r1, "bf01_r1", "bf01_gw_tresult", "Kết quả Test", dashed=True, color="#0284c7")
    add_edge(r1, "bf01_gw_tresult", "bf01_p3", "Đạt")
    add_edge(r1, "bf01_gw_tresult", "bf01_p1", "Lỗi: Sửa Canvas", exitX=0.5, exitY=0, entryX=0.5, entryY=0, color="#dc2626")
    add_edge(r1, "bf01_p3", "bf01_b1", "Sync API", dashed=True, color="#d97706")
    add_edge(r1, "bf01_b1", "bf01_p4", "Draft Saved", dashed=True, color="#d97706")
    add_edge(r1, "bf01_p4", "bf01_p5")
    add_edge(r1, "bf01_p5", "bf01_b2", "Submit API", color="#2563eb")
    add_edge(r1, "bf01_b2", "bf01_b3")
    add_edge(r1, "bf01_b3", "bf01_gw_scan")
    add_edge(r1, "bf01_gw_scan", "bf01_b4", "Pass")
    add_edge(r1, "bf01_gw_scan", "bf01_p1", "Vi phạm Scan", exitX=0.5, exitY=0, entryX=0.8, entryY=0, color="#dc2626")
    add_edge(r1, "bf01_b4", "bf01_adm1")
    add_edge(r1, "bf01_adm1", "bf01_gw_adm")
    add_edge(r1, "bf01_gw_adm", "bf01_b5", "Approve", color="#16a34a")
    add_edge(r1, "bf01_gw_adm", "bf01_p1", "Changes Requested / Reject", exitX=0.5, exitY=1, entryX=0.2, entryY=1, color="#ea580c")
    add_edge(r1, "bf01_b5", "bf01_p6", "Notify Active", dashed=True, color="#16a34a")
    add_edge(r1, "bf01_p6", "bf01_end")

    # =========================================================================
    # PAGE 2: BF-02 Coin Top-up, Tool Purchase & Entitlement Provisioning
    # =========================================================================
    r2 = create_page("BF-02 Coin Top-up & Purchase", "bf02_commerce")

    # 4 Lanes
    l2_cus = add_lane(r2, "l2_cus", "Customer (Marketplace Web)", 50, 190, 1800, "#f8fafc", "#94a3b8", "#2563eb", "#ffffff")
    l2_bank = add_lane(r2, "l2_bank", "Banking / SePay Gateway", 240, 150, 1800, "#ffffff", "#94a3b8", "#059669", "#ffffff")
    l2_back = add_lane(r2, "l2_back", "Backend (Ledger & Entitlement)", 390, 220, 1800, "#f8fafc", "#94a3b8", "#d97706", "#ffffff")
    l2_pub = add_lane(r2, "l2_pub", "Publisher (Wallet & Revenue)", 610, 140, 1800, "#ffffff", "#94a3b8", "#7c3aed", "#ffffff")

    add_start(r2, "bf02_start", "l2_cus", 60, 75)
    add_task(r2, "bf02_c1", "l2_cus", "Duyệt Marketplace,\nTìm kiếm & Xem chi tiết\nKịch bản (Giá Coin, Đánh giá)", 130, 65, 140, 60)
    add_task(r2, "bf02_c2", "l2_cus", "Bấm 'Mua Kịch bản'\n& Xác nhận Đơn hàng", 300, 65, 130, 60)
    add_task(r2, "bf02_b1", "l2_back", "Kiểm tra Số dư Coin\ntrong Ví Customer", 300, 50, 130, 60, "#fef3c7", "#d97706", "#92400e")
    add_gateway(r2, "bf02_gw_balance", "l2_back", "Số dư Ví\nĐủ Coin?", 460, 45, 95, 70)

    # Top-up Sub-flow
    add_task(r2, "bf02_c3", "l2_cus", "Chọn gói Nạp Coin (VND)\n& Yêu cầu tạo mã VietQR", 580, 65, 140, 60)
    add_task(r2, "bf02_b2", "l2_back", "Tạo Topup Order (PENDING)\nGọi SePay sinh mã VietQR", 580, 50, 140, 60, "#fef3c7", "#d97706", "#92400e")
    add_task(r2, "bf02_bk1", "l2_bank", "Hiển thị VietQR kèm nội dung\nchuyển khoản định danh", 580, 45, 140, 60, "#d1fae5", "#059669", "#065f46")
    add_task(r2, "bf02_c4", "l2_cus", "Mở App Ngân hàng quét QR,\nThực hiện Chuyển tiền (VND)", 750, 65, 140, 60)
    add_task(r2, "bf02_bk2", "l2_bank", "Ngân hàng nhận biến động,\nSePay bắn Webhook xác nhận", 750, 45, 140, 60, "#d1fae5", "#059669", "#065f46")
    add_task(r2, "bf02_b3", "l2_back", "Xác thực Webhook Signature,\nCộng Coin vào Ví Customer", 750, 50, 140, 60, "#fef3c7", "#d97706", "#92400e")

    # Purchase execution
    add_task(r2, "bf02_b4", "l2_back", "Giao dịch Ví nguyên tử (Atomic):\n- Trừ Coin ví Customer\n- Cộng 80% Coin ví Publisher\n- Giữ 20% Phí sàn Platform", 930, 40, 160, 75, "#dcfce7", "#16a34a", "#15803d")
    add_task(r2, "bf02_b5", "l2_back", "Khởi tạo Entitlement Bản quyền:\n- Gắn Product ID, Max Devices,\n- Max Windows PC, Expiration", 1130, 45, 150, 65, "#fef3c7", "#d97706", "#92400e")

    add_task(r2, "bf02_pub1", "l2_pub", "Nhận Thông báo Doanh thu,\nCộng Coin vào Ví Publisher", 930, 40, 150, 60, "#f3e8ff", "#7c3aed", "#5b21b6")

    # Final acquisition
    add_task(r2, "bf02_c5", "l2_cus", "Tool xuất hiện trong 'My Products'\nHiển thị nút 'Open in Launcher'", 1320, 65, 150, 60)
    add_end(r2, "bf02_end", "l2_cus", 1510, 75, "Sở hữu")

    # Connectors for BF-02
    add_edge(r2, "bf02_start", "bf02_c1")
    add_edge(r2, "bf02_c1", "bf02_c2")
    add_edge(r2, "bf02_c2", "bf02_b1", "Gửi Order API", color="#2563eb")
    add_edge(r2, "bf02_b1", "bf02_gw_balance")
    add_edge(r2, "bf02_gw_balance", "bf02_c3", "Thiếu Coin", exitX=0.5, exitY=0, entryX=0.5, entryY=1, color="#ea580c")
    add_edge(r2, "bf02_c3", "bf02_b2", "Request Top-up")
    add_edge(r2, "bf02_b2", "bf02_bk1", "API Create QR", dashed=True, color="#059669")
    add_edge(r2, "bf02_bk1", "bf02_c4", "Quét mã QR", dashed=True, color="#2563eb")
    add_edge(r2, "bf02_c4", "bf02_bk2", "Chuyển tiền")
    add_edge(r2, "bf02_bk2", "bf02_b3", "Webhook IPN", dashed=True, color="#059669")
    add_edge(r2, "bf02_b3", "bf02_b4", "Ví đã nạp đủ Coin", color="#16a34a")
    add_edge(r2, "bf02_gw_balance", "bf02_b4", "Đủ Coin", exitX=1, exitY=0.5, entryX=0, entryY=0.5, color="#16a34a")
    add_edge(r2, "bf02_b4", "bf02_pub1", "Ledger Split", dashed=True, color="#7c3aed")
    add_edge(r2, "bf02_b4", "bf02_b5", "Order Completed")
    add_edge(r2, "bf02_b5", "bf02_c5", "Entitlement Granted", dashed=True, color="#2563eb")
    add_edge(r2, "bf02_c5", "bf02_end")

    # =========================================================================
    # PAGE 3: BF-03 Multi-Device Launcher, Lease Licensing & Parallel Execution
    # =========================================================================
    r3 = create_page("BF-03 Launcher & Execution", "bf03_execution")

    # 4 Lanes:
    # Lane 1: Customer (Launcher UI - Electron) -> y: 50, h: 180
    # Lane 2: A2MaTex Cloud Backend (License Authority) -> y: 230, h: 150
    # Lane 3: A2MaTex Runtime Agent (Local Daemon) -> y: 380, h: 220
    # Lane 4: LDPlayer Instances (Emulators 0..N) -> y: 600, h: 140

    l3_cus = add_lane(r3, "l3_cus", "Customer (Launcher Desktop)", 50, 180, 1850, "#f8fafc", "#94a3b8", "#2563eb", "#ffffff")
    l3_back = add_lane(r3, "l3_back", "A2MaTex Backend (License & Lease)", 230, 150, 1850, "#ffffff", "#94a3b8", "#d97706", "#ffffff")
    l3_run = add_lane(r3, "l3_run", "Runtime Agent (Go Daemon)", 380, 220, 1850, "#f8fafc", "#94a3b8", "#0284c7", "#ffffff")
    l3_ldp = add_lane(r3, "l3_ldp", "LDPlayer Instances (Emulators 0, 1..N)", 600, 140, 1850, "#ffffff", "#94a3b8", "#059669", "#ffffff")

    add_start(r3, "bf03_start", "l3_cus", 60, 70)
    add_task(r3, "bf03_c1", "l3_cus", "Mở Launcher, Đăng nhập &\nĐăng ký Installation (HW ID/DPAPI)", 125, 60, 145, 60)
    add_task(r3, "bf03_b1", "l3_back", "Xác thực Installation Limit,\nTrả danh sách Tool đã mua", 125, 45, 145, 60, "#fef3c7", "#d97706", "#92400e")
    add_task(r3, "bf03_c2", "l3_cus", "Tải gói .a2m (Signed URL)\n& Kiểm tra SHA-256 Hash", 300, 60, 140, 60)

    # Discovery
    add_task(r3, "bf03_r1", "l3_run", "Quét tự động:\nldconsole list2 & adb devices -l\nđể nhận diện giả lập online", 300, 45, 150, 65, "#e0f2fe", "#0284c7", "#0369a1")
    add_task(r3, "bf03_c3", "l3_cus", "Chọn các máy LDPlayer (ví dụ 3 máy)\n& Cấu hình Input Profiles riêng", 480, 60, 150, 60)
    add_task(r3, "bf03_c4", "l3_cus", "Bấm 'Chạy Kịch bản'\nThực hiện Preflight Checks", 660, 60, 140, 60)
    add_gateway(r3, "bf03_gw_pre", "l3_cus", "Preflight\nCheck Đạt?", 830, 55, 95, 70)

    # Lease acquisition
    add_task(r3, "bf03_c5", "l3_cus", "Gửi yêu cầu xin Execution Lease\n(requestedDevices: 3)", 950, 60, 140, 60)
    add_task(r3, "bf03_b2", "l3_back", "Kiểm tra Entitlement Active &\nDevice Quota -> Sinh leaseToken\n(Server chỉ lưu SHA256 Hash)", 950, 45, 150, 65, "#fef3c7", "#d97706", "#92400e")
    add_task(r3, "bf03_r2", "l3_run", "Validate leaseToken với Backend,\nNhận workflowKey trong RAM\n& Giải mã kịch bản (Không lưu đĩa)", 1130, 45, 160, 70, "#e0f2fe", "#0284c7", "#0369a1")

    # Multi-device Goroutines execution
    add_task(r3, "bf03_r3", "l3_run", "Khởi tạo Goroutines song song\ncho từng LDPlayer được chọn\n(Quản lý Khóa độc quyền Device Lock)", 1320, 35, 160, 70, "#e0f2fe", "#0284c7", "#0369a1")
    add_task(r3, "bf03_ld1", "l3_ldp", "Thực thi Typed ADB Commands\ntheo nguyên tắc Dispatched vs Confirmed\n(Tap, Swipe, Wait Element trên từng máy)", 1320, 35, 160, 70, "#d1fae5", "#059669", "#065f46")

    # SQLite checkpoint & WebSocket
    add_task(r3, "bf03_r4", "l3_run", "Ghi Checkpoint SQLite cục bộ &\nStream Realtime Log / Screenshot / Node\nqua WebSocket lên Launcher", 1510, 35, 160, 70, "#e0f2fe", "#0284c7", "#0369a1")
    add_task(r3, "bf03_c6", "l3_cus", "Giám sát Dashboard Tiến độ,\nTrạng thái từng Máy giả lập", 1510, 60, 150, 60)

    # Lease renewal & Finish
    add_task(r3, "bf03_r5", "l3_run", "Gia hạn Lease (Heartbeat)\nNếu mất mạng: PAUSED_LICENSE;\nKhi xong: Gửi Run Summary về Cloud", 1700, 45, 150, 65, "#dcfce7", "#16a34a", "#15803d")
    add_end(r3, "bf03_end", "l3_cus", 1750, 70, "Kết thúc")

    # Connectors for BF-03
    add_edge(r3, "bf03_start", "bf03_c1")
    add_edge(r3, "bf03_c1", "bf03_b1", "Verify API", dashed=True, color="#d97706")
    add_edge(r3, "bf03_b1", "bf03_c2", "Tools List", dashed=True, color="#2563eb")
    add_edge(r3, "bf03_r1", "bf03_c3", "Devices List", dashed=True, color="#0284c7")
    add_edge(r3, "bf03_c2", "bf03_c3")
    add_edge(r3, "bf03_c3", "bf03_c4")
    add_edge(r3, "bf03_c4", "bf03_gw_pre")
    add_edge(r3, "bf03_gw_pre", "bf03_c3", "Lỗi: Device offline / Quota vượt", exitX=0.5, exitY=1, entryX=0.5, entryY=1, color="#dc2626")
    add_edge(r3, "bf03_gw_pre", "bf03_c5", "Đạt")
    add_edge(r3, "bf03_c5", "bf03_b2", "Request Lease", color="#d97706")
    add_edge(r3, "bf03_b2", "bf03_r2", "leaseToken trong RAM", dashed=True, color="#0284c7")
    add_edge(r3, "bf03_r2", "bf03_r3", "Decrypted IR")
    add_edge(r3, "bf03_r3", "bf03_ld1", "Goroutine ADB exec", dashed=True, color="#059669")
    add_edge(r3, "bf03_ld1", "bf03_r4", "ADB Events / UI Dump", dashed=True, color="#059669")
    add_edge(r3, "bf03_r4", "bf03_c6", "WebSocket Stream", dashed=True, color="#0284c7")
    add_edge(r3, "bf03_r4", "bf03_r5", "Complete / Heartbeat")
    add_edge(r3, "bf03_r5", "bf03_end")

    # =========================================================================
    # PAGE 4: BF-04 Publisher Coin Payout & Withdrawal
    # =========================================================================
    r4 = create_page("BF-04 Publisher Payout", "bf04_payout")

    # 4 Lanes
    l4_pub = add_lane(r4, "l4_pub", "Publisher (Publisher Portal)", 50, 180, 1750, "#f8fafc", "#94a3b8", "#16a34a", "#ffffff")
    l4_back = add_lane(r4, "l4_back", "Backend (Escrow Ledger & Payout)", 230, 180, 1750, "#ffffff", "#94a3b8", "#d97706", "#ffffff")
    l4_adm = add_lane(r4, "l4_adm", "Admin / Kế toán (Audit Console)", 410, 160, 1750, "#f8fafc", "#94a3b8", "#7c3aed", "#ffffff")
    l4_bank = add_lane(r4, "l4_bank", "Hệ thống Ngân hàng (Napas247 / VietQR)", 570, 150, 1750, "#ffffff", "#94a3b8", "#059669", "#ffffff")

    add_start(r4, "bf04_start", "l4_pub", 60, 70)
    add_task(r4, "bf04_p1", "l4_pub", "Xem Báo cáo Doanh thu &\nSố dư Coin khả dụng trong Ví", 130, 60, 140, 60)
    add_gateway(r4, "bf04_gw_min", "l4_pub", "Đạt Hạn mức\nRút tối thiểu?", 300, 55, 95, 70)
    add_task(r4, "bf04_p2", "l4_pub", "Tạo Yêu cầu Rút tiền (Payout):\nNhập số Coin rút, Số tài khoản,\nTên Ngân hàng & Tên chủ thẻ", 425, 60, 155, 60)

    # Backend lock
    add_task(r4, "bf04_b1", "l4_back", "Kiểm tra Tính hợp lệ:\n- Không có tranh chấp/khiếu nại\n- Khóa số Coin tương ứng (Hold balance)\n- Tạo bản ghi Payout Request (PENDING)", 425, 45, 165, 75, "#fef3c7", "#d97706", "#92400e")

    # Admin review
    add_task(r4, "bf04_adm1", "l4_adm", "Admin / Kế toán kiểm tra:\n- Lịch sử đơn hàng sinh doanh thu\n- Thông tin tài khoản thụ hưởng", 630, 45, 155, 65, "#f3e8ff", "#7c3aed", "#5b21b6")
    add_gateway(r4, "bf04_gw_audit", "l4_adm", "Phê duyệt\nChi trả?", 820, 42, 95, 70)

    # Rejected flow
    add_task(r4, "bf04_b2", "l4_back", "Hủy Payout Request,\nMở khóa hoàn trả Coin về Ví", 800, 45, 140, 60, "#fee2e2", "#dc2626", "#b91c1c")
    add_task(r4, "bf04_p3", "l4_pub", "Nhận thông báo Từ chối\nkèm Lý do kiểm duyệt", 800, 60, 140, 60)

    # Approved flow -> Banking payout
    add_task(r4, "bf04_adm2", "l4_adm", "Thực hiện Lệnh Chuyển tiền\nqua Cổng Ngân hàng / Napas247", 955, 45, 150, 65, "#f3e8ff", "#7c3aed", "#5b21b6")
    add_task(r4, "bf04_bk1", "l4_bank", "Xử lý Lệnh Chuyển tiền 24/7\nvào Tài khoản Ngân hàng Publisher", 955, 40, 155, 65, "#d1fae5", "#059669", "#065f46")
    add_gateway(r4, "bf04_gw_bank", "l4_bank", "Ngân hàng\nThành công?", 1140, 38, 95, 70)

    # Finalize
    add_task(r4, "bf04_b3", "l4_back", "Trừ vĩnh viễn số Coin đã Hold,\nCập nhật trạng thái Payout COMPLETED,\nGhi nhận Báo cáo Tài chính Sàn", 1270, 45, 160, 70, "#dcfce7", "#16a34a", "#15803d")
    add_task(r4, "bf04_p4", "l4_pub", "Nhận Tiền VND trong Tài khoản,\nNhận Email & Biên lai Điện tử", 1460, 60, 150, 60)
    add_end(r4, "bf04_end", "l4_pub", 1640, 70, "Hoàn tất")

    # Connectors for BF-04
    add_edge(r4, "bf04_start", "bf04_p1")
    add_edge(r4, "bf04_p1", "bf04_gw_min")
    add_edge(r4, "bf04_gw_min", "bf04_p2", "Đạt")
    add_edge(r4, "bf04_gw_min", "bf04_p1", "Chưa đủ", exitX=0.5, exitY=0, entryX=0.5, entryY=0, color="#ea580c")
    add_edge(r4, "bf04_p2", "bf04_b1", "Submit Request", color="#2563eb")
    add_edge(r4, "bf04_b1", "bf04_adm1", "Queue Payout", dashed=True, color="#7c3aed")
    add_edge(r4, "bf04_adm1", "bf04_gw_audit")
    add_edge(r4, "bf04_gw_audit", "bf04_b2", "Từ chối", exitX=0.5, exitY=0, entryX=0.5, entryY=1, color="#dc2626")
    add_edge(r4, "bf04_b2", "bf04_p3", "Notify Rejection", dashed=True, color="#dc2626")
    add_edge(r4, "bf04_gw_audit", "bf04_adm2", "Duyệt", exitX=1, exitY=0.5, entryX=0, entryY=0.5, color="#16a34a")
    add_edge(r4, "bf04_adm2", "bf04_bk1", "Lệnh chuyển tiền", color="#059669")
    add_edge(r4, "bf04_bk1", "bf04_gw_bank")
    add_edge(r4, "bf04_gw_bank", "bf04_b3", "Thành công", color="#16a34a")
    add_edge(r4, "bf04_gw_bank", "bf04_b2", "Lỗi chuyển tiền (Refund)", exitX=0.5, exitY=0, entryX=0.8, entryY=1, color="#dc2626")
    add_edge(r4, "bf04_b3", "bf04_p4", "Notify Payout", dashed=True, color="#16a34a")
    add_edge(r4, "bf04_p4", "bf04_end")

    # Generate XML string
    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ", level=0)
    tree.write("business_flows.drawio", encoding="utf-8", xml_declaration=True)
    print("Successfully generated business_flows.drawio with 4 standard pages!")

if __name__ == "__main__":
    build_drawio()
