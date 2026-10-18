"""Exact finite masked-Walsh census. Apache-2.0; substantial Codex assistance."""

import argparse
from collections import Counter
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import random
from fractions import Fraction

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("p112_geometry", HERE / "vendor/pr845-geometry.py")
geometry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(geometry)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows, limit=9):
    pivots = [0] * 9
    size = 0
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if pivots[p]:
                row ^= pivots[p]
            else:
                pivots[p] = row
                size += 1
                if size == limit:
                    return size
                break
    return size


def support(values):
    return sum(1 << i for i, value in enumerate(values) if value)


def beta(readers, sources, data):
    return geometry.term_cost(readers, sources, data)


def recipe(data, p, q, h, matrix):
    xp, xq = ([row[j] for row in data["X"]] for j in (p, q))
    z = [a + b if (label & h).bit_count() % 2 == 0 else 0
         for a, b, label in zip(xp, xq, data["labels"])]
    w = [a - b if (label & h).bit_count() % 2 else 0
         for a, b, label in zip(xp, xq, data["labels"])]
    ap, bp, aq, bq = matrix
    rp = [2*x - ap*u - bp*v for x, u, v in zip(xp, z, w)]
    rq = [2*x - aq*u - bq*v for x, u, v in zip(xq, z, w)]
    d1 = [ap*x + aq*y for x, y in zip(xp, xq)]
    d2 = [bp*x + bq*y for x, y in zip(xp, xq)]
    return xp, xq, z, w, rp, rq, d1, d2


def check_endpoint(values):
    xp, xq, z, w, rp, rq, d1, d2 = values
    for i in range(112):
        for j in range(112):
            require(xp[i]*rp[j] + xq[i]*rq[j] + d1[i]*z[j] + d2[i]*w[j]
                    == 2*(xp[i]*xp[j] + xq[i]*xq[j]), "endpoint identity")


def controls(data):
    require(rank([0, 3, 5, 6]) == 2, "dependent rank control")
    require(rank([1, 2, 4]) == 3, "independent rank control")
    cols = list(map(list, zip(*data["X"])))
    require(sum(beta(c, c, data) for c in cols) == 64, "baseline")
    values = recipe(data, 0, 1, 48, (1, 1, 0, 1))
    check_endpoint(values)
    broken = [list(v) for v in values]
    broken[4][0] += 1
    try:
        check_endpoint(broken)
    except ValueError:
        pass
    else:
        raise ValueError("corrupted residual accepted")
    broken = [list(v) for v in values]
    broken[6] = [0] * 112
    try:
        check_endpoint(broken)
    except ValueError:
        pass
    else:
        raise ValueError("omitted added total accepted")
    require(beta([0]*112, cols[0], data) == 0, "zero reader cost")
    require(beta(cols[0], [0]*112, data) == 0, "zero source cost")
    # Unmasked orthogonal Walsh replacement zeroes both old columns, but costs 18.
    plus = [a+b for a, b in zip(cols[0], cols[1])]
    minus = [a-b for a, b in zip(cols[0], cols[1])]
    require(beta(plus, plus, data) + beta(minus, minus, data) == 18,
            "unmasked Walsh cost")
    # Check the support-cell reduction at rational points outside the grid.
    critical = {-2, -1, 0, 1, 2}
    rational_points = {Fraction(n, d) for n in range(-15, 16) for d in (1, 2, 3, 5)}
    for cut in (1, 2, 48, 511):
        xp, xq, z, w, *_ = recipe(data, 0, 1, cut, (1, 0, 0, 1))
        require(not any(a*b for a, b in zip(z, w)), "disjoint masked sources")
        for a in rational_points:
            representative = a if a in critical else 3
            for source in (z, w):
                require(support([2*x-a*u for x, u in zip(xp, source)])
                        == support([2*x-representative*u for x, u in zip(xp, source)]),
                        "residual support-cell control")
            if a not in (0, 1, -1):
                require(support([x+a*y for x, y in zip(xp, xq)])
                        == support([x+3*y for x, y in zip(xp, xq)]),
                        "reader support-cell control")
    require(support([2*x-2*zv for x, zv in zip(xp, z)])
            != support([2*x-3*zv for x, zv in zip(xp, z)]),
            "coefficient 2 must not be treated as generic")
    return {"baseline": 64, "unmasked_walsh_total": 66,
            "rank_controls": 2, "endpoint_rejections": 2, "zero_term_controls": 2,
            "rational_support_points": len(rational_points), "support_cuts": 4,
            "critical_two_distinguished": True}


def census(data):
    matrices = [m for m in product((-1, 0, 1), repeat=4)
                if abs(m[0]*m[3] - m[1]*m[2]) == 1]
    require(len(matrices) == 40, "matrix count")
    cuts = list(range(1, 512))
    random.Random(48).shuffle(cuts)
    columns = list(map(list, zip(*data["X"])))
    all_histogram = Counter()
    pairs = []
    witness = None
    best = 100
    zero_source_pairs = 0
    grid_nonzero_minimum = 100
    relaxed_histogram = Counter()
    nonzero_sources_minimum = 100
    # Membership in col(X) is tested with exact rank below for a frozen witness;
    # the census itself depends only on nonzero scalar supports.
    for p, q in combinations(range(8), 2):
        xp, xq = columns[p], columns[q]
        reader_values = {(a, b): [a*x + b*y for x, y in zip(xp, xq)]
                         for a, b in product((-1, 0, 1), repeat=2) if a or b}
        # Project source labels against an exact basis of each reader space.
        projections = {}
        dimensions = {}
        for key, values in reader_values.items():
            space = geometry.reader_space(values, data["duals"])
            projections[key] = [geometry.evaluate(space, lab) for lab in data["labels"]]
            dimensions[key] = len(space)
        generic = (1, 3)
        space = geometry.reader_space([x+3*y for x, y in zip(xp, xq)], data["duals"])
        projections[generic] = [geometry.evaluate(space, lab) for lab in data["labels"]]
        dimensions[generic] = len(space)
        cache = {}

        def cost(key, values):
            mask = support(values)
            cache_key = (key, mask)
            if cache_key not in cache:
                cache[cache_key] = rank((v for i, v in enumerate(projections[key])
                                         if mask >> i & 1), dimensions[key])
            return cache[cache_key]

        hist = Counter()
        for h in cuts:
            z = [x+y if (h & label).bit_count() % 2 == 0 else 0
                 for x, y, label in zip(xp, xq, data["labels"])]
            w = [x-y if (h & label).bit_count() % 2 else 0
                 for x, y, label in zip(xp, xq, data["labels"])]
            if not any(z) or not any(w):
                zero_source_pairs += 1
            residual_costs = {}
            for row, key in ((xp, (1, 0)), (xq, (0, 1))):
                for a, b in product((-1, 0, 1), repeat=2):
                    if a or b:
                        residual = [2*x-a*u-b*v for x, u, v in zip(row, z, w)]
                        residual_costs[key, a, b] = cost(key, residual)
            added_z = {key: cost(key, z) for key in reader_values}
            added_w = {key: cost(key, w) for key in reader_values}
            representatives = (-2, -1, 0, 1, 2, 3)
            lower_original = [min(cost(key, [2*x-a*u-b*v for x, u, v in zip(row, z, w)])
                                  for a, b in product(representatives, repeat=2))
                              for row, key in ((xp, (1, 0)), (xq, (0, 1)))]
            reader_types = ((1, 0), (0, 1), (1, 1), (1, -1), generic)
            lower_added = [min(cost(key, src) for key in reader_types) for src in (z, w)]
            lower = 48 + sum(lower_original + lower_added)
            relaxed_histogram[lower] += 1
            if any(z) and any(w):
                nonzero_sources_minimum = min(nonzero_sources_minimum, lower)
            for matrix in matrices:
                ap, bp, aq, bq = matrix
                terms = [residual_costs[(1, 0), ap, bp], residual_costs[(0, 1), aq, bq],
                         added_z[ap, aq], added_w[bp, bq]]
                total = 48 + sum(terms)
                hist[total] += 1
                if any(z) and any(w):
                    grid_nonzero_minimum = min(grid_nonzero_minimum, total)
                if total < best:
                    best = total
                    witness = {"pair": [p, q], "cut": h, "matrix": list(matrix),
                               "changed_term_costs": terms, "unchanged_cost": 48,
                               "total": total}
        pair_result = {"pair": [p, q], "histogram": dict(sorted(hist.items())),
                       "minimum": min(hist), "maximum": max(hist)}
        pairs.append(pair_result)
        all_histogram.update(hist)
    require(sum(all_histogram.values()) == 572320, "incomplete census")
    values = recipe(data, *witness["pair"], witness["cut"], witness["matrix"])
    check_endpoint(values)
    direct_costs = [beta(values[a], values[b], data) for a, b in ((0, 4), (1, 5), (6, 2), (7, 3))]
    require(direct_costs == witness["changed_term_costs"], "witness direct cost")
    # Seed-chosen nondegenerate cut demonstrates that this is outside PR717's code-only class.
    outside = recipe(data, 0, 1, 48, (1, 1, 0, 1))
    ranks = [len(geometry.rational_basis_indices([row + [v] for row, v in zip(data["X"], vec)]))
             for vec in outside[2:4]]
    require(ranks == [9, 9], "masked sources must leave col(X) in escape control")
    return {"status": "complete finite census; no new kappa", "seed": 48,
            "cases": sum(all_histogram.values()), "histogram": dict(sorted(all_histogram.items())),
            "minimum": min(all_histogram), "maximum": max(all_histogram), "per_pair": pairs,
            "nonzero_sources_minimum": grid_nonzero_minimum,
            "minimum_witness": witness, "zero_source_cut_pairs": zero_source_pairs,
            "outside_colX_control": {"pair": [0, 1], "cut": 48, "augmented_ranks": ranks},
            "relaxation": {"histogram": dict(sorted(relaxed_histogram.items())),
                           "minimum": min(relaxed_histogram),
                           "nonzero_sources_minimum": nonzero_sources_minimum,
                           "cut_pairs": sum(relaxed_histogram.values()),
                           "critical_coefficients": [-2, -1, 0, 1, 2],
                           "generic_representative": 3},
            "controls": controls(data)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write a fresh certificate; refuse existing paths")
    args = parser.parse_args()
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in pins["files"].items():
        require(hashlib.sha256((HERE / path).read_bytes()).hexdigest() == expected,
                "source mismatch: " + path)
    data = geometry.build()
    geometry.check_geometry(data)
    require(data == json.loads((HERE / "GEOMETRY.json").read_text()), "geometry mismatch")
    report = census(data)
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.write:
        with args.write.open("x") as stream:
            stream.write(encoded)
    else:
        require(encoded == (HERE / "RESULT.json").read_text(), "certificate mismatch")
    print(f"PASS_P112_MASKED_WALSH cases={report['cases']} minimum={report['minimum']} baseline=64 no_new_kappa")


if __name__ == "__main__":
    main()
