#!/usr/bin/env python3
"""Check affine supports without the producer code."""

import hashlib
import itertools
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
PRODUCER = LANES / "portable-source-codes/correlated-access-20261015"
PINS = {
    "ACCESS.md": "a5a91cdc4deed08aa15693aedbcc01f48186859f8902acdb864aa74fb6feba4d",
    "ACCESS.json": "5d4cbe5c3f3ff18e215828c0ec1575c9cb5f253217ed73bbd0c57f4678fdd057",
    "check_access.py": "7475320ad213bd0cd9ab93042ae9836f489286cc1438be0b3604a21744d8211a",
}


def check(value, name):
    if not value:
        raise ValueError(name)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p in pivots:
                row ^= pivots[p]
            else:
                pivots[p] = row
                break
    return len(pivots)


def linear_space(basis):
    result = [0]
    for row in basis:
        result += [value ^ row for value in result]
    return result


def subspaces(dimension):
    for size in range(dimension + 1):
        for pivots in itertools.combinations(range(dimension), size):
            free = [(i, j) for i, p in enumerate(pivots)
                    for j in range(p + 1, dimension) if j not in pivots]
            for mask in range(1 << len(free)):
                basis = [1 << p for p in pivots]
                for bit, (i, j) in enumerate(free):
                    basis[i] |= ((mask >> bit) & 1) << j
                yield basis


def rows(value, n, width):
    mask = (1 << width) - 1
    return [(value >> (i * width)) & mask for i in range(n)]


def phase(value, n, width):
    parts = rows(value, n, width)
    residues = set()
    for q in range(1, 1 << n):
        if q.bit_count() % 2:
            result = 0
            for i in range(n):
                if (q >> i) & 1:
                    result ^= parts[i]
            residues.add(result.bit_count() % 4)
    return next(iter(residues)) if len(residues) == 1 else None


def radical_check(basis, n, width):
    size = len(basis)
    projections = [[rows(v, n, width)[i] for v in basis] for i in range(n)]
    grams = [[sum((((a & b).bit_count() & 1) << j)
                  for j, b in enumerate(projected)) for a in projected]
             for projected in projections]
    check(all(gram == grams[0] for gram in grams), "common pulled-back form")
    common = grams[0]
    r = rank(common)
    kernel = [v for v in range(1 << size)
              if all((row & v).bit_count() % 2 == 0 for row in common)]
    s = []
    for projected in projections:
        image = []
        for v in kernel:
            result = 0
            for j, p in enumerate(projected):
                if (v >> j) & 1:
                    result ^= p
            image.append(result)
        s_i = rank(image)
        s.append(s_i)
        check(r + 2 * s_i <= width, "ambient radical bound")
        check(rank(projected) == r + s_i, "radical image dimension")
    check(size <= r + sum(s), "joint radical injection")
    check(size <= r + n * ((width - r) // 2), "common-rank inequality")


def exhaustive(n, width):
    ambient = n * width
    values = [phase(x, n, width) for x in range(1 << ambient)]
    tested = accepted = fixed = 0
    maximum = fixed_maximum = 0
    directions = 0
    for basis in subspaces(ambient):
        directions += 1
        space = linear_space(basis)
        seen = set()
        checked_radical = False
        for offset in range(1 << ambient):
            if offset in seen:
                continue
            coset = [offset ^ x for x in space]
            seen.update(coset)
            tested += 1
            if any(values[x] is None for x in coset):
                continue
            accepted += 1
            maximum = max(maximum, len(basis))
            check(len(basis) <= n * (width // 2) + width % 2, "affine bound")
            if not checked_radical:
                radical_check(basis, n, width)
                checked_radical = True
            if len({values[x] for x in coset}) == 1:
                fixed += 1
                fixed_maximum = max(fixed_maximum, len(basis))
                check(len(basis) <= n * (width // 2), "fixed-phase bound")
    return {"n": n, "width": width, "linear_directions": directions,
            "affine_sets": tested, "contained_sets": accepted,
            "fixed_phase_sets": fixed, "maximum_dimension": maximum,
            "fixed_phase_maximum_dimension": fixed_maximum}


def equality(n, width):
    half = width // 2
    basis = [(1 << (i * width + j)) | (1 << (i * width + half + j))
             for i in range(n) for j in range(half)]
    offset = sum(((1 << half) - 1) << (i * width) for i in range(n))
    check(rank(basis) == n * half, "fixed equality dimension")
    fixed_values = [phase(offset ^ x, n, width) for x in linear_space(basis)]
    check(set(fixed_values) == {half % 4}, "fixed equality phase")
    if width % 2:
        basis.append(sum(1 << (i * width + width - 1) for i in range(n)))
    check(rank(basis) == n * half + width % 2, "equality dimension")
    values = [phase(offset ^ x, n, width) for x in linear_space(basis)]
    check(None not in values, "all equality points")
    radical_check(basis, n, width)
    return {"n": n, "width": width, "dimension": len(basis),
            "phase_residues": sorted(set(values)), "points": len(values)}


def main():
    for name, expected in PINS.items():
        check(hashlib.sha256((PRODUCER / name).read_bytes()).hexdigest() == expected, name)
    small = [exhaustive(n, width) for n, width in ((2, 1), (3, 1), (2, 2), (2, 3), (3, 2))]
    examples = [equality(n, width) for n in (2, 3, 4) for width in range(1, 7)]
    for n in range(2, 17):
        for width in range(33):
            check(max(r + n * ((width - r) // 2) for r in range(width + 1))
                  == n * (width // 2) + width % 2, "rank maximization")
    receipt = {
        "status": "PASS_INDEPENDENT_AFFINE_SECTOR",
        "producer_pins": PINS, "all_affine_cases": small,
        "equality_examples": examples,
        "n73_width152_affine_cover_log2_lower_bound": 73 * 76 - 2700,
        "scope": "Finite checks support the separate general proof review. No producer code was imported or run. Stream admission is separate.",
    }
    (HERE / "REVIEW.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
