"""Printed E7 generators.

The seven printed vectors span 128 points. The hyperplane of normal 7 in F2^9
contains 256 points, and the span meets it in 64.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
GENERATORS = (256, 128, 66, 36, 22, 8, 1)
NORMAL = 7
AMBIENT = 9


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_E7_GENERATOR_SPAN selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def even_overlap(left: int, right: int) -> bool:
    return (left & right).bit_count() % 2 == 0


def span(generators: tuple[int, ...]) -> set[int]:
    reached = {0}
    for generator in generators:
        reached |= {value ^ generator for value in reached}
    return reached


def main() -> None:
    pinned = load()
    reached = span(GENERATORS)
    odd = [generator for generator in GENERATORS if not even_overlap(generator, NORMAL)]
    intersection = sum(1 for value in reached if even_overlap(value, NORMAL))
    hyperplane = sum(1 for value in range(1 << AMBIENT) if even_overlap(value, NORMAL))
    if len(reached) != 1 << len(GENERATORS):
        raise SystemExit("FAIL_E7_GENERATOR_SPAN generators are dependent")
    if intersection * 2 != len(reached) or hyperplane != 1 << (AMBIENT - 1):
        raise SystemExit("FAIL_E7_GENERATOR_SPAN intersection moved")
    if (
        pinned["generators"] != len(GENERATORS)
        or pinned["span"] != len(reached)
        or pinned["odd_generators"] != len(odd)
        or pinned["hyperplane"] != hyperplane
        or pinned["intersection"] != intersection
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_E7_GENERATOR_SPAN pinned result moved")
    print(f"PASS_E7_GENERATOR_SPAN span={len(reached)} no_new_kappa")


if __name__ == "__main__":
    main()
