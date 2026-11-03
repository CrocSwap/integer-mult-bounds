"""Bounded search for three-query integer-direction dyadic cubic repairs.

For each arity r in the uncovered set U(N) (see `uncovered`), search all
integer direction triples c1 < c2 < c3 with c1, c2 in [-W, r + W) that
satisfy the node condition e2 = m*e1 - S1, and keep those whose unique
weights are dyadic.  Writes the lexicographically first certificate per
arity plus the list of arities with no certificate in the box.

Usage: search.py OUT.json [--max-r N] [--width W]
       search.py --check FILE.json   (regenerate and compare bytes)

Nick Petalas. Apache-2.0.
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction

MAX_R = 160
WIDTH = 160


def is_power_of_two(x: int) -> bool:
    return x >= 1 and x & (x - 1) == 0


def covered_by_predecessors(r: int) -> str | None:
    """Return the predecessor family that already gives three queries, if any."""
    if r % 3 == 2:
        return "PR6212: r = 2 mod 3"
    if r in (3, 4):
        return "PR6212: r in {3,4}"
    if r % 9 in (0, 1):
        return "PR6215: original-b family, r mod 9 in {0,1}"
    if is_power_of_two(r):
        return "PR6246: r = 2^s"
    if is_power_of_two(r - 1):
        return "PR6250: r = 2^s + 1"
    return None


def uncovered(max_r: int) -> list[int]:
    return [r for r in range(3, max_r + 1) if covered_by_predecessors(r) is None]


def is_dyadic(x: Fraction) -> bool:
    d = x.denominator
    return d & (d - 1) == 0


def weights(r: int, c: tuple[Fraction, Fraction, Fraction]) -> list[Fraction]:
    s1 = Fraction(r * (r - 1), 2)
    m = Fraction(2 * r - 1, 3)
    out = []
    for j in range(3):
        k, l = (i for i in range(3) if i != j)
        out.append(s1 * (m - c[k] - c[l]) / ((c[j] - c[k]) * (c[j] - c[l])))
    return out


def first_certificate(r: int, width: int) -> list[int] | None:
    s1 = Fraction(r * (r - 1), 2)
    m = Fraction(2 * r - 1, 3)
    for c1 in range(-width, r + width):
        for c2 in range(c1 + 1, r + width):
            den = (c1 + c2) - m
            c3 = (m * (c1 + c2) - s1 - c1 * c2) / den  # den != 0: m is not an integer
            if c3.denominator != 1 or c3 <= c2:
                continue
            c = (Fraction(c1), Fraction(c2), c3)
            if all(is_dyadic(w) for w in weights(r, c)):
                return [c1, c2, int(c3)]
    return None


def build(max_r: int, width: int) -> dict:
    certs, missing = [], []
    for r in uncovered(max_r):
        found = first_certificate(r, width)
        if found is None:
            missing.append(r)
        else:
            w = weights(r, tuple(Fraction(x) for x in found))
            certs.append({"r": r, "directions": found, "weights": [str(x) for x in w]})
    return {
        "schema_version": 1,
        "search": {"max_r": max_r, "width": width,
                   "domain": "integers c1<c2<c3, c1 and c2 in [-width, r+width)"},
        "uncovered_arities": uncovered(max_r),
        "certificates": certs,
        "no_certificate_in_box": missing,
    }


def dump(data: dict) -> str:
    return json.dumps(data, indent=1) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--check":
        with open(argv[2], encoding="utf-8") as handle:
            committed = handle.read()
        old = json.loads(committed)["search"]
        fresh = dump(build(old["max_r"], old["width"]))
        if fresh != committed:
            print("FAIL_SEARCH_MISMATCH")
            return 1
        print("PASS_SEARCH_REPRODUCED")
        return 0
    if len(argv) not in (2, 4, 6):
        print(__doc__)
        return 2
    max_r, width = MAX_R, WIDTH
    args = argv[2:]
    for flag, value in zip(args[::2], args[1::2]):
        if flag == "--max-r":
            max_r = int(value)
        elif flag == "--width":
            width = int(value)
        else:
            print(__doc__)
            return 2
    with open(argv[1], "w", encoding="utf-8") as handle:
        handle.write(dump(build(max_r, width)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
