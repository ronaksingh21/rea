from __future__ import annotations

import json
import re
from textwrap import dedent
import google.generativeai as genai

from agent.config import settings
from agent.models import ExtractedDeal


PROMPT_TEMPLATE = dedent(
    """
    Extract the following fields from this commercial real estate offering memorandum text.

    Required JSON shape:
    {
      "property_name": string|null,
      "address": string|null,
      "purchase_price": number|null,
      "noi": number|null,
      "reported_cap_rate": number|null,
      "rent_roll": [
        {
          "unit": string|null,
          "tenant_name": string|null,
          "sqft": number|null,
          "annual_rent": number|null,
          "monthly_rent": number|null,
          "lease_start": string|null,
          "lease_end": string|null,
          "percent_of_income": number|null
        }
      ],
      "lease_expiration_dates": [string]
    }

    Rules:
    - Output STRICT JSON only.
    - If field is missing, return null (or empty list for arrays).
    - No markdown. No explanation.

    OM text:
    {text}
    """
)


def _strip_fences(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z]*", "", s).strip()
        s = s.removesuffix("```").strip()
    return s


def _first_money(text: str, label_patterns: list[str]) -> float | None:
    for lp in label_patterns:
        m = re.search(lp + r"[^\n\r$]{0,50}\$\s*([\d,]+(?:\.\d+)?)", text, flags=re.I)
        if m:
            return float(m.group(1).replace(",", ""))
    return None


def _first_percent(text: str, label_patterns: list[str]) -> float | None:
    for lp in label_patterns:
        m = re.search(lp + r"[^\n\r%]{0,40}([\d]+(?:\.\d+)?)\s*%", text, flags=re.I)
        if m:
            return float(m.group(1)) / 100.0
    return None


def regex_extract_fallback(raw_text: str) -> ExtractedDeal:
    purchase_price = _first_money(raw_text, [r"purchase\s*price", r"list\s*price", r"asking\s*price"])
    noi = _first_money(raw_text, [r"\bnoi\b", r"net\s*operating\s*income"])
    reported_cap_rate = _first_percent(raw_text, [r"cap\s*rate", r"going\s*in\s*cap"])

    lease_dates = re.findall(r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|\d{4}-\d{2}-\d{2})\b", raw_text)

    return ExtractedDeal(
        property_name=None,
        address=None,
        purchase_price=purchase_price,
        noi=noi,
        reported_cap_rate=reported_cap_rate,
        rent_roll=[],
        lease_expiration_dates=lease_dates[:200],
    )


def extract_structured_data(raw_text: str) -> ExtractedDeal:
    if settings.llm_provider == "regex":
        return regex_extract_fallback(raw_text)

    if settings.llm_provider != "gemini":
        raise NotImplementedError("Implemented providers: gemini, regex")

    if not settings.gemini_api_key:
        return regex_extract_fallback(raw_text)

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)

    prompt = PROMPT_TEMPLATE.format(text=raw_text[:200000])
    resp = model.generate_content(prompt)
    text = _strip_fences((resp.text or "").strip())

    try:
        payload = json.loads(text)
        return ExtractedDeal.model_validate(payload)
    except Exception:
        return regex_extract_fallback(raw_text)
