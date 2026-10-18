"""Sharp rank-six full-axis concentration at fourteen labels. Apache-2.0."""

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (
    PACKAGE,
    basis,
    canonical,
    coordinates,
    polar,
    quadratic,
    require,
    root_data,
    span,
)


def model(g, roots, labels):
    pair = (0, next(j for j, r in enumerate(roots) if not g.dot(roots[0], r)))
    a, b = (roots[i] for i in pair)
    axis = tuple(i for i, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r))
    bulk = tuple(i for i in axis if i != pair[0])
    values = tuple(labels[i] for i in bulk)
    space = span(values)
    origin = values[0]
    directions = span(tuple(x ^ origin for x in values))
    gram = tuple(tuple(g.dot(s, t) // 4 for t in g.SIMPLE) for s in g.SIMPLE)
    radical = {x for x in directions if all(not polar(gram, x, y) for y in directions)}
    require(len(axis) == 33 and len(bulk) == 32, "axis decomposition")
    require(len(space) == 128 and len(directions) == 64, "bulk dimensions")
    require(labels[pair[0]] not in space, "exception outside bulk span")
    require(
        {i for i, x in enumerate(labels) if x in space} == set(bulk),
        "whole root closure",
    )
    require(len(radical) == 4, "polar radical dimension two")
    require(
        {quadratic(gram, origin ^ d) ^ quadratic(gram, origin) for d in radical}
        == {0, 1},
        "nonzero radical derivative",
    )
    require(
        {origin ^ d for d in directions if quadratic(gram, origin ^ d)} == set(values),
        "quadratic-one bulk",
    )
    return pair, axis, bulk


def sections(labels, bulk, exception):
    mapping = coordinates(tuple(labels[i] for i in bulk))
    require(len(mapping) == 128, "seven-space")
    seen, histogram, witness = set(), Counter(), None
    for x, y in combinations(range(1, 128), 2):
        normal_plane = tuple(sorted((x, y, x ^ y)))
        if normal_plane in seen:
            continue
        seen.add(normal_plane)
        support = tuple(
            i
            for i in bulk
            if not (mapping[labels[i]] & x).bit_count() % 2
            and not (mapping[labels[i]] & y).bit_count() % 2
        )
        histogram[len(support)] += 1
        require(len(support) <= 12, "four-section analytic capacity")
        if len(support) == 12 and witness is None:
            ambient = basis((labels[exception], *(labels[i] for i in support)))
            closure = tuple(
                i for i, value in enumerate(labels) if value in span(ambient)
            )
            witness = {
                "ambient_basis": ambient,
                "axis_indices": (exception, *support),
                "outside_indices": tuple(
                    i for i in closure if i not in bulk and i != exception
                ),
            }
    require(len(seen) == 2667 and witness is not None, "all five-spaces and witness")
    require(
        len(witness["ambient_basis"]) == 6 and witness["outside_indices"],
        "sharp nonconcentration",
    )
    return dict(sorted(histogram.items())), witness


def transport(g, roots, labels, pair):
    # The reflection/label-graph method retains PR3292's exact transport convention.
    index = {root: i for i, root in enumerate(roots)}
    permutations = []
    for simple in g.SIMPLE:
        permutation = tuple(
            index[
                g.canonical(
                    tuple(
                        x - g.dot(r, simple) // 4 * y
                        for x, y in zip(r, simple, strict=True)
                    )
                )
            ]
            for r in roots
        )
        require(len(set(permutation)) == 120, "reflection permutation")
        graph = tuple(labels[j] | (labels[permutation[j]] << 9) for j in range(120))
        require(len(basis(graph, bits=18)) == 9, "linear invertible label transport")
        permutations.append(permutation)
    all_pairs = {
        (i, j) for i in range(120) for j in range(120) if not g.dot(roots[i], roots[j])
    }
    queue, visited = [pair], {pair}
    for cursor in range(7560):
        require(cursor < len(queue), "orbit exhausted")
        a, b = queue[cursor]
        for permutation in permutations:
            image = permutation[a], permutation[b]
            require(image in all_pairs, "orthogonal pair preserved")
            if image not in visited:
                visited.add(image)
                queue.append(image)
    require(len(all_pairs) == 7560 and visited == all_pairs, "all ordered pairs")
    return len(visited)


def compute():
    g, roots, labels = root_data()
    require(
        all(
            quadratic(
                tuple(tuple(g.dot(s, t) // 4 for t in g.SIMPLE) for s in g.SIMPLE), x
            )
            == 1
            for x in labels
        ),
        "all root quadratic norms",
    )
    pair, axis, bulk = model(g, roots, labels)
    histogram, witness = sections(labels, bulk, pair[0])
    require(len(set(witness["axis_indices"]) & set(axis)) == 13, "thirteen axis labels")
    return json.loads(
        json.dumps(
            {
                "claim": "sharp-full-D6-axis-rank6-concentration14",
                "pair": pair,
                "axis_size": len(axis),
                "bulk_size": len(bulk),
                "bulk_rank": 7,
                "affine_dimension": 6,
                "polar_rank": 4,
                "radical_dimension": 2,
                "rank5_bulk_capacity": 12,
                "nonconcentrated_rank6_axis_max": 13,
                "concentration_threshold": 14,
                "five_space_count": 2667,
                "five_space_histogram": histogram,
                "ordered_pair_orbit": transport(g, roots, labels, pair),
                "witness": witness,
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-result", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit_result:
        print(json.dumps(result, indent=2))
    else:
        require(
            canonical(result)
            == canonical(json.loads((PACKAGE / "RESULT.json").read_bytes())),
            "result receipt",
        )
        print(
            "PASS_D6_AXIS_CONCENTRATION threshold=14 "
            "sharp_nonconcentrated=13 ordered_pairs=7560"
        )


if __name__ == "__main__":
    main()
