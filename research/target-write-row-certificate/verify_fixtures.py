#!/usr/bin/env python3
"""Small independent exact checks; NOT a Lean kernel check or optimality search.

SPDX-License-Identifier: Apache-2.0
Rows are integer bitsets for coefficients of all n initial dirty registers.
This script checks the supplied fixtures, every prefix's computed mask, and
one small exhaustive algebra check. It never invokes or emulates Lean.
"""
from __future__ import annotations

from itertools import product
from functools import reduce
from operator import xor

Gate = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def combine(rows: list[int], mask: list[bool]) -> int:
    require(len(rows) == len(mask), "mask length mismatch")
    return reduce(xor, (v for v, b in zip(rows, mask) if b), 0)


def execute(n: int, word: list[Gate]) -> list[int]:
    rows = [1 << r for r in range(n)]
    for d, s in word:
        require(0 <= d < n and 0 <= s < n and d != s, "invalid gate")
        rows[d] ^= rows[s]
    return rows


def reduced_mask(mask: list[bool]) -> list[bool]:
    if not mask:
        return []
    return [not b for b in mask[1:]] if mask[0] else mask[1:]


def scan(n: int, y: int, word: list[Gate]) -> tuple[list[int], list[int], list[int], list[list[bool]]]:
    require(0 <= y < n, "invalid target")
    raw = [1 << r for r in range(n)]
    projected = raw.copy()
    donors: list[int] = []
    masks: list[list[bool]] = [[] for _ in range(n)]

    def invariant() -> None:
        for r in range(n):
            require(len(masks[r]) == len(donors), "prefix mask length")
            require(combine(donors, masks[r]) == (raw[r] ^ projected[r]), "prefix row invariant")
        require(raw[y] == ((1 << y) ^ reduce(xor, donors, 0)), "target telescope")

    invariant()
    for d, s in word:
        require(0 <= d < n and 0 <= s < n and d != s, "invalid gate")
        donor = raw[s]
        if d == y:
            donors.append(donor)
            masks = [mask + [r == y] for r, mask in enumerate(masks)]
        else:
            projected[d] ^= projected[s]
            require(len(masks[d]) == len(masks[s]), "xor mask length")
            masks[d] = [a != b for a, b in zip(masks[d], masks[s])]
        raw[d] ^= donor
        require(raw[s] == donor, "same-gate donor must be unchanged")
        invariant()

    require(raw == execute(n, word), "independent raw replay mismatch")
    require(projected == execute(n, [g for g in word if g[0] != y]), "filtered replay mismatch")
    require(len(donors) == sum(d == y for d, _ in word), "target count mismatch")
    if raw == [1 << r for r in range(n)] and donors:
        require(reduce(xor, donors, 0) == 0, "restored donor sum")
        for r in range(n):
            mask = reduced_mask(masks[r])
            require(len(mask) == len(donors) - 1, "reduced length")
            require(combine(donors[1:], mask) == ((1 << r) ^ projected[r]), "reduced certificate")
    if not donors:
        require(projected == raw, "zero-target equality")
    return raw, projected, donors, masks


def main() -> None:
    print("NON-KERNEL EXACT CHECKS; no Lean execution, no BFS, no rank/optimality claim")
    feedback: list[Gate] = [(1, 0), (0, 1)] * 3
    raw, proj, donors, masks = scan(2, 1, feedback)
    require(raw == [1, 2] and proj == [3, 2], "feedback endpoints")
    require(donors == [1, 2, 3], "feedback actual donors")
    reduced = [reduced_mask(mask) for mask in masks]
    require(reduced == [[True, False], [False, False]], "feedback reduced masks")
    require(donors[1] != raw[0], "final-state timing control")
    projected_prefix = execute(2, [g for g in feedback[:2] if g[0] != 1])
    require(donors[1] != projected_prefix[0], "projected-state timing control")
    print(f"PASS feedback: R={raw}, P={proj}, donors={donors}, reduced_masks={reduced}")
    print("PASS timing controls: second donor differs from final raw and projected-prefix donor")

    commutator: list[Gate] = [(2, 0), (1, 2), (2, 0), (1, 2), (1, 0)]
    raw, proj, donors, masks = scan(3, 2, commutator)
    require(raw == [1, 2, 4] and proj == [1, 3, 4], "commutator endpoints")
    require(donors == [1, 1], "commutator donor occurrences")
    require((proj[1] & 1) != (raw[1] & 1), "raw helper-block control")
    print(f"PASS commutator: R={raw}, P={proj}, donors={donors}, kept={donors[1:]}")
    print("PASS raw-helper-block control: projected(b,a)=1, raw(b,a)=0")

    chronology: list[Gate] = [(0, 2), (2, 1), (1, 0)]
    _, proj, _, _ = scan(3, 2, chronology)
    wrong = execute(3, [(1, 0), (0, 2)])
    require(proj == execute(3, [(0, 2), (1, 0)]), "chronological projection")
    require((proj[1] & 4) != (wrong[1] & 4), "reversed-order control")
    print(f"PASS chronology: projected={proj}, reversed_retained={wrong}")

    raw, proj, donors, _ = scan(3, 2, [(0, 2), (0, 2)])
    require(raw == proj == [1, 2, 4] and donors == [], "zero-target fixture")
    print("PASS zero-target feedback fixture")

    checks = 0
    for m in range(1, 5):
        # Every zero-sum donor list of length m over two-bit rows is obtained
        # by choosing its tail, then making its head the XOR of that tail.
        for tail in product(range(4), repeat=m - 1):
            rows = [reduce(xor, tail, 0), *tail]
            for bits in product((False, True), repeat=m):
                mask = list(bits)
                reduced = reduced_mask(mask)
                require(combine(rows, mask) == combine(rows[1:], reduced), "local elimination")
                require(len(reduced) == m - 1, "local elimination length")
                checks += 1
    print(f"PASS local elimination: {checks} donor-list/mask cases; two-bit rows, m=1..4")
    print("All listed checks passed. These do not establish that the Lean source elaborates.")


if __name__ == "__main__":
    main()
