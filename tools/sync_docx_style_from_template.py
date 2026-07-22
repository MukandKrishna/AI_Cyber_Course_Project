import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

ET.register_namespace("w", W_NS)
ET.register_namespace("", CT_NS)
ET.register_namespace("", REL_NS)

STYLE_PARTS = [
    "word/styles.xml",
    "word/numbering.xml",
    "word/settings.xml",
    "word/webSettings.xml",
    "word/fontTable.xml",
    "word/theme/theme1.xml",
    "word/footnotes.xml",
    "word/endnotes.xml",
]

CONTENT_TYPES = {
    "/word/styles.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
    "/word/numbering.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml",
    "/word/settings.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml",
    "/word/webSettings.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.webSettings+xml",
    "/word/fontTable.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml",
    "/word/theme/theme1.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
    "/word/footnotes.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml",
    "/word/endnotes.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml",
}

REL_TYPES = {
    "word/styles.xml": "styles",
    "word/numbering.xml": "numbering",
    "word/settings.xml": "settings",
    "word/webSettings.xml": "webSettings",
    "word/fontTable.xml": "fontTable",
    "word/theme/theme1.xml": "theme",
    "word/footnotes.xml": "footnotes",
    "word/endnotes.xml": "endnotes",
}


def qn(ns, name):
    return f"{{{ns}}}{name}"


def read_zip(path):
    with zipfile.ZipFile(path, "r") as z:
        return {name: z.read(name) for name in z.namelist()}


def ensure_content_types(files):
    root = ET.fromstring(files["[Content_Types].xml"])
    existing = {node.attrib.get("PartName") for node in root.findall(qn(CT_NS, "Override"))}
    for part_name, content_type in CONTENT_TYPES.items():
        if part_name not in existing:
            node = ET.Element(qn(CT_NS, "Override"), {"PartName": part_name, "ContentType": content_type})
            root.append(node)
    files["[Content_Types].xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def ensure_doc_rels(files):
    rel_path = "word/_rels/document.xml.rels"
    root = ET.fromstring(files[rel_path])
    used_ids = {node.attrib["Id"] for node in root.findall(qn(REL_NS, "Relationship")) if "Id" in node.attrib}
    existing_types = {node.attrib.get("Type") for node in root.findall(qn(REL_NS, "Relationship"))}

    next_id = 1
    for part, short_type in REL_TYPES.items():
        rel_type = f"{OFFICE_REL_NS}/{short_type}"
        if rel_type in existing_types:
            continue
        while f"rId{next_id}" in used_ids:
            next_id += 1
        target = part.replace("word/", "")
        node = ET.Element(qn(REL_NS, "Relationship"), {"Id": f"rId{next_id}", "Type": rel_type, "Target": target})
        root.append(node)
        used_ids.add(f"rId{next_id}")
        existing_types.add(rel_type)
    files[rel_path] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def force_times_new_roman(files):
    root = ET.fromstring(files["word/document.xml"])
    for run in root.iter(qn(W_NS, "r")):
        rpr = run.find(qn(W_NS, "rPr"))
        if rpr is None:
            rpr = ET.Element(qn(W_NS, "rPr"))
            run.insert(0, rpr)
        rfonts = rpr.find(qn(W_NS, "rFonts"))
        if rfonts is None:
            rfonts = ET.Element(qn(W_NS, "rFonts"))
            rpr.insert(0, rfonts)
        for attr in ["ascii", "hAnsi", "cs", "eastAsia"]:
            rfonts.set(qn(W_NS, attr), "Times New Roman")
    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)


def sync(template, target):
    template_files = read_zip(template)
    files = read_zip(target)
    for part in STYLE_PARTS:
        if part in template_files:
            files[part] = template_files[part]
    ensure_content_types(files)
    ensure_doc_rels(files)
    force_times_new_roman(files)

    backup = target.with_name(f"{target.stem}.before_style_sync{target.suffix}")
    if not backup.exists():
        shutil.copyfile(target, backup)

    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    print(target)


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: sync_docx_style_from_template.py template.docx target1.docx [target2.docx ...]")
    template = Path(sys.argv[1])
    for arg in sys.argv[2:]:
        target = Path(arg)
        if target.resolve() == template.resolve() or target.name.startswith("~$"):
            continue
        sync(template, target)


if __name__ == "__main__":
    main()
