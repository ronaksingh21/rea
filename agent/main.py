from __future__ import annotations

from datetime import datetime
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler

from agent.config import settings
from agent.models import DealRecord
from extractors.pdf_reader import extract_pdf_text, has_usable_text
from extractors.ocr import ocr_pdf
from extractors.llm_extract import extract_structured_data
from integrations.gmail_client import list_candidate_messages, download_pdf_attachments
from integrations.slack_client import send_deal_summary
from storage.db import init_db, already_processed, save_deal
from underwriting.scoring import run_underwriting


def process_once() -> None:
    inbox_dir = Path(settings.data_dir) / "pdfs"
    inbox_dir.mkdir(parents=True, exist_ok=True)

    ids = list_candidate_messages(max_results=20)
    for message_id in ids:
        if already_processed(message_id):
            continue

        attachments = download_pdf_attachments(message_id=message_id, output_dir=str(inbox_dir))
        for item in attachments:
            raw_text = extract_pdf_text(item["pdf_path"])
            if not has_usable_text(raw_text) and settings.ocr_enabled:
                raw_text = ocr_pdf(item["pdf_path"])

            extracted = extract_structured_data(raw_text)
            underwriting = run_underwriting(extracted)

            record = DealRecord(
                message_id=item["message_id"],
                subject=item["subject"],
                sender=item["sender"],
                received_at=datetime.utcnow(),
                pdf_path=item["pdf_path"],
                extracted=extracted,
                underwriting=underwriting,
            )

            save_deal(record)
            send_deal_summary(record)


def run() -> None:
    init_db()
    scheduler = BlockingScheduler()
    scheduler.add_job(process_once, "interval", minutes=settings.gmail_poll_minutes, max_instances=1)
    process_once()
    scheduler.start()


if __name__ == "__main__":
    run()
