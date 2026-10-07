import xml.etree.ElementTree as ET

def create_drawio():
    mxfile = ET.Element("mxfile", host="app.diagrams.net", pages="3")

    # ------------------ PAGE 1: Flow 1 ------------------
    diag1 = ET.SubElement(mxfile, "diagram", name="Flow 1 - Publisher Authoring & Release", id="flow1_authoring")
    model1 = ET.SubElement(diag1, "mxGraphModel", dx="1422", dy="800", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1600", pageHeight="700", math="0", shadow="0")
    root1 = ET.SubElement(model1, "root")
    ET.SubElement(root1, "mxCell", id="0")
    ET.SubElement(root1, "mxCell", id="1", parent="0")

    # Swimlanes
    # Actor Swimlane
    s1 = ET.SubElement(root1, "mxCell", id="lane_actor", parent="1", style="swimlane;horizontal=0;fillColor=#f0fdf4;strokeColor=#16a34a;fontColor=#15803d;fontStyle=1;align=center;", value="Publisher (Studio / Web Portal)", vertex="1")
    ET.SubElement(s1, "mxGeometry", x="40", y="60", width="1500", height="240", as="geometry")

    # System Swimlane
    s2 = ET.SubElement(root1, "mxCell", id="lane_sys", parent="1", style="swimlane;horizontal=0;fillColor=#fefce8;strokeColor=#ca8a04;fontColor=#854d0e;fontStyle=1;align=center;", value="A2MaTeX System (Studio / Runtime / Backend)", vertex="1")
    ET.SubElement(s2, "mxGeometry", x="40", y="300", width="1500", height="250", as="geometry")

    # Nodes Page 1
    # Start
    n_start = ET.SubElement(root1, "mxCell", id="f1_start", parent="lane_actor", style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dcfce7;strokeColor=#16a34a;fontStyle=1;fontColor=#15803d;", value="Start", vertex="1")
    ET.SubElement(n_start, "mxGeometry", x="50", y="90", width="50", height="50", as="geometry")

    # Act 1: Create & Design
    n_act1 = ET.SubElement(root1, "mxCell", id="f1_act1", parent="lane_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Create Project &amp;&#xa;Design Graph Canvas", vertex="1")
    ET.SubElement(n_act1, "mxGeometry", x="130", y="85", width="130", height="60", as="geometry")

    # Sys 1: Realtime Validate
    n_sys1 = ET.SubElement(root1, "mxCell", id="f1_sys1", parent="lane_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Validate Schema &amp;&#xa;Detect Cycles", vertex="1")
    ET.SubElement(n_sys1, "mxGeometry", x="130", y="95", width="130", height="60", as="geometry")

    # Dec 1: Test Locally?
    n_dec1 = ET.SubElement(root1, "mxCell", id="f1_dec1", parent="lane_actor", style="rhombus;whiteSpace=wrap;html=1;fillColor=#ffedd5;strokeColor=#ea580c;fontStyle=1;fontColor=#9a3412;", value="Test locally on&#xa;LDPlayer?", vertex="1")
    ET.SubElement(n_dec1, "mxGeometry", x="290", y="75", width="120", height="80", as="geometry")

    # Act 2: Local Test
    n_act2 = ET.SubElement(root1, "mxCell", id="f1_act2", parent="lane_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Select Target LDPlayer &amp;&#xa;Trigger Test Run", vertex="1")
    ET.SubElement(n_act2, "mxGeometry", x="440", y="145", width="140", height="60", as="geometry")

    # Sys 2: Local Execute
    n_sys2 = ET.SubElement(root1, "mxCell", id="f1_sys2", parent="lane_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Execute on Device &amp;&#xa;Stream Logs/Screenshots", vertex="1")
    ET.SubElement(n_sys2, "mxGeometry", x="440", y="95", width="140", height="60", as="geometry")

    # Act 3: Cloud Sync
    n_act3 = ET.SubElement(root1, "mxCell", id="f1_act3", parent="lane_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Save &amp; Sync Draft&#xa;to Cloud Backend", vertex="1")
    ET.SubElement(n_act3, "mxGeometry", x="620", y="85", width="130", height="60", as="geometry")

    # Sys 3: Store Draft
    n_sys3 = ET.SubElement(root1, "mxCell", id="f1_sys3", parent="lane_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Store ProjectDraft&#xa;&amp; Assets in S3", vertex="1")
    ET.SubElement(n_sys3, "mxGeometry", x="620", y="95", width="130", height="60", as="geometry")

    # Act 4: Self-review & Listing Info
    n_act4 = ET.SubElement(root1, "mxCell", id="f1_act4", parent="lane_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Review Checklist &amp;&#xa;Input Listing Metadata", vertex="1")
    ET.SubElement(n_act4, "mxGeometry", x="780", y="85", width="140", height="60", as="geometry")

    # Act 5: Submit
    n_act5 = ET.SubElement(root1, "mxCell", id="f1_act5", parent="lane_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Click 'Submit for Review'", vertex="1")
    ET.SubElement(n_act5, "mxGeometry", x="950", y="85", width="130", height="60", as="geometry")

    # Sys 4: Freeze & Scan
    n_sys4 = ET.SubElement(root1, "mxCell", id="f1_sys4", parent="lane_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Freeze WorkflowRevision;&#xa;Run Automated Scanner", vertex="1")
    ET.SubElement(n_sys4, "mxGeometry", x="940", y="95", width="150", height="60", as="geometry")

    # Sys Dec: Admin Review
    n_dec2 = ET.SubElement(root1, "mxCell", id="f1_dec2", parent="lane_sys", style="rhombus;whiteSpace=wrap;html=1;fillColor=#ffedd5;strokeColor=#ea580c;fontStyle=1;fontColor=#9a3412;", value="Admin Review&#xa;Approved?", vertex="1")
    ET.SubElement(n_dec2, "mxGeometry", x="1130", y="85", width="120", height="80", as="geometry")

    # Sys 5: Encrypt & Publish
    n_sys5 = ET.SubElement(root1, "mxCell", id="f1_sys5", parent="lane_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Compile IR, Encrypt,&#xa;Build .a2m &amp; Publish", vertex="1")
    ET.SubElement(n_sys5, "mxGeometry", x="1290", y="95", width="140", height="60", as="geometry")

    # Act 6: Track Sales
    n_act6 = ET.SubElement(root1, "mxCell", id="f1_act6", parent="lane_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Track Active Release&#xa;&amp; View Sales Metrics", vertex="1")
    ET.SubElement(n_act6, "mxGeometry", x="1295", y="85", width="130", height="60", as="geometry")

    # End
    n_end = ET.SubElement(root1, "mxCell", id="f1_end", parent="lane_actor", style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fee2e2;strokeColor=#dc2626;fontStyle=1;fontColor=#b91c1c;", value="End", vertex="1")
    ET.SubElement(n_end, "mxGeometry", x="1445", y="90", width="50", height="50", as="geometry")

    # Page 1 Edges
    def add_edge(parent, sid, tid, val="", dashed=False, color="#334155"):
        style = f"edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;strokeColor={color};strokeWidth=1.5;endArrow=classic;"
        if dashed:
            style += "dashed=1;strokeColor=#64748b;"
        e = ET.SubElement(parent, "mxCell", edge="1", parent=parent.attrib["id"], source=sid, target=tid, style=style, value=val)
        ET.SubElement(e, "mxGeometry", relative="1", as="geometry")

    add_edge(root1, "f1_start", "f1_act1")
    add_edge(root1, "f1_act1", "f1_dec1")
    add_edge(root1, "f1_act1", "f1_sys1", "validate", dashed=True)
    add_edge(root1, "f1_dec1", "f1_act2", "Yes")
    add_edge(root1, "f1_act2", "f1_sys2", "dispatch commands", dashed=True)
    add_edge(root1, "f1_sys2", "f1_act2", "test results", dashed=True)
    add_edge(root1, "f1_dec1", "f1_act3", "No / Passed")
    add_edge(root1, "f1_act2", "f1_act3")
    add_edge(root1, "f1_act3", "f1_sys3", "upload draft", dashed=True)
    add_edge(root1, "f1_act3", "f1_act4")
    add_edge(root1, "f1_act4", "f1_act5")
    add_edge(root1, "f1_act5", "f1_sys4", "submit snapshot", dashed=True)
    add_edge(root1, "f1_sys4", "f1_dec2")
    add_edge(root1, "f1_dec2", "f1_sys5", "Approved")
    add_edge(root1, "f1_dec2", "f1_act1", "Reject / Changes Requested", color="#ea580c")
    add_edge(root1, "f1_sys5", "f1_act6", "published notice", dashed=True)
    add_edge(root1, "f1_act6", "f1_end")

    # ------------------ PAGE 2: Flow 2 ------------------
    diag2 = ET.SubElement(mxfile, "diagram", name="Flow 2 - Customer Acquisition & Entitlement", id="flow2_commerce")
    model2 = ET.SubElement(diag2, "mxGraphModel", dx="1422", dy="800", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1600", pageHeight="700", math="0", shadow="0")
    root2 = ET.SubElement(model2, "root")
    ET.SubElement(root2, "mxCell", id="0")
    ET.SubElement(root2, "mxCell", id="1", parent="0")

    s2_1 = ET.SubElement(root2, "mxCell", id="lane2_actor", parent="1", style="swimlane;horizontal=0;fillColor=#f0fdf4;strokeColor=#16a34a;fontColor=#15803d;fontStyle=1;align=center;", value="Customer (Web Browser)", vertex="1")
    ET.SubElement(s2_1, "mxGeometry", x="40", y="60", width="1500", height="240", as="geometry")

    s2_2 = ET.SubElement(root2, "mxCell", id="lane2_sys", parent="1", style="swimlane;horizontal=0;fillColor=#fefce8;strokeColor=#ca8a04;fontColor=#854d0e;fontStyle=1;align=center;", value="A2MaTeX / SePay System", vertex="1")
    ET.SubElement(s2_2, "mxGeometry", x="40", y="300", width="1500", height="250", as="geometry")

    # Nodes Page 2
    n2_start = ET.SubElement(root2, "mxCell", id="f2_start", parent="lane2_actor", style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dcfce7;strokeColor=#16a34a;fontStyle=1;fontColor=#15803d;", value="Start", vertex="1")
    ET.SubElement(n2_start, "mxGeometry", x="50", y="90", width="50", height="50", as="geometry")

    n2_act1 = ET.SubElement(root2, "mxCell", id="f2_act1", parent="lane2_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Browse Marketplace &amp;&#xa;Search Tools", vertex="1")
    ET.SubElement(n2_act1, "mxGeometry", x="130", y="85", width="130", height="60", as="geometry")

    n2_sys1 = ET.SubElement(root2, "mxCell", id="f2_sys1", parent="lane2_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Query Catalog &amp;&#xa;Return Active Listings", vertex="1")
    ET.SubElement(n2_sys1, "mxGeometry", x="130", y="95", width="130", height="60", as="geometry")

    n2_act2 = ET.SubElement(root2, "mxCell", id="f2_act2", parent="lane2_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="View Tool Details,&#xa;Compatibility &amp; Pricing", vertex="1")
    ET.SubElement(n2_act2, "mxGeometry", x="290", y="85", width="130", height="60", as="geometry")

    n2_dec1 = ET.SubElement(root2, "mxCell", id="f2_dec1", parent="lane2_actor", style="rhombus;whiteSpace=wrap;html=1;fillColor=#ffedd5;strokeColor=#ea580c;fontStyle=1;fontColor=#9a3412;", value="Free or Paid&#xa;Offering?", vertex="1")
    ET.SubElement(n2_dec1, "mxGeometry", x="450", y="75", width="120", height="80", as="geometry")

    n2_act3 = ET.SubElement(root2, "mxCell", id="f2_act3", parent="lane2_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Click 'Buy Now' &amp;&#xa;Confirm Order", vertex="1")
    ET.SubElement(n2_act3, "mxGeometry", x="600", y="85", width="130", height="60", as="geometry")

    n2_sys2 = ET.SubElement(root2, "mxCell", id="f2_sys2", parent="lane2_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Create Order PENDING;&#xa;Generate SePay QR", vertex="1")
    ET.SubElement(n2_sys2, "mxGeometry", x="600", y="95", width="130", height="60", as="geometry")

    n2_act4 = ET.SubElement(root2, "mxCell", id="f2_act4", parent="lane2_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Scan QR Code &amp;&#xa;Transfer Payment", vertex="1")
    ET.SubElement(n2_act4, "mxGeometry", x="760", y="85", width="130", height="60", as="geometry")

    n2_sys3 = ET.SubElement(root2, "mxCell", id="f2_sys3", parent="lane2_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="SePay Webhook: Verify&#xa;Transaction &amp; Mark PAID", vertex="1")
    ET.SubElement(n2_sys3, "mxGeometry", x="760", y="95", width="130", height="60", as="geometry")

    n2_sys4 = ET.SubElement(root2, "mxCell", id="f2_sys4", parent="lane2_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Grant Entitlement;&#xa;Set Device Limit &amp; Expiry", vertex="1")
    ET.SubElement(n2_sys4, "mxGeometry", x="920", y="95", width="140", height="60", as="geometry")

    n2_act5 = ET.SubElement(root2, "mxCell", id="f2_act5", parent="lane2_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="View Tool in&#xa;'My Products' Library", vertex="1")
    ET.SubElement(n2_act5, "mxGeometry", x="1090", y="85", width="130", height="60", as="geometry")

    n2_act6 = ET.SubElement(root2, "mxCell", id="f2_act6", parent="lane2_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Click 'Open in&#xa;Launcher' Protocol", vertex="1")
    ET.SubElement(n2_act6, "mxGeometry", x="1250", y="85", width="130", height="60", as="geometry")

    n2_sys5 = ET.SubElement(root2, "mxCell", id="f2_sys5", parent="lane2_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Dispatch Desktop&#xa;Launcher URI Handler", vertex="1")
    ET.SubElement(n2_sys5, "mxGeometry", x="1250", y="95", width="130", height="60", as="geometry")

    n2_end = ET.SubElement(root2, "mxCell", id="f2_end", parent="lane2_actor", style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fee2e2;strokeColor=#dc2626;fontStyle=1;fontColor=#b91c1c;", value="End", vertex="1")
    ET.SubElement(n2_end, "mxGeometry", x="1420", y="90", width="50", height="50", as="geometry")

    add_edge(root2, "f2_start", "f2_act1")
    add_edge(root2, "f2_act1", "f2_sys1", "fetch catalog", dashed=True)
    add_edge(root2, "f2_act1", "f2_act2")
    add_edge(root2, "f2_act2", "f2_dec1")
    add_edge(root2, "f2_dec1", "f2_act3", "Paid")
    add_edge(root2, "f2_dec1", "f2_sys4", "Free Acquisition", color="#16a34a")
    add_edge(root2, "f2_act3", "f2_sys2", "create order", dashed=True)
    add_edge(root2, "f2_sys2", "f2_act4", "display QR", dashed=True)
    add_edge(root2, "f2_act3", "f2_act4")
    add_edge(root2, "f2_act4", "f2_sys3", "bank transfer", dashed=True)
    add_edge(root2, "f2_sys3", "f2_sys4")
    add_edge(root2, "f2_sys4", "f2_act5", "grant notice", dashed=True)
    add_edge(root2, "f2_act4", "f2_act5")
    add_edge(root2, "f2_act5", "f2_act6")
    add_edge(root2, "f2_act6", "f2_sys5", "open URI", dashed=True)
    add_edge(root2, "f2_act6", "f2_end")

    # ------------------ PAGE 3: Flow 3 ------------------
    diag3 = ET.SubElement(mxfile, "diagram", name="Flow 3 - Multi-Device Launcher & Runtime", id="flow3_runtime")
    model3 = ET.SubElement(diag3, "mxGraphModel", dx="1422", dy="800", grid="1", gridSize="10", guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1", pageScale="1", pageWidth="1600", pageHeight="700", math="0", shadow="0")
    root3 = ET.SubElement(model3, "root")
    ET.SubElement(root3, "mxCell", id="0")
    ET.SubElement(root3, "mxCell", id="1", parent="0")

    s3_1 = ET.SubElement(root3, "mxCell", id="lane3_actor", parent="1", style="swimlane;horizontal=0;fillColor=#f0fdf4;strokeColor=#16a34a;fontColor=#15803d;fontStyle=1;align=center;", value="Customer (Launcher UI)", vertex="1")
    ET.SubElement(s3_1, "mxGeometry", x="40", y="60", width="1500", height="240", as="geometry")

    s3_2 = ET.SubElement(root3, "mxCell", id="lane3_sys", parent="1", style="swimlane;horizontal=0;fillColor=#fefce8;strokeColor=#ca8a04;fontColor=#854d0e;fontStyle=1;align=center;", value="A2MaTeX Runtime Agent / Backend", vertex="1")
    ET.SubElement(s3_2, "mxGeometry", x="40", y="300", width="1500", height="250", as="geometry")

    # Nodes Page 3
    n3_start = ET.SubElement(root3, "mxCell", id="f3_start", parent="lane3_actor", style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#dcfce7;strokeColor=#16a34a;fontStyle=1;fontColor=#15803d;", value="Start", vertex="1")
    ET.SubElement(n3_start, "mxGeometry", x="50", y="90", width="50", height="50", as="geometry")

    n3_act1 = ET.SubElement(root3, "mxCell", id="f3_act1", parent="lane3_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Open Launcher &amp;&#xa;Download .a2m Package", vertex="1")
    ET.SubElement(n3_act1, "mxGeometry", x="130", y="85", width="130", height="60", as="geometry")

    n3_sys1 = ET.SubElement(root3, "mxCell", id="f3_sys1", parent="lane3_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Verify SHA-256 Hash;&#xa;Scan LDPlayer Instances", vertex="1")
    ET.SubElement(n3_sys1, "mxGeometry", x="130", y="95", width="130", height="60", as="geometry")

    n3_act2 = ET.SubElement(root3, "mxCell", id="f3_act2", parent="lane3_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Select Target Devices &amp;&#xa;Assign Input Profiles", vertex="1")
    ET.SubElement(n3_act2, "mxGeometry", x="290", y="85", width="130", height="60", as="geometry")

    n3_act3 = ET.SubElement(root3, "mxCell", id="f3_act3", parent="lane3_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Click 'Run Tool'&#xa;(Trigger Execution)", vertex="1")
    ET.SubElement(n3_act3, "mxGeometry", x="450", y="85", width="130", height="60", as="geometry")

    n3_sys2 = ET.SubElement(root3, "mxCell", id="f3_sys2", parent="lane3_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Run Preflight Checks &amp;&#xa;Issue Execution Lease", vertex="1")
    ET.SubElement(n3_sys2, "mxGeometry", x="450", y="95", width="130", height="60", as="geometry")

    n3_dec1 = ET.SubElement(root3, "mxCell", id="f3_dec1", parent="lane3_sys", style="rhombus;whiteSpace=wrap;html=1;fillColor=#ffedd5;strokeColor=#ea580c;fontStyle=1;fontColor=#9a3412;", value="Preflight&#xa;Valid?", vertex="1")
    ET.SubElement(n3_dec1, "mxGeometry", x="620", y="85", width="110", height="80", as="geometry")

    n3_sys3 = ET.SubElement(root3, "mxCell", id="f3_sys3", parent="lane3_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Validate LeaseToken, Decrypt&#xa;IR in RAM &amp; Spawn Goroutines", vertex="1")
    ET.SubElement(n3_sys3, "mxGeometry", x="760", y="95", width="150", height="60", as="geometry")

    n3_sys4 = ET.SubElement(root3, "mxCell", id="f3_sys4", parent="lane3_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Execute Typed ADB Commands,&#xa;Record SQLite &amp; Renew Lease", vertex="1")
    ET.SubElement(n3_sys4, "mxGeometry", x="940", y="95", width="150", height="60", as="geometry")

    n3_act4 = ET.SubElement(root3, "mxCell", id="f3_act4", parent="lane3_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="Monitor Live Sequence,&#xa;Screenshots &amp; Logs", vertex="1")
    ET.SubElement(n3_act4, "mxGeometry", x="950", y="85", width="130", height="60", as="geometry")

    n3_dec2 = ET.SubElement(root3, "mxCell", id="f3_dec2", parent="lane3_actor", style="rhombus;whiteSpace=wrap;html=1;fillColor=#ffedd5;strokeColor=#ea580c;fontStyle=1;fontColor=#9a3412;", value="Pause or Cancel&#xa;Requested?", vertex="1")
    ET.SubElement(n3_dec2, "mxGeometry", x="1110", y="75", width="120", height="80", as="geometry")

    n3_sys5 = ET.SubElement(root3, "mxCell", id="f3_sys5", parent="lane3_sys", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fef9c3;strokeColor=#ca8a04;fontStyle=2;fontColor=#854d0e;", value="Conclude Run, Finalize SQLite&#xa;&amp; Sync Summary to Cloud", vertex="1")
    ET.SubElement(n3_sys5, "mxGeometry", x="1115", y="95", width="140", height="60", as="geometry")

    n3_act5 = ET.SubElement(root3, "mxCell", id="f3_act5", parent="lane3_actor", style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#64748b;fontStyle=1;", value="View Final Report &amp;&#xa;Execution Artifacts", vertex="1")
    ET.SubElement(n3_act5, "mxGeometry", x="1270", y="85", width="130", height="60", as="geometry")

    n3_end = ET.SubElement(root3, "mxCell", id="f3_end", parent="lane3_actor", style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;fillColor=#fee2e2;strokeColor=#dc2626;fontStyle=1;fontColor=#b91c1c;", value="End", vertex="1")
    ET.SubElement(n3_end, "mxGeometry", x="1430", y="90", width="50", height="50", as="geometry")

    add_edge(root3, "f3_start", "f3_act1")
    add_edge(root3, "f3_act1", "f3_sys1", "verify hash", dashed=True)
    add_edge(root3, "f3_act1", "f3_act2")
    add_edge(root3, "f3_act2", "f3_act3")
    add_edge(root3, "f3_act3", "f3_sys2", "request lease", dashed=True)
    add_edge(root3, "f3_sys2", "f3_dec1")
    add_edge(root3, "f3_dec1", "f3_act2", "No: Device offline / Limit exceeded", color="#ea580c")
    add_edge(root3, "f3_dec1", "f3_sys3", "Yes")
    add_edge(root3, "f3_sys3", "f3_sys4")
    add_edge(root3, "f3_sys4", "f3_act4", "stream events", dashed=True)
    add_edge(root3, "f3_act3", "f3_act4")
    add_edge(root3, "f3_act4", "f3_dec2")
    add_edge(root3, "f3_dec2", "f3_sys5", "Yes: User Stop / Pause", color="#ea580c")
    add_edge(root3, "f3_dec2", "f3_act5", "No: Completed")
    add_edge(root3, "f3_sys5", "f3_act5", "final summary", dashed=True)
    add_edge(root3, "f3_act5", "f3_end")

    tree = ET.ElementTree(mxfile)
    tree.write("/Users/poiuyt/RoCode/a2matex/01. Đồ án FPTU /02. Documents/03. Reports/Diagrams/Business flows.drawio", encoding="utf-8", xml_declaration=True)
    print("Draw.io file generated successfully!")

if __name__ == "__main__":
    create_drawio()
