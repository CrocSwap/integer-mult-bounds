#!/usr/bin/env python3
"""Exact checks for component cuts on transposition targets.

The uniform claim (transposition targets whose coordinate graph has
components of at most three vertices cost exactly 3t paid calls, for every
n) is the written proof in README.md. This verifier checks the two
exchangeability lemmas exactly, the averaged cut counts in the GL_3 regular
representation over all 5,040 orders, exact formal minima for mixed targets
at n = 3, and the attaining words. No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "swap-component-cut"
sys.path.insert(0, str(PACKAGE))

import formal  # noqa: E402


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def sign(sequence) -> int:
    inversions = sum(1 for a, b in itertools.combinations(sequence, 2) if a > b)
    return inversions % 2


def exchangeability_lemmas() -> None:
    # Pair cut {a before b}: rows a, b and the fresh vector w are uniformly ordered.
    orders = list(itertools.permutations("abw"))
    leave = Fraction(sum(1 for o in orders if o.index("a") < o.index("b") and o.index("w") > o.index("b")),
                     len(orders))
    need(leave == Fraction(1, 6), "pair cut: CNOT writing row a leaves with probability 1/6")
    # Triple parity cut on rows (a, b, c) with label order a < b < c; w replaces row a.
    orders = list(itertools.permutations("abcw"))
    def parity(o, labels):
        ranks = [o.index(x) for x in labels]
        return sign(ranks)
    flips = Fraction(sum(1 for o in orders
                         if parity(o, "abc") == 0 and parity(o, "wbc") == 1), len(orders))
    need(flips == Fraction(1, 6), "triple parity cut: CNOT writing row a leaves with probability 1/6")
    stays = Fraction(sum(1 for o in orders if parity(o, "abc") == 0), len(orders))
    need(stays == Fraction(1, 2), "triple parity cut has measure 1/2")
    # Any transposition of two rows of the triple flips the parity.
    for x, y in itertools.combinations(range(3), 2):
        for perm in itertools.permutations(range(3)):
            swapped = list(perm)
            swapped[x], swapped[y] = swapped[y], swapped[x]
            need(sign(perm) != sign(swapped), "row transposition flips parity")


def regular_check() -> None:
    n = 3
    group = [g for g in formal.word_lengths(n)]
    need(len(group) == 168, "GL_3(F2) order")
    index = {g: k for k, g in enumerate(group)}
    left = lambda g: [index[formal.mul(g, x, n)] for x in group]
    cnot_perms = {}
    for i in range(n):
        for j in range(n):
            if i != j:
                g = list(formal.identity(n))
                g[i] ^= 1 << j
                cnot_perms[("cnot", i, j)] = left(tuple(g))
    swaps = {("swap", a, b): left(formal.row_permutation(n, tuple(b if x == a else a if x == b else x for x in range(n))))
             for a, b in itertools.combinations(range(n), 2)}
    orders = list(itertools.permutations(range(1, 8)))
    pair_sum = {key: 0 for key in list(cnot_perms) + list(swaps)}
    parity_sum = dict(pair_sum)
    for order in orders:
        position = {v: k for k, v in enumerate(order)}
        pair_cut = [position[x[0]] < position[x[1]] for x in group]
        parity_cut = [sign([position[r] for r in x]) == 0 for x in group]
        for key, perm in list(cnot_perms.items()) + list(swaps.items()):
            pair_sum[key] += sum(1 for x in range(168) if pair_cut[x] and not pair_cut[perm[x]])
            parity_sum[key] += sum(1 for x in range(168) if parity_cut[x] and not parity_cut[perm[x]])
    unit = len(orders) * 168 // 6
    for key in cnot_perms:
        i, j = key[1], key[2]
        need(pair_sum[key] == (unit if i in (0, 1) else 0), f"pair cut CNOT({i},{j})")
        need(parity_sum[key] == unit, f"parity cut CNOT({i},{j})")
    need(pair_sum[("swap", 0, 1)] == 3 * unit, "pair cut on its own transposition")
    for key in swaps:
        need(parity_sum[key] == 3 * unit, f"parity cut on transposition {key}")
    # A transposition sharing one row with the pair is worth one unit: the component rule needs
    # disjoint rows, and this is why a 2-path needs the parity cut instead.
    need(pair_sum[("swap", 0, 2)] == unit and pair_sum[("swap", 1, 2)] == unit, "pair cut on overlapping transpositions")


def formal_minima() -> None:
    model = formal.Model(3, 2)
    forward = model.layers(model.diagonal([]), 3)
    need(len(forward) == 26551, "forward ball size n=3 R=2 depth 3")
    s01 = formal.row_permutation(3, (1, 0, 2))
    s12 = formal.row_permutation(3, (0, 2, 1))
    c3 = formal.row_permutation(3, (1, 2, 0))
    lengths = formal.word_lengths(3)
    need(lengths[s01] == 3 and lengths[s12] == 3 and lengths[c3] == 6, "group word lengths")
    need(model.shortest(model.diagonal([s01, s12]), forward, 2) is None, "s01+s12 needs more than five")
    need(model.shortest(model.diagonal([s01, s12]), forward, 3) == 6, "s01+s12 costs six")
    need(model.shortest(model.diagonal([c3]), forward, 2) is None, "a 3-cycle needs more than five")
    need(model.shortest(model.diagonal([c3]), forward, 3) == 6, "a 3-cycle costs six")


def attaining_words() -> None:
    n, registers = 4, 3
    model = formal.Model(n, registers)
    one, zero = model.one, model.zero
    targets = [(0, 1), (1, 2), (2, 3)]
    product = model.diagonal([])
    calls = 0
    for r, (a, b) in enumerate(targets):
        for i, j in ((a, b), (b, a), (a, b)):
            g = list(formal.identity(n))
            g[i] ^= 1 << j
            entries = [one] * registers
            entries[r] = frozenset([tuple(g)])
            factor = tuple(tuple(entries[x] if x == y else zero for y in range(registers)) for x in range(registers))
            product = formal.matrix_product(product, factor, registers, n)
            calls += 1
    elements = [formal.row_permutation(n, tuple(b if x == a else a if x == b else x for x in range(n)))
                for a, b in targets]
    need(product == model.diagonal(elements) and calls == 9, "attaining word for three transpositions")


def main() -> None:
    pins()
    exchangeability_lemmas()
    regular_check()
    formal_minima()
    attaining_words()
    print("PASS_SWAP_COMPONENT_CUT uniform=3t_for_components_of_at_most_three_vertices "
          "regular_check=GL3_all_orders formal_minima=s01+s12:6,c3:6 no_new_kappa")


if __name__ == "__main__":
    main()
