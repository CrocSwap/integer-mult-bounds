"""Check the stated scalar-cache dimensions with rational arithmetic."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path


PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
NORMALS = [42, 7, 25, 52, 82, 127, 97, 76]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def basis(rows):
    """Return an echelon basis over Q."""
    pivots = {}
    for source in rows:
        row = list(map(Fraction, source))
        for column, pivot in sorted(pivots.items()):
            factor = row[column]
            if factor:
                row = [a - factor * b for a, b in zip(row, pivot)]
        column = next((i for i, value in enumerate(row) if value), None)
        if column is not None:
            factor = row[column]
            pivots[column] = [value / factor for value in row]
    return [row for _, row in sorted(pivots.items())]


def fibers(labels, directions):
    groups = defaultdict(list)
    for column, label in enumerate(labels):
        key = tuple((label & direction).bit_count() % 2 for direction in directions)
        groups[key].append(column)
    return groups


def fiber_dimension(rows, labels, directions):
    return sum(len(basis([[row[i] for i in group] for row in rows]))
               for group in fibers(labels, directions).values())


def main(args):
    raw = args.interface.read_bytes()
    require(sha256(raw).hexdigest() == PIN, "The interface digest must match")
    data = json.loads(raw)
    labels = data["ports"]
    rows = [[int(row.get(str(i), 0)) for i in range(112)] for row in data["R"]]
    require(len(rows) == 8 and len(labels) == len(set(labels)) == 112,
            "The query must have eight rows and112 distinct columns")
    normal_dimensions = [fiber_dimension(rows, labels, NORMALS[:k]) for k in range(9)]
    coordinate_dimensions = [fiber_dimension(rows, labels, [1 << j for j in range(k)])
                             for k in range(10)]
    require(normal_dimensions == [8, 15, 28, 44, 44, 56, 56, 56, 56],
            "The normal-character dimensions must match")
    require(coordinate_dimensions == [8, 16, 31, 53, 85, 101, 112, 112, 112, 112],
            "The coordinate-character dimensions must match")
    histogram = Counter()
    for direction in range(512):
        signs = [1 - 2 * ((label & direction).bit_count() % 2) for label in labels]
        phased = [[a * b for a, b in zip(row, signs)] for row in rows]
        histogram[len(basis(rows + phased))] += 1
    require(histogram == {8: 2, 15: 16, 16: 494}, "The two-demand ranks must match")

    cache = []
    projected_rows = []
    fiber_sizes_and_ranks = []
    for group in fibers(labels, NORMALS).values():
        local_basis = basis([[row[i] for i in group] for row in rows])
        fiber_sizes_and_ranks.append([len(group), len(local_basis)])
        for local_row in local_basis:
            row = [Fraction(0)] * 112
            for i, value in zip(group, local_row):
                row[i] = value
            cache.append(row)
        for source in rows:
            projected_rows.append([source[i] if i in group else 0 for i in range(112)])
    require(fiber_sizes_and_ranks == [[8, 4]] * 14, "The final fibers must have rank four")
    require(len(basis(cache)) == 56 and len(basis(cache + rows)) == 56,
            "The cache basis must be independent and contain the query rows")
    for row in cache:
        support = [i for i, value in enumerate(row) if value]
        for direction in NORMALS:
            signs = {1 - 2 * ((labels[i] & direction).bit_count() % 2) for i in support}
            require(len(signs) == 1, "Each cache row must be an eigenvector for each update")
    reduced = cache[1:]
    require(len(basis(reduced)) == 55, "The reduced cache must have rank55")
    rejected_projection = next((i for i, row in enumerate(projected_rows)
                                if len(basis(reduced + [row])) == 56), None)
    require(rejected_projection is not None, "A required projection must fail in the reduced cache")
    report = {
        "status": "PASS_EXACT_MINIMAL_SCALAR_CACHE_COUNTS",
        "interface_sha256": PIN,
        "arithmetic": "fractions.Fraction over Q",
        "normal_directions": NORMALS,
        "normal_dimensions": normal_dimensions,
        "coordinate_dimensions": coordinate_dimensions,
        "stacked_rank_histogram": dict(sorted(histogram.items())),
        "normal_fiber_sizes_and_ranks": fiber_sizes_and_ranks,
        "explicit_cache_rank": 56,
        "query_rows_in_cache": True,
        "cache_invariant_under_all_normal_directions": True,
        "removed_row_control_rejected": True,
        "missing_projection_index": rejected_projection,
        "scope": "Finite counts and a basis construction for the pinned query. The written proof gives the general theorem. No native cost or kappa claim.",
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())
