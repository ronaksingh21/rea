from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main(path: str = "data/sample_run_results.json") -> None:
    p = Path(path)
    if not p.exists():
        print("No sample results found.")
        return

    rows = json.loads(p.read_text(encoding="utf-8"))
    total = len(rows)
    with_cap = sum(1 for r in rows if r["underwriting"].get("calculated_cap_rate") is not None)
    with_noi_price = sum(
        1
        for r in rows
        if r["extracted"].get("noi") is not None and r["extracted"].get("purchase_price") is not None
    )

    print(f"total_deals={total}")
    print(f"deals_with_noi_and_price={with_noi_price}")
    print(f"deals_with_calculated_cap_rate={with_cap}")

    risks = {}
    for r in rows:
        lbl = r["underwriting"].get("risk_label", "Unknown")
        risks[lbl] = risks.get(lbl, 0) + 1
    print("risk_distribution=", risks)


if __name__ == "__main__":
    main()
