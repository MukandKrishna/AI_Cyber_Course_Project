import json
import re
import shutil
import sys
import zipfile
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)


def qn(name):
    return f"{{{W_NS}}}{name}"


def paragraph_text(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", NS))


def iter_docx_paragraphs(docx_path):
    with zipfile.ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find("w:body", NS)
    for p in body.iter(qn("p")):
        text = paragraph_text(p)
        if text.strip():
            yield text


def extract(paths):
    data = {}
    for path in paths:
        data[str(path)] = list(iter_docx_paragraphs(path))
    return data


def split_runs_like(original, replacement, run_count):
    if run_count <= 1:
        return [replacement]
    lengths = [len(part) for part in original]
    total = sum(lengths) or 1
    chunks = []
    start = 0
    for i, length in enumerate(lengths):
        if i == run_count - 1:
            chunks.append(replacement[start:])
            break
        end = round((sum(lengths[: i + 1]) / total) * len(replacement))
        chunks.append(replacement[start:end])
        start = end
    return chunks


def replace_paragraph_text(p, replacement):
    text_nodes = p.findall(".//w:t", NS)
    if not text_nodes:
        return
    original_parts = [node.text or "" for node in text_nodes]
    chunks = split_runs_like(original_parts, replacement, len(text_nodes))
    for node, chunk in zip(text_nodes, chunks):
        node.text = chunk
        if chunk.startswith(" ") or chunk.endswith(" "):
            node.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def apply_replacements(src, dst, replacements):
    src = Path(src)
    dst = Path(dst)
    shutil.copyfile(src, dst)
    with zipfile.ZipFile(src, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    remaining = dict(replacements)
    for p in root.iter(qn("p")):
        current = paragraph_text(p)
        if current in remaining:
            replace_paragraph_text(p, remaining[current])

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)


def main(argv):
    if len(argv) < 3:
        raise SystemExit("usage: docx_text_tools.py extract|apply ...")
    cmd = argv[1]
    if cmd == "extract":
        paths = [Path(p) for p in argv[2:]]
        print(json.dumps(extract(paths), indent=2, ensure_ascii=False))
    elif cmd == "apply":
        src = argv[2]
        dst = argv[3]
        repl_path = Path(argv[4])
        replacements = json.loads(repl_path.read_text(encoding="utf-8"))
        apply_replacements(src, dst, replacements)
    else:
        raise SystemExit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main(sys.argv)
