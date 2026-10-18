#!/usr/bin/env python3
"""Exact premises and controls for the matched-frame COPY obstruction.

Apache-2.0. Adam Gall, with substantial OpenAI Codex assistance.
Finite checks support the quantified proof in README.md, not a full theorem audit.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    "research/p112-single-lift/geometry.py",
    "research/complex-local-word-ceiling/ceiling.py",
    "research/complex-local-word-ceiling/RESULT.json",
}
CAPACITY = {1: 1, 2: 2, 3: 4, 4: 5}
SUPPORTS = {
    1: [41],
    2: [20, 99],
    3: [18, 25, 31, 105],
    4: [3, 7, 9, 22, 63, 65, 66, 72],
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def load(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def bits(row):
    return sum(int(value) << j for j, value in enumerate(row))


def rankq(matrix):
    """Fraction row elimination; never use a floating-point rank tolerance."""
    if not matrix:
        return 0
    rows = [list(map(Q, row)) for row in matrix]
    pivot = 0
    for col in range(len(rows[0])):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        divisor = rows[pivot][col]
        rows[pivot] = [value / divisor for value in rows[pivot]]
        for i in range(pivot + 1, len(rows)):
            factor = rows[i][col]
            if factor:
                rows[i] = [a - factor * b for a, b in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def rankmod(matrix, prime=101):
    """Independent column-oriented odd-prime elimination: a lower rank bound over Q."""
    if not matrix:
        return 0
    basis = {}
    for col in zip(*matrix):
        vector = [int(x) % prime for x in col]
        for pos, old in sorted(basis.items()):
            factor = vector[pos]
            vector = [(a - factor * b) % prime for a, b in zip(vector, old)]
        pos = next((i for i, x in enumerate(vector) if x), None)
        if pos is not None:
            inv = pow(vector[pos], -1, prime)
            basis[pos] = [x * inv % prime for x in vector]
    return len(basis)


def span(vectors):
    values = {0}
    for vector in vectors:
        values.update(value ^ vector for value in tuple(values))
    return values


def submatrix(matrix, left, right):
    return [[matrix[i][j] for j in right] for i in left]


def ranks(matrix):
    return rank2(map(bits, matrix)), rankq(matrix)


def check_sources():
    source = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in source["files"] if row["usage"] == "input"]
    require(len(rows) == len(INPUTS) and {row["path"] for row in rows} == INPUTS,
            "complete live input inventory")
    for row in rows:
        require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
                == row["sha256"], "source digest: " + row["path"])


def geometry():
    source = load("research/p112-single-lift/geometry.py", "pinned_geometry")
    data = source.build()
    roots, labels, duals, x = (data[k] for k in ("roots", "labels", "duals", "X"))
    # Independently construct all Euclidean lines, then bind every live root.
    lines = set()
    for i, j in combinations(range(8), 2):
        for si, sj in product((-2, 2), repeat=2):
            row = [0] * 8
            row[i], row[j] = si, sj
            lines.add(max(tuple(row), tuple(-v for v in row)))
    for row in product((-1, 1), repeat=8):
        if row.count(-1) % 2 == 0:
            lines.add(max(row, tuple(-v for v in row)))
    frame = []
    for j in range(4):
        for sign in (1, -1):
            row = [0] * 8
            row[2 * j], row[2 * j + 1] = 2, 2 * sign
            frame.append(tuple(row))
    canonical = {max(tuple(r), tuple(-v for v in r)) for r in roots}
    require(len(lines) == 120 and len(roots) == len(canonical) == 112,
            "root-line cardinalities")
    require(canonical == lines - set(frame), "independent P112 root set")
    dot = lambda a, b: sum(u * v for u, v in zip(a, b))
    b = []
    for i, ri in enumerate(roots):
        require(x[i] == [dot(ri, f) // 4 for f in frame], "coordinate binding")
        row = []
        for j, rj in enumerate(roots):
            require(dot(ri, rj) % 4 == 0, "integral root Gram")
            gram = dot(ri, rj) // 4
            binary = (1 + gram) % 2
            require(binary == ((duals[i] & labels[j]).bit_count() & 1),
                    "binary label pairing binding")
            require(dot(x[i], x[j]) == 2 * gram, "full coordinate decoder identity")
            require(not binary or 2 * gram == 4 * (i == j), "masked target is 4I")
            row.append(binary)
        b.append(row)
    require(all(b[i][i] == 1 for i in range(112)), "all live labels have self-pairing one")
    require(rank2(map(bits, b)) == rank2(labels) == 9, "ambient binary rank nine")
    return data, b


def quotient_census():
    """All nonalternating nonsingular symmetric forms in dimensions one through four."""
    summary = {}
    for r in range(1, 5):
        positions = [(i, j) for i in range(r) for j in range(i, r)]
        counts = Counter()
        for encoding in range(1 << len(positions)):
            h = [[0] * r for _ in range(r)]
            for k, (i, j) in enumerate(positions):
                h[i][j] = h[j][i] = (encoding >> k) & 1
            hb = list(map(bits, h))
            if rank2(hb) != r or not any(h[i][i] for i in range(r)):
                continue
            def pairing(u, v):
                return sum(((u >> i) & 1) * ((hb[i] & v).bit_count() & 1)
                           for i in range(r)) % 2
            odd = [u for u in range(1 << r) if pairing(u, u)]
            diagonal = sum(h[i][i] << i for i in range(r))
            characteristic = [c for c in range(1 << r)
                              if all(pairing(1 << i, c) == (diagonal >> i & 1)
                                     for i in range(r))]
            require(len(characteristic) == 1, "unique characteristic vector")
            c = characteristic[0]
            require(c != 0 and pairing(c, c) == r % 2, "characteristic parity")
            require(len(odd) == 1 << (r - 1), "odd affine hyperplane cardinality")
            lifted = [[pairing(u, v) for v in odd] for u in odd]
            require(ranks(lifted) == (r, CAPACITY[r]), "sharp quotient lift capacity")
            require(rankmod(lifted) == CAPACITY[r], "odd-prime capacity corroboration")
            if r % 2 == 0:
                require(all(u ^ c in odd and u ^ c != u for u in odd),
                        "fixed-point-free characteristic pairing")
                require(all(pairing(u, v) + pairing(u ^ c, v) == 1
                            for u in odd for v in odd), "complementary lifted rows")
            counts[rankq(lifted)] += 1
        summary[str(r)] = {"forms": sum(counts.values()),
                           "lift_rank_counts": {str(k): v for k, v in sorted(counts.items())}}
    require([summary[str(r)]["forms"] for r in range(1, 5)] == [1, 3, 28, 420],
            "complete symmetric-form census")
    return summary


def fixtures(data, b):
    labels = data["labels"]
    rows = {}
    for r, ids in SUPPORTS.items():
        matrix = submatrix(b, ids, ids)
        require(ranks(matrix) == (r, CAPACITY[r]), "P112 attaining capacity fixture")
        require(rankmod(matrix) == CAPACITY[r], "P112 odd-prime rank corroboration")
        scaled = [[(i + 1) * value * (-2 * j - 1) for j, value in enumerate(row)]
                  for i, row in enumerate(matrix)]
        require(rankq(scaled) == CAPACITY[r], "nonzero coefficient scaling preserves lift rank")
        rows[str(r)] = {"left": ids, "right": ids, "copy_rank": r,
                        "lift_rank": CAPACITY[r], "label_span_dimension": rank2(labels[i] for i in ids)}
    left, right = [3, 7, 9, 22, 63], SUPPORTS[4]
    require(left != right and span(labels[i] for i in left) == span(labels[i] for i in right),
            "different actual supports with equal label spans")
    require(ranks(submatrix(b, left, right)) == (4, 5), "nonidentical-support matched fixture")
    rows["different_supports"] = {"left": left, "right": right, "copy_rank": 4, "lift_rank": 5}
    # These are counterexamples to *dropping* hypotheses, not rejected decoder candidates.
    left, right = [0, 1, 2], [0, 72, 56]
    require(span(labels[i] for i in left) != span(labels[i] for i in right), "unmatched boundary")
    require(ranks(submatrix(b, left, right)) == (2, 3), "unmatched spans defeat rank-two cap")
    rows["unmatched_control"] = {"left": left, "right": right, "copy_rank": 2, "lift_rank": 3}
    ids = [8, 10, 24, 33, 50, 51, 74, 75, 88, 97]
    require(ranks(submatrix(b, ids, ids)) == (5, 10), "rank-five capacity exceeds four-thirds rank")
    require(rankmod(submatrix(b, ids, ids)) == 10, "rank-five odd-prime corroboration")
    rows["rank_five_control"] = {"left": ids, "right": ids, "copy_rank": 5, "lift_rank": 10}
    return rows


def masked_errors(b, terms):
    total = [[Q(0) for _ in b] for _ in b]
    for left, right in terms:
        for i, di in left.items():
            for j, tj in right.items():
                total[i][j] += di * tj
    return sum(bool(b[i][j] and total[i][j] != 4 * (i == j))
               for i in range(len(b)) for j in range(len(b)))


def decoder_controls(data, b):
    x = data["X"]
    coordinate = [({i: row[k] for i, row in enumerate(x) if row[k]},
                   {i: row[k] for i, row in enumerate(x) if row[k]}) for k in range(8)]
    require(masked_errors(b, coordinate) == 0, "incumbent masked positive control")
    require([ranks(submatrix(b, list(d), list(t)))[0] for d, t in coordinate] == [8] * 8,
            "incumbent eight rank-eight COPY charges")
    diagonal = [({i: 2}, {i: 2}) for i in range(112)]
    require(masked_errors(b, diagonal) == 0, "admissible COPY112 diagonal positive control")
    odd = next((i, j) for i in range(112) for j in range(112) if not b[i][j])
    free = ({odd[0]: 7}, {odd[1]: -3})
    require(ranks(submatrix(b, list(free[0]), list(free[1])))[0] == 0, "zero-cost odd correction")
    require(masked_errors(b, diagonal + [free]) == 0, "arbitrary free correction is invisible to mask")
    require(masked_errors(b, diagonal[:-1]) == 1, "omitted diagonal term fails exactness")
    require(masked_errors(b, diagonal + [({0: 1}, {0: 1})]) == 1, "false free diagonal correction fails")
    changed_mask = [row[:] for row in b]
    changed_mask[odd[0]][odd[1]] = 1
    require(masked_errors(changed_mask, diagonal + [free]) == 1, "wrong mask exposes free term")
    wrong = [{i: 2} for i in range(112)]
    wrong[0] = {0: 3}
    require(masked_errors(b, list(zip(wrong, [t for _, t in diagonal]))) == 1,
            "wrong coefficient fails exact diagonal")
    return {"baseline_copy_ranks": [8] * 8, "diagonal_copy_bill": 112,
            "free_pair": list(odd), "semantic_rejections": 4,
            "hypothesis_counterexamples": 2}


def invoice():
    # Unbounded integer relaxation; overshoot by more than max capacity-1 is unnecessary.
    upper = 112 + max(CAPACITY.values())
    best = [None] * upper
    best[0] = (0, {(0, 0, 0, 0)})
    for capacity in range(1, upper):
        for r, contribution in CAPACITY.items():
            if capacity < contribution or best[capacity - contribution] is None:
                continue
            cost, profiles = best[capacity - contribution]
            cost += r
            candidates = set()
            for profile in profiles:
                profile = list(profile)
                profile[r - 1] += 1
                candidates.add(tuple(profile))
            if best[capacity] is None or cost < best[capacity][0]:
                best[capacity] = (cost, candidates)
            elif cost == best[capacity][0]:
                best[capacity][1].update(candidates)
    minimum = min(best[k][0] for k in range(112, upper))
    optimizers = sorted({p for k in range(112, upper) if best[k][0] == minimum for p in best[k][1]})
    require(minimum == 84 and optimizers == [(0, 0, 28, 0)], "integer relaxation optimum")
    require(all(Q(c, r) <= Q(4, 3) for r, c in CAPACITY.items()), "four-thirds capacity bound")
    # For 0<=a<=1/5, q=1-a>=4/5; rank-three cost/capacity is smallest.
    require(4 ** 4 * 4 ** 5 > 3 ** 4 * 5 ** 5, "exact rank-four versus rank-three moment inequality")
    return {"minimum_copy_bill": minimum, "optimizers_n1_n2_n3_n4": [list(p) for p in optimizers],
            "universal_copy_moment_ratio_lower": "21/16", "attainment": "rank relaxation only; no COPY84 decoder"}


def screen():
    c = load("research/complex-local-word-ceiling/ceiling.py", "pinned_ceiling")
    pinned = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text())
    local = {int(r): n for r, n in pinned["selected"]["local_profile_per_call"].items()}
    require(local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
            "selected per-call profile binding")
    baseline = c.ceiling(local, 73, 896, 9, 64)
    optimistic = dict(local)
    optimistic.pop(8)
    optimistic[3] += 28
    obstruction = c.ceiling(optimistic, 73, 896, 9, 84)
    target = baseline[1] * Q(21, 20)
    require(obstruction[1] < baseline[0] < target < Q(1, 5), "fails unchanged five-percent target")
    require(c.model(local, 73, 896, 9, 64)["idle_mass"] ==
            c.model(optimistic, 73, 896, 9, 84)["idle_mass"] == 1646,
            "centre charge and local COPY mass changed together")
    require(c.relax(optimistic, 73, 896, 9, 84, obstruction[0])[1] < 1 and
            c.relax(optimistic, 73, 896, 9, 84, obstruction[1])[0] > 1,
            "certified obstruction bracket")
    # A bogus centre=64 calculation would hide twenty units of added paid mass.
    require(c.model(optimistic, 73, 896, 9, 64)["idle_mass"] == 1626,
            "undercharged-centre negative control")
    return {"baseline_a_bracket": list(map(str, baseline)),
            "optimistic_a_bracket": list(map(str, obstruction)),
            "five_percent_target": str(target), "centre_charge": 84,
            "optimistic_local_profile": {str(r): n for r, n in sorted(optimistic.items())},
            "idle_mass": 1646, "additional_physical_charges": "waived for rejection only"}


def result():
    check_sources()
    data, b = geometry()
    return {"schema_version": 1, "claim": "matched-span COPY ranks one through four force COPY at least84",
            "geometry": {"ports": 112, "checked_entries": 12544, "binary_rank": 9,
                         "constrained_entries": sum(map(sum, b))},
            "capacity": {str(r): value for r, value in CAPACITY.items()},
            "quotient_census": quotient_census(), "fixtures": fixtures(data, b),
            "controls": decoder_controls(data, b), "invoice": invoice(), "screen": screen()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate the deterministic certificate")
    args = parser.parse_args()
    evidence = result()
    path = HERE / "CERTIFICATE.json"
    if args.write:
        path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(path.read_text()) == evidence, "committed certificate reproduces exactly")
    print("PASS_P112_MATCHED_FRAME_COPY_FLOOR forms=452 entries=12544 capacities=1,2,4,5 "
          "COPY>=84 moment_ratio>=21/16 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
