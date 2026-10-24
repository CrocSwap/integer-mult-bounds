#!/usr/bin/env python3
"""Exact finite checks for the row-order cut on coordinate-SWAP targets.

The uniform claim (t SWAP targets cost 3t paid calls in F2[GL_n(F2)] for
every n >= 2) is the written proof in README.md. This verifier checks its
finite ingredients exactly: the cut counts in the regular representation
for n = 2, 3, 4, the all-order average at n = 3, the spread identity for
n <= 6, the crossing-rank lemma for actual paid factors, and the 3t-call
attaining word. No new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from fractions import Fraction
from functools import reduce
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "swap-row-order-cut"
PREDECESSOR = ROOT / "research/gl2-swap-cut-corollary/README.md"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    text = PREDECESSOR.read_text(encoding="utf-8")
    need("the exact\ncost of `t` SWAP targets is **3t paid calls**" in text, "n=2 predecessor statement")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


# Matrices are tuples of row bitmasks; bit k of row i is the (i, k) entry.
def mul(a, b, n):
    return tuple(reduce(lambda acc, k: acc ^ (b[k] if a[i] >> k & 1 else 0), range(n), 0)
                 for i in range(n))


def identity(n):
    return tuple(1 << i for i in range(n))


def general_linear(n):
    group = []
    for rows in itertools.product(range(1, 1 << n), repeat=n):
        span = {0}
        for row in rows:
            if row in span:
                break
            span |= {x ^ row for x in span}
        else:
            group.append(rows)
    return group


def cnot(n, i, j):
    g = list(identity(n))
    g[i] ^= 1 << j
    return tuple(g)


def swap01(n):
    g = list(identity(n))
    g[0], g[1] = g[1], g[0]
    return tuple(g)


def lines(n):
    vectors = range(1, 1 << n)
    return sorted({tuple(sorted((a, b, a ^ b))) for a in vectors for b in vectors if a < b and a ^ b})


class Regular:
    """Left regular action of GL_n(F2) on itself."""

    def __init__(self, n):
        self.n = n
        self.group = general_linear(n)
        self.index = {g: k for k, g in enumerate(self.group)}
        self.cnots = {(i, j): cnot(n, i, j) for i in range(n) for j in range(n) if i != j}
        self.perm = {key: self.left(g) for key, g in self.cnots.items()}
        self.swap = self.left(swap01(n))

    def left(self, g):
        return [self.index[mul(g, x, self.n)] for x in self.group]

    def cut(self, order):
        position = {v: k for k, v in enumerate(order)}
        return [position[x[0]] < position[x[1]] for x in self.group]

    @staticmethod
    def out(perm, member):
        return sum(1 for x, inside in enumerate(member) if inside and not member[perm[x]])


def regular_counts(reg: Regular, order) -> tuple[int, dict, int]:
    member = reg.cut(order)
    size = sum(member)
    counts = {key: Regular.out(p, member) for key, p in reg.perm.items()}
    return size, counts, Regular.out(reg.swap, member)


def spread(order, n) -> int:
    position = {v: k for k, v in enumerate(order)}
    total = 0
    for line in lines(n):
        p = sorted(position[v] for v in line)
        total += p[2] - p[0]
    return total


def check_regular(n: int, orders, average: bool) -> None:
    reg = Regular(n)
    vectors = (1 << n) - 1
    line_count = len(lines(n))
    need(line_count * 6 == vectors * (vectors - 1), f"line count n={n}")
    completions = len(reg.group) // (vectors * (vectors - 1))
    sums = {key: 0 for key in reg.perm}
    for order in orders:
        size, counts, swap_out = regular_counts(reg, order)
        need(size == completions * line_count * 3, f"|A| n={n}")
        need(swap_out == size, f"the swap moves all of A out, n={n}")
        third = size // 3
        for (i, j), value in counts.items():
            if i >= 2:
                need(value == 0, f"spectator-row CNOT({i},{j}) never cuts, n={n}")
            elif j < 2:
                need(value == third, f"CNOT({i},{j}) cuts exactly |A|/3, n={n}")
            else:
                # line formula: spread D decides both spectator directions
                d = spread(order, n)
                if i == 0:
                    predicted = sum(3 * vectors - 4 - sorted_pos[1] - 2 * sorted_pos[2]
                                    for sorted_pos in sorted_positions(order, n))
                else:
                    predicted = sum(2 * sorted_pos[0] + sorted_pos[1] - 1
                                    for sorted_pos in sorted_positions(order, n))
                need(Fraction(value, completions) == Fraction(predicted, vectors - 3),
                     f"line formula CNOT({i},{j}) n={n}")
                need((value <= third) == (2 * d >= (vectors + 1) * line_count),
                     f"spread criterion CNOT({i},{j}) n={n}")
            sums[(i, j)] += value
    if average:
        for key, total in sums.items():
            expected = 0 if key[0] >= 2 else len(orders) * (completions * line_count)
            need(total == expected, f"all-order average CNOT{key} n={n}")


def sorted_positions(order, n):
    position = {v: k for k, v in enumerate(order)}
    return [sorted(position[v] for v in line) for line in lines(n)]


def spread_identity() -> None:
    # E[max - min] and E[mid + 2 max] over uniform 3-subsets of {0..N-1}.
    for n in range(2, 7):
        size = (1 << n) - 1
        triples = list(itertools.combinations(range(size), 3))
        gap = Fraction(sum(t[2] - t[0] for t in triples), len(triples))
        need(gap == Fraction(size + 1, 2), f"mean spread N={size}")
        upper = Fraction(sum(t[1] + 2 * t[2] for t in triples), len(triples))
        lower = Fraction(sum(2 * t[0] + t[1] for t in triples), len(triples))
        need(upper == 2 * size - 1 and lower == size - 2, f"spectator means N={size}")


def rank_f2(rows):
    rank, rows = 0, [r for r in rows if r]
    while rows:
        pivot = rows.pop()
        low = pivot & -pivot
        rows = [r ^ pivot if r & low else r for r in rows]
        rows = [r for r in rows if r]
        rank += 1
    return rank


def crossing_rank_lemma() -> None:
    """rank of the [A^c, A] block of I + (P_g - I) (x) N equals out(g, A) rank N."""
    n, registers = 3, 2
    reg = Regular(n)
    order = (1, 3, 2, 6, 7, 5, 4)
    member = reg.cut(order)
    inside = [x for x, m in enumerate(member) if m]
    outside = [x for x, m in enumerate(member) if not m]
    column = {x: k for k, x in enumerate(inside)}
    projectors = [(u, v) for u in range(1, 4) for v in range(1, 4) if bin(u & v).count("1") % 2]
    checked = 0
    for key, perm in list(reg.perm.items()) + [("swap", reg.swap)]:
        for u, v in projectors:
            rows = []
            for y in outside:
                for r in range(registers):
                    bits = 0
                    for x in inside:
                        if perm[x] == y and u >> r & 1:
                            for c in range(registers):
                                if v >> c & 1:
                                    bits |= 1 << (column[x] * registers + c)
                    rows.append(bits)
            need(rank_f2(rows) == Regular.out(perm, member), f"crossing rank {key}")
            checked += 1
    need(checked == 7 * len(projectors), "crossing-rank cases")


def subadditivity_spot_check() -> None:
    random.seed(4939)
    n = 3
    reg = Regular(n)
    member = reg.cut((1, 3, 2, 6, 7, 5, 4))
    size = len(member)
    perms = list(reg.perm.values())
    for _ in range(200):
        word = [random.choice(perms) for _ in range(random.randint(1, 6))]
        composite = list(range(size))
        for p in word:
            composite = [p[c] for c in composite]
        need(Regular.out(composite, member) <= sum(Regular.out(p, member) for p in word),
             "permutation cut subadditivity")


# Formal algebra M_R(F2[GL_n]) for the attaining word.
def formal_product(x, y, n):
    acc = set()
    for g in x:
        for h in y:
            acc ^= {mul(g, h, n)}
    return frozenset(acc)


def formal_matmul(a, b, registers, n):
    out = []
    for i in range(registers):
        row = []
        for j in range(registers):
            entry = set()
            for k in range(registers):
                if a[i][k] and b[k][j]:
                    entry ^= formal_product(a[i][k], b[k][j], n)
            row.append(frozenset(entry))
        out.append(tuple(row))
    return tuple(out)


def attaining_word(n: int, swaps: int, registers: int) -> None:
    one = frozenset([identity(n)])
    zero = frozenset()

    def diag(entries):
        return tuple(tuple(entries[i] if i == j else zero for j in range(registers))
                     for i in range(registers))

    word = []
    for r in range(swaps):
        for g in (cnot(n, 0, 1), cnot(n, 1, 0), cnot(n, 0, 1)):
            entries = [one] * registers
            entries[r] = frozenset([g])  # I + ([g] + 1) E_rr
            word.append(diag(entries))
    product = diag([one] * registers)
    for factor in word:
        product = formal_matmul(product, factor, registers, n)
    target = diag([frozenset([swap01(n)])] * swaps + [one] * (registers - swaps))
    need(product == target and len(word) == 3 * swaps, f"attaining word n={n} t={swaps}")


def main() -> None:
    pins()
    check_regular(2, list(itertools.permutations(range(1, 4))), average=True)
    check_regular(3, list(itertools.permutations(range(1, 8))), average=True)
    random.seed(1541)
    sample = [tuple(random.sample(range(1, 16), 15)) for _ in range(6)]
    gray = tuple(k ^ (k >> 1) for k in range(1, 16))
    check_regular(4, sample + [gray, tuple(range(1, 16))], average=False)
    spread_identity()
    crossing_rank_lemma()
    subadditivity_spot_check()
    for n, swaps, registers in ((2, 3, 3), (3, 3, 4), (4, 2, 3)):
        attaining_word(n, swaps, registers)
    print("PASS_SWAP_ROW_ORDER_CUT uniform_minimum=3t_by_written_proof "
          "regular_checks=n2_all_orders,n3_all_orders,n4_eight_orders no_new_kappa")


if __name__ == "__main__":
    main()
