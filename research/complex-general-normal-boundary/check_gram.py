#!/usr/bin/env python3
"""Separate exact Gram-minor checker for the p=25 certificate.

Imports no producer or predecessor code. Dense binary elimination, Gram
determinants and root-reflection closure replace the producer's rank engines.
Prepared by Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
This is implementation separation, not independent human review.
"""
from collections import Counter, deque
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def scalar(u, v):
    return sum(x * y for x, y in zip(u, v))


def roots_from_coordinates():
    # Fix the first nonzero coordinate positive; no set-based +/- quotient.
    result = []
    for a in range(8):
        for b in range(a + 1, 8):
            for sign in (-1, 1):
                row = [0] * 8
                row[a], row[b] = 2, 2 * sign
                result.append(tuple(row))
    for tail in product((-1, 1), repeat=7):
        if tail.count(-1) % 2 == 0:
            result.append((1,) + tail)
    return sorted(result)


def dense_binary_rank(matrix):
    rows = [list(x) for x in matrix]
    pivot = 0
    for col in range(len(rows[0]) if rows else 0):
        found = next((i for i in range(pivot, len(rows)) if rows[i][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        for i in range(pivot + 1, len(rows)):
            if rows[i][col]:
                rows[i] = [x ^ y for x, y in zip(rows[i], rows[pivot])]
        pivot += 1
        if pivot == len(rows):
            break
    return pivot


def bareiss(matrix):
    """Exact determinant, including row pivots; division is checked."""
    a = [row[:] for row in matrix]
    n, sign, previous = len(a), 1, 1
    if n == 0:
        return 1
    for k in range(n - 1):
        p = next((i for i in range(k, n) if a[i][k]), None)
        if p is None:
            return 0
        if p != k:
            a[p], a[k] = a[k], a[p]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                need(numerator % previous == 0, "nonintegral Bareiss step")
                a[i][j] = numerator // previous
        for i in range(k + 1, n):
            a[i][k] = 0
        previous = pivot
    return sign * a[-1][-1]


def decode_mask(text):
    value = int(text, 16)
    need(0 <= value < 1 << 120, "mask outside root universe")
    return frozenset(i for i in range(120) if value >> i & 1)


def encode_mask(indices):
    return hex(sum(1 << i for i in indices))


def compute_supports(roots):
    return [frozenset(j for j, other in enumerate(roots) if scalar(r, other)) for r in roots]


def check_witness(witness, roots, pairing):
    puncture = set(witness["puncture"])
    need(len(puncture) == 25 and all(0 <= i < 120 for i in puncture), "witness puncture")
    live = [i for i in range(120) if i not in puncture]
    left, right = witness["left_columns_doubled"], witness["right_columns_doubled"]
    need(len(left) == len(right) == 8 and all(len(c) == 8 for c in left + right), "witness shape")
    d = [[scalar(roots[i], a) for a in left] for i in live]
    t = [[scalar(roots[j], b) for b in right] for j in live]
    for i, row in enumerate(d):
        for j, col in enumerate(t):
            need(scalar(row, col) == 8 * scalar(roots[live[i]], roots[live[j]]), "full witness identity")
    costs = []
    for k in range(8):
        rows = [live[i] for i in range(95) if d[i][k]]
        cols = [live[j] for j in range(95) if t[j][k]]
        costs.append(dense_binary_rank([[pairing[i][j] for j in cols] for i in rows]))
    need(costs == witness["term_costs"] and sum(costs) == witness["copy_cost"], "full witness copy bill")
    return costs


def check(certificate):
    roots = roots_from_coordinates()
    need(len(roots) == len(set(roots)) == 120, "independent root count")
    encoded = json.dumps(roots, sort_keys=True, separators=(",", ":"))
    need(hashlib.sha256(encoded.encode()).hexdigest() == certificate["root_order_sha256"], "root order")
    pairing = [[(scalar(a, b) // 4 + 1) % 2 for b in roots] for a in roots]
    need(dense_binary_rank(pairing) == 9, "independent label rank")
    indices = []
    for i in range(120):
        if dense_binary_rank([pairing[j] for j in indices + [i]]) > len(indices):
            indices.append(i)
    need(len(indices) == 9, "independent functional basis")
    functions = []
    for coeffs in product((0, 1), repeat=9):
        if not any(coeffs):
            continue
        functions.append(frozenset(i for i in range(120)
                                   if sum(coeffs[k] * pairing[indices[k]][i] for k in range(9)) % 2))
    need(len(set(functions)) == 511, "independent complete dual")
    support = compute_supports(roots)
    alpha = certificate["root_index"]
    need(alpha == 31, "assignment root")
    cuts = set()
    minimum, multiplicity = 120, 0
    restricted = [s & support[alpha] for s in functions]
    for a, b in combinations(restricted, 2):
        union = a | b
        n = len(union)
        if n < minimum:
            minimum, multiplicity, cuts = n, 1, {union}
        elif n == minimum:
            multiplicity += 1
            cuts.add(union)
    need((minimum, multiplicity, len(cuts)) == (25, 189, 63), "independent boundary exhaustion")
    records = certificate["representative_cuts"]
    need(len(records) == 63 and {decode_mask(r["puncture_hex"]) for r in records} == cuts,
         "certificate must contain every representative exactly once")
    outer = [[[a * b for b in r] for a in r] for r in roots]
    tested = 0
    for record in records:
        puncture = decode_mask(record["puncture_hex"])
        saved_kernels = record["kernel_by_functional_hex"]
        need(set(saved_kernels) <= {encode_mask(f) for f in functions}, "kernel key domain")
        counts = Counter()
        seen_kernels = {}
        for function in functions:
            live = function - puncture
            gram = [[sum(outer[i][a][b] for i in live) for b in range(8)] for a in range(8)]
            key = encode_mask(function)
            if key in saved_kernels:
                k = saved_kernels[key]
                need(type(k) is int and 0 <= k < 120, "kernel root index")
                normal = roots[k]
                need(all(scalar(roots[i], normal) == 0 for i in live), "claimed kernel annihilates rows")
                drop = next(i for i in range(8) if normal[i])
                kept = [i for i in range(8) if i != drop]
                minor = [[gram[i][j] for j in kept] for i in kept]
                need(bareiss(minor) > 0, "rank-seven Gram minor")
                seen_kernels[key] = k
                counts[7] += 1
            else:
                need(bareiss(gram) > 0, "rank-eight Gram determinant")
                counts[8] += 1
            tested += 1
        need(counts == Counter({8: 483, 7: 28}) and seen_kernels == saved_kernels,
             "complete independently certified rank inventory")
        need(record["rank_counts"] == {str(k): v for k, v in sorted(counts.items())}, "saved rank counts")
        reduced = sorted(set(seen_kernels.values()))
        dims, costs = {}, {}
        for k in reduced:
            rows = sorted(support[k] - puncture)
            dims[str(k)] = dense_binary_rank([[pairing[i][j] for j in indices] for i in rows])
            cols = sorted(support[alpha] - puncture)
            costs[str(k)] = dense_binary_rank([[pairing[i][j] for j in cols] for i in rows])
        need(dims == record["support_dimensions"] and Counter(dims.values()) == Counter({8: 25, 7: 1}),
             "independent support dimensions")
        need(dims[str(alpha)] == 7 and costs == record["distinguished_partner_costs"], "independent term ranks")
        special = [k for k in reduced if scalar(roots[alpha], roots[k]) and costs[str(k)] <= 6]
        need(special == [alpha] and costs[str(alpha)] == 6, "nonparallel lower bound")
        orthogonal = [k for k in reduced if scalar(roots[alpha], roots[k]) == 0]
        need(orthogonal == [record["orthogonal_reduced_root"]], "one reduced orthogonal direction")
        frame = record["attaining_frame"]
        need(len(set(frame)) == 8 and frame[:2] == [alpha, orthogonal[0]], "completion frame")
        need(all(scalar(roots[i], roots[j]) == 0 for i, j in combinations(frame, 2)), "orthogonal completion")
        costs = [dense_binary_rank([[pairing[i][j] for j in sorted(support[k] - puncture)]
                                   for i in sorted(support[k] - puncture)]) for k in frame]
        need(costs == record["attaining_term_costs"] == [6, 7, 9, 9, 9, 9, 9, 9], "sharp completion bill")
    need(tested == certificate["rational_matrices_checked"] == 32193, "complete rational matrix count")
    # Rebuild the entire boundary family by joint (root, cut) reflection closure.
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0),
              (-2, 2, 0, 0, 0, 0, 0, 0)]
    simple += [tuple(2 * ((i == k + 1) - (i == k)) for i in range(8)) for k in range(1, 6)]
    lookup = {r: i for i, r in enumerate(roots)}
    permutations = []
    for s in simple:
        permutation = []
        for r in roots:
            image = tuple(x - scalar(r, s) // 4 * y for x, y in zip(r, s))
            if next(x for x in image if x) < 0:
                image = tuple(-x for x in image)
            permutation.append(lookup[image])
        need(len(set(permutation)) == 120, "independent reflection permutation")
        need(all(pairing[i][j] == pairing[permutation[i]][permutation[j]] and
                 (scalar(roots[i], roots[j]) == 0) ==
                 (scalar(roots[permutation[i]], roots[permutation[j]]) == 0)
                 for i in range(120) for j in range(120)), "independent equivariance")
        permutations.append(permutation)
    seen = {(alpha, p) for p in cuts}
    todo = deque(seen)
    while todo:
        a, p = todo.popleft()
        for permutation in permutations:
            state = (permutation[a], frozenset(permutation[i] for i in p))
            if state not in seen:
                seen.add(state)
                todo.append(state)
    all_cuts = {p for _, p in seen}
    need(len(seen) == len(all_cuts) == certificate["distinct_boundary_cuts"] == 7560, "global boundary closure")
    need(Counter(a for a, _ in seen) == Counter({i: 63 for i in range(120)}), "all-root boundary coverage")
    encoded = json.dumps(sorted(encode_mask(p) for p in all_cuts), sort_keys=True, separators=(",", ":"))
    need(hashlib.sha256(encoded.encode()).hexdigest() == certificate["all_boundary_cuts_sha256"], "global cut digest")
    need(check_witness(certificate["witness67"], roots, pairing) == [6, 7, 9, 9, 9, 9, 9, 9], "67 witness")
    need(check_witness(certificate["witness56"], roots, pairing) == [7] * 8, "56 witness")
    previous = certificate["predecessor_nonparallel_witness"]
    a, b = previous["pair"]
    p = set(previous["puncture"])
    need(a != b and scalar(roots[a], roots[b]) != 0 and len(p) == 26, "26 witness scope")
    need(dense_binary_rank([[pairing[i][j] for j in sorted(support[b] - p)]
                            for i in sorted(support[a] - p)]) == 6, "26 witness cost")
    return tested


def main():
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    tested = check(certificate)
    print(f"PASS_GENERAL_NORMAL_GRAM_CHECK matrices={tested} boundary_cuts=7560 witness_entries=18050")


if __name__ == "__main__":
    main()
