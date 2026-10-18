#!/usr/bin/env python3
"""Exact p=25 E8 decoder boundary; explicit checks also run under -O.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance. Apache-2.0.
Model and predecessor credit: DreamingOfClouds/PR717, themilkman216/PR968,
woklerx/PR1077 and the retained root-pair-first-drop-seed48 package.
The root-flat classification F6 is a cited premise, not proved by this replay.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from math import gcd, lcm
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED_ROOT = 31
SIMPLE = [(1, -1, -1, -1, -1, -1, -1, 1),
          (2, 2, 0, 0, 0, 0, 0, 0), (-2, 2, 0, 0, 0, 0, 0, 0)] + [
    tuple(-2 if i == k else 2 if i == k + 1 else 0 for i in range(8))
    for k in range(1, 6)]
PAIRS56 = [(119, 84), (106, 54), (29, 17), (11, 4),
           (118, 20), (39, 6), (75, 1), (49, 0)]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def canonical(value):
    # JSON object keys are strings; normalize integer-indexed rank maps before
    # sorting so a serialized/reloaded receipt has the same canonical bytes.
    normalized = json.loads(json.dumps(value, allow_nan=False))
    return json.dumps(normalized, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def direction(vector):
    den = lcm(*(Fraction(x).denominator for x in vector))
    integers = [int(Fraction(x) * den) for x in vector]
    common = gcd(*integers)
    require(common != 0, "zero direction")
    integers = tuple(x // common for x in integers)
    return max(integers, tuple(-x for x in integers))


def root_lines():
    roots = set()
    for i, j in combinations(range(8), 2):
        for x, y in product((-2, 2), repeat=2):
            v = [0] * 8
            v[i], v[j] = x, y
            roots.add(max(tuple(v), tuple(-a for a in v)))
    for v in product((-1, 1), repeat=8):
        if v.count(-1) % 2 == 0:
            roots.add(max(v, tuple(-a for a in v)))
    return sorted(roots)


def binary_basis(rows):
    basis = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in basis:
                basis[p] = row
                break
            row ^= basis[p]
    return list(basis.values())


def rank2(rows):
    return len(binary_basis(rows))


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def echelon(rows):
    """Integer fraction-free row operations over Q; no numerical decisions."""
    pivots = {}
    for values in rows:
        row = list(values)
        for col in sorted(pivots):
            if row[col]:
                pivot = pivots[col]
                a, b = row[col], pivot[col]
                row = [b * x - a * y for x, y in zip(row, pivot)]
                divisor = gcd(*row)
                if divisor > 1:
                    row = [x // divisor for x in row]
        col = next((i for i, x in enumerate(row) if x), None)
        if col is not None:
            pivots[col] = row
    return pivots


def kernel_direction(pivots):
    require(len(pivots) == 7, "one-dimensional rational kernel required")
    free = next(i for i in range(8) if i not in pivots)
    vector = [Fraction(i == free) for i in range(8)]
    for col, row in sorted(pivots.items(), reverse=True):
        vector[col] = -sum((Fraction(row[j]) * vector[j]
                            for j in range(col + 1, 8)), Fraction(0)) / row[col]
    return direction(vector)


def inverse(matrix):
    n = len(matrix)
    rows = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for col in range(n):
        p = next((i for i in range(col, n) if rows[i][col]), None)
        require(p is not None, "singular matrix")
        rows[col], rows[p] = rows[p], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for i in range(n):
            if i != col:
                scale = rows[i][col]
                rows[i] = [x - scale * y for x, y in zip(rows[i], rows[col])]
    return [row[n:] for row in rows]


def model():
    roots = root_lines()
    require(len(roots) == 120 and all(dot(r, r) == 8 for r in roots), "E8 roots")
    require(all(dot(a, b) % 4 == 0 for a in roots for b in roots), "integral pairing")
    pairing = [sum(((dot(a, b) // 4 + 1) & 1) << j for j, b in enumerate(roots))
               for a in roots]
    require(rank2(pairing) == 9, "unit-coordinate pairing must have rank nine")
    basis = binary_basis(pairing)
    # Symmetry identifies the row space with every functional evaluation mask.
    words = [0]
    for row in basis:
        words += [x ^ row for x in words]
    words = sorted(words[1:])
    require(len(words) == len(set(words)) == 511, "complete nonzero dual space")
    supports = [sum((dot(a, b) != 0) << j for j, b in enumerate(roots)) for a in roots]
    return roots, pairing, words, supports


def two_annihilator_census(support, words):
    restricted = [support & w for w in words]
    minimum, count, masks = 121, 0, set()
    for i, x in enumerate(restricted):
        for y in restricted[i + 1:]:
            puncture = x | y
            size = puncture.bit_count()
            if size < minimum:
                minimum, count, masks = size, 1, {puncture}
            elif size == minimum:
                count += 1
                masks.add(puncture)
    return minimum, count, masks


def flat_census(roots, words):
    inv = inverse(SIMPLE)
    normals = [direction([row[i] for row in inv]) for i in range(8)]
    table = []
    for normal in normals:
        require(sum(dot(normal, s) == 0 for s in SIMPLE) == 7, "fundamental flat")
        support = sum((dot(normal, r) != 0) << i for i, r in enumerate(roots))
        minimum, _, _ = two_annihilator_census(support, words)
        table.append({"normal": list(normal), "flat_lines": 120 - support.bit_count(),
                      "minimum_punctures_for_span_at_most_seven": minimum})
    table.sort(key=lambda x: x["flat_lines"], reverse=True)
    require([(x["flat_lines"], x["minimum_punctures_for_span_at_most_seven"])
             for x in table] == [(63, 25), (42, 42), (37, 51), (28, 56),
                                 (23, 61), (22, 62), (16, 68), (14, 70)],
            "inherited flat census")
    return table


def symmetry(roots, pairing):
    index = {r: i for i, r in enumerate(roots)}
    generators = []
    for normal in SIMPLE:
        require(dot(normal, normal) == 8, "reflection normal")
        permutation = []
        for r in roots:
            require(dot(r, normal) % 4 == 0, "integral reflection")
            s = tuple(x - dot(r, normal) // 4 * y for x, y in zip(r, normal))
            permutation.append(index[max(s, tuple(-x for x in s))])
        require(len(set(permutation)) == 120, "root permutation")
        for i, j in product(range(120), repeat=2):
            require(((pairing[i] >> j) & 1) ==
                    ((pairing[permutation[i]] >> permutation[j]) & 1), "pairing equivariance")
            require((dot(roots[i], roots[j]) == 0) ==
                    (dot(roots[permutation[i]], roots[permutation[j]]) == 0),
                    "support equivariance")
        generators.append(permutation)
    transports = {SEED_ROOT: list(range(120))}
    queue = deque([SEED_ROOT])
    while queue:
        a = queue.popleft()
        for g in generators:
            b = g[a]
            if b not in transports:
                transports[b] = [g[i] for i in transports[a]]
                queue.append(b)
    require(set(transports) == set(range(120)), "all-root orbit coverage")
    return generators, transports


def term_cost(pairing, left, right, puncture):
    return rank2(pairing[i] & right & ~puncture for i in bits(left & ~puncture))


def decoder(roots, pairing, puncture, left_columns, right_columns):
    """Columns are doubled normal coordinates. Check every surviving pair."""
    require(len(left_columns) == len(right_columns) == 8, "eight terms required")
    for i, j in product(range(8), repeat=2):
        require(sum(a[i] * b[j] for a, b in zip(left_columns, right_columns)) == 8 * (i == j),
                "exact dual identity")
    live = [i for i in range(120) if not puncture >> i & 1]
    left = [[dot(roots[i], a) for a in left_columns] for i in live]
    right = [[dot(roots[i], b) for b in right_columns] for i in live]
    for ii, i in enumerate(live):
        for jj, j in enumerate(live):
            require(dot(left[ii], right[jj]) == 8 * dot(roots[i], roots[j]),
                    "all-pairs decoder identity")
    costs = []
    for k in range(8):
        rows = sum((left[ii][k] != 0) << i for ii, i in enumerate(live))
        cols = sum((right[jj][k] != 0) << j for jj, j in enumerate(live))
        costs.append(term_cost(pairing, rows, cols, 0))
    return {"puncture": list(bits(puncture)), "ports": len(live),
            "left_columns_doubled": [list(a) for a in left_columns],
            "right_columns_doubled": [list(b) for b in right_columns],
            "term_costs": costs, "copy_cost": sum(costs),
            "copy_per_port": str(Fraction(sum(costs), len(live))),
            "identity_entries": len(live) ** 2}


def reduced_inventory(roots, pairing, words, supports, puncture):
    index = {direction(r): i for i, r in enumerate(roots)}
    ranks = Counter()
    kernels = {}
    for word in words:
        rows = [roots[i] for i in bits(word & ~puncture)]
        pivots = echelon(rows)
        rank = len(pivots)
        require(rank in (7, 8), "boundary rational ranks must be seven or eight")
        ranks[rank] += 1
        if rank == 7:
            normal = kernel_direction(pivots)
            require(normal in index and all(dot(r, normal) == 0 for r in rows),
                    "reduced normal must be a root direction")
            kernels[hex(word)] = index[normal]
    reduced = sorted(set(kernels.values()))
    dimensions = {i: rank2(pairing[j] for j in bits(supports[i] & ~puncture)) for i in reduced}
    require(ranks == Counter({8: 483, 7: 28}), "complete rational rank inventory")
    require(Counter(dimensions.values()) == Counter({8: 25, 7: 1}), "support inventory")
    require(dimensions[SEED_ROOT] == 7, "distinguished rank-seven support")
    orthogonal = [i for i in reduced if dot(roots[i], roots[SEED_ROOT]) == 0]
    require(len(orthogonal) == 1, "unique reduced direction perpendicular to distinguished root")
    costs = {i: term_cost(pairing, supports[SEED_ROOT], supports[i], puncture) for i in reduced}
    admissible_six = [i for i in reduced if dot(roots[i], roots[SEED_ROOT]) and costs[i] <= 6]
    require(admissible_six == [SEED_ROOT] and costs[SEED_ROOT] == 6,
            "only parallel root normals give an admissible cost-six term")
    frame = [SEED_ROOT, orthogonal[0]]
    for i in range(120):
        if all(dot(roots[i], roots[j]) == 0 for j in frame):
            frame.append(i)
        if len(frame) == 8:
            break
    require(len(frame) == 8, "orthogonal completion exists")
    frame_costs = [term_cost(pairing, supports[i], supports[i], puncture) for i in frame]
    require(frame_costs == [6, 7, 9, 9, 9, 9, 9, 9], "sharp 67-copy completion")
    return {"puncture_hex": hex(puncture), "rank_counts": dict(sorted(ranks.items())),
            "kernel_by_functional_hex": kernels,
            "support_dimensions": dimensions, "distinguished_partner_costs": costs,
            "orthogonal_reduced_root": orthogonal[0], "attaining_frame": frame,
            "attaining_term_costs": frame_costs}


def source_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    require(sources["base_commit"] == "ef5f39403610d231a0c27e8a6b4f08c10209bcd6", "base pin")
    for entry in sources["files"]:
        if entry["usage"] == "input":
            require(hashlib.sha256((ROOT / entry["path"]).read_bytes()).hexdigest() == entry["sha256"],
                    "source pin mismatch: " + entry["path"])


def run():
    source_pins()
    roots, pairing, words, supports = model()
    table = flat_census(roots, words)
    generators, transports = symmetry(roots, pairing)
    minimum, count, cuts = two_annihilator_census(supports[SEED_ROOT], words)
    require((minimum, count, len(cuts)) == (25, 189, 63), "first boundary is complete")
    all_cuts = set()
    root_cut_counts = []
    for a in range(120):
        m, n, actual = two_annihilator_census(supports[a], words)
        transported = {sum(1 << transports[a][i] for i in bits(p)) for p in cuts}
        require((m, n, len(actual)) == (25, 189, 63) and actual == transported,
                "transported cuts equal complete root census")
        require(not (all_cuts & actual), "distinguished root is unique for every cut")
        all_cuts.update(actual)
        root_cut_counts.append(len(actual))
    records = [reduced_inventory(roots, pairing, words, supports, p) for p in sorted(cuts)]
    record = records[SEED_ROOT % len(records)]
    puncture67 = int(record["puncture_hex"], 16)
    frame = [roots[i] for i in record["attaining_frame"]]
    witness67 = decoder(roots, pairing, puncture67, frame, frame)
    require(witness67["copy_cost"] == 67, "completed exceptional bill")
    deleted = set(i for pair in PAIRS56 for i in pair)
    require(len(deleted) == 16, "P104 parent puncture")
    deleted.update([i for i in range(120) if i not in deleted][:9])
    puncture56 = sum(1 << i for i in deleted)
    a_columns = [roots[a] for a, _ in PAIRS56]
    b_columns = [tuple(2 * (dot(roots[a], roots[b]) // 4) * x for x in roots[b])
                 for a, b in PAIRS56]
    witness56 = decoder(roots, pairing, puncture56, a_columns, b_columns)
    require(witness56["term_costs"] == [7] * 8, "attaining 56-copy decoder at p=25")
    predecessor = json.loads((ROOT / "research/root-pair-first-drop-seed48/CERTIFICATE.json").read_text())
    p26 = sum(1 << i for i in predecessor["witness_puncture"])
    a26, b26 = predecessor["canonical_pair"]
    require(p26.bit_count() == 26 and a26 != b26 and dot(roots[a26], roots[b26]) != 0,
            "predecessor nonparallel witness scope")
    require(term_cost(pairing, supports[a26], supports[b26], p26) == 6, "sharp nonparallel threshold")
    require(Fraction(67, 95) > Fraction(56, 95) > Fraction(7, 13), "copy/port budget gate")
    controls = controls_for(roots, pairing, words, supports, cuts, witness56, puncture67)
    return {"schema_version": 1, "status": "PASS_COMPLEX_GENERAL_NORMAL_BOUNDARY",
            "assignment_seed": 31, "base_commit": "ef5f39403610d231a0c27e8a6b4f08c10209bcd6",
            "root_order_sha256": digest(roots), "root_index": SEED_ROOT,
            "flat_census": table, "functional_pairs_per_support": 130305,
            "weyl_generators": len(generators), "root_orbit": len(transports),
            "equivariance_pairs": len(generators) * 120 * 120,
            "root_cut_counts": root_cut_counts, "distinct_boundary_cuts": len(all_cuts),
            "all_boundary_cuts_sha256": digest(sorted(hex(p) for p in all_cuts)),
            "representative_functional_pairs_attaining_25": count,
            "representative_cuts": records, "rational_matrices_checked": len(records) * len(words),
            "witness67": witness67, "witness56": witness56,
            "predecessor_nonparallel_witness": {"pair": [a26, b26], "puncture": list(bits(p26)), "cost": 6},
            "controls": controls,
            "scope": "Written proof plus exact finite premises; inherited real root-flat classification F6. No physical supplier, new kappa, cold replay, or formal multiplication theorem."}


def controls_for(roots, pairing, words, supports, cuts, witness56, puncture67):
    passed = []

    def reject(name, action, reason):
        try:
            action()
        except ValueError as error:
            require(reason in str(error), "wrong control failure: " + name)
            passed.append(name)
            return
        raise ValueError("accepted negative control: " + name)

    reject("universal term-cost-seven claim at p25",
           lambda: require(term_cost(pairing, supports[SEED_ROOT], supports[SEED_ROOT], puncture67) >= 7,
                           "parallel-root counterexample"), "parallel-root counterexample")
    bad = [[x for x in col] for col in witness56["right_columns_doubled"]]
    bad[0] = [x // 2 for x in bad[0]]
    reject("missing dual factor two", lambda: decoder(roots, pairing,
           sum(1 << i for i in witness56["puncture"]), witness56["left_columns_doubled"], bad),
           "exact dual identity")
    wrong_pairing = [sum(((dot(a, b) // 4) & 1) << j for j, b in enumerate(roots)) for a in roots]
    reject("omitted unit label", lambda: require(rank2(wrong_pairing) == 9, "pairing rank"), "pairing rank")
    reject("omitted boundary cut", lambda: require(len(cuts - {min(cuts)}) == 63, "cut coverage"), "cut coverage")
    reject("omitted dual functional", lambda: require(len(words[:-1]) == 511, "dual coverage"), "dual coverage")
    for i in bits(puncture67):
        restored = puncture67 ^ (1 << i)
        require(term_cost(pairing, supports[SEED_ROOT], supports[SEED_ROOT], restored) >= 7,
                "single-line restoration must remove the cost-six term")
    passed.append("all 25 one-line restorations remove the cost-six exception")
    def gaussian_dot(xs, ys):
        return (sum(a * c - b * d for (a, b), (c, d) in zip(xs, ys)),
                sum(a * d + b * c for (a, b), (c, d) in zip(xs, ys)))

    aa, bb = [(1, 0), (0, 1)], [(1, 0), (0, -1)]
    require(gaussian_dot(aa, bb) == (2, 0) and
            gaussian_dot(aa, [(a, -b) for a, b in bb]) == (0, 0),
            "ordinary-transpose complex convention")
    passed.append("conjugate transpose changes the exact identity")
    require(gaussian_dot(aa, aa) == (0, 0),
            "complex parallel cross-terms need not be forbidden")
    passed.append("isotropic parallel cross-term is not assumed impossible")
    return passed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    result = run()
    path = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        path.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        require(canonical(json.loads(path.read_text())) == canonical(result), "saved certificate mismatch")
    print("PASS_COMPLEX_GENERAL_NORMAL_BOUNDARY cuts=7560 representatives=63 rational_matrices=32193 "
          "p25_minimum=56 cost6_completion_minimum=67 nonparallel_threshold=26 controls=8")


if __name__ == "__main__":
    main()
