import sys
import docx
from docx.document import Document as _Doc
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    for child in parent.element.body.iterchildren():
        if child.tag == qn("w:p"):
            yield Paragraph(child, parent)
        elif child.tag == qn("w:tbl"):
            yield Table(child, parent)


def main(path):
    d = docx.Document(path)
    for block in iter_block_items(d):
        if isinstance(block, Paragraph):
            t = block.text.strip()
            if t:
                print(f"[{block.style.name}] {t}")
        else:
            print("=== TABLE ===")
            for row in block.rows:
                print(" | ".join(c.text.strip() for c in row.cells))
            print("=== END TABLE ===")


if __name__ == "__main__":
    main(sys.argv[1])
