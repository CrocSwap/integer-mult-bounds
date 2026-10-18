"""Analytic capacity18 model binding and literal attainment, with bounded replay."""

import argparse
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from common import (
    PACKAGE,
    basis,
    coordinate_map,
    geometry,
    polar,
    quadratic,
    require,
    span,
)


def reflection_orbit(g, roots, labels, pair):
    require(len(basis(labels)) == 9, "full input label span")
    index = {r: j for j, r in enumerate(roots)}
    permutations = []
    for simple in g.SIMPLE:
        perm = tuple(
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
        require(len(set(perm)) == 120, "root permutation")
        require(
            len(
                basis(
                    tuple(labels[j] | (labels[perm[j]] << 9) for j in range(120)),
                    bits=18,
                )
            )
            == 9,
            "reflection label map is linear and invertible",
        )
        permutations.append(perm)
    all_pairs = {
        (i, j)
        for i in range(120)
        for j in range(120)
        if i != j and g.dot(roots[i], roots[j]) == 0
    }
    queue, visited = [pair], {pair}
    require(len(all_pairs) == 7560, "ordered orthogonal-pair inventory")
    for cursor in range(7560):
        require(cursor < len(queue), "orthogonal orbit ended early")
        a, b = queue[cursor]
        for perm in permutations:
            image = (perm[a], perm[b])
            require(image in all_pairs, "reflection left orthogonal pairs")
            if image not in visited:
                visited.add(image)
                queue.append(image)
    require(visited == all_pairs, "orthogonal-pair transitivity")
    return len(visited)


def canonical_model(g, roots, labels, pair):
    a, b = (roots[i] for i in pair)
    axis = tuple(i for i, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r))
    bulk = tuple(i for i in axis if roots[i] != a)
    values = tuple(labels[i] for i in bulk)
    origin = values[0]
    directions = span(tuple(v ^ origin for v in values))
    gram = tuple(tuple(g.dot(a, b) // 4 for b in g.SIMPLE) for a in g.SIMPLE)
    radical = {h for h in directions if all(not polar(gram, h, x) for x in directions)}
    require(len(axis) == 33 and len(bulk) == 32, "exceptional-root decomposition")
    require(len(directions) == 64 and len(span(values)) == 128, "affine six-space")
    require(labels[pair[0]] not in span(values), "exceptional label outside bulk span")
    require(len(radical) == 4, "polar radical dimension two")
    require(
        {quadratic(gram, h) ^ polar(gram, origin, h) for h in radical} == {0, 1},
        "nonzero radical character",
    )
    ones = {origin ^ x for x in directions if quadratic(gram, origin ^ x)}
    require(ones == set(values), "bulk is exactly quadratic-one locus")
    quads = tuple(
        z
        for z in combinations(bulk, 4)
        if all(g.dot(roots[i], roots[j]) == 0 for i, j in combinations(z, 2))
    )
    require(len(quads) == 120, "all orthogonal four-root punctures")
    for quad in quads:
        tangent = span(tuple(labels[i] ^ labels[quad[0]] for i in quad))
        require(
            len(tangent) == 4 and tangent & radical == {0},
            "puncture is affine plane transverse to radical",
        )
    return axis, bulk, quads, len(radical)


def hyperplane_receipt(labels, bulk, quads):
    values = tuple(labels[i] for i in bulk)
    mapping = coordinate_map(values)
    require(len(mapping) == 128, "bulk span dimension seven")
    counts, intersection_counts = Counter(), Counter()
    witness = None
    maxima = [0] * len(quads)
    for normal in range(1, 128):
        support = tuple(
            i for i in bulk if not (mapping[labels[i]] & normal).bit_count() % 2
        )
        counts[len(support)] += 1
        require(len(support) in (0, 12, 16, 20), "affine hyperplane root count")
        for j, quad in enumerate(quads):
            overlap = len(set(support) & set(quad))
            if len(support) == 20:
                require(overlap >= 2, "twenty-root section misses puncture")
                intersection_counts[overlap] += 1
            retained = tuple(i for i in support if i not in quad)
            require(len(retained) <= 18, "punctured capacity")
            maxima[j] = max(maxima[j], len(retained))
            if len(retained) == 18 and witness is None:
                witness = {
                    "puncture": quad,
                    "support": retained,
                    "ambient_basis": basis(tuple(labels[i] for i in support)),
                }
    require(witness is not None, "literal attaining support")
    require(set(maxima) == {18}, "all punctures attain eighteen")
    require(
        len(basis(tuple(labels[i] for i in witness["support"]))) == 6, "witness rank"
    )
    return (
        dict(sorted(counts.items())),
        dict(sorted(intersection_counts.items())),
        witness,
    )


def fixed_p112_witness(g, roots, points, labels):
    pair = next(
        (i, j)
        for i, j in combinations(range(120), 2)
        if not g.dot(roots[i], roots[j])
        and sum(bool(g.dot(roots[i], r) or g.dot(roots[j], r)) for r in points) == 82
    )
    a, b = (roots[j] for j in pair)
    axis = tuple(i for i, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r))
    bulk = tuple(i for i in axis if i != pair[0])
    puncture = tuple(i for i in axis if roots[i] not in points)
    require(
        len(puncture) == 4 and pair[0] not in puncture,
        "actual four-root frame puncture",
    )
    _, _, witness = hyperplane_receipt(labels, bulk, (puncture,))
    require(
        all(roots[i] in points for i in witness["support"]), "actual live attainment"
    )
    return {"pair": pair, **witness}


def compute():
    g = geometry()
    roots, points, live_labels, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    require(
        tuple(labels[roots.index(r)] for r in points) == live_labels,
        "live label binding",
    )
    pair = (0, next(j for j, r in enumerate(roots) if not g.dot(roots[0], r)))
    axis, bulk, quads, radical_size = canonical_model(g, roots, labels, pair)
    counts, intersections, witness = hyperplane_receipt(labels, bulk, quads)
    result = {
        "claim": "sharp-D6-four-orthogonal-puncture-rank6-capacity18",
        "ordered_axis_orbit": reflection_orbit(g, roots, labels, pair),
        "axis_size": len(axis),
        "bulk_size": len(bulk),
        "affine_dimension": 6,
        "polar_rank": 4,
        "radical_size": radical_size,
        "orthogonal_punctures": len(quads),
        "hyperplane_counts": counts,
        "twenty_section_puncture_intersections": intersections,
        "capacity": 18,
        "exceptional_case_counting_bound": 17,
        "witness": witness,
        "pair": pair,
        "fixed_p112_witness": fixed_p112_witness(g, roots, points, labels),
    }
    return json.loads(json.dumps(result))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = compute()
    if args.output:
        require(
            not args.output.resolve().is_relative_to(PACKAGE.parents[1]),
            "external output",
        )
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(
            result == json.loads((PACKAGE / "RESULT.json").read_text()),
            "result mismatch",
        )
    print("PASS_D6_ANALYTIC_CAPACITY18 axes=7560 punctures=120 affine_hyperplanes=127")


if __name__ == "__main__":
    main()
