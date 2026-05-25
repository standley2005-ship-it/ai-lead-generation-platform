"""Run the lead scoring prototype against a CSV file."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

try:
    from .scoring import Lead, score_lead
except ImportError:  # Allows running as: python src/lead_generation/main.py
    from scoring import Lead, score_lead


def load_leads(path: Path) -> list[Lead]:
    with path.open(newline="", encoding="utf-8") as file:
        return [Lead.from_row(row) for row in csv.DictReader(file)]


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    csv_path = Path(args[0]) if args else Path("data/example_leads.csv")

    if not csv_path.exists():
        print(f"Lead file not found: {csv_path}")
        return 1

    for lead in load_leads(csv_path):
        result = score_lead(lead)
        print(f"{lead.lead_id} | {lead.business_name} | {result.score} | {result.status}")
        for reason in result.reasons:
            print(f"  - {reason}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

