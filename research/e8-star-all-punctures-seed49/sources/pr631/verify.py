#!/usr/bin/env python3
"""Exact E8 reader-flat census. Standard library only; Python >= 3.9.

Chi Zhao, with substantial OpenAI Codex assistance. Apache-2.0.
See README.md for proof scope,
prior work, and the mathematical argument making the finite census exhaustive.
"""
if not __debug__:
    raise SystemExit("Refusing optimized Python: exact validation requires assertions enabled.")

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import gcd, lcm
from pathlib import Path
import subprocess
import sys
import tempfile


def pop(x):
    return bin(x).count("1")


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def basis2(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return list(pivots.values())


def rankq(rows):
    """Fraction-free exact Gaussian elimination over Q."""
    pivots = {}
    for original in rows:
        row = list(original)
        for p, b in sorted(pivots.items()):
            if row[p]:
                a, c = row[p], b[p]
                row = [c * x - a * y for x, y in zip(row, b)]
                g = gcd(*row)
                if g:
                    row = [x // g for x in row]
        p = next((j for j, x in enumerate(row) if x), None)
        if p is not None:
            pivots[p] = row
    return len(pivots)


def inverse(matrix):
    n = len(matrix)
    a = [[Fraction(x) for x in row] +
         [Fraction(int(i == j)) for j in range(n)]
         for i, row in enumerate(matrix)]
    for j in range(n):
        k = next(i for i in range(j, n) if a[i][j])
        a[j], a[k] = a[k], a[j]
        pivot = a[j][j]
        a[j] = [x / pivot for x in a[j]]
        for i in range(n):
            if i != j:
                c = a[i][j]
                a[i] = [x - c * y for x, y in zip(a[i], a[j])]
    return [row[n:] for row in a]


def geometry(fault=None):
    lines = []
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0] * 8
            r[i], r[j] = 2, 2 * sign
            lines.append(tuple(r))
    for signs in product((-1, 1), repeat=7):
        r = (1,) + signs
        if sum(x < 0 for x in r) % 2 == 0:
            lines.append(r)
    simple = [(1, -1, -1, -1, -1, -1, -1, 1),
              (2, 2, 0, 0, 0, 0, 0, 0)]
    for i in range(6):
        r = [0] * 8
        r[i], r[i + 1] = -2, 2
        simple.append(tuple(r))
    if fault == "geometry":
        lines[0] = tuple(x + (i == 0) for i, x in enumerate(lines[0]))
    assert len(lines) == 120 and all(dot(r, r) == 8 for r in lines), "invalid root geometry"
    ainv = inverse(simple)
    supports = []
    for r in lines:
        coordinates = [sum(r[k] * ainv[k][j] for k in range(8))
                       for j in range(8)]
        assert all(x.denominator == 1 for x in coordinates)
        assert all(x >= 0 for x in coordinates) or all(x <= 0 for x in coordinates)
        supports.append(sum(1 << j for j, x in enumerate(coordinates) if x))
    return lines, simple, ainv, supports


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", type=Path, help="write the deterministic JSON receipt")
    parser.add_argument("--negative-controls", action="store_true",
                        help="also check rejection of three corruptions and Python -O")
    parser.add_argument("--fault", choices=("geometry", "parity", "flat"), help=argparse.SUPPRESS)
    args = parser.parse_args()
    lines, simple, ainv, supports = geometry(args.fault)
    b = [sum(((1 + dot(x, y) // 4) % 2) << j
             for j, y in enumerate(lines)) for x in lines]
    assert all(dot(x, y) % 4 == 0 for x in lines for y in lines)
    assert len(basis2(b)) == 9
    # Track self-pairing parity as well as reader supports. In characteristic
    # two, q(sum a_i u_i) = sum a_i q(u_i); all root labels have q=1.
    pivots = {}
    for row in b:
        x, odd = row, 1
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p][0]
                odd ^= pivots[p][1]
            else:
                pivots[p] = (x, odd)
                break
        if not x:
            assert odd == 0
    code = [(0, 0)]
    for row, odd in pivots.values():
        code += [(x ^ row, q ^ odd) for x, q in code]
    code.sort()
    if args.fault == "parity":
        code = [(x, q ^ int(x == b[0])) for x, q in code]
    assert len(set(x for x, _ in code)) == 512
    assert all((row, 1) in code for row in b), "invalid root-label parity"
    nonzero = [(x, q) for x, q in code if x]
    code_set = set(code)
    # Check Weyl equivariance using all eight simple reflections, including
    # parity. This avoids assuming an arbitrary labeling is preserved.
    index = {r: i for i, r in enumerate(lines)}
    index.update({tuple(-x for x in r): i for i, r in enumerate(lines)})
    for a in simple:
        perm = []
        for r in lines:
            t = dot(r, a)
            assert t % 4 == 0
            perm.append(index[tuple(x - t // 4 * y for x, y in zip(r, a))])
        assert len(set(perm)) == 120
        for support, odd in code:
            transported = sum(1 << perm[i] for i in range(120) if support >> i & 1)
            assert (transported, odd) in code_set
    census = []
    minima = []
    witnesses = []
    for d in range(8):
        best = None
        for chosen in combinations(range(8), d):
            subset = sum(1 << j for j in chosen)
            flat = sum(1 << i for i, support in enumerate(supports)
                       if support & ~subset == 0)
            if args.fault == "flat" and d == 6:
                flat |= 1 << next(i for i in range(120) if not (flat >> i & 1))
            assert rankq([r for i, r in enumerate(lines) if flat >> i & 1]) == d, "invalid flat rank"
            distances = [(pop(reader & ~flat), reader, odd) for reader, odd in nonzero]
            distance, reader, odd = min(distances)
            record = {"dimension": d, "simple_indices": list(chosen),
                      "root_lines": pop(flat), "minimum_deletions": distance,
                      "odd_minimum_deletions": min(x[0] for x in distances if x[2]),
                      "minimizer_count": sum(x[0] == distance for x in distances)}
            census.append(record)
            if best is None or distance < best[0]:
                best = (distance, reader, flat, chosen)
        distance, reader, flat, chosen = best
        deletion = reader & ~flat
        surviving = [r for i, r in enumerate(lines) if (reader & flat) >> i & 1]
        assert rankq(surviving) == d
        minima.append(distance)
        witnesses.append({"dimension": d, "simple_indices": list(chosen),
                          "reader_lines": [i for i in range(120) if reader >> i & 1],
                          "punctures": [i for i in range(120) if deletion >> i & 1]})
    assert minima == [56, 55, 53, 50, 44, 36, 26, 1]
    hyperplanes = [r for r in census if r["dimension"] == 7]
    # Unique exceptional root hyperplane; all other normal lines need >=14.
    assert sorted(r["minimum_deletions"] for r in hyperplanes) == [1, 14, 27, 28, 33, 35, 40, 43]
    for record in hyperplanes:
        omitted = next(j for j in range(8) if j not in record["simple_indices"])
        normal = [ainv[i][omitted] for i in range(8)]
        den = lcm(*(x.denominator for x in normal))
        normal = [int(x * den) for x in normal]
        g = gcd(*normal)
        normal = [x // g for x in normal]
        if next(x for x in normal if x) < 0:
            normal = [-x for x in normal]
        record["normal"] = normal
        is_root = any(rankq([normal, r]) == 1 for r in lines)
        assert is_root == (record["minimum_deletions"] == 1)
        if is_root:
            flat = sum(1 << i for i, r in enumerate(lines) if dot(normal, r) == 0)
            cheap = [R for R, _ in nonzero if pop(R & ~flat) < 14]
            root = next(i for i, r in enumerate(lines) if rankq([normal, r]) == 1)
            assert cheap == [b[root]] and pop(b[root] & ~flat) == 1

    def star_cost(punctures):
        weighted = []
        for reader, _ in nonzero:
            live = reader & ~punctures
            rank = rankq([r for i, r in enumerate(lines) if live >> i & 1])
            weighted.append((rank, reader))
        selected, cost = [], 0
        for weight, reader in sorted(weighted):
            if len(basis2(selected + [reader])) > len(selected):
                selected.append(reader)
                cost += weight
            if len(selected) == 9:
                break
        return cost, dict(sorted(Counter(x[0] for x in weighted).items()))

    independent = []
    for i in range(120):
        if len(basis2([b[j] for j in independent + [i]])) > len(independent):
            independent.append(i)
        if len(independent) == 9:
            break
    control_cost, control_hist = star_cost(sum(1 << i for i in independent))
    assert control_cost == 63
    d7 = next(r for r in hyperplanes if r["minimum_deletions"] == 14)
    h = sum(1 << i for i, r in enumerate(lines) if dot(d7["normal"], r) == 0)
    d7_readers = [r for r, odd in nonzero if pop(r & ~h) == 14]
    assert len(d7_readers) == 1
    punctures = d7_readers[0] & ~h
    d7_cost, d7_hist = star_cost(punctures)
    assert pop(punctures) == 14 and d7_cost == 64
    assert len(basis2([b[i] for i in range(120) if punctures >> i & 1])) == 8
    assert Fraction(54, 94) > Fraction(63, 111)
    result = {"schema": 1, "arithmetic": "exact integer and rational; standard library",
              "root_lines": 120, "label_rank": 9,
              "reader_weight_histogram": dict(sorted(Counter(pop(x) for x, _ in code).items())),
              "minimum_punctures_for_reader_rank_at_most_d": minima,
              "census": census, "sharp_witnesses": witnesses,
              "independent_nine_control": {"punctures": independent, "star_cost": control_cost,
                                            "reader_rank_histogram": control_hist},
              "sharp_fourteen_control": {"punctures": [i for i in range(120) if punctures >> i & 1],
                                         "star_cost": d7_cost, "reader_rank_histogram": d7_hist},
              "optimal_star_cost_per_port_up_to_35_punctures": "63/111",
              "scope": "bit E8 label decoders, star copy cost only; no supplier or kappa claim"}
    if args.write:
        args.write.write_text(json.dumps(result, indent=2) + "\n")
    print("PASS: 255 standard parabolic flats; 511 nonzero reader supports; 8 Weyl generators")
    print("PASS: sharp rank thresholds", minima)
    print("PASS: non-root normal threshold 14; sharp D7 puncture costs 64")
    print("PASS: optimum star cost/port among <=35 punctures is 63/111 (proof in README)")
    if args.negative_controls:
        script = str(Path(__file__).resolve())
        for fault, expected in [("geometry", "invalid root geometry"),
                                ("parity", "invalid root-label parity"),
                                ("flat", "invalid flat rank")]:
            run = subprocess.run([sys.executable, script, "--fault", fault],
                                 capture_output=True, text=True)
            assert run.returncode != 0 and expected in run.stderr, (fault, run.stderr)
        with tempfile.TemporaryDirectory(prefix="e8-puncture-negative-") as tmp:
            receipt = Path(tmp) / "must-not-exist.json"
            run = subprocess.run([sys.executable, "-O", script, "--write", str(receipt)],
                                 capture_output=True, text=True)
            assert run.returncode != 0 and "Refusing optimized Python" in run.stderr
            assert not receipt.exists()
        print("PASS: rejected corrupt geometry, parity and flat; rejected -O before writing")


if __name__ == "__main__":
    main()
