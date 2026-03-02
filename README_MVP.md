# AI Deal Intake & Underwriting Assistant (MVP)

## Scope
Phase 1 pipeline:
1. Poll Gmail for deal emails with OM PDFs
2. Download PDF attachments
3. Extract OM fields into strict JSON
4. Run basic underwriting + risk score
5. Post summary to Slack
6. Store full output in SQLite

## Quickstart

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `.env` values:
- `GMAIL_CREDENTIALS_PATH`: OAuth desktop credentials JSON from Google Cloud
- `GEMINI_API_KEY`: model API key
- `SLACK_BOT_TOKEN` + `SLACK_CHANNEL`

Then run:

```bash
python -m agent.main
```

## Data Output
- PDFs: `data/pdfs/`
- SQLite DB: `data/deals.db`

## JSON Contract
See `agent/models.py` (`ExtractedDeal`, `RentRollRow`).

## Success Criteria (MVP)
- Process 10 OMs with no manual correction
- Rent roll extracted as structured rows
- Calculated cap rate within ±3% of reported cap rate
- Slack summary auto-generated

## Notes
- OCR path requires local Tesseract + poppler.
- Current LLM extractor implements Gemini first; provider abstraction is in place for OpenAI/Anthropic extension.
