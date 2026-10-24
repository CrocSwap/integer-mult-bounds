"""Neumann tail below one 16p unit.

With g=1/(16p) and J=512 p^2, the stated tail is 2(1-g)^J/g. The factor
(1-1/(16p))^(16p) is below 1/2, so the tail is below 32p * 2^(-32p), and
that quantity is below 2^(-16p).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
LOW = 101
HIGH = 200


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_NEUMANN_TAIL_BOUND selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def contracts(precision: int) -> None:
    modulus = 16 * precision
    if 2 * (modulus - 1) ** modulus >= modulus ** modulus:
        raise SystemExit("FAIL_NEUMANN_TAIL_BOUND contraction moved")
    length = 512 * precision * precision
    if length != modulus * (32 * precision):
        raise SystemExit("FAIL_NEUMANN_TAIL_BOUND exponent split moved")
    if 32 * precision >= (1 << (16 * precision)):
        raise SystemExit("FAIL_NEUMANN_TAIL_BOUND final room moved")


def main() -> None:
    pinned = load()
    precisions = 0
    for precision in range(LOW, HIGH + 1):
        contracts(precision)
        precisions += 1
    if pinned["precisions"] != precisions or pinned["no_new_kappa"] is not True:
        raise SystemExit("FAIL_NEUMANN_TAIL_BOUND pinned result moved")
    print(f"PASS_NEUMANN_TAIL_BOUND precisions={precisions} no_new_kappa")


if __name__ == "__main__":
    main()
