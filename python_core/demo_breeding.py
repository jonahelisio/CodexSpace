from __future__ import annotations

import json
import random
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from python_core.breeder import breed_until_interesting
else:
    from .breeder import breed_until_interesting


def main() -> int:
    session_path = Path(__file__).resolve().parent.parent / "breeding_session_1773344612627.json"
    sessions = json.loads(session_path.read_text())
    latest = sessions[-1]
    parent1 = latest["parent1"]
    parent2 = latest["parent2"]

    child1, child2 = breed_until_interesting(
        parent1,
        parent2,
        attempts=50,
        rng=random.Random(7474),
    )

    print("Parent 1:", parent1)
    print("Parent 2:", parent2)
    print("Child 1 :", child1.formula)
    print("Child 2 :", child2.formula)
    print("Validation 1:", child1.validation)
    print("Validation 2:", child2.validation)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
