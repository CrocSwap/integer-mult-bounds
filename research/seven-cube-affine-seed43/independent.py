#!/usr/bin/env python3
"""Separate Walsh/Fraction/RREF oracle; no imports from the census generator.

Hanson Sun with substantial OpenAI Codex assistance; Apache-2.0.
Implementation independence is not independent human review.
"""
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations, combinations_with_replacement, product
import json
from math import factorial
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def insist(condition, message):
    if not condition:
        raise ValueError(message)


def rational_rank(matrix):
    """Normalized rational row echelon form, separate from integer elimination."""
    basis = {}
    for original in matrix:
        row = [Fraction(x) for x in original]
        for pivot, old in sorted(basis.items()):
            if row[pivot]:
                scale = row[pivot]
                row = [a - scale * b for a, b in zip(row, old)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            scale = row[pivot]
            basis[pivot] = [x / scale for x in row]
    return len(basis)


POINTS = [tuple((x >> j) & 1 for j in range(7)) + (1,) for x in range(128)]
VALUES = {f: [sum(((f >> j) & 1) * v[j] for j in range(8)) % 2 for v in POINTS]
          for f in range(1, 256)}
SUPPORTS = {f: [x for x, b in enumerate(values) if b] for f, values in VALUES.items()}


def classify(f, g):
    cells = Counter((((f >> j) & 1), ((g >> j) & 1)) for j in range(7))
    equal_nonzero = f % 128 == g % 128 != 0
    phase = int((f >= 128) != (g >= 128)) if equal_nonzero else 0
    return cells[1, 0], cells[0, 1], cells[1, 1], phase


def ranks():
    features = [mask for mask in range(128) if mask.bit_count() <= 3]
    insist(len(features) == 64, "cubic feature count")
    kernel = [sum(-1 if (m & x).bit_count() % 2 else 1 for m in features) for x in range(128)]
    for x in range(128):
        j = 7 - x.bit_count()
        insist(3 * kernel[x] == 4 * (j - 1) * (j - 3) * (j - 5), "Walsh/cubic mismatch")
    counts = Counter(classify(f, g) for f in range(1, 256) for g in range(1, 256))
    rows = []
    for a in range(8):
        for b in range(8 - a):
            for c in range(8 - a - b):
                d = 7 - a - b - c
                equal = a == b == 0 and c > 0
                for flip in range(2 if equal else 1):
                    f = sum(1 << j for j in list(range(a)) + list(range(a + b, a + b + c)))
                    g = sum(1 << j for j in range(a, a + b + c))
                    if f == 0:
                        f = 128
                    if g == 0:
                        g = 128
                    elif flip:
                        g += 128
                    ways = factorial(7) // (factorial(a) * factorial(b) * factorial(c) * factorial(d))
                    constants = 1 if a + b + c == 0 else (2 if equal or a + c == 0 or b + c == 0 else 4)
                    key = [a, b, c, flip]
                    insist(counts[tuple(key)] == ways * constants, "orbit multiplicity")
                    A, B = SUPPORTS[f], SUPPORTS[g]
                    rows.append({"key": key, "forms": [f, g], "multiplicity": ways * constants,
                                 "rank": rational_rank([[kernel[x ^ y] for y in B] for x in A]),
                                 "diagonal": sum(VALUES[f][x] * VALUES[g][x] for x in range(128))})
    insist(len(rows) == len(counts) == 127 and sum(counts.values()) == 65025, "rank coverage")
    return sorted(rows, key=lambda r: r["key"])


def solve_sources(readers):
    """RREF of eight equations whose right sides are source-code vectors."""
    n = len(readers)
    rows = [[sum(((f >> bit) & 1) << i for i, f in enumerate(readers)), 128 if bit < 7 else 255]
            for bit in range(8)]
    pivots, pos = [], 0
    for col in range(n):
        k = next((k for k in range(pos, 8) if (rows[k][0] >> col) & 1), None)
        if k is None:
            continue
        rows[pos], rows[k] = rows[k], rows[pos]
        for k in range(8):
            if k != pos and rows[k][0] >> col & 1:
                rows[k][0] ^= rows[pos][0]
                rows[k][1] ^= rows[pos][1]
        pivots.append(col)
        pos += 1
    if any(lhs == 0 and rhs for lhs, rhs in rows):
        return None
    free = [i for i in range(n) if i not in pivots]
    insist(len(free) <= 1, "unexpected RREF nullity")
    solutions = []
    for h in range(256 if free else 1):
        gs = [0] * n
        if free:
            gs[free[0]] = h
        for i, col in enumerate(pivots):
            gs[col] = rows[i][1] ^ (h if free and rows[i][0] >> free[0] & 1 else 0)
        solutions.append(tuple(gs))
    return solutions


def valid_coefficients(fs, gs):
    for bit in range(8):
        row = 0
        for f, g in zip(fs, gs):
            if f >> bit & 1:
                row ^= g
        if row != (128 if bit < 7 else 255):
            return False
    return True


def census(cost):
    u = (0, 127, 128, 255)
    # Unique quotient representatives with coefficient bits6 and7 set to zero.
    spaces = [sorted(u + tuple(h ^ q for q in u)) for h in range(1, 64)]
    answers = {}
    for n in (2, 3, 4):
        if n == 2:
            readers = list(combinations(u[1:], 2))
        elif n == 3:
            readers = list(combinations_with_replacement(u[1:], 3))
        else:
            readers = [fs for W in spaces for fs in combinations(W[1:], 4)]
        insist(len(readers) == len(set(readers)), "duplicate reader subset")
        sets = assignments = nonzero = 0
        hist = Counter()
        best = None
        for fs in readers:
            solutions = solve_sources(fs)
            if solutions is None:
                continue
            sets += 1
            for gs in solutions:
                assignments += 1
                insist(valid_coefficients(fs, gs), "RREF produced a false identity")
                if any(g == 0 for g in gs):
                    continue
                nonzero += 1
                bill = sum(cost(f, g) for f, g in zip(fs, gs))
                hist[bill] += 1
                item = (bill, fs, gs)
                if best is None or item < best:
                    best = item
        answers[str(n)] = {"reader_sets": sets, "source_assignments": assignments,
                           "nonzero_assignments": nonzero, "cost_histogram": sorted([k, v] for k, v in hist.items()),
                           "minimum": best[0], "witness": [list(x) for x in zip(best[1], best[2])]}
    return answers


def literal(word, binary=True):
    for x, y in product(range(128), repeat=2):
        z = sum(VALUES[f][x] * VALUES[g][y] for f, g in word)
        if (z % 2 if binary else z) != (1 + x.bit_count() + y.bit_count()) % 2:
            return False
    return True


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    live = [s for s in sources["files"] if s["usage"] == "input"]
    insist(len(live) == 3, "source count")
    for s in live:
        insist(hashlib.sha256((ROOT / s["path"]).read_bytes()).hexdigest() == s["sha256"], "source hash: " + s["path"])
    rows = ranks()
    by_key = {tuple(r["key"]): r["rank"] for r in rows}
    cost = lambda f, g: by_key[classify(f, g)]
    # Precompute all ordered costs without consulting the committed rank table.
    costs = {(f, g): cost(f, g) for f in range(1, 256) for g in range(1, 256)}
    factors = census(lambda f, g: costs[f, g])
    hist, diag = Counter(), {}
    for r in rows:
        hist[r["rank"]] += r["multiplicity"]
        diag[r["rank"]] = max(diag.get(r["rank"], 0), r["diagonal"])
    # Enumerate unordered rank-type multisets, rather than dynamic programming.
    bounds = {}
    for limit in (127, 128):
        bounds[limit] = {}
        for n in range(1, 7):
            bounds[limit][str(n)] = max((sum(diag[c] for c in cs)
                                       for cs in combinations_with_replacement(sorted(diag), n)
                                       if sum(cs) <= limit), default=-1)
    maxima = bounds[127]
    words = {
        "two_terms": [(127, 127), (255, 255)],
        "four_terms": [(2, 125), (125, 130), (130, 253), (253, 2)],
        "peak30": [(6, 129), (134, 1), (1, 134), (129, 6),
                   (24, 96), (96, 152), (152, 224), (224, 24)],
    }
    witnesses = {}
    for name, word in words.items():
        insist(literal(word), "literal decoder failed")
        rs = [costs[f, g] for f, g in word]
        witnesses[name] = {"terms": [list(t) for t in word], "ranks": rs,
                           "total": sum(rs), "peak": max(rs), "entries_checked": 16384}
    bad = words["four_terms"][:]
    bad[0] = (2, 253)
    tests = [not literal(words["four_terms"][:-1]), not literal(bad), not literal([(128, 128)]),
             not literal(words["four_terms"], binary=False), diag[20] == 0,
             maxima["4"] >= 128, 3 * 42 < 128 < factors["3"]["minimum"],
             16 * 128 - 17 * 127 > 16 * 128 - 17 * 128,
             next(r for r in rows if r["key"] == [0, 0, 0, 0])["multiplicity"] == 1,
             costs[1, 129] == 20 != costs[1, 1]]
    insist(all(tests), "negative/logic control failed")
    insist([factors[str(n)]["minimum"] for n in (2, 3, 4)] == [128, 138, 128], "short factor bound")
    insist(maxima["5"] == 64 and maxima["6"] == 0 and min(hist) == 20, "long factor bound")
    insist(bounds[128]["5"] == 64 and bounds[128]["6"] == 0, "equality-length bound")
    insist(witnesses["four_terms"]["total"] == 128 and witnesses["four_terms"]["peak"] == 32,
           "sharp sum witness")
    insist(witnesses["peak30"]["peak"] == 30 and min(k for k, d in diag.items() if d) == 30,
           "sharp peak witness")
    expected = {"schema_version": 1, "assignment_seed": 43, "dimension": 7, "ports": 128,
                "affine_forms": 255, "ordered_pairs": 65025, "rank_orbits": rows,
                "rank_histogram": sorted([k, v] for k, v in hist.items()),
                "maximum_diagonal_by_rank": sorted([k, v] for k, v in diag.items()),
                "factor_census": factors, "max_diagonal_at_cost127": maxima,
                "max_diagonal_at_cost128": bounds[128],
                "witnesses": witnesses, "total_floor": 128, "peak_floor": 30,
                "minimum_peak_at_total_floor": 32, "optimistic_deficit_upper_bound": -128,
                "controls": ["omitted_fourth_term", "flipped_source_constant", "empty_star_only",
                             "rational_sum_is_not_binary_sum", "rank20_cannot_cover_diagonal",
                             "four_term_diagonal_relaxation_is_insufficient", "three_term_naive_minimum_is_insufficient",
                             "copy127_would_change_budget", "constant_form_orbit_not_duplicated",
                             "complementary_coordinate_rank_is20"]}
    insist(json.loads((HERE / "CERTIFICATE.json").read_text()) == expected,
           "certificate differs from independent Walsh/Fraction/RREF reconstruction")
    print("PASS_SEVEN_CUBE_INDEPENDENT pairs=65025 orbits=127 assignments=566275 "
          "literal_entries=49152 controls=10 no_new_kappa")


if __name__ == "__main__":
    main()
