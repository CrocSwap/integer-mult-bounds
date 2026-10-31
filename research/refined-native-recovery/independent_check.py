#!/usr/bin/env python3
"""Independent exact checks of the refined native recovery chain.

No primary recovery implementation is imported. Literal quotient trajectories,
scalar interval enumeration and pair-parity convolution provide separate checks.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Source matrix and one-step construction: zxv #5444, Ali Romman #5323 and lineage.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


SOURCE_SHA256 = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"
V = {1: 1, 12: 1, 0: -1, 16: -1}
W = {0: 1, 8: 1, 2: -1, 6: -1}
FRAMES = ((V, 2), (W, 3), (V, 2))


def check(ok, label):
    if not ok:
        raise ValueError(label)


def rounded(n):
    magnitude = (abs(n) + 26) // 52
    return magnitude if n >= 0 else -magnitude


def scalar(s, q):
    return q - rounded(s + 56 * q)


def scalar_power(s, q, depth):
    for _ in range(depth):
        q = scalar(s, q)
    return q


def load_matrix(path):
    raw = path.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source hash")
    columns = json.loads(raw)["mode_columns"]
    check(len(columns) == 8 and all(len(c) == 112 for c in columns), "shape")
    matrix = [list(row) for row in zip(*columns)]
    check(all(type(x) is int for row in matrix for x in row), "exact integers")
    check(gram_ok(matrix), "source Gram")
    return matrix


def gram_ok(matrix):
    return all(sum(row[i] * row[j] for row in matrix) == 56 * (i == j)
               for i in range(8) for j in range(8))


def modes(matrix, x):
    return [sum(matrix[i][j] * x[i] for i in range(112)) for j in range(8)]


def lift(matrix, q):
    return [sum(row[j] * q[j] for j in range(8)) for row in matrix]


def shifted(x, frame, reverse=False):
    null, source = frame
    y = list(x)
    amount = (-2 if reverse else 2) * x[source]
    for index, value in null.items():
        y[index] += amount * value
    return y


def native(matrix, x):
    q = [rounded(z) for z in modes(matrix, x)]
    correction = lift(matrix, q)
    return [a - b for a, b in zip(x, correction)], q


def literal_chain(matrix, x, frames):
    current = [2 * z for z in x]
    total = [0] * 8
    for stage in range(len(frames) + 1):
        if stage:
            current = shifted(current, frames[stage - 1])
        current, q = native(matrix, current)
        total = [a + b for a, b in zip(total, q)]
    return current, total


def reverse_total(matrix, y, total, frames, omit_frames=False):
    s = modes(matrix, y)
    residual = list(total)
    quotients = []
    for _ in range(len(frames) + 1):
        q = [rounded(a + 56 * b) for a, b in zip(s, residual)]
        quotients.append(q)
        residual = [a - b for a, b in zip(residual, q)]
    check(residual == [0] * 8, "total quotient endpoint")
    current = list(y)
    for stage in range(len(quotients) - 1, -1, -1):
        correction = lift(matrix, quotients[stage])
        current = [a + b for a, b in zip(current, correction)]
        if stage and not omit_frames:
            current = shifted(current, frames[stage - 1], reverse=True)
    check(all(x % 2 == 0 for x in current), "input integrality")
    return [x // 2 for x in current]


def source_code(matrix):
    code = {0}
    for row in matrix:
        mask = sum((entry % 2) << j for j, entry in enumerate(row))
        code |= {word ^ mask for word in tuple(code)}
    check(len(code) == 16, "source binary rank")
    check(all((a & b).bit_count() % 2 == 0 for a in code for b in code),
          "source code self-dual")
    check(Counter(x.bit_count() for x in code) == {0: 1, 4: 14, 8: 1},
          "source weight enumerator")
    return sorted(code)


def scalar_census():
    cases = 0
    checked_inputs = 0
    for s in range(-104, 105):
        interval = [0]
        for depth in range(1, 4):
            low = -((26 + s + 52 * interval[-1]) // 4)
            high = (26 - s - 52 * interval[0]) // 4
            scan = range(low - 1, high + 2)
            found = [q for q in scan if scalar_power(s, q, depth) == 0]
            check(found and found == list(range(found[0], found[-1] + 1)),
                  "scalar preimage is not an interval")
            check(len(found) <= 13 ** depth, "scalar cardinality")
            if s == 0:
                radius = (13 ** depth - 1) // 2
                check(found == list(range(-radius, radius + 1)), "sharp fiber")
            interval = found
            cases += 1
            checked_inputs += len(scan)
    return cases, checked_inputs


def pair_convolution(code):
    pairs = []
    totals = []
    for q2 in range(-7, 8):
        if rounded(56 * q2) != q2:
            continue
        for q1 in range(-14 * q2 - 7, -14 * q2 + 8):
            if rounded(56 * (q1 + q2)) == q1:
                pairs.append((q1 & 1, q2 & 1))
                totals.append(q1 + q2)
    check(sorted(totals) == list(range(-84, 85)), "169 distinct quotient sums")
    table = Counter(pairs)
    check(table == {(0, 0): 49, (0, 1): 42, (1, 0): 42, (1, 1): 36},
          "literal pair-parity census")
    parity = [sum(n for (a, b), n in table.items() if (a ^ b) == p)
              for p in (0, 1)]
    cosets = {tuple(sorted(word ^ mask for word in code)) for mask in range(256)}
    counts = []
    for coset in sorted(cosets):
        count = 0
        for word in coset:
            term = 1
            for j in range(8):
                term *= parity[(word >> j) & 1]
            count += term
        counts.append(count)
    expected = (13 ** 16 + 14 * 13 ** 8 + 1) // 16
    check(len(cosets) == 16 and max(counts) == expected, "exact coset maximum")
    return table, counts, expected


def frame_census(matrix):
    for frame in FRAMES[:2]:
        null, source = frame
        vector = [null.get(i, 0) for i in range(112)]
        check(modes(matrix, vector) == [0] * 8 and null.get(source, 0) == 0,
              "mode-preserving unimodular transvection")
        for j in range(112):
            e = [int(i == j) for i in range(112)]
            changed = shifted(e, frame)
            check(shifted(changed, frame, True) == e, "frame inverse")
            check(modes(matrix, changed) == modes(matrix, e), "mode preservation")
            check(all((a - b) % 2 == 0 for a, b in zip(e, changed)), "parity")
    e3 = [int(i == 3) for i in range(112)]
    uv = shifted(shifted(e3, FRAMES[1]), FRAMES[0])
    vu = shifted(shifted(e3, FRAMES[0]), FRAMES[1])
    check([a - b for a, b in zip(uv, vu)] == [-4 * V.get(i, 0) for i in range(112)],
          "two frames genuinely fail to commute")
    x = [52 * int(i == 2) for i in range(112)]
    ku, _ = native(matrix, shifted(x, FRAMES[0]))
    k, _ = native(matrix, x)
    uk = shifted(k, FRAMES[0])
    check([a - b for a, b in zip(ku, uk)] == [8 * V.get(i, 0) for i in range(112)],
          "frame genuinely fails to commute with native map")
    return 224


def roundtrip_census(matrix, code):
    checks = 0
    omitted_frame_rejected = False
    for depth in range(1, 5):
        frames = FRAMES[:depth - 1]
        radius = (13 ** depth - 1) // 2
        for word in code:
            for choice in range(3):
                total = [(-radius + ((word >> j) & 1)) *
                         (-1 if choice == 1 or (choice == 2 and j % 2) else 1)
                         for j in range(8)]
                x = reverse_total(matrix, [0] * 112, total, frames)
                y, actual = literal_chain(matrix, x, frames)
                check(y == [0] * 112 and actual == total, "attaining reconstruction")
                if depth > 1:
                    mutant = reverse_total(matrix, y, total, frames, True)
                    omitted_frame_rejected |= literal_chain(matrix, mutant, frames)[0] != y
                checks += 1
        for seed in range(24):
            x = [((i * (seed + 3) + seed * seed) % 107) - 53 for i in range(112)]
            y, total = literal_chain(matrix, x, frames)
            check(reverse_total(matrix, y, total, frames) == x, "arbitrary-output reconstruction")
            check([2 * a - b for a, b in zip(modes(matrix, x), modes(matrix, y))]
                  == [56 * q for q in total], "mode invariant")
            checks += 1
    check(omitted_frame_rejected, "omitted inverse-frame control did not reject")
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path,
                        default=Path(__file__).resolve().parents[1] /
                        "precision-state-frontier/FIXTURE.json")
    args = parser.parse_args()
    matrix = load_matrix(args.source)
    code = source_code(matrix)
    scalar_cases, scalar_inputs = scalar_census()
    table, cosets, maximum = pair_convolution(code)
    frames = frame_census(matrix)
    roundtrips = roundtrip_census(matrix, code)
    altered = [row[:] for row in matrix]
    altered[0][0] += 1
    check(not gram_ok(altered), "altered Gram control did not reject")
    check(rounded(26) == 1 and rounded(-26) == -1, "half-away tie controls")
    check(maximum != 169 ** 8, "omitted lattice constraint control")
    check(maximum != ((13 ** 8 + 14 * 13 ** 4 + 1) // 16) * 13 ** 8,
          "naive multiplication control")
    check(scalar(0, 13) == -1 and scalar(0, -13) == 1, "wrong recursion sign")
    result = {"scalar_interval_cases": scalar_cases, "scalar_inputs": scalar_inputs,
              "pair_parities": {str(k): v for k, v in sorted(table.items())},
              "coset_counts": sorted(cosets), "two_step_maximum": maximum,
              "frame_basis_checks": frames, "source_sized_roundtrips": roundtrips,
              "controls": 6, "source_sha256": SOURCE_SHA256}
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_REFINED_NATIVE_RECOVERY")


if __name__ == "__main__":
    main()
