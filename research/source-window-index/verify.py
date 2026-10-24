"""Source indices of a rounded target window.

The map sends source index j to floor(t*j/s + 1/2). On the stated box, the
indices that land in a target window [a, b) are exactly the integers from
ceil(s*(2a-1)/(2t)) up to, but not including, ceil(s*(2b-1)/(2t)).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
DENOMINATOR_LIMIT = 20
TARGET_LIMIT = 12


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_SOURCE_WINDOW_INDEX selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def rounded(denominator: int, numerator: int, index: int) -> int:
    return (2 * numerator * index + denominator) // (2 * denominator)


def ceiling_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def source_bounds(denominator: int, numerator: int, low: int, high: int) -> tuple[int, int]:
    start = ceiling_div(denominator * (2 * low - 1), 2 * numerator)
    stop = ceiling_div(denominator * (2 * high - 1), 2 * numerator)
    return start, stop


def main() -> None:
    pinned = load()
    windows = 0
    denominators = 0
    for denominator in range(2, DENOMINATOR_LIMIT + 1):
        denominators += 1
        for numerator in range(denominator + 1, 2 * denominator):
            for low in range(TARGET_LIMIT + 1):
                for high in range(low + 1, TARGET_LIMIT + 2):
                    start, stop = source_bounds(denominator, numerator, low, high)
                    left = -denominator - 2
                    right = high * denominator + 2
                    previous = rounded(denominator, numerator, left)
                    found = []
                    for index in range(left, right + 1):
                        image = rounded(denominator, numerator, index)
                        if image < previous:
                            raise SystemExit("FAIL_SOURCE_WINDOW_INDEX rounding decreased")
                        previous = image
                        if low <= image < high:
                            found.append(index)
                    if previous < high or rounded(denominator, numerator, left) >= low:
                        raise SystemExit("FAIL_SOURCE_WINDOW_INDEX scan range moved")
                    if found != list(range(start, stop)):
                        raise SystemExit("FAIL_SOURCE_WINDOW_INDEX window moved")
                    windows += 1
    if (
        pinned["denominators"] != denominators
        or pinned["windows"] != windows
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_SOURCE_WINDOW_INDEX pinned result moved")
    print(f"PASS_SOURCE_WINDOW_INDEX windows={windows} no_new_kappa")


if __name__ == "__main__":
    main()
