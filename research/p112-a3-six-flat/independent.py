#!/usr/bin/env python3
"""Independent finite audit for the A3/six-flat obstruction.

E8/P112 labels follow Nick Petalas's PR3161/PR3162 convention, retained in
SOURCES.json. This checker independently enumerates lattice vectors, solves
simple coordinates by back substitution, enumerates affine five-flats rather
than annihilator three-spaces, and computes binary closure by explicit spans.
It imports neither geometry.py nor the primary checker. Standard library only.

Power-of-Ten managed-runtime deviation: Python allocates during enumeration;
all domains have fixed capacities (256 affine points, 120 root lines, 788035
six-spaces, 2025 frames, 20 maximizing flats). No user-controlled search size.
"""

import argparse
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def lattice_roots():
    """Doubled E8: uniform coordinate parity, norm 8, sum divisible by 4."""
    roots = []
    for alphabet in ((-2, 0, 2), (-1, 1)):
        for row in product(alphabet, repeat=8):
            if sum(x * x for x in row) == 8 and sum(row) % 4 == 0:
                if row > tuple(-x for x in row):
                    roots.append(row)
    require(len(roots) == len(set(roots)) == 120, "root-line census")
    return tuple(sorted(roots))


def simple_label(row):
    """Back substitution for the retained doubled simple-root convention."""
    coefficients = [0] * 8
    coefficients[0] = row[7]
    for i in range(7, 2, -1):
        numerator = row[i - 1] + coefficients[0]
        if i < 7:
            numerator += 2 * coefficients[i + 1]
        require(numerator % 2 == 0, "nonintegral chain coordinate")
        coefficients[i] = numerator // 2
    numerator = row[0] + row[1] + 2 * coefficients[3]
    require(numerator % 4 == 0, "nonintegral fork coordinate")
    coefficients[1] = numerator // 4
    numerator = coefficients[0] + 2 * coefficients[1] - row[0]
    require(numerator % 2 == 0, "nonintegral remaining coordinate")
    coefficients[2] = numerator // 2
    simple = ((1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0),
              (-2, 2, 0, 0, 0, 0, 0, 0), (0, -2, 2, 0, 0, 0, 0, 0),
              (0, 0, -2, 2, 0, 0, 0, 0), (0, 0, 0, -2, 2, 0, 0, 0),
              (0, 0, 0, 0, -2, 2, 0, 0), (0, 0, 0, 0, 0, -2, 2, 0))
    require(tuple(sum(coefficients[j] * simple[j][i] for j in range(8))
                  for i in range(8)) == row, "coordinate reconstruction")
    return 1 | sum((x % 2) << (i + 1) for i, x in enumerate(coefficients))


def coordinate_costs(roots):
    values, costs = [], []
    for row in roots:
        require(all((row[0] + row[j]) % 2 == 0 for j in range(1, 4)),
                "nonintegral A3 values")
        value = (0,) + tuple((row[0] + row[j]) // 2 for j in range(1, 4))
        values.append(value)
        costs.append(4 - max(Counter(value).values()))
    require(Counter(costs) == {0: 20, 1: 64, 2: 36}, "A3 cost spectrum")
    return tuple(values), tuple(costs)


def binary_span(generators):
    """Explicit subset sums; no elimination is shared with the main checker."""
    require(len(generators) <= 9, "span generator capacity")
    members = {0}
    for row in generators:
        require(type(row) is int and 0 <= row < 512, "binary vector range")
        members.update(tuple(x ^ row for x in members))
    require(len(members) <= 512, "span capacity")
    return members


def independent_basis(vectors):
    """Greedily enlarge an explicitly materialized span, without row reduction."""
    basis, members = [], {0}
    require(len(vectors) <= 120, "root subset capacity")
    for row in vectors:
        if row not in members:
            require(len(basis) < 9, "binary rank capacity")
            basis.append(row)
            members.update(tuple(x ^ row for x in members))
    return basis, members


def rref_direction_options(pivots):
    options = []
    for pivot in pivots:
        free = tuple(i for i in range(pivot) if i not in pivots)
        rows = tuple((1 << pivot) | sum(((code >> j) & 1) << col
                                      for j, col in enumerate(free))
                     for code in range(1 << len(free)))
        options.append(rows)
    return options


def affine_flat_census(labels, costs):
    """Each six-space meeting odd vectors gives one affine five-flat in F2^8."""
    root_by_point = {label >> 1: i for i, label in enumerate(labels)}
    occupancy, weights = Counter(), Counter()
    maxima = []
    direction_count = 0
    for pivots in combinations(range(8), 5):
        nonpivots = tuple(i for i in range(8) if i not in pivots)
        offsets = tuple(sum(((code >> j) & 1) << col
                            for j, col in enumerate(nonpivots)) for code in range(8))
        for basis in product(*rref_direction_options(pivots)):
            direction_count += 1
            members = tuple(sorted(binary_span(basis)))
            require(len(members) == 32, "five-direction dimension")
            for offset in offsets:
                indices = tuple(root_by_point[x ^ offset] for x in members
                                if x ^ offset in root_by_point)
                weight = sum(costs[i] for i in indices)
                occupancy[len(indices)] += 1
                weights[weight] += 1
                if weight == 36:
                    maxima.append(tuple(sorted(indices)))
                    require(len(maxima) <= 20, "maximizing-flat storage capacity")
    # A six-space contained in the even hyperplane contains no root labels.
    even_only = 10795  # Gaussian binomial [8 choose 6]_2 = [8 choose 2]_2.
    require(even_only == ((256 - 1) * (256 - 2)) // ((4 - 1) * (4 - 2)),
            "even-hyperplane six-space count")
    occupancy[0] += even_only
    weights[0] += even_only
    require(direction_count == 97155, "five-direction census")
    require(sum(occupancy.values()) == 788035, "six-space census")
    require(max(occupancy) == 20, "six-space root capacity")
    require(max(weights) == 36 and weights[36] == 20, "weighted flat maximum")
    require(max(x for x in weights if x != 36) == 32, "weighted runner-up")
    require(len(maxima) == len(set(maxima)) == 20, "distinct maximizing subsets")
    return sorted(maxima), dict(sorted(occupancy.items())), dict(sorted(weights.items()))


def orthogonal_frames(roots):
    adjacency = tuple(sum(1 << j for j in range(i + 1, 120)
                          if dot(roots[i], roots[j]) == 0) for i in range(120))
    stack, frames = [((), (1 << 120) - 1)], []
    for _ in range(2000000):
        if not stack:
            break
        chosen, candidates = stack.pop()
        for _ in range(120):
            if not candidates:
                break
            bit = candidates & -candidates
            candidates ^= bit
            index = bit.bit_length() - 1
            extended = chosen + (index,)
            if len(extended) == 8:
                frames.append(extended)
            else:
                remaining = candidates & adjacency[index]
                if remaining.bit_count() >= 8 - len(extended):
                    stack.append((extended, remaining))
        require(len(stack) <= 960 and len(frames) <= 2025, "frame storage capacity")
    else:
        raise ValueError("frame traversal node limit")
    require(len(frames) == len(set(frames)) == 2025, "orthogonal frame census")
    return tuple(sorted(frames))


def singleton_sets(values, costs, removed):
    endpoints = [set() for _ in range(4)]
    for i in range(120):
        if i not in removed and costs[i] == 1:
            frequencies = Counter(values[i])
            modes = tuple(x for x, count in frequencies.items() if count == 3)
            require(len(modes) == 1, "singleton modal multiplicity")
            exceptional = tuple(j for j in range(4) if values[i][j] != modes[0])
            require(len(exceptional) == 1, "singleton endpoint")
            endpoints[exceptional[0]].add(i)
    return endpoints


def equality_census(maxima, frames, labels, values, costs):
    frame_histogram = Counter(sum(costs[i] for i in frame) for frame in frames)
    require(frame_histogram == {8: 1005, 10: 960, 12: 60}, "frame cost histogram")
    union_histogram, closure_histogram = Counter(), Counter()
    equality_pairs = []
    for flat in maxima:
        for frame in frames:
            removed = set(flat) | set(frame)
            weight = sum(costs[i] for i in removed)
            union_histogram[weight] += 1
            if weight != 48:
                continue
            endpoints = singleton_sets(values, costs, removed)
            require(sum(map(len, endpoints)) == 64, "all singleton coordinates remain")
            closure_sizes = []
            for endpoint in endpoints:
                basis, closure = independent_basis(tuple(labels[i] for i in sorted(endpoint)))
                live = {i for i in range(120) if i not in frame and labels[i] in closure}
                require(len(endpoint) == 16 and len(basis) == 6 and live == endpoint,
                        "rank-six endpoint closure obstruction")
                closure_sizes.append((len(endpoint), len(basis), len(live)))
            closure_histogram[str(closure_sizes)] += 1
            equality_pairs.append({"flat_root_labels": sorted(labels[i] for i in flat),
                                   "frame_root_labels": sorted(labels[i] for i in frame),
                                   "singleton_root_labels": [sorted(labels[i] for i in group)
                                                             for group in endpoints]})
            require(len(equality_pairs) <= 60, "equality-pair storage capacity")
    require(max(union_histogram) == 48 and union_histogram[48] == 60,
            "flat/frame union maximum")
    return frame_histogram, union_histogram, closure_histogram, equality_pairs


def receipt():
    roots = lattice_roots()
    labels = tuple(simple_label(row) for row in roots)
    require(len(set(labels)) == 120, "distinct root labels")
    values, costs = coordinate_costs(roots)
    maxima, occupancy, weights = affine_flat_census(labels, costs)
    frames = orthogonal_frames(roots)
    frame_hist, union_hist, closure_hist, pairs = equality_census(
        maxima, frames, labels, values, costs)
    return {"schema": 1, "method": "direct affine-five-flat census; explicit binary spans",
            "root_lines": len(roots), "six_spaces": 788035,
            "affine_five_directions": 97155, "affine_five_flats": 777240,
            "even_only_six_spaces": 10795,
            "root_occupancy_histogram": {str(k): v for k, v in occupancy.items()},
            "weighted_flat_histogram": {str(k): v for k, v in weights.items()},
            "maximizing_flat_root_labels": sorted(sorted(labels[i] for i in flat)
                                                   for flat in maxima),
            "orthogonal_frames": len(frames),
            "frame_cost_histogram": {str(k): v for k, v in sorted(frame_hist.items())},
            "union_cost_histogram": {str(k): v for k, v in sorted(union_hist.items())},
            "closure_shape_histogram": dict(closure_hist),
            "equality_pairs": sorted(pairs, key=lambda row: (row["flat_root_labels"],
                                                            row["frame_root_labels"]))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a newly computed external receipt")
    args = parser.parse_args()
    result = receipt()
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output = args.output.expanduser().resolve()
        repo = Path(__file__).resolve().parent.parent.parent
        require(not output.is_relative_to(repo), "external output only")
        with output.open("x", encoding="utf-8") as stream:
            written = stream.write(encoded)
            require(written == len(encoded), "incomplete receipt write")
    else:
        path = Path(__file__).with_name("INDEPENDENT.json")
        require(path.is_file() and not path.is_symlink(), "missing or linked receipt")
        require(path.stat().st_size <= 100_000, "receipt capacity")
        expected = json.loads(path.read_bytes())
        require(result == expected, "independent receipt differs")
    print("Independent census passed: 788035 six-spaces, 2025 frames, 60 equality pairs.")


if __name__ == "__main__":
    main()
