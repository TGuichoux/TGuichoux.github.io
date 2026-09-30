import sys
from pathlib import Path

import fitz  # PyMuPDF


if len(sys.argv) != 2:
    print(f"Usage: python {Path(sys.argv[0]).name} file.pdf")
    sys.exit(1)

pdf_path = Path(sys.argv[1])
png_path = pdf_path.with_suffix(".png")

doc = fitz.open(pdf_path)
page = doc[0]
pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
pix.save(png_path)
doc.close()

print(png_path)