#!/usr/bin/env python3
"""Exact census of one global ternary gauge family on one E8 P112 puncture."""
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / "research/nine-term-decoder-normal-form-seed42"
PINNED = {
    "e8lab.py": "772349edc9dff45fa3cac89fdbbe8bf1bab734e9776a245fcac8e8bd60d94634",
    "verify.py": "248763cf5ff85f073766aa8a85187a1d314fcf3a716b2586ca8fc1197d4c6c4e",
}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


for name, expected in PINNED.items():
    actual = hashlib.sha256((PREDECESSOR / name).read_bytes()).hexdigest()
    need(actual == expected, f"pinned predecessor drift: {name}")
sys.path.insert(0, str(PREDECESSOR))
import e8lab as E  # noqa: E402
import verify as V  # noqa: E402


def make_rows(bases, z, roots, w):
    rows = {}
    for i in roots:
        t = sum(a * b for a, b in zip(E.LINES[i], w))
        rows[i] = [bases[i][k] + t * z[k] for k in range(9)]
    return rows


def support_data(bases_scaled, z_scaled, roots, w, Y):
    X = [0] * 9
    for i in roots:
        t = sum(a * b for a, b in zip(E.LINES[i], w))
        live_terms = 0
        for k in range(9):
            if bases_scaled[i][k] + t * z_scaled[k] != 0:
                live_terms |= 1 << k
        while live_terms:
            bit = live_terms & -live_terms
            X[bit.bit_length() - 1] |= 1 << i
            live_terms ^= bit
    ranks = tuple(E.pairing_rank(X[k], Y[k]) for k in range(9))
    return ranks, tuple(E.popcount(x) for x in X), X


def run():
    puncture = V.coordinate_frame()
    need(puncture == [0, 13, 90, 99, 108, 113, 118, 119], "coordinate puncture changed")
    extra = next(i for i in range(E.N) if i not in puncture and
                 sum(E.G[i][f] != 0 for f in puncture) == 4)
    need(extra == 1, "first four-contact extra root changed")
    frame = V.Frame("coordinate frame + root", [E.LINES[f] for f in puncture] + [E.LINES[extra]])
    need(frame.z == [Fraction(-1), Fraction(-1), Fraction(-1), Fraction(-1),
                     Fraction(0), Fraction(0), Fraction(0), Fraction(0), Fraction(2)],
         "coefficient dependency changed")
    live = E.FULL ^ sum(1 << i for i in puncture)
    roots = list(E.bits(live))
    need(len(roots) == 112, "not the pinned P112 live set")
    bases = {i: frame.base(i) for i in roots}
    denominator = math.lcm(*(x.denominator for row in bases.values() for x in row),
                           *(x.denominator for x in frame.z))
    bases_scaled = {i: [int(x * denominator) for x in bases[i]] for i in roots}
    z_scaled = [int(x * denominator) for x in frame.z]
    Y = [E.support(b, live) for b in frame.F]
    need([E.popcount(y) for y in Y] == [56] * 8 + [53], "normal supports changed")

    all_hist = Counter()
    active_hist = Counter()
    best_active = None
    low = []
    for w in itertools.product((-1, 0, 1), repeat=8):
        ranks, sizes, X = support_data(bases_scaled, z_scaled, roots, w, Y)
        cost = sum(ranks)
        active = all(sizes)
        all_hist[cost] += 1
        if active:
            active_hist[cost] += 1
            candidate = (cost, tuple(w), ranks, sizes)
            if best_active is None or candidate < best_active:
                best_active = candidate
        if cost <= 72:
            low.append((cost, tuple(w), ranks, sizes))

    need(sum(all_hist.values()) == 6561, "ternary box not exhausted")
    need(dict(sorted(all_hist.items())) == {64: 2, 72: 3, 73: 6556}, "unexpected full cost census")
    need(dict(sorted(active_hist.items())) == {72: 3, 73: 6556}, "unexpected active cost census")
    need(best_active == (72, (-1, -1, 0, 0, 0, 0, 0, 0), (8,) * 9,
                         (56, 76, 76, 76, 56, 56, 56, 56, 56)), "best active result changed")
    need(len(low) == 5, "low-cost representatives changed")

    exact_examples = []
    for cost, w, ranks, sizes in low:
        rows = make_rows(bases, frame.z, roots, w)
        exact, count = V.exact_on_pairs(rows, frame.F, live)
        need(exact and count == 112 ** 2, f"decoder identity failed for {w}")
        if cost == 72:
            need(all(sizes) and ranks == (8,) * 9, "active control is malformed")
        else:
            need(not all(sizes), "cost-64 control unexpectedly has nine active terms")
        exact_examples.append({
            "cost": cost,
            "w": list(w),
            "term_ranks": list(ranks),
            "term_support_sizes": list(sizes),
            "exact_live_pairs": count,
        })

    # A deliberately false coefficient row must be detected by the exact pair check.
    bad = make_rows(bases, frame.z, roots, best_active[1])
    bad[roots[0]][0] += 1
    need(V.exact_on_pairs(bad, frame.F, live)[0] is False, "one-coefficient mutation escaped control")

    result = {
        "schema_version": 1,
        "seed": "655425ccd826280b13917975e2854d16",
        "base_commit": "0b1cccf86e2f5132ed286a26ef0a681a495740ea",
        "selected_record_sha256": "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
        "puncture_indices": puncture,
        "extra_root_index": extra,
        "normal_dependency": [int(x) for x in frame.z],
        "live_roots": len(roots),
        "global_shift_domain": [-1, 0, 1],
        "assignments": sum(all_hist.values()),
        "all_cost_histogram": {str(k): v for k, v in sorted(all_hist.items())},
        "all_active_cost_histogram": {str(k): v for k, v in sorted(active_hist.items())},
        "best_all_active": {
            "cost": best_active[0],
            "w": list(best_active[1]),
            "term_ranks": list(best_active[2]),
            "term_support_sizes": list(best_active[3]),
            "exact_pairs": 112 ** 2,
        },
        "low_cost_exact_controls": exact_examples,
        "negative_control": "adding 1 to coefficient row 0, term 0 fails at a live pair",
        "scope_limit": "This is only the fixed frame, puncture, global coefficient shift, and ternary box; it does not bound independent per-root gauges or other shifts.",
    }
    (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PASS_COORD_ROOT_P112_GLOBAL_GAUGE", json.dumps({
        "assignments": result["assignments"],
        "all_cost_histogram": result["all_cost_histogram"],
        "all_active_cost_histogram": result["all_active_cost_histogram"],
        "best_active": result["best_all_active"],
        "exact_controls": len(exact_examples),
        "mutation_rejected": True,
    }, sort_keys=True))


if __name__ == "__main__":
    run()
