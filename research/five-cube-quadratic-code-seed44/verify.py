#!/usr/bin/env python3
"""Exact finite certificate for quadratic-augmented five-cube parity codes.

Hanson Sun (@bbMisk), with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor implementation is imported.
"""

import argparse
from collections import Counter
from functools import reduce
import hashlib
from heapq import heappop, heappush
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FULL = (1 << 32) - 1
PARITY = sum((x.bit_count() % 2) << x for x in range(32))
MONOMIALS = [(i,) for i in range(4)] + list(combinations(range(5), 2))
TARGET = (1 << 0) | (1 << 4)  # E E^t + O O^t, in basis (E,O,h).
INFINITY = 10**6  # Above 511 edges times the maximum possible rank 32.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def check_sources():
    raw = (HERE / "SOURCES.json").read_bytes()
    manifest = json.loads(raw)
    for record in manifest["retained_files"]:
        path = HERE / record["local_path"]
        require(path.resolve().is_relative_to(HERE), "source path escapes package")
        data = path.read_bytes()
        require(hashlib.sha256(data).hexdigest() == record["sha256"],
                "source SHA256 mismatch: " + record["local_path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == record["git_blob_sha1"],
                "source Git blob mismatch: " + record["local_path"])
    return hashlib.sha256(raw).hexdigest()


def gram_matrix():
    return [[2 * (4 - (x ^ y).bit_count()) * (2 - (x ^ y).bit_count())
             for y in range(32)] for x in range(32)]


def canonical_mask(mask):
    # Unique representative modulo <1,p>: constant and x4 coefficient zero.
    if mask & 1:
        mask ^= FULL
    if (mask >> 16) & 1:
        mask ^= PARITY
    return mask


def code_masks():
    monomials = [sum(int(all((x >> i) & 1 for i in term)) << x
                     for x in range(32)) for term in MONOMIALS]
    masks = [0] * (1 << 14)
    for c in range(1, len(masks)):
        low = c & -c
        masks[c] = masks[c ^ low] ^ monomials[low.bit_length() - 1]
    require(len(set(masks)) == 1 << 14, "quadratic quotient is not injective")
    return masks


def cube_generators():
    # Pullbacks x -> x+e_i, then x_i <-> x_(i+1).
    generators = [[x ^ (1 << i) for x in range(32)] for i in range(5)]
    for i in range(4):
        generators.append([
            x ^ (((x >> i ^ x >> (i + 1)) & 1) * ((1 << i) | (1 << (i + 1))))
            for x in range(32)
        ])
    return generators


def permute_mask(mask, permutation):
    return sum(((mask >> x) & 1) << y for y, x in enumerate(permutation))


def orbit_certificate(masks):
    lookup = {mask: c for c, mask in enumerate(masks)}
    remaining = set(range(1, len(masks)))
    records, orbits = [], []
    generators = cube_generators()
    while remaining:
        representative = min(remaining)
        queue = [representative]
        remaining.remove(representative)
        records.append([representative, 0, -1, representative])
        for parent in queue:
            for index, permutation in enumerate(generators):
                image = canonical_mask(permute_mask(masks[parent], permutation))
                child = lookup[image]
                if child in remaining:
                    remaining.remove(child)
                    queue.append(child)
                    records.append([child, parent, index, representative])
        orbits.append((representative, len(queue)))
    require(len(records) == 16383 and len(orbits) == 64, "orbit coverage changed")
    return orbits, records


def rational_rank(rows):
    """Integer row elimination; gcd normalization preserves rational row span."""
    matrix = [list(row) for row in rows]
    if not matrix:
        return 0
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        for i in range(rank + 1, len(matrix)):
            entry = matrix[i][column]
            if entry:
                common = gcd(matrix[rank][column], entry)
                left, right = matrix[rank][column] // common, entry // common
                matrix[i] = [left * x - right * y
                             for x, y in zip(matrix[i], matrix[rank])]
                divisor = reduce(gcd, matrix[i], 0)
                if divisor:
                    matrix[i] = [x // divisor for x in matrix[i]]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def factor_masks(mask):
    basis = [FULL ^ PARITY, PARITY, mask]
    return [reduce(int.__xor__, (basis[i] for i in range(3) if c >> i & 1), 0)
            for c in range(8)]


def term_ranks(mask, gram):
    functions = factor_masks(mask)
    supports = [[x for x in range(32) if f >> x & 1] for f in functions]
    weights = [[0] * 7 for _ in range(7)]
    for a in range(1, 8):
        for b in range(a, 8):
            cost = rational_rank([[gram[x][y] for y in supports[b]] for x in supports[a]])
            weights[a - 1][b - 1] = weights[b - 1][a - 1] = cost
    return weights


def dyad(a, b):
    return sum(((a >> i & 1) & (b >> j & 1)) << (3 * i + j)
               for i in range(3) for j in range(3))


def shortest_paths(weights, rank_cap):
    terms = [(dyad(a, b), weights[a - 1][b - 1], a, b)
             for a in range(1, 8) for b in range(1, 8)
             if weights[a - 1][b - 1] <= rank_cap]
    distance = [INFINITY] * 512
    predecessor = {}
    distance[0] = 0
    heap = [(0, 0)]
    while heap:
        cost, state = heappop(heap)
        if cost != distance[state]:
            continue
        for step, weight, a, b in terms:
            target = state ^ step
            if cost + weight < distance[target]:
                distance[target] = cost + weight
                predecessor[target] = (state, a, b)
                heappush(heap, (cost + weight, target))
    word = []
    if distance[TARGET] != INFINITY:
        state = TARGET
        while state:
            state, a, b = predecessor[state]
            word.append([a, b])
        word.reverse()
    return {
        "rank_cap": rank_cap,
        "minimum": None if distance[TARGET] == INFINITY else distance[TARGET],
        "potential": [None if d == INFINITY else d for d in distance],
        "word": word,
    }


def validate_graph_certificate(weights, receipt):
    cap, potential = receipt["rank_cap"], receipt["potential"]
    require(len(potential) == 512 and potential[0] == 0, "invalid potential origin/size")
    require(all(d is None or type(d) is int and 0 <= d < INFINITY for d in potential),
            "invalid potential value")
    for state, distance in enumerate(potential):
        if distance is None:
            continue
        for a in range(1, 8):
            for b in range(1, 8):
                cost = weights[a - 1][b - 1]
                if cost <= cap:
                    other = potential[state ^ dyad(a, b)]
                    require(other is not None and other <= distance + cost,
                            "potential violates transition/closed reachability")
    require(potential[TARGET] == receipt["minimum"], "wrong target potential")
    if receipt["minimum"] is None:
        require(not receipt["word"], "unreachable target has a word")
        return
    state, cost = 0, 0
    for a, b in receipt["word"]:
        require(type(a) is int and type(b) is int and 1 <= a <= 7 and 1 <= b <= 7,
                "invalid word factor")
        weight = weights[a - 1][b - 1]
        require(weight <= cap, "word exceeds rank cap")
        state ^= dyad(a, b)
        cost += weight
    require(state == TARGET and cost == receipt["minimum"], "invalid attaining word")


def compute_certificate():
    source_hash = check_sources()
    gram = gram_matrix()
    require(rational_rank(gram) == 16, "wrong five-cube Gram")
    masks = code_masks()
    orbits, transports = orbit_certificate(masks)
    results = []
    capped_histogram = Counter()
    for representative, size in orbits:
        weights = term_ranks(masks[representative], gram)
        unrestricted = shortest_paths(weights, 32)
        capped = shortest_paths(weights, 15)
        validate_graph_certificate(weights, unrestricted)
        validate_graph_certificate(weights, capped)
        require(unrestricted["minimum"] == 32, "quadratic copy floor changed")
        nonlinear = representative >= 16
        require(not nonlinear or capped["minimum"] is None or capped["minimum"] >= 34,
                "nonlinear peak-rank gap changed")
        key = "unreachable" if capped["minimum"] is None else str(capped["minimum"])
        capped_histogram[key] += size
        results.append({
            "representative": representative, "mask": masks[representative],
            "orbit_size": size, "nonlinear": nonlinear, "ranks": weights,
            "unrestricted": unrestricted, "rank15": capped,
        })
    return {
        "schema": "five-cube-quadratic-code-v1",
        "source_manifest_sha256": source_hash,
        "basis": ["even", "odd", "h"],
        "quotient_monomials": [list(m) for m in MONOMIALS],
        "target_coefficient_matrix_bits": TARGET,
        "transport_columns": ["child", "parent", "generator", "representative"],
        "transports": transports,
        "orbits": results,
        "summary": {
            "quadratic_quotient_codes": 16383, "nonlinear_codes": 16368,
            "orbit_count": 64, "nonlinear_orbits": 62,
            "ordered_term_ranks": 64 * 49, "coefficient_states_per_code": 512,
            "unrestricted_transition_checks": 64 * 512 * 49,
            "minimum_copy_rank_sum": 32,
            "nonlinear_minimum_with_rank_cap15": 34,
            "rank15_minimum_histogram_weighted_by_codes": dict(sorted(capped_histogram.items())),
            "finite_rank34_attaining_codes": capped_histogram["34"],
            "no_new_kappa": True,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write regenerated certificate to a new path")
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    args = parser.parse_args()
    result = compute_certificate()
    encoded = canonical_bytes(result)
    if args.write:
        with args.write.open("xb") as stream:
            stream.write(encoded)
    else:
        require(args.certificate.read_bytes() == encoded, "certificate differs from exact regeneration")
    print("PASS_FIVE_CUBE_QUADRATIC_CODES codes=16383 orbits=64 ranks=3136 "
          "copy_floor=32 nonlinear_rank15_floor=34 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print("FAIL_FIVE_CUBE_QUADRATIC_CODES: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
