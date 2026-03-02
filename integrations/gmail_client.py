from __future__ import annotations

import base64
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from agent.config import settings

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _get_creds() -> Credentials:
    token_path = Path(settings.gmail_token_path)
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(settings.gmail_credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return creds


def _service():
    return build("gmail", "v1", credentials=_get_creds())


def list_candidate_messages(max_results: int = 10) -> List[str]:
    svc = _service()
    result = svc.users().messages().list(userId="me", q=settings.gmail_query, maxResults=max_results).execute()
    return [m["id"] for m in result.get("messages", [])]


def download_pdf_attachments(message_id: str, output_dir: str) -> List[Dict]:
    svc = _service()
    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = msg.get("payload", {})
    headers = {h["name"].lower(): h["value"] for h in payload.get("headers", [])}

    sender = headers.get("from", "")
    subject = headers.get("subject", "")
    date_hdr = headers.get("date", "")

    out = []
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    parts = payload.get("parts", []) or []
    for p in parts:
        filename = p.get("filename", "")
        if not filename.lower().endswith(".pdf"):
            continue
        body = p.get("body", {})
        attach_id = body.get("attachmentId")
        if not attach_id:
            continue
        att = svc.users().messages().attachments().get(userId="me", messageId=message_id, id=attach_id).execute()
        raw = att.get("data", "")
        content = base64.urlsafe_b64decode(raw.encode("utf-8"))

        save_path = Path(output_dir) / f"{message_id}_{filename}"
        save_path.write_bytes(content)

        out.append(
            {
                "message_id": message_id,
                "subject": subject,
                "sender": sender,
                "date": date_hdr,
                "received_at": datetime.utcnow().isoformat(),
                "pdf_path": str(save_path),
            }
        )

    return out
