import os
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_docx(path):
    if not os.path.exists(path):
        return f"File not found: {path}"
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read("word/document.xml")
            tree = ET.fromstring(xml_content)
            paragraphs = []
            for p in tree.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p"):
                texts = [node.text for node in p.iter("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t") if node.text]
                if texts:
                    paragraphs.append("".join(texts))
            return "\n".join(paragraphs)
    except Exception as e:
        return f"Error reading {path}: {e}"

def extract_sheets_from_xlsx(path):
    if not os.path.exists(path):
        return f"File not found: {path}"
    try:
        with zipfile.ZipFile(path) as z:
            shared_strings = []
            if "xl/sharedStrings.xml" in z.namelist():
                sst_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in sst_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                    t_nodes = [t.text for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t") if t.text]
                    shared_strings.append("".join(t_nodes))

            # Read sheet names from workbook.xml
            wb_tree = ET.fromstring(z.read("xl/workbook.xml"))
            sheets = []
            for sheet in wb_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"):
                sheets.append((sheet.attrib.get("name"), sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id", "")))

            result = [f"Workbook: {path}"]
            for idx, (s_name, r_id) in enumerate(sheets, 1):
                sheet_filename = f"xl/worksheets/sheet{idx}.xml"
                if sheet_filename in z.namelist():
                    s_tree = ET.fromstring(z.read(sheet_filename))
                    result.append(f"\n--- Sheet: {s_name} ---")
                    row_count = 0
                    for row in s_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row"):
                        row_vals = []
                        for c in row.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c"):
                            t = c.attrib.get("t")
                            v = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v")
                            val = ""
                            if v is not None and v.text is not None:
                                if t == "s":
                                    idx_s = int(v.text)
                                    val = shared_strings[idx_s] if idx_s < len(shared_strings) else v.text
                                else:
                                    val = v.text
                            elif c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is") is not None:
                                is_node = c.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}is")
                                t_node = is_node.find("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")
                                if t_node is not None and t_node.text:
                                    val = t_node.text
                            if val:
                                row_vals.append(val)
                        if row_vals:
                            result.append(" | ".join(row_vals))
                            row_count += 1
                        if row_count > 50:
                            result.append(f"... (truncated after 50 rows)")
                            break
            return "\n".join(result)
    except Exception as e:
        return f"Error reading {path}: {e}"

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    target = sys.argv[2] if len(sys.argv) > 2 else ""
    if mode == "docx":
        print(extract_text_from_docx(target))
    elif mode == "xlsx":
        print(extract_sheets_from_xlsx(target))
