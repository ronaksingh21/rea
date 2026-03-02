from __future__ import annotations

import pdfplumber
from pathlib import Path


def extract_pdf_text(pdf_path: str) -> str:
    chunks: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                chunks.append(text)
    return "\n\n".join(chunks)


def has_usable_text(text: str) -> bool:
    return len(text.strip()) > 300


def ensure_path(path: str) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    return p
