#!/usr/bin/env python3
"""Exact finite premises for the two-coordinate small-rectangle obstruction.

Apache-2.0. Prepared for commdata2338 with substantial OpenAI Codex assistance.
The quantified complex theorem is in README.md; examples are controls only.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import importlib.util
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {"research/p112-single-lift/geometry.py",
          "research/complex-frame-pair-decoders/PROOF.md"}
STRATA = [("x", 1, 0), ("y", 0, 1), ("plus", 1, 1),
          ("minus", 1, -1), ("generic", 1, 2)]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def check_sources(sources):
    rows = [r for r in sources["files"] if r["usage"] == "input"]
    need(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS,
         "complete live source inventory")
    for row in rows:
        need(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
             == row["sha256"], "source digest: " + row["path"])


def rank(rows):
    basis = {}
    for v in rows:
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                break
    return len(basis)


def rational_rank(rows):
    pivots = {}
    for original in rows:
        row = list(map(F, original))
        for j, previous in sorted(pivots.items()):
            if row[j]:
                scale = row[j]
                row = [a-scale*c for a, c in zip(row, previous)]
        pivot = next((j for j, value in enumerate(row) if value), None)
        if pivot is not None:
            scale = row[pivot]
            pivots[pivot] = [value/scale for value in row]
    return len(pivots)


def bitmask(indices):
    return sum(1 << i for i in indices)


def cost(b, left, right):
    m = bitmask(right)
    return rank(b[i] & m for i in left)


def model():
    spec = importlib.util.spec_from_file_location("p112_geometry", ROOT /
                            "research/p112-single-lift/geometry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.build()
    module.check_geometry(data)
    ordering = sorted(range(112), key=lambda i: max(tuple(data["roots"][i]),
                                    tuple(-v for v in data["roots"][i])))
    roots, x, labels, duals = [], [], [], []
    for i in ordering:
        r = data["roots"][i]
        canonical = max(tuple(r), tuple(-v for v in r))
        sign = 1 if tuple(r) == canonical else -1
        roots.append(list(canonical))
        x.append([sign * v for v in data["X"][i]])
        labels.append(data["labels"][i])
        duals.append(data["duals"][i])
    b = [bitmask(j for j in range(112) if (a & labels[j]).bit_count() % 2)
         for a in duals]
    need(rank(b) == 9 and rank(labels) == 9, "ambient rank nine")
    return roots, x, labels, b


def premises(roots, x, labels, b):
    characters = [bitmask(i for i, v in enumerate(labels)
                         if (f & v).bit_count() % 2) for f in range(1, 512)]
    pairs, dims, distances, pair_ranks = [], Counter(), Counter(), Counter()
    free_distances = Counter()
    boundary = free_boundary = None
    for k, l in combinations(range(8), 2):
        records = []
        for name, a, c in STRATA:
            support = [i for i, row in enumerate(x) if a * row[k] + c * row[l]]
            m = bitmask(support)
            spectrum = Counter((m & ch).bit_count() for ch in characters)
            distance = min(w for w in spectrum if w)
            dimension = rank(labels[i] for i in support)
            viable = []
            for f, ch in enumerate(characters, 1):
                deleted_mask = m & ch
                if deleted_mask:
                    neighbors = [j for j in range(112) if not (b[j] & deleted_mask)]
                    if neighbors:
                        viable.append((deleted_mask.bit_count(), f, deleted_mask, neighbors))
            free_distance = min(v[0] for v in viable)
            need(free_distance >= 24, "free-compatible erasure distance")
            free_spectrum = Counter(v[0] for v in viable)
            free_distances[free_distance] += 1
            if free_boundary is None and free_distance == 24:
                weight, f, deleted_mask, neighbors = min(viable)
                deleted = [i for i in support if deleted_mask >> i & 1]
                after = rank(labels[i] for i in support if i not in deleted)
                need(after < dimension, "free-compatible boundary span loss")
                free_boundary = {"pair": [k, l], "stratum": name, "functional": f,
                                 "deleted": deleted, "common_odd_neighbors": neighbors,
                                 "span_before": dimension, "span_after": after}
            need(dimension in (8, 9) and distance >= 12, "span and erasure distance")
            need(spectrum.get(0, 0) == 2 ** (9-dimension) - 1,
                 "annihilator count")
            if name == "generic":
                need(support == [i for i, row in enumerate(x) if row[k] or row[l]],
                     "generic stratum is the union")
            records.append({"name": name, "support": support, "span": dimension,
                            "distance": distance, "free_distance": free_distance,
                            "free_weight_spectrum": {str(w): free_spectrum[w] for w in sorted(free_spectrum)},
                            "weight_spectrum": {str(w): spectrum[w] for w in sorted(spectrum)}})
            dims[dimension] += 1
            distances[distance] += 1
            if distance == 12 and boundary is None:
                f = next(f for f, ch in enumerate(characters, 1)
                         if (m & ch).bit_count() == distance)
                deleted = [i for i in support if (f & labels[i]).bit_count() % 2]
                remaining = [i for i in support if i not in deleted]
                after = rank(labels[i] for i in remaining)
                need(after < dimension, "twelve-erasure boundary witness")
                boundary = {"pair": [k, l], "stratum": name, "functional": f,
                            "deleted": deleted, "span_before": dimension,
                            "span_after": after,
                            "common_odd_neighbors": [j for j in range(112)
                                if all(not (b[i] >> j & 1) for i in deleted)]}
        matrix = [[cost(b, a["support"], c["support"]) for c in records]
                  for a in records]
        need(all(v >= 8 for row in matrix for v in row), "all support pairings >= eight")
        pair_ranks.update(v for row in matrix for v in row)
        pairs.append({"pair": [k, l], "strata": records, "pairing_ranks": matrix})
    coordinate_costs = [cost(b, [i for i in range(112) if x[i][k]],
                            [i for i in range(112) if x[i][k]]) for k in range(8)]
    need(coordinate_costs == [8] * 8, "coordinate positive control")
    return {"schema_version": 1, "root_order": "lexicographic positive-first doubled E8 roots",
            "roots": roots, "pairs": pairs, "boundary": boundary, "free_boundary": free_boundary,
            "summary": {"coordinate_pairs": 28, "support_strata": 140,
                        "nonzero_functionals_per_stratum": 511,
                        "functional_evaluations": 71540, "pairings": 700,
                        "span_counts": {str(k): v for k, v in sorted(dims.items())},
                        "distance_counts": {str(k): v for k, v in sorted(distances.items())},
                        "pairing_rank_counts": {str(k): v for k, v in sorted(pair_ranks.items())},
                        "free_distance_counts": {str(k): v for k, v in sorted(free_distances.items())},
                        "max_deleted_per_side": 11, "max_nonzero_free_deleted_per_side": 23,
                        "coordinate_costs": coordinate_costs,
                        "whole_copy_floor": 64}}


# A pair of rational numbers represents a Gaussian rational, without floats.
def q(z):
    if isinstance(z, tuple):
        return tuple(map(F, z))
    return F(z), F(0)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def neg(a):
    return -a[0], -a[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def inv(a):
    n = a[0]*a[0]+a[1]*a[1]
    need(bool(n), "nonzero Gaussian divisor")
    return a[0]/n, -a[1]/n


def nz(a):
    return bool(a[0] or a[1])


def total(values):
    result = q(0)
    for value in values:
        result = add(result, value)
    return result


def inverse(matrix):
    n = len(matrix)
    rows = [list(row)+[q(i == j) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if nz(rows[i][j])), None)
        need(pivot is not None, "invertible factor change")
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = inv(rows[j][j])
        rows[j] = [mul(z, scale) for z in rows[j]]
        for i in range(n):
            if i != j:
                factor = rows[i][j]
                rows[i] = [add(a, neg(mul(factor, c))) for a, c in zip(rows[i], rows[j])]
    return [row[n:] for row in rows]


def mix(x, pair, u, v, raw_matrix, wrong_transpose=False):
    matrix = [[q(z) for z in row] for row in raw_matrix]
    back = inverse(matrix)
    left, right = [], []
    k, l = pair
    for i in range(112):
        a, c = [q(x[i][k]), q(x[i][l]), u[i]], [q(x[i][k]), q(x[i][l]), v[i]]
        left.append([total(mul(a[t], matrix[t][j]) for t in range(3)) for j in range(3)])
        right.append([total(mul(c[t], back[t][j] if wrong_transpose else back[j][t])
                            for t in range(3)) for j in range(3)])
    return left, right


def check_fixture(x, b, pair, u, v, matrix, wrong_transpose=False):
    us, vs = [i for i, z in enumerate(u) if nz(z)], [i for i, z in enumerate(v) if nz(z)]
    cap = 23 if us and vs else 11
    need(len(us) <= cap and len(vs) <= cap, "small support domain")
    need(cost(b, us, vs) == 0, "free odd rectangle")
    left, right = mix(x, pair, u, v, matrix, wrong_transpose)
    k, l = pair
    for i in range(112):
        for j in range(112):
            wanted = add(q(x[i][k]*x[j][k]+x[i][l]*x[j][l]), mul(u[i], v[j]))
            actual = total(mul(left[i][t], right[j][t]) for t in range(3))
            need(wanted == actual, "ordinary-transpose factor identity")
    costs = [cost(b, [i for i in range(112) if nz(left[i][t])],
                    [i for i in range(112) if nz(right[i][t])]) for t in range(3)]
    need(sum(c >= 8 for c in costs) >= 2, "two separately rank-eight products")
    return costs


def rejected(call, expected):
    try:
        call()
    except ValueError as exc:
        need(expected in str(exc), "wrong rejection: " + str(exc))
        return
    raise ValueError("control unexpectedly accepted: " + expected)


def fixtures_and_controls(x, labels, b, certificate, sources):
    z = [q(0)] * 112
    odd = next((i, j) for i in range(112) for j in range(112) if not (b[i] >> j & 1))
    u, v = list(z), list(z)
    u[odd[0]], v[odd[1]] = q(1), q((2, 1))
    identity = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    dense = [[1, 1, 1], [1, 2, 3], [1, 4, 6]]
    complex_matrix = [[1, (0, 1), 1], [0, 1, 1], [1, 0, (0, 1)]]
    # A genuinely two-sided, non-singleton zero rectangle.
    U = [odd[0]]
    for i in range(112):
        if i not in U and len(U) < 4:
            V = [j for j in range(112) if all(not (b[t] >> j & 1) for t in U+[i])]
            if len(V) >= 5:
                U.append(i)
    V = [j for j in range(112) if all(not (b[t] >> j & 1) for t in U)][:5]
    need(len(U) == 4 and len(V) == 5, "non-singleton fixture rectangle")
    ru, rv = list(z), list(z)
    for i in U:
        ru[i] = q(x[i][0]+x[i][1] or 1)
    for i in V:
        rv[i] = q((1, -1))
    # Force an actual support cancellation in a coherent three-term change.
    cu = list(z)
    cancellation_row = next(i for i in range(112) if x[i][0]+x[i][1])
    cu[cancellation_row] = q(-(x[cancellation_row][0]+x[cancellation_row][1]))
    cv = list(z)
    cv[next(j for j in range(112) if not (b[cancellation_row] >> j & 1))] = q(1)
    fu, fv = list(z), list(z)
    for i in certificate["free_boundary"]["deleted"][:-1]:
        fu[i] = q(1)
    fv[certificate["free_boundary"]["common_odd_neighbors"][0]] = q(1)
    cases = [("sharp singleton", (0, 1), u, v, identity),
             ("dense singleton", (0, 1), u, v, dense),
             ("complex ordinary transpose", (0, 7), u, v, complex_matrix),
             ("four by five rectangle", (2, 6), ru, rv, dense),
             ("zero left correction", (1, 5), z, v, dense),
             ("zero right correction", (3, 4), u, z, dense),
             ("zero correction", (0, 1), z, z, complex_matrix),
             ("support cancellation", (0, 1), cu, cv, dense),
             ("twenty-three by one rectangle", (0, 1), fu, fv, dense)]
    results = [{"name": name, "pair": list(pair), "costs": check_fixture(x, b, pair, a, c, m)}
               for name, pair, a, c, m in cases]
    need(results[0]["costs"] == [8, 8, 0], "sharp copy floor")
    need(all(rational_rank([row + [int(i == point)] for i, row in enumerate(x)]) == 9
             for point in odd), "singleton completion has rank nine")
    results[0]["full_masked_matrix_rank"] = 9
    left, _ = mix(x, (0, 1), cu, cv, dense)
    need(not nz(left[cancellation_row][0]), "actual cancellation exercised")
    controls = []
    wrong = list(z); wrong[odd[0]] = q(1)
    rejected(lambda: check_fixture(x, b, (0, 1), u, wrong, identity), "free odd rectangle")
    controls.append("nonfree diagonal correction")
    rejected(lambda: check_fixture(x, b, (0, 1), u, v, [[1, 1, 0]]*3), "invertible")
    controls.append("singular factor change")
    rejected(lambda: check_fixture(x, b, (0, 1), u, v, dense, True), "factor identity")
    controls.append("inverse without ordinary transpose")
    large = list(z)
    for i in range(12): large[i] = q(1)
    rejected(lambda: check_fixture(x, b, (0, 1), large, z, identity), "small support domain")
    controls.append("twelve-row zero-product input outside theorem domain")
    fu24 = list(fu)
    fu24[certificate["free_boundary"]["deleted"][-1]] = q(1)
    rejected(lambda: check_fixture(x, b, (0, 1), fu24, fv, identity), "small support domain")
    controls.append("twenty-four-row nonzero input outside theorem domain")
    bad_sources = deepcopy(sources)
    next(r for r in bad_sources["files"] if r["usage"] == "input")["sha256"] = "0"*64
    rejected(lambda: check_sources(bad_sources), "source digest")
    controls.append("source digest drift")
    bad_sources = deepcopy(sources)
    bad_sources["files"] = [r for r in bad_sources["files"] if r["path"] != sorted(INPUTS)[0]]
    rejected(lambda: check_sources(bad_sources), "complete live source inventory")
    controls.append("omitted live input")
    boundary = certificate["boundary"]
    row = next(p for p in certificate["pairs"] if p["pair"] == boundary["pair"])
    st = next(s for s in row["strata"] if s["name"] == boundary["stratum"])
    remaining = [i for i in st["support"] if i not in boundary["deleted"]]
    rejected(lambda: need(rank(labels[i] for i in remaining) == st["span"],
                          "false twelve-erasure extension"), "false twelve-erasure extension")
    controls.append("false twelve-erasure span extension")
    return results, controls


def compare_receipt(actual, expected):
    need(actual == expected, "certificate mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a fresh receipt; never overwrite")
    args = parser.parse_args()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    check_sources(sources)
    roots, x, labels, b = model()
    certificate = premises(roots, x, labels, b)
    fixtures, controls = fixtures_and_controls(x, labels, b, certificate, sources)
    certificate["fixtures"] = fixtures
    certificate["controls"] = controls
    changed = deepcopy(certificate)
    changed["pairs"][0]["strata"][0]["support"].pop()
    rejected(lambda: compare_receipt(changed, certificate), "certificate mismatch")
    certificate["controls"].append("corrupted support receipt")
    if args.write:
        with args.write.open("x") as f:
            f.write(json.dumps(certificate, indent=2, sort_keys=True)+"\n")
    else:
        compare_receipt(json.loads((HERE / "CERTIFICATE.json").read_text()), certificate)
    print("PASS_P112_TWO_COORDINATE_SMALL_RECTANGLE pairs=28 strata=140 "
          "characters=71540 pairings=700 erasures=11 nonzero_free_erasures=23 fixtures=9 controls=9 copy_floor=64")


if __name__ == "__main__":
    main()
