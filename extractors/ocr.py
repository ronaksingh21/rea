from __future__ import annotations

from pdf2image import convert_from_path
import pytesseract


def ocr_pdf(pdf_path: str) -> str:
    images = convert_from_path(pdf_path, dpi=200)
    out = []
    for img in images:
        out.append(pytesseract.image_to_string(img))
    return "\n\n".join(out)
