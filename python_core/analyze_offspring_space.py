from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from python_core.breeder import analyze_offspring_space
else:
    from .breeder import analyze_offspring_space


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate bounded offspring space for a parsed parent pair.")
    parser.add_argument("--formula-a", help="First parent formula")
    parser.add_argument("--formula-b", help="Second parent formula")
    parser.add_argument("--session-json", help="Optional breeding session JSON to read parents from")
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

    analysis = analyze_offspring_space(formula_a, formula_b)
    print("Parent A nodes:", analysis.parent_a_nodes)
    print("Parent B nodes:", analysis.parent_b_nodes)
    print("Raw swap pairs:", analysis.raw_swap_pairs)
    print("Unique child formulas:", analysis.unique_child_formulas)
    print("Valid child formulas:", analysis.valid_formulas)
    print("Interesting child formulas:", analysis.interesting_formulas)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
