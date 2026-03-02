from __future__ import annotations

import json
import sys
from agent.models import ExtractedDeal


def main(path: str) -> None:
    data = json.loads(open(path, "r", encoding="utf-8").read())
    _ = ExtractedDeal.model_validate(data)
    print("OK: valid ExtractedDeal JSON")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/validate_output.py <json-file>")
        raise SystemExit(1)
    main(sys.argv[1])
