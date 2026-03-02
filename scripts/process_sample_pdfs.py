from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.models import DealRecord
from extractors.pdf_reader import extract_pdf_text, has_usable_text
from extractors.ocr import ocr_pdf
from extractors.llm_extract import extract_structured_data
from underwriting.scoring import run_underwriting


def process_folder(folder: str, out_file: str) -> None:
    root = Path(folder)
    results: list[dict] = []

    for pdf in sorted(root.glob("*.pdf"))[:5]:
        text = extract_pdf_text(str(pdf))
        if not has_usable_text(text):
            text = ocr_pdf(str(pdf))

        extracted = extract_structured_data(text)
        uw = run_underwriting(extracted)

        rec = DealRecord(
            message_id=pdf.stem,
            subject=pdf.name,
            sender="sample",
            received_at=datetime.utcnow(),
            pdf_path=str(pdf),
            extracted=extracted,
            underwriting=uw,
        )
        results.append(rec.model_dump(mode="json"))

    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    Path(out_file).write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Processed {len(results)} PDFs -> {out_file}")


if __name__ == "__main__":
    process_folder("tests/om_samples", "data/sample_run_results.json")
