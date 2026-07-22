import shutil
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)


ROWS = [
    ["Experiment", "Top-1", "MRR", "F1", "ROC-AUC", "PR-AUC"],
    ["EXP-01 Highest message count baseline", "0.00", "0.31", "0.00", "0.68", "0.26"],
    ["EXP-02 Lowest mean length baseline", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-03 Random Forest base", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-04 Random Forest contextual", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-05 Random Forest no length", "0.70", "0.80", "0.70", "0.96", "0.84"],
    ["EXP-06 SVM base", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-07 SVM contextual", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-08 SVM no length", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-09 MLP base", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-10 MLP contextual", "1.00", "1.00", "1.00", "1.00", "1.00"],
    ["EXP-11 MLP no length", "0.90", "0.91", "0.90", "0.93", "0.91"],
]

INTERPRETATION = (
    "The 11 experiments show that the full-feature models perform perfectly on PASYDA, "
    "but the baselines and no-length ablations make the interpretation more cautious. "
    "The lowest-mean-length baseline also reached perfect performance, suggesting that "
    "message length is a strong synthetic cue in this dataset. The no-length results are "
    "therefore important because they test whether the models still work when that cue is removed."
)


def qn(name):
    return f"{{{W_NS}}}{name}"


def el(name, attrs=None, text=None):
    node = ET.Element(qn(name), attrs or {})
    if text is not None:
        node.text = text
    return node


def paragraph(text="", style=None, bold=False):
    p = el("p")
    if style:
        ppr = el("pPr")
        pstyle = el("pStyle", {qn("val"): style})
        ppr.append(pstyle)
        p.append(ppr)
    r = el("r")
    if bold:
        rpr = el("rPr")
        rpr.append(el("b"))
        r.append(rpr)
    t = el("t", text=text)
    if text.startswith(" ") or text.endswith(" "):
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    r.append(t)
    p.append(r)
    return p


def table_cell(text, width, header=False, center=False):
    tc = el("tc")
    tcpr = el("tcPr")
    tcpr.append(el("tcW", {qn("w"): str(width), qn("type"): "dxa"}))
    tcpr.append(el("vAlign", {qn("val"): "center"}))
    if header:
        shd = el("shd", {qn("fill"): "D9EAF7", qn("val"): "clear", qn("color"): "auto"})
        tcpr.append(shd)
    tc.append(tcpr)

    p = el("p")
    ppr = el("pPr")
    if center:
        ppr.append(el("jc", {qn("val"): "center"}))
    p.append(ppr)
    r = el("r")
    if header:
        rpr = el("rPr")
        rpr.append(el("b"))
        r.append(rpr)
    r.append(el("t", text=text))
    p.append(r)
    tc.append(p)
    return tc


def build_table():
    tbl = el("tbl")
    tblpr = el("tblPr")
    tblpr.append(el("tblW", {qn("w"): "9360", qn("type"): "dxa"}))
    tblpr.append(el("tblLook", {qn("val"): "04A0"}))
    borders = el("tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        borders.append(el(side, {qn("val"): "single", qn("sz"): "4", qn("space"): "0", qn("color"): "A6A6A6"}))
    tblpr.append(borders)
    tbl.append(tblpr)

    widths = [4200, 1000, 900, 900, 1180, 1180]
    grid = el("tblGrid")
    for width in widths:
        grid.append(el("gridCol", {qn("w"): str(width)}))
    tbl.append(grid)

    for row_index, row in enumerate(ROWS):
        tr = el("tr")
        for col_index, value in enumerate(row):
            tr.append(table_cell(value, widths[col_index], header=row_index == 0, center=col_index > 0))
        tbl.append(tr)
    return tbl


def paragraph_text(p):
    return "".join(t.text or "" for t in p.findall(".//w:t", NS))


def remove_existing_section(body):
    marker = "Full Experiment Portfolio Results"
    children = list(body)
    start = None
    for index, child in enumerate(children):
        if child.tag == qn("p") and paragraph_text(child).strip() == marker:
            start = index
            break
    if start is None:
        return
    sect_index = next((i for i, child in enumerate(children) if child.tag == qn("sectPr")), len(children))
    for child in children[start:sect_index]:
        body.remove(child)


def append_table(docx_path):
    docx_path = Path(docx_path)
    backup = docx_path.with_name(f"{docx_path.stem}.before_experiment_table{docx_path.suffix}")
    if not backup.exists():
        shutil.copyfile(docx_path, backup)

    with zipfile.ZipFile(docx_path, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    body = root.find("w:body", NS)
    remove_existing_section(body)

    sect = body.find("w:sectPr", NS)
    insert_at = list(body).index(sect) if sect is not None else len(list(body))

    additions = [
        paragraph("Full Experiment Portfolio Results", style="Heading1"),
        paragraph(
            "The table below summarises the 11 experiment reports included in the project portfolio.",
            style=None,
        ),
        build_table(),
        paragraph(INTERPRETATION),
    ]
    for offset, node in enumerate(additions):
        body.insert(insert_at + offset, node)

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)
    print(f"Updated {docx_path}")
    print(f"Backup {backup}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: append_experiment_table.py report.docx")
    append_table(sys.argv[1])
