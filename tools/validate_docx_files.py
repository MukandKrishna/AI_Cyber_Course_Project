import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


REQUIRED = {
    "[Content_Types].xml",
    "_rels/.rels",
    "word/document.xml",
}


def validate(path):
    path = Path(path)
    with zipfile.ZipFile(path) as zf:
        names = set(zf.namelist())
        missing = REQUIRED - names
        if missing:
            return False, f"missing {sorted(missing)}"
        ET.fromstring(zf.read("word/document.xml"))
        text_count = sum(1 for _ in ET.fromstring(zf.read("word/document.xml")).iter())
    return True, f"valid OOXML, {text_count} XML elements"


def main(argv):
    failed = False
    for arg in argv[1:]:
        ok, message = validate(arg)
        print(f"{arg}: {message}")
        failed = failed or not ok
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv)
