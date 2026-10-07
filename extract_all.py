import os
import glob
import zipfile
import xml.etree.ElementTree as ET

def extract_docx(path):
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
        return f"Error: {e}"

def extract_xlsx(path):
    try:
        with zipfile.ZipFile(path) as z:
            shared_strings = []
            if "xl/sharedStrings.xml" in z.namelist():
                sst_tree = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in sst_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                    t_nodes = [t.text for t in si.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t") if t.text]
                    shared_strings.append("".join(t_nodes))

            wb_tree = ET.fromstring(z.read("xl/workbook.xml"))
            sheets = []
            for sheet in wb_tree.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet"):
                sheets.append(sheet.attrib.get("name"))

            res = []
            for idx, s_name in enumerate(sheets, 1):
                fname = f"xl/worksheets/sheet{idx}.xml"
                if fname not in z.namelist():
                    continue
                s_tree = ET.fromstring(z.read(fname))
                res.append(f"--- Sheet: {s_name} ---")
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
                            row_vals.append(val.strip())
                    if row_vals:
                        res.append(" | ".join(row_vals))
            return "\n".join(res)
    except Exception as e:
        return f"Error: {e}"

os.makedirs("extracted_texts", exist_ok=True)

# Find all files in 01. Đồ án FPTU (ignoring Sample Document to focus on G52 A2MaTex)
target_dir = [d for d in os.listdir(".") if "Đồ án FPTU" in d or "Đồ án FPTU" in d][0]

for root, dirs, files in os.walk(target_dir):
    if "Sample Document" in root or "01. Sample report" in root or "00. Template Report" in root or "00. Templates" in root:
        continue
    for f in files:
        full_p = os.path.join(root, f)
        clean_name = f.replace(" ", "_").replace("/", "_")
        out_p = os.path.join("extracted_texts", clean_name + ".txt")
        if f.endswith(".docx"):
            print(f"Extracting docx: {full_p}")
            txt = extract_docx(full_p)
            with open(out_p, "w", encoding="utf-8") as out_f:
                out_f.write(txt)
        elif f.endswith(".xlsx"):
            print(f"Extracting xlsx: {full_p}")
            txt = extract_xlsx(full_p)
            with open(out_p, "w", encoding="utf-8") as out_f:
                out_f.write(txt)

print("Extraction completed!")
