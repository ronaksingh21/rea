from __future__ import annotations

import json
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


def extract_structured_data(raw_text: str) -> ExtractedDeal:
    if settings.llm_provider != "gemini":
        raise NotImplementedError("Only gemini provider is implemented in MVP scaffold")

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)

    prompt = PROMPT_TEMPLATE.format(text=raw_text[:200000])
    resp = model.generate_content(prompt)
    text = (resp.text or "").strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON: {e}\nRaw output:\n{text[:1500]}")

    return ExtractedDeal.model_validate(payload)
