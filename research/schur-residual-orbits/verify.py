#!/usr/bin/env python3
"""Exact residual-pair census over F2; no predecessor executable imported.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
Matrices are tuples of integer rows; bit j is column j (least significant first).
"""
import argparse
from collections import Counter
from fractions import Fraction
from itertools import permutations, product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return tuple(1 << i for i in range(n))


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            bit = row.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = row
                break
            row ^= pivots[bit]
    return len(pivots)


def multiply(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length() - 1]
            row ^= bit
        out.append(value)
    return tuple(out)


def inverse(a):
    n = len(a)
    work = [row | (1 << (n + i)) for i, row in enumerate(a)]
    for col in range(n):
        pivot = next((i for i in range(col, n) if work[i] & (1 << col)), None)
        need(pivot is not None, "singular matrix")
        work[col], work[pivot] = work[pivot], work[col]
        for i in range(n):
            if i != col and work[i] & (1 << col):
                work[i] ^= work[col]
    return tuple(row >> n for row in work)


def from_columns(columns):
    return tuple(sum(((v >> i) & 1) << j for j, v in enumerate(columns))
                 for i in range(len(columns)))


def conjugate(a, k, ki):
    return multiply(multiply(ki, a), k)


def schur(a):
    need(a[0] & 1, "zero pivot")
    return tuple((row >> 1) ^ ((a[0] >> 1) if row & 1 else 0)
                 for row in a[1:])


def commutator(a, b):
    return tuple(x ^ y for x, y in zip(multiply(a, b), multiply(b, a)))


def gl(n):
    """All ordered independent row tuples, each exactly once."""
    def extend(rows, span):
        if len(rows) == n:
            yield rows
            return
        for row in range(1, 1 << n):
            if row not in span:
                yield from extend(rows + (row,), span | {x ^ row for x in span})
    return list(extend((), {0}))


def completion(a, b, n):
    """Header with first column a and inverse first row b, given b*a=1."""
    need((a & b).bit_count() % 2 == 1, "not a split pair")
    basis, span = [], {0}
    for v in range(1, 1 << n):
        if (v & b).bit_count() % 2 == 0 and v not in span:
            basis.append(v)
            span |= {x ^ v for x in span}
    need(len(basis) == n - 1, "kernel dimension")
    m = from_columns([a] + basis)
    need(inverse(m)[0] == b, "completion projection")
    return m


def split_pairs(p, q):
    n = len(p)
    accepted, total = [], 0
    for a, b in product(range(1, 1 << n), repeat=2):
        if (a & b).bit_count() % 2 == 0:
            continue
        total += 1
        m = completion(a, b, n)
        mi = inverse(m)
        pm, qm = conjugate(p, m, mi), conjugate(q, m, mi)
        if pm[0] & qm[0] & 1:
            accepted.append((a, b, schur(pm), schur(qm)))
    return total, accepted


def guard_depth(pair):
    """Number of simultaneous successful scalar pivots (at most rank two)."""
    p, q = pair
    depth = 0
    while p and p[0] & q[0] & 1:
        p, q = schur(p), schur(q)
        depth += 1
    return depth


def classify(seeds, group):
    inverses = [inverse(k) for k in group]
    for k, ki in zip(group, inverses):
        need(multiply(k, ki) == multiply(ki, k) == identity(4), "group inverse")
    orbit_lookup, states = {}, []
    for a, b, s, t in seeds:
        pair = (s, t)
        if pair in orbit_lookup:
            state = states[orbit_lookup[pair]]
        else:
            images = Counter((conjugate(s, k, ki), conjugate(t, k, ki))
                             for k, ki in zip(group, inverses))
            representative = min(images)
            stabilizer = images[pair]
            need(set(images.values()) == {stabilizer}, "uniform orbit fibres")
            need(len(images) * stabilizer == len(group), "orbit-stabilizer")
            need(not (images.keys() & orbit_lookup.keys()), "disjoint orbits")
            depths = Counter(guard_depth(image) for image in images)
            need(set(depths) <= {0, 1, 2}, "rank-two guard depth")
            state = {
                "representative": representative,
                "commutator_rank": rank(commutator(s, t)),
                "product_rank": rank(multiply(s, t)),
                "reverse_product_rank": rank(multiply(t, s)),
                "sum_rank": rank(tuple(x ^ y for x, y in zip(s, t))),
                "common_kernel_dimension": 4 - rank(s + t),
                "orbit_size": len(images),
                "stabilizer": stabilizer,
                "depth_counts_in_orbit": dict(sorted(depths.items())),
                "split_pairs": [],
            }
            index = len(states)
            for image in images:
                orbit_lookup[image] = index
            states.append(state)
        state["split_pairs"].append([a, b])
    states.sort(key=lambda s: s["representative"])
    for state in states:
        count = len(state["split_pairs"])
        state["headers"] = count * len(group)
        state["headers_per_orbit_element"] = count * state["stabilizer"]
        state["full_guard_headers"] = (state["headers_per_orbit_element"]
                                       * state["depth_counts_in_orbit"].get(2, 0))
    return states


def leading_det(a, size):
    """Leibniz determinant over F2, independent of elimination/Schur code."""
    parity = 0
    for order in permutations(range(size)):
        parity ^= all((a[i] >> j) & 1 for i, j in enumerate(order))
    return int(parity)


def direct_header_check(states, group, p, q):
    checked = 0
    for state in states:
        a, b = state["split_pairs"][0]
        m0 = completion(a, b, 5)
        depths = Counter()
        for k in group:
            block = (1,) + tuple(row << 1 for row in k)
            m = multiply(m0, block)
            mi = inverse(m)
            pm, qm = conjugate(p, m, mi), conjugate(q, m, mi)
            need(leading_det(pm, 1) == leading_det(qm, 1) == 1, "first guard")
            depth = 0
            for size in (2, 3):
                if leading_det(pm, size) != 1 or leading_det(qm, size) != 1:
                    break
                depth += 1
            if depth == 2 and "full_guard_witness_header" not in state:
                state["full_guard_witness_header"] = m
            if depth == 0 and "first_guard_only_witness_header" not in state:
                state["first_guard_only_witness_header"] = m
            depths[depth] += 1
            checked += 1
        predicted = {d: n * state["stabilizer"]
                     for d, n in state["depth_counts_in_orbit"].items()}
        need(dict(depths) == predicted, "literal complete-header guard counts")
    return checked


def rejection_controls(states):
    def rejected(fn, message):
        try:
            fn()
        except ValueError:
            return
        raise ValueError("accepted control: " + message)

    rejected(lambda: inverse((1, 1)), "singular header")
    rejected(lambda: completion(1, 2, 2), "unsplit inclusion/projection")
    rejected(lambda: schur((0, 2)), "zero pivot")
    sharp = next(s for s in states if s["commutator_rank"] == 2)
    rejected(lambda: need(sharp["headers"] == len(sharp["split_pairs"]),
                          "omitted completion multiplier"), "counting splits as headers")
    rejected(lambda: need(sharp["full_guard_headers"] == sharp["headers"],
                          "one guard does not imply full guards"), "one-block shortcut")
    # Equal commutator ranks do not determine the conditional continuation law.
    commuting = [s for s in states if s["commutator_rank"] == 0]
    rates = {Fraction(s["full_guard_headers"], s["headers"]) for s in commuting}
    rejected(lambda: need(len(rates) == 1, "different continuation rates"),
             "commutator-rank-only state")
    # Not even all the displayed simple rank invariants distinguish these two.
    x, y = states[1], states[4]
    keys = ("commutator_rank", "product_rank", "reverse_product_rank", "sum_rank")
    need(all(x[k] == y[k] for k in keys), "equal-rank control premise")
    rejected(lambda: need(x["common_kernel_dimension"] == y["common_kernel_dimension"],
                          "different common kernels"), "same simple ranks imply same orbit")
    # Cross-check rank and direct determinant by independent 4x4 raw enumeration.
    raw_gl = {a for a in product(range(16), repeat=4) if leading_det(a, 4)}
    need(raw_gl == set(gl(4)), "raw determinant census equals independent-row GL4")
    return 7


def run():
    # Sectors (00,10,01,11,11), fixed before the header is selected.
    p, q = (0, 2, 0, 8, 16), (0, 0, 4, 8, 16)
    need(multiply(p, p) == p and multiply(q, q) == q, "projectors")
    need(multiply(p, q) == multiply(q, p), "commuting input")
    total, seeds = split_pairs(p, q)
    need(total == 496 and len(seeds) == 172, "split census")
    group = gl(4)
    need(len(group) == len(set(group)) == 20160, "complete GL4")
    for _, _, s, t in seeds:
        need(multiply(s, s) == s and multiply(t, t) == t, "residual projectors")
        need(rank(s) == rank(t) == 2, "residual ranks")
    states = classify(seeds, group)
    need(len(states) == 7, "seven residual orbits")
    direct_cases = direct_header_check(states, group, p, q)
    controls = rejection_controls(states)
    header_total = sum(s["headers"] for s in states)
    full_total = sum(s["full_guard_headers"] for s in states)
    sharp = [s for s in states if s["commutator_rank"] == 2]
    need(header_total == 3467520 and full_total == 93564, "complete-header totals")
    need(len(sharp) == 1 and sharp[0]["headers"] == 60480, "sharp predecessor count")
    need(sharp[0]["full_guard_headers"] == 3240, "sharp full-guard count")
    return {"field": 2, "sector_dimensions": [1, 1, 1, 2],
            "matrix_encoding": "integer rows, bit j is column j; ordered pair",
            "input_projectors": [p, q], "total_splits": total,
            "admitted_splits": len(seeds), "group_order": len(group),
            "all_headers": total * len(group), "first_guard_headers": header_total,
            "full_guard_headers": full_total,
            "full_guard_fraction": str(Fraction(full_total, total * len(group))),
            "direct_complete_header_checks": direct_cases,
            "raw_matrix_determinant_checks": 65536, "controls": controls,
            "states": states}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate RESULT.json")
    args = parser.parse_args()
    result = run()
    payload = json.dumps(result, indent=2) + "\n"
    path = Path(__file__).with_name("RESULT.json")
    if args.write:
        path.write_text(payload, encoding="utf-8", newline="\n")
    else:
        need(json.loads(path.read_text(encoding="utf-8")) == json.loads(payload),
             "committed result differs from the exact census")
    print("PASS_SCHUR_RESIDUAL_ORBITS")
    print(json.dumps({key: value for key, value in result.items() if key != "states"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
