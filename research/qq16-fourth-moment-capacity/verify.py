#!/usr/bin/env python3
"""Exact QQ16 fourth moment and transcript bound; Apache-2.0.

Prepared for commdata2338, with substantial OpenAI Codex assistance.
See README.md for construction and method predecessors.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("qq16_source", HERE / "source.py")
src = importlib.util.module_from_spec(spec)
spec.loader.exec_module(src)
need = src.need
MARKER = "PASS_QQ16_FOURTH_MOMENT_CAPACITY"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read_receipt(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, "duplicate receipt key")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def check_polynomial(polynomial, residual):
    need(len(polynomial) == 5 and len(residual) == 3 and residual[0] == 1,
         "polynomial shape")
    square = [sum(residual[i]*residual[j]
                  for i in range(3) for j in range(3) if i+j == k)
              for k in range(5)]
    need(polynomial == [Q(int(k == 0))-square[k] for k in range(5)],
         "polynomial square identity")
    need(polynomial[0] == 0, "zero constant polynomial")


def pair_census(routes, ports=src.U):
    """All pairs, including zero scalar coefficients, on all active axes."""
    tables, receipt = {}, {}
    for s, t in product(range(3), repeat=2):
        if s == t:
            continue
        h = {p: src.compose(routes[s][p], routes[t][p]) for p in ports}
        inv = {p: src.compose(routes[t][p], routes[s][p]) for p in ports}
        need(len(set(h.values())) == len(ports), "relative route distinctness")
        table = {}
        for p, q in product(ports, repeat=2):
            key = src.compose(h[p], inv[q])
            table.setdefault(key, []).append((p, q))
        need(table.get(src.IDENTITY) == [(p, p) for p in ports],
             "diagonal identity fibre")
        need(all(len(v) == 1 for g, v in table.items() if g != src.IDENTITY),
             "nonidentity pair collision")
        need(len(table) == len(ports)**2-len(ports)+1, "pair coverage")
        tables[s, t] = table
        payload = [[list(g), v] for g, v in sorted(table.items())]
        receipt[f"{s}{t}"] = {
            "ordered_pairs": len(ports)**2,
            "distinct_products": len(table),
            "identity_fibre": len(table[src.IDENTITY]),
            "largest_nonidentity_fibre": max(len(v) for g, v in table.items()
                                               if g != src.IDENTITY),
            "sha256": hashlib.sha256(json.dumps(payload, separators=(",", ":"))
                                      .encode()).hexdigest(),
        }
    intersections = {}
    for s in range(3):
        t, u = [i for i in range(3) if i != s]
        common = tables[s, t].keys() & tables[s, u].keys()
        need(common == {src.IDENTITY}, "cross-stage product intersection")
        intersections[str(s)] = len(common)
    return receipt, intersections


def cyclic_reduce(word):
    word = list(word)
    changed = True
    while changed and len(word) > 1:
        changed = False
        for i in range(len(word)):
            if word[i] == word[(i+1) % len(word)]:
                del word[i]
                changed = True
                break
    return tuple(word)


def moments_from_columns(R):
    c = [tuple(R[i][p] for i in range(8)) for p in src.U]
    dots = [[src.dot(a, b) for b in c] for a in c]
    square_sum = sum(x*x for row in dots for x in row)
    need(square_sum == 18432, "full Gram Frobenius mass")
    diagonal_mass = sum(dots[i][i]**2 for i in range(96))
    need(diagonal_mass == 1536, "diagonal Gram mass")
    identity_coefficient = [[sum(src.dot(v, v)*v[i]*v[j] for v in c)
                             for j in range(8)] for i in range(8)]
    need(identity_coefficient == [[192*int(i == j) for j in range(8)]
                                  for i in range(8)], "identity coefficient")
    diagonal_square = sum(x*x for row in identity_coefficient for x in row)
    off_diagonal_square = 16*(square_sum-diagonal_mass)
    alternating = Q(diagonal_square+off_diagonal_square, 48**4)
    mixed = Q(diagonal_square, 48**4)
    triple = Q(sum(src.dot(v, v)**3 for v in c), 48**3)
    pair = Q(diagonal_mass, 48**2)
    need((pair, triple, alternating, mixed) ==
         (Q(2, 3), Q(1, 18), Q(23, 216), Q(1, 18)), "trace classes")
    moments, counts = [], []
    values = {"single": Q(8), "pair": pair, "triple": triple,
              "alternating": alternating, "mixed": mixed}
    for power in range(1, 5):
        census = Counter()
        for word in product(range(3), repeat=power):
            reduced = cyclic_reduce(word)
            if len(reduced) <= 3:
                key = {1: "single", 2: "pair", 3: "triple"}[len(reduced)]
            else:
                key = "alternating" if len(set(reduced)) == 2 else "mixed"
            census[key] += 1
        need(sum(census.values()) == 3**power, "stage-word coverage")
        moments.append(sum(n*values[k] for k, n in census.items()))
        counts.append(dict(sorted(census.items())))
    need(moments == [Q(24), Q(28), Q(109, 3), Q(1823, 36)], "moments")
    return moments, {
        "gram_square_sum": square_sum,
        "identity_coefficient_diagonal": 192,
        "identity_coefficient_square_trace": diagonal_square,
        "off_identity_square_trace": off_diagonal_square,
        "alternating_four_trace": str(alternating),
        "mixed_four_trace": str(mixed),
        "cyclic_stage_word_counts": counts,
    }


def spectral_bound(moments):
    m1, m2, m3, m4 = moments
    det = m2*m4-m3*m3
    need(det > 0, "positive moment determinant")
    a, b = (m4*m1-m3*m2)/det, (m2*m2-m3*m1)/det
    # p(t)=1-(1-a*t-b*t^2)^2 is <=1 for EVERY real t, and p(0)=0.
    coefficients = [Q(0), 2*a, 2*b-a*a, -2*a*b, -b*b]
    check_polynomial(coefficients, [Q(1), -a, -b])
    bound = sum(x*y for x, y in zip(coefficients[1:], moments))
    need((a, b, bound) == (Q(81, 40), Q(-9, 10), Q(117, 5)),
         "quartic rank bound")
    need(bound-8-15 == Q(2, 5), "positive width-fifteen residual")
    return {
        "residual_polynomial": ["1", str(-a), str(-b)],
        "rank_polynomial": list(map(str, coefficients)),
        "stacked_rank_lower_per_owner": str(bound),
        "selected_defect_lower_per_owner": str(bound-8),
        "width_fourteen_residual_lower_per_owner": str(bound-22),
        "width_fifteen_residual_lower_per_owner": str(bound-23),
        "necessary_integer_record_width": 16,
    }


def certificate(repo):
    R, routes = src.packet_data(src.load_packet(repo))
    src.check_grams(R)
    src.check_swap_charts(routes)
    pairs, intersections = pair_census(routes)
    moments, traces = moments_from_columns(R)
    return {
        "status": MARKER,
        "pair_census": pairs,
        "cross_stage_intersections": intersections,
        "trace_calculation": traces,
        "moments_per_owner": list(map(str, moments)),
        "spectral_bound": spectral_bound(moments),
        "scope": "Regular-owner information dimension under the inherited fixed-pair erased-family observation contract; no physical invoice or new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=HERE.parents[1])
    parser.add_argument("--receipt", type=Path, default=HERE / "RESULT.json")
    args = parser.parse_args()
    result = certificate(args.repo)
    need(canonical(read_receipt(args.receipt)) == canonical(result), "receipt mismatch")
    print(MARKER + " moment4=1823/36 rank>=117|G|/5 defect>=77|G|/5 width>=16 no_new_kappa")


if __name__ == "__main__":
    main()
