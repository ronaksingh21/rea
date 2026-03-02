#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "Created .env from .env.example"
else
  echo ".env already exists"
fi

echo "\nNext required files:"
echo "- Gmail OAuth desktop credentials JSON (set GMAIL_CREDENTIALS_PATH)"
echo "- Gemini/OpenAI/Anthropic API key (set in .env)"
echo "- Slack bot token + channel"

echo "\nRun this after credentials are in place:"
echo "python -m agent.main"
