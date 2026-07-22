import html
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML_NS = "http://www.w3.org/XML/1998/namespace"

ET.register_namespace("w", W_NS)
ET.register_namespace("r", R_NS)


def qn(ns, name):
    return f"{{{ns}}}{name}"


def w(name, attrs=None, text=None):
    node = ET.Element(qn(W_NS, name), attrs or {})
    if text is not None:
        node.text = text
    return node


def clean_inline(text):
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    return html.unescape(text).strip()


def paragraph(text="", style=None, bold=False, italic=False):
    p = w("p")
    if style:
        ppr = w("pPr")
        ppr.append(w("pStyle", {qn(W_NS, "val"): style}))
        p.append(ppr)
    r = w("r")
    if bold or italic:
        rpr = w("rPr")
        if bold:
            rpr.append(w("b"))
        if italic:
            rpr.append(w("i"))
        r.append(rpr)
    t = w("t", text=clean_inline(text))
    if text.startswith(" ") or text.endswith(" "):
        t.set(qn(XML_NS, "space"), "preserve")
    r.append(t)
    p.append(r)
    return p


def bullet(text):
    p = paragraph(clean_inline(text))
    ppr = p.find(qn(W_NS, "pPr"))
    if ppr is None:
        ppr = w("pPr")
        p.insert(0, ppr)
    ppr.append(w("numPr"))
    numpr = ppr.find(qn(W_NS, "numPr"))
    numpr.append(w("ilvl", {qn(W_NS, "val"): "0"}))
    numpr.append(w("numId", {qn(W_NS, "val"): "1"}))
    return p


def table(rows):
    tbl = w("tbl")
    tblpr = w("tblPr")
    tblpr.append(w("tblW", {qn(W_NS, "w"): "9360", qn(W_NS, "type"): "dxa"}))
    borders = w("tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        borders.append(w(side, {qn(W_NS, "val"): "single", qn(W_NS, "sz"): "4", qn(W_NS, "space"): "0", qn(W_NS, "color"): "A6A6A6"}))
    tblpr.append(borders)
    tbl.append(tblpr)
    if not rows:
        return tbl
    widths = [max(1200, int(9360 / len(rows[0]))) for _ in rows[0]]
    grid = w("tblGrid")
    for width in widths:
        grid.append(w("gridCol", {qn(W_NS, "w"): str(width)}))
    tbl.append(grid)
    for row_index, row in enumerate(rows):
        tr = w("tr")
        for col_index, value in enumerate(row):
            tc = w("tc")
            tcpr = w("tcPr")
            tcpr.append(w("tcW", {qn(W_NS, "w"): str(widths[col_index]), qn(W_NS, "type"): "dxa"}))
            if row_index == 0:
                tcpr.append(w("shd", {qn(W_NS, "val"): "clear", qn(W_NS, "color"): "auto", qn(W_NS, "fill"): "D9EAF7"}))
            tc.append(tcpr)
            tc.append(paragraph(value, bold=row_index == 0))
            tr.append(tc)
        tbl.append(tr)
    return tbl


def parse_table(lines, start):
    rows = []
    i = start
    while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
        parts = [clean_inline(x) for x in lines[i].strip().strip("|").split("|")]
        if not all(re.fullmatch(r"[:\-\s]+", part) for part in parts):
            rows.append(parts)
        i += 1
    return rows, i


def markdown_blocks(text):
    lines = text.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("|") and stripped.endswith("|"):
            rows, i = parse_table(lines, i)
            blocks.append(table(rows))
            continue
        if stripped.startswith("# "):
            blocks.append(paragraph(stripped[2:], style="Title"))
        elif stripped.startswith("## "):
            blocks.append(paragraph(stripped[3:], style="Heading1"))
        elif stripped.startswith("### "):
            blocks.append(paragraph(stripped[4:], style="Heading2"))
        elif stripped.startswith("- "):
            blocks.append(bullet(stripped[2:]))
        else:
            blocks.append(paragraph(stripped))
        i += 1
    return blocks


def styles_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/></w:rPr><w:pPr><w:spacing w:after="120"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="36"/></w:rPr><w:pPr><w:spacing w:after="240"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="Heading 1"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="28"/></w:rPr><w:pPr><w:spacing w:before="180" w:after="120"/></w:pPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="Heading 2"/><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:b/><w:sz w:val="24"/></w:rPr><w:pPr><w:spacing w:before="120" w:after="80"/></w:pPr></w:style>
</w:styles>"""


def numbering_xml():
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="bullet"/><w:lvlText w:val="•"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum>
  <w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>
</w:numbering>"""


def document_xml(blocks):
    doc = ET.Element(qn(W_NS, "document"))
    body = w("body")
    for block in blocks:
        body.append(block)
    sect = w("sectPr")
    sect.append(w("pgSz", {qn(W_NS, "w"): "12240", qn(W_NS, "h"): "15840"}))
    sect.append(w("pgMar", {qn(W_NS, "top"): "1440", qn(W_NS, "right"): "1440", qn(W_NS, "bottom"): "1440", qn(W_NS, "left"): "1440", qn(W_NS, "header"): "720", qn(W_NS, "footer"): "720", qn(W_NS, "gutter"): "0"}))
    body.append(sect)
    doc.append(body)
    return ET.tostring(doc, encoding="utf-8", xml_declaration=True)


def write_docx(md_path, docx_path):
    text = Path(md_path).read_text(encoding="utf-8")
    blocks = markdown_blocks(text)
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>
</Types>"""
    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""
    doc_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>
</Relationships>"""
    docx_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("word/document.xml", document_xml(blocks))
        z.writestr("word/styles.xml", styles_xml())
        z.writestr("word/numbering.xml", numbering_xml())


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: markdown_to_simple_docx.py output_dir file1.md [file2.md ...]")
    out_dir = Path(sys.argv[1])
    for arg in sys.argv[2:]:
        md = Path(arg)
        out = out_dir / f"{md.stem}.docx"
        write_docx(md, out)
        print(out)


if __name__ == "__main__":
    main()
