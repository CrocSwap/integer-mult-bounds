#!/usr/bin/env python3
"""Exact additivity census at n = 3, R = 2.

For every pair (g, h) in GL_3(F2) x GL_3(F2), with word lengths l(g), l(h)
in coordinate CNOTs, search for a formal word of length <= min(l(g)+l(h)-1, 5)
realizing diag([g], [h]). None exists, so the formal cost is at least
min(l(g)+l(h), 6), and equals l(g)+l(h) whenever that sum is at most six.

Symmetry reduction: conjugation by a coordinate permutation and the
inverse-transpose map g -> g^(-T) are automorphisms of GL_3(F2) that map the
coordinate-CNOT set onto itself, so they extend to algebra automorphisms of
F2[GL_3] preserving every paid call (projectors unchanged) and word lengths.
Exchanging the two registers conjugates every rank-one idempotent projector
by the register swap. Hence the formal cost and l(g)+l(h) are constant on
orbits of this 24-element group, and one representative per orbit suffices.
The orbit sizes are checked to cover all pairs.
"""

from __future__ import annotations

import itertools
import sys
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))

import formal  # noqa: E402


def main() -> None:
    model = formal.Model(3, 2)
    forward = model.layers(model.diagonal([]), 3)
    lengths = formal.word_lengths(3)
    if sorted(lengths.values()).count(6) != 2 or len(lengths) != 168:
        raise SystemExit("FAIL: GL_3 word lengths")
    n = 3

    def transpose(g):
        return tuple(sum(((g[r] >> c) & 1) << r for r in range(n)) for c in range(n))

    def inverse(g):
        return next(x for x in lengths if formal.mul(g, x, n) == formal.identity(n))

    autos = []
    for sigma in itertools.permutations(range(n)):
        p = formal.row_permutation(n, sigma)
        p_inv = inverse(p)
        conj = {g: formal.mul(formal.mul(p, g, n), p_inv, n) for g in lengths}
        autos.append(conj)
        autos.append({g: inverse(transpose(conj[g])) for g in lengths})
    cnots = set(formal.cnots(n))
    for auto in autos:
        if {auto[c] for c in cnots} != cnots or any(lengths[auto[g]] != lengths[g] for g in lengths):
            raise SystemExit("FAIL: symmetry does not preserve CNOTs and lengths")

    def orbit(g, h):
        return {pair for a in autos for pair in ((a[g], a[h]), (a[h], a[g]))}

    covered = 0
    checked = 0
    representatives = []
    for g, h in itertools.product(lengths, lengths):
        members = orbit(g, h)
        if (g, h) != min(members):
            continue
        covered += len(members)
        representatives.append((g, h))
    if covered != 168 * 168:
        raise SystemExit("FAIL: orbits do not cover all pairs")
    for g, h in representatives:
        total = lengths[g] + lengths[h]
        if total <= 1:
            continue
        budget = min(total - 1, 5)
        target = model.diagonal([g, h])
        best = model.shortest(target, forward, max(0, budget - 3)) if budget > 3 else forward.get(target)
        if best is not None and best <= budget:
            raise SystemExit(f"FAIL: shorter word for {g}, {h}: {best} < {total}")
        checked += len(orbit(g, h))
    if checked != 168 * 168 - 13:
        raise SystemExit("FAIL: census size")
    print(f"PASS_SWAP_COMPONENT_CENSUS pairs={checked} orbits={len(representatives)} no_shorter_word")


if __name__ == "__main__":
    main()
