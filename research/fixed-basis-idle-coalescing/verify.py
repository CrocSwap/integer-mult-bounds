#!/usr/bin/env python3
"""Corroborate support matching and degree-preserving idle allocation."""

from hashlib import sha256
from itertools import permutations, product
from pathlib import Path
import json


def need(condition, message):
    if not condition:
        raise ValueError(message)


def validate(columns, prime):
    need(prime in (2, 3), "finite checker supports F2 and F3")
    n = len(columns)
    need(1 <= n <= 4, "checker dimension must be between one and four")
    need(all(len(v) == n for v in columns), "square column matrix required")
    need(all(type(x) is int and 0 <= x < prime for v in columns for x in v),
         "canonical field entries required")
    return n


def rank(columns, prime):
    n = len(columns)
    rows = [list(row) for row in zip(*columns)]
    pivot = 0
    for col in range(n):
        found = next((r for r in range(pivot, n) if rows[r][col]), None)
        if found is None:
            continue
        rows[pivot], rows[found] = rows[found], rows[pivot]
        inv = pow(rows[pivot][col], -1, prime)
        rows[pivot] = [x * inv % prime for x in rows[pivot]]
        for r in range(pivot + 1, n):
            coefficient = rows[r][col]
            rows[r] = [(a - coefficient * b) % prime
                       for a, b in zip(rows[r], rows[pivot])]
        pivot += 1
    return pivot


def support_matching(columns, prime):
    """Bounded augmenting paths; map each column to a nonzero support row."""
    n = validate(columns, prime)
    need(rank(columns, prime) == n, "directions must form a basis")
    owner = [-1] * n
    for start in range(n):
        queue = [start]
        seen = {start}
        parent = [-1] * n
        endpoint = None
        for position in range(n):
            if position == len(queue) or endpoint is not None:
                break
            col = queue[position]
            for row in range(n):
                if not columns[col][row] or parent[row] != -1:
                    continue
                parent[row] = col
                if owner[row] == -1:
                    endpoint = row
                    break
                if owner[row] not in seen:
                    seen.add(owner[row])
                    queue.append(owner[row])
        need(endpoint is not None, "basis has no support matching")
        row = endpoint
        for _ in range(n):
            col = parent[row]
            previous = next((r for r in range(n) if owner[r] == col), -1)
            owner[row] = col
            if previous == -1:
                break
            row = previous
        else:
            raise ValueError("augmenting path exceeds dimension")
    return tuple(owner.index(col) for col in range(n))


def check_basis(columns, prime):
    n = len(columns)
    matching = support_matching(columns, prime)
    oracle = [perm for perm in permutations(range(n))
              if all(columns[j][perm[j]] for j in range(n))]
    need(matching in oracle, "matching disagrees with determinant support")
    supports = [sum(1 << i for i, x in enumerate(v) if x) for v in columns]
    checks = 0
    for mask in range(1 << n):
        eligible = sum(1 << j for j, s in enumerate(supports) if s & ~mask == 0)
        for subset in range(1 << n):
            if subset & ~eligible:
                continue
            mapped = sum(1 << matching[j] for j in range(n) if subset >> j & 1)
            need(mapped & ~mask == 0, "mapped idle direction leaves stage mask")
            need(mapped.bit_count() == subset.bit_count(), "idle count changed")
            checks += 1
    return checks


def census(n, prime):
    vectors = tuple(product(range(prime), repeat=n))
    matrices = bases = stage_checks = 0
    for columns in product(vectors, repeat=n):
        matrices += 1
        if rank(columns, prime) != n:
            continue
        bases += 1
        stage_checks += check_basis(columns, prime)
    expected_bases = 1
    for i in range(n):
        expected_bases *= prime ** n - prime ** i
    need(matrices == prime ** (n * n), "matrix enumeration is incomplete")
    need(bases == expected_bases, "basis enumeration disagrees with GL order")
    return {"field": prime, "dimension": n, "matrices": matrices,
            "bases": bases, "stage_subset_checks": stage_checks}


def controls():
    invalid = [(((1, 0), (1, 0)), 2), (((1, 0),), 2),
               (((1, 0), (0, 1)), 5), (((2, 0), (0, 1)), 2),
               (((True, 0), (0, 1)), 2), ((), 2)]
    rejected = 0
    for columns, prime in invalid:
        try:
            support_matching(columns, prime)
        except ValueError:
            rejected += 1
    need(rejected == len(invalid), "malformed input accepted")
    # Three dependent directions cannot have distinct coordinate anchors in F2^2.
    supports = (1, 2, 3)
    need(not any(all(supports[j] >> rows[j] & 1 for j in range(3))
                 for rows in permutations(range(2), 3)), "dependent boundary")
    # An injective assignment must also use nonzero entries.
    columns = ((1, 0), (1, 1))
    need(not columns[0][1], "wrong-support control must leave a singleton mask")
    return {"rejections": rejected, "boundary_controls": 2}


def schedule_fixture():
    columns = ((1, 0, 0), (1, 1, 0), (0, 1, 1))
    matching = support_matching(columns, 2)
    masks = (1, 3, 7, 6, 7)
    idles = ((0,), (0, 1), (1, 2), (2,), (0, 2))
    mapped = tuple(tuple(matching[j] for j in stage) for stage in idles)
    for mask, stage, coordinates in zip(masks, idles, mapped):
        need(all(all(not x or mask >> i & 1 for i, x in enumerate(columns[j]))
                 for j in stage), "fixture has an ineligible direction")
        need(all(mask >> i & 1 for i in coordinates), "fixture translation failed")
    degrees = tuple(sum(j in stage for stage in idles) for j in range(3))
    translated = tuple(sum(matching[j] in stage for stage in mapped) for j in range(3))
    need(degrees == translated == (3, 2, 3), "chronological degrees changed")
    return {"matching": matching, "degrees": degrees, "stages": len(masks)}


def main():
    results = [census(n, p) for p, top in ((2, 4), (3, 3))
               for n in range(1, top + 1)]
    fixture = schedule_fixture()
    checked_controls = controls()
    directory = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = directory / name
        need(path.stat().st_size <= 131072, "package file exceeds receipt read cap")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    receipt = {"status": "PASS_FIXED_BASIS_IDLE_COALESCING", "censuses": results,
               "schedule": fixture, "controls": checked_controls, "sha256": hashes,
               "scope": "finite corroboration; universal theorem is in PROOF.md"}
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
