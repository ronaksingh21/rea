from __future__ import annotations

import json
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, Session

from agent.config import settings
from agent.models import DealRecord

Base = declarative_base()


class DealRow(Base):
    __tablename__ = "deals"

    id = Column(Integer, primary_key=True)
    message_id = Column(String, index=True)
    subject = Column(String)
    sender = Column(String)
    received_at = Column(String)
    pdf_path = Column(String)
    extracted_json = Column(Text)
    underwriting_json = Column(Text)


engine = create_engine(settings.database_url, future=True)


def init_db() -> None:
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(engine)


def already_processed(message_id: str) -> bool:
    with Session(engine) as s:
        return s.query(DealRow).filter(DealRow.message_id == message_id).first() is not None


def save_deal(record: DealRecord) -> None:
    with Session(engine) as s:
        row = DealRow(
            message_id=record.message_id,
            subject=record.subject,
            sender=record.sender,
            received_at=record.received_at.isoformat(),
            pdf_path=record.pdf_path,
            extracted_json=json.dumps(record.extracted.model_dump(), default=str),
            underwriting_json=json.dumps(record.underwriting.model_dump(), default=str),
        )
        s.add(row)
        s.commit()
