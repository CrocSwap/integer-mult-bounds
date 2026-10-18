#!/usr/bin/env python3
"""Exact affine seven-cube census. Hanson Sun; substantial OpenAI Codex assistance.

Apache-2.0. Standard library only. Does not import predecessor or oracle code.
The quantified reduction from arbitrary finite words is in README.md.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
N, V, P, ONE = 7, 128, 127, 128
U = (0, P, ONE, P ^ ONE)


def require(ok, message):
    if not ok:
        raise ValueError(message)


def value(f, x):
    return ((f % V & x).bit_count() ^ (f // V)) & 1


def gram(x, y):
    j = N - (x ^ y).bit_count()
    numerator = 4 * (j - 1) * (j - 3) * (j - 5)
    require(numerator % 3 == 0, "nonintegral cubic Gram")
    return numerator // 3


def rank_integer(matrix):
    """Gaussian elimination using gcd-normalized integer row operations."""
    a = [list(row) for row in matrix]
    nr, nc, r = len(a), len(a[0]), 0
    for j in range(nc):
        k = next((k for k in range(r, nr) if a[k][j]), None)
        if k is None:
            continue
        a[r], a[k] = a[k], a[r]
        for k in range(r + 1, nr):
            if a[k][j]:
                d = math.gcd(a[r][j], a[k][j])
                u, v = a[r][j] // d, a[k][j] // d
                row = [u * x - v * y for x, y in zip(a[k][j:], a[r][j:])]
                d = math.gcd(*row)
                a[k][j:] = [x // d for x in row] if d else row
        r += 1
        if r == nr:
            break
    return r


def orbit(f, g):
    a, b = f % V, g % V
    return ((a & ~b).bit_count(), (b & ~a).bit_count(),
            (a & b).bit_count(), ((f // V) ^ (g // V)) if a == b and a else 0)


def representative(key):
    aonly, bonly, both, flip = key
    a = (1 << aonly) - 1
    b = ((1 << bonly) - 1) << aonly
    shared = ((1 << both) - 1) << (aonly + bonly)
    a, b = a | shared, b | shared
    return a | (V if not a else 0), b | (V if not b else flip * V)


def dyad(f, g):
    return sum((f if g >> j & 1 else 0) << (8 * j) for j in range(8))


TARGET = dyad(P, ONE) ^ dyad(ONE, P ^ ONE)


def symbolic_word(word):
    z = 0
    for f, g in word:
        z ^= dyad(f, g)
    return z


def literal_word(word):
    return all(sum(value(f, x) * value(g, y) for f, g in word) % 2
               == (1 + x.bit_count() + y.bit_count()) % 2
               for x in range(V) for y in range(V))


def rank_census():
    counts = Counter(orbit(f, g) for f in range(1, 256) for g in range(1, 256))
    supports = {f: [x for x in range(V) if value(f, x)] for f in range(1, 256)}
    G = [[gram(x, y) for y in range(V)] for x in range(V)]
    rows = []
    for key, count in sorted(counts.items()):
        f, g = representative(key)
        A, B = supports[f], supports[g]
        rows.append({"key": list(key), "forms": [f, g], "multiplicity": count,
                     "rank": rank_integer([[G[x][y] for y in B] for x in A]),
                     "diagonal": len(set(A) & set(B))})
    require(len(rows) == 127 and sum(counts.values()) == 65025, "incomplete rank domain")
    return rows


def histogram(counter):
    return [[k, counter[k]] for k in sorted(counter)]


def factor_census(cost):
    spaces = sorted({tuple(sorted(set(U) | {h ^ u for u in U}))
                     for h in range(256) if h not in U})
    require(len(spaces) == 63, "wrong quotient-space count")
    result = {}
    for n in (2, 3, 4):
        if n == 2:
            readers = list(itertools.combinations(U[1:], 2))
        elif n == 3:
            readers = list(itertools.combinations_with_replacement(U[1:], 3))
        else:
            readers = sorted({fs for W in spaces for fs in itertools.combinations(W[1:], 4)})
        sets = candidates = valid = 0
        bills = Counter()
        best = None
        for fs in readers:
            syndromes = [0] * (1 << n)
            for mask in range(1, 1 << n):
                bit = mask & -mask
                syndromes[mask] = syndromes[mask ^ bit] ^ fs[bit.bit_length() - 1]
            if ONE not in syndromes or P ^ ONE not in syndromes:
                continue
            sets += 1
            left, right = syndromes.index(ONE), syndromes.index(P ^ ONE)
            null = [i for i, x in enumerate(syndromes) if x == 0]
            require(len(null) == (1 if n == 2 else 2), "unexpected nullity")
            base = [((P if left >> i & 1 else 0) ^ (ONE if right >> i & 1 else 0))
                    for i in range(n)]
            for h in range(1 if n == 2 else 256):
                candidates += 1
                gs = tuple(b ^ (h if null[-1] >> i & 1 else 0) for i, b in enumerate(base))
                if 0 in gs:
                    continue
                valid += 1
                bill = sum(cost(f, g) for f, g in zip(fs, gs))
                bills[bill] += 1
                candidate = (bill, fs, gs)
                if best is None or candidate < best:
                    best = candidate
        result[str(n)] = {"reader_sets": sets, "source_assignments": candidates,
                          "nonzero_assignments": valid, "cost_histogram": histogram(bills),
                          "minimum": best[0], "witness": [list(x) for x in zip(best[1], best[2])]}
    require([result[str(n)]["source_assignments"] for n in (2, 3, 4)]
            == [3, 1792, 564480], "incomplete factor domain")
    return result


def diagonal_relaxation(rows, limit=127):
    types = {(r["rank"], r["diagonal"]) for r in rows}
    dp = {0: 0}
    maxima = {}
    for n in range(1, 7):
        nxt = {}
        for old, covered in dp.items():
            for rank, diagonal in types:
                bill = old + rank
                if bill <= limit:
                    nxt[bill] = max(nxt.get(bill, -1), covered + diagonal)
        dp = nxt
        maxima[str(n)] = max(dp.values(), default=-1)
    return maxima


def check_sources():
    source = json.loads((HERE / "SOURCES.json").read_text())
    inputs = [f for f in source["files"] if f["usage"] == "input"]
    require(len(inputs) == 3, "source inventory changed")
    for f in inputs:
        require(hashlib.sha256((ROOT / f["path"]).read_bytes()).hexdigest() == f["sha256"],
                "source mismatch: " + f["path"])


def compute():
    rows = rank_census()
    table = {tuple(r["key"]): r["rank"] for r in rows}
    cost = lambda f, g: table[orbit(f, g)]
    counts, diagonal = Counter(), {}
    for row in rows:
        counts[row["rank"]] += row["multiplicity"]
        diagonal[row["rank"]] = max(diagonal.get(row["rank"], 0), row["diagonal"])
    factors = factor_census(cost)
    require([factors[str(n)]["minimum"] for n in (2, 3, 4)] == [128, 138, 128],
            "unexpected factor optimum")
    relax = diagonal_relaxation(rows)
    at_floor = diagonal_relaxation(rows, 128)
    require(relax["5"] == 64 and relax["6"] == 0, "long-word exclusion failed")
    require(at_floor["5"] == 64 and at_floor["6"] == 0, "equality-length exclusion failed")
    require(min(counts) == 20 and 7 * min(counts) > 128, "term-count cutoff failed")
    # Assignment seed43 chooses coordinate 43 mod7 =1 for the four-term witness.
    h, q = 1 << (43 % N), P ^ (1 << (43 % N))
    words = {
        "two_terms": [(P, P), (P ^ ONE, P ^ ONE)],
        "four_terms": [(h, q), (q, h ^ ONE), (h ^ ONE, q ^ ONE), (q ^ ONE, h)],
        "peak30": [(6, 129), (134, 1), (1, 134), (129, 6),
                   (24, 96), (96, 152), (152, 224), (224, 24)],
    }
    witnesses = {}
    for name, word in words.items():
        require(symbolic_word(word) == TARGET and literal_word(word), "bad decoder " + name)
        ranks = [cost(f, g) for f, g in word]
        witnesses[name] = {"terms": [list(t) for t in word], "ranks": ranks,
                           "total": sum(ranks), "peak": max(ranks), "entries_checked": V * V}
    controls = []
    def control(name, rejects):
        require(rejects, "negative control accepted: " + name)
        controls.append(name)
    control("omitted_fourth_term", not literal_word(words["four_terms"][:-1]))
    bad = list(words["four_terms"])
    bad[0] = (bad[0][0], bad[0][1] ^ ONE)
    control("flipped_source_constant", not literal_word(bad))
    control("empty_star_only", not literal_word([(ONE, ONE)]))
    control("rational_sum_is_not_binary_sum", any(
        sum(value(f, x) * value(g, y) for f, g in words["four_terms"])
        != (1 + x.bit_count() + y.bit_count()) % 2 for x in range(V) for y in range(V)))
    control("rank20_cannot_cover_diagonal", diagonal[20] == 0)
    control("four_term_diagonal_relaxation_is_insufficient", relax["4"] >= V)
    control("three_term_naive_minimum_is_insufficient", 3 * 42 < V and factors["3"]["minimum"] > V)
    control("copy127_would_change_budget", (17 - 1) * V - 17 * 127 > (17 - 1) * V - 17 * V)
    control("constant_form_orbit_not_duplicated", next(r for r in rows if r["key"] == [0, 0, 0, 0])["multiplicity"] == 1)
    control("complementary_coordinate_rank_is20", cost(1, 129) == 20 and cost(1, 1) != 20)
    return {"schema_version": 1, "assignment_seed": 43, "dimension": N, "ports": V,
            "affine_forms": 255, "ordered_pairs": 65025, "rank_orbits": rows,
            "rank_histogram": histogram(counts),
            "maximum_diagonal_by_rank": [[r, diagonal[r]] for r in sorted(diagonal)],
            "factor_census": factors, "max_diagonal_at_cost127": relax,
            "max_diagonal_at_cost128": at_floor,
            "witnesses": witnesses, "total_floor": 128, "peak_floor": 30,
            "minimum_peak_at_total_floor": 32, "optimistic_deficit_upper_bound": -128,
            "controls": controls}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-certificate", type=Path)
    args = ap.parse_args()
    check_sources()
    receipt = compute()
    if args.write_certificate:
        with args.write_certificate.open("x") as out:
            json.dump(receipt, out, indent=2)
            out.write("\n")
    else:
        require(json.loads((HERE / "CERTIFICATE.json").read_text()) == receipt,
                "certificate differs from complete recomputation")
    print("PASS_SEVEN_CUBE_AFFINE pairs=65025 orbits=127 assignments=566275 "
          "copy_floor=128 peak_floor=30 controls=10 no_new_kappa")


if __name__ == "__main__":
    main()
