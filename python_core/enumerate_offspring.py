from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from python_core.breeder import enumerate_labeled_offspring, labeled_offspring_to_jsonable
else:
    from .breeder import enumerate_labeled_offspring, labeled_offspring_to_jsonable


def main() -> int:
    parser = argparse.ArgumentParser(description="Enumerate and label all unique single-swap offspring.")
    parser.add_argument("--formula-a", help="First parent formula")
    parser.add_argument("--formula-b", help="Second parent formula")
    parser.add_argument("--session-json", help="Optional breeding session JSON to read parents from")
    parser.add_argument("--out", required=True, help="Output JSON path")
    args = parser.parse_args()

    formula_a = args.formula_a
    formula_b = args.formula_b

    if args.session_json:
        sessions = json.loads(Path(args.session_json).read_text())
        latest = sessions[-1]
        formula_a = formula_a or latest["parent1"]
        formula_b = formula_b or latest["parent2"]

    if not formula_a or not formula_b:
        parser.error("Provide both formulas directly or via --session-json")

    labeled = enumerate_labeled_offspring(formula_a, formula_b)
    payload = {
        "parent1": formula_a,
        "parent2": formula_b,
        "counts_by_label": dict(Counter(item.label for item in labeled)),
        "offspring": labeled_offspring_to_jsonable(labeled),
    }

    destination = Path(args.out)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(payload, indent=2) + "\n")

    print(f"Wrote {len(labeled)} offspring to {destination}")
    print(f"Counts by label: {payload['counts_by_label']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
