#!/usr/bin/env python3
"""Sharp support twelve for rational trace-zero E7 quadratics. Exact integers."""

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import platform


PIVOT = (2, 0, 0, 0, 2, 0, 0, 0)
DIAGONAL = (1, 1, 1, 1, -1, -1, -1, -1)
N = 63
DIMENSION = 27


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    require(len(left) == len(right) == 8, "eight coordinates required")
    return sum(left[i] * right[i] for i in range(8))


def e8_lines():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.append(tuple(root))
    for tail in itertools.product((-1, 1), repeat=7):
        root = (1,) + tail
        if root.count(-1) % 2 == 0:
            roots.append(root)
    require(len(roots) == len(set(roots)) == 120, "E8 line count")
    require(all(dot(root, root) == 8 for root in roots), "E8 norms")
    return tuple(sorted(roots))


def intrinsic_e7():
    roots = []
    for i, j in itertools.combinations((1, 2, 3, 5, 6, 7), 2):
        for sign in (-1, 1):
            root = [0] * 8
            root[i], root[j] = 2, 2 * sign
            roots.append(tuple(root))
    roots.append((2, 0, 0, 0, -2, 0, 0, 0))
    for signs in itertools.product((-1, 1), repeat=6):
        if signs.count(-1) % 2 == 1:
            roots.append((1,) + signs[:3] + (-1,) + signs[3:])
    return tuple(sorted(roots))


def validate_domain(roots):
    require(len(roots) == len(set(roots)) == N, "63 distinct root lines")
    require(tuple(sorted(roots)) == intrinsic_e7(), "intrinsic E7 agreement")
    require(all(dot(PIVOT, root) == 0 for root in roots), "orthogonal slice")


def root_transport(root, generator):
    out = list(root)
    if generator < 7:
        out[generator], out[generator + 1] = out[generator + 1], out[generator]
    elif generator == 7:
        out[0], out[1] = -out[0], -out[1]
    else:
        require(generator == 8, "nine fixed orthogonal generators")
        normal = (1, -1, -1, -1, 1, -1, -1, -1)
        inner = dot(root, normal)
        require(inner % 4 == 0, "integral E8 reflection")
        out = [root[i] - inner // 4 * normal[i] for i in range(8)]
    first = next(value for value in out if value)
    return tuple(value if first > 0 else -value for value in out)


def check_root_transitivity():
    domain = set(e8_lines())
    for generator, root in itertools.product(range(9), domain):
        require(root_transport(root, generator) in domain, "root-set automorphism")
    orbit = {PIVOT}
    stack = [PIVOT]
    for _ in range(120):
        if not stack:
            break
        root = stack.pop()
        for generator in range(9):
            image = root_transport(root, generator)
            if image not in orbit:
                orbit.add(image)
                stack.append(image)
    require(not stack and orbit == domain, "all 120 root lines reached")
    return len(orbit)


def orthogonal_frames(roots):
    adjacency = [{j for j in range(N) if j != i and dot(roots[i], roots[j]) == 0}
                 for i in range(N)]
    frames = []
    stack = [((), tuple(range(N)))]
    # Each state is an increasing orthogonal subset; 100000 is a fail-closed cap.
    for _ in range(100000):
        if not stack:
            break
        frame, candidates = stack.pop()
        if len(frame) == 7:
            frames.append(frame)
            continue
        for offset, j in enumerate(candidates):
            tail = tuple(k for k in candidates[offset + 1:] if k in adjacency[j])
            if len(tail) >= 6 - len(frame):
                stack.append((frame + (j,), tail))
    else:
        raise ValueError("frame enumeration exceeded its state cap")
    require(len(frames) == len(set(frames)) == 135, "135 complete frames")
    for frame in frames:
        require(len(frame) == 7 and all(j in adjacency[i] for i, j in
                itertools.combinations(frame, 2)), "orthogonal frame")
    return tuple(sorted(frames))


def binary_kernel(rows):
    echelon = {}
    for row in rows:
        for pivot in range(N - 1, -1, -1):
            if row >> pivot & 1:
                if pivot in echelon:
                    row ^= echelon[pivot]
                else:
                    echelon[pivot] = row
                    break
    free = tuple(j for j in range(N) if j not in echelon)
    basis = []
    for j in free:
        vector = 1 << j
        for pivot in sorted(echelon):
            if (echelon[pivot] & vector).bit_count() % 2:
                vector |= 1 << pivot
        basis.append(vector)
    require(len(echelon) == 36 and len(free) == DIMENSION, "binary rank 36")
    validate_basis(rows, basis, free)
    return tuple(basis), free


def validate_basis(rows, basis, free):
    require(len(basis) == len(free) == DIMENSION, "complete kernel dimension")
    require(len(set(free)) == DIMENSION, "distinct free coordinates")
    for index, vector in enumerate(basis):
        require(0 < vector < 1 << N, "bounded nonzero kernel vector")
        require(all((vector & row).bit_count() % 2 == 0 for row in rows),
                "every frame parity vanishes")
        require(tuple(vector >> j & 1 for j in free) ==
                tuple(int(k == index) for k in range(DIMENSION)),
                "identity on free coordinates proves independence")


def full_weight_census(basis):
    word = 0
    minimum = N
    visited = 0
    for index in range(1, 1 << DIMENSION):
        word ^= basis[(index & -index).bit_length() - 1]
        weight = word.bit_count()
        require(weight != 0, "independent basis cannot revisit zero")
        if weight < minimum:
            minimum = weight
        visited += 1
    require(visited == 134217727, "every nonzero binary kernel vector visited")
    require(minimum == 12, "binary frame code has minimum weight twelve")
    return visited, minimum


def check_witness(roots, frames):
    values = tuple(sum(DIAGONAL[i] * root[i] ** 2 for i in range(8))
                   for root in roots)
    require(sum(DIAGONAL) == 0, "ambient quadratic has trace zero")
    require(sum(DIAGONAL[i] * PIVOT[i] ** 2 for i in range(8)) == 0,
            "pivot diagonal entry vanishes, so restricted trace is zero")
    require(Counter(values) == {0: 51, 8: 6, -8: 6}, "twelve-line attainer")
    require(all(sum(values[j] for j in frame) == 0 for frame in frames),
            "literal rational frame sums vanish")
    # Odd-parity six-sign rows span all six remaining coordinates. Together
    # with coordinate +/- pairs and e0-e4, this proves quadratic injectivity.
    signs = [tuple(root[j] for j in (1, 2, 3, 5, 6, 7))
             for root in roots if root[0] == 1]
    require(len(signs) == 32, "all odd-parity sign rows")
    for i, j in itertools.product(range(6), repeat=2):
        require(sum(row[i] * row[j] for row in signs) == 32 * int(i == j),
                "sign-row Gram identity")
    return values


def rejection_controls(roots, rows, basis, free):
    rejected = 0
    for j in range(N):
        try:
            validate_domain(roots[:j] + roots[j + 1:])
        except ValueError:
            rejected += 1
        else:
            raise ValueError("incomplete root domain accepted")
    for j in range(DIMENSION):
        changed = list(basis)
        changed[j] ^= 1
        try:
            validate_basis(rows, changed, free)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("non-kernel basis accepted")
    for changed in (basis[:-1], basis + (basis[0],)):
        try:
            validate_basis(rows, changed, free)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("wrong kernel dimension accepted")
    require(rejected == 92, "all 92 omission and basis controls executed")
    return rejected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write generated receipt outside package")
    args = parser.parse_args()
    orbit_size = check_root_transitivity()
    roots = tuple(root for root in e8_lines() if dot(root, PIVOT) == 0)
    validate_domain(roots)
    frames = orthogonal_frames(roots)
    rows = tuple(sum(1 << j for j in frame) for frame in frames)
    basis, free = binary_kernel(rows)
    values = check_witness(roots, frames)
    controls = rejection_controls(roots, rows, basis, free)
    visited, minimum = full_weight_census(basis)
    package = Path(__file__).resolve().parent
    files = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    receipt = {
        "status": "PASS_E7_TRACE_ZERO_SUPPORT", "e7_lines": len(roots),
        "pivot_orbit": orbit_size,
        "frames": len(frames), "binary_rank": N - len(basis),
        "binary_kernel_dimension": len(basis), "nonzero_codewords": visited,
        "minimum_binary_weight": minimum, "quadratic_support": sum(v != 0 for v in values),
        "positive_values": sum(v > 0 for v in values),
        "negative_values": sum(v < 0 for v in values), "rejecting_controls": controls,
        "python": platform.python_version(),
        "source_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                          for name in files},
    }
    serialized = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt is not None:
        require(not args.receipt.resolve().is_relative_to(package),
                "receipt must be outside the source package")
        args.receipt.write_text(serialized, encoding="utf-8")
    print(serialized, end="")


if __name__ == "__main__":
    main()
