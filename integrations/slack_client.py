from __future__ import annotations

from slack_sdk import WebClient

from agent.config import settings
from agent.models import DealRecord


def send_deal_summary(record: DealRecord) -> None:
    if not settings.slack_bot_token:
        return

    client = WebClient(token=settings.slack_bot_token)
    d = record.extracted
    u = record.underwriting

    cap = f"{(u.calculated_cap_rate or 0) * 100:.2f}%" if u.calculated_cap_rate is not None else "null"
    line = (
        f"*New Deal Detected*\n"
        f"• Subject: {record.subject}\n"
        f"• Price: {d.purchase_price}\n"
        f"• NOI: {d.noi}\n"
        f"• Cap Rate: {cap}\n"
        f"• Lease Expiry <=24m: {u.lease_expiry_24m_percent}\n"
        f"• Risk Score: {u.risk_label} ({u.risk_score})"
    )

    client.chat_postMessage(channel=settings.slack_channel, text=line)
