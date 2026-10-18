"""D6 pair-union certificate for the conditional mixed566 cut33 theorem."""

import argparse
import json
from collections import Counter
from itertools import combinations, product
from pathlib import Path

from common import PACKAGE, basis, geometry, read_json, require, span


def echelon_spaces(dimension, rank):
    require(dimension == 8 and rank in (2, 3), "annihilator dimensions")
    for pivots in combinations(range(dimension), rank):
        free = [tuple(c for c in range(p) if c not in pivots) for p in pivots]
        for codes in product(*(range(1 << len(f)) for f in free)):
            yield tuple(
                (1 << p) | sum(((code >> k) & 1) << c for k, c in enumerate(f))
                for p, f, code in zip(pivots, free, codes, strict=True)
            )


def axis_closures(labels, axis, rank):
    mapping = {value: j for j, value in enumerate(span(tuple(labels[i] for i in axis)))}
    require(len(mapping) == 256 and len(axis) == 33, "eight-dimensional D6 axis")
    coordinates = tuple(mapping[labels[i]] for i in axis)
    kernels = tuple(
        sum(1 << j for j, c in enumerate(coordinates) if not (c & v).bit_count() % 2)
        for v in range(256)
    )
    masks, count = set(), 0
    for annihilator in echelon_spaces(8, 8 - rank):
        mask = (1 << 33) - 1
        for row in annihilator:
            mask &= kernels[row]
        masks.add(mask)
        count += 1
    require(count == {5: 97155, 6: 10795}[rank], "complete subspace count")
    return masks, count


def orbit_receipt(g, roots, labels, pair):
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
        require(len(set(perm)) == 120, "reflection permutation")
        graph = tuple(labels[j] | labels[perm[j]] << 9 for j in range(120))
        require(
            len(basis(graph, 18)) == len(basis(labels)) == 9,
            "invertible linear label transport",
        )
        permutations.append(perm)
    expected = {
        (i, j)
        for i in range(120)
        for j in range(120)
        if i != j and not g.dot(roots[i], roots[j])
    }
    require(len(expected) == 7560, "ordered pair inventory")
    queue, visited = [pair], {pair}
    for cursor in range(7560):
        require(cursor < len(queue), "orbit ended early")
        a, b = queue[cursor]
        for perm in permutations:
            image = perm[a], perm[b]
            if image not in visited:
                visited.add(image)
                queue.append(image)
    require(visited == expected, "full ordered-pair orbit")
    return len(visited)


def model_receipt(g, roots, labels, pair, axis):
    bulk = tuple(i for i in axis if i != pair[0])
    bulk_span = set(span(tuple(labels[i] for i in bulk)))
    require(len(bulk) == 32 and len(bulk_span) == 128, "bulk seven-space")
    require(labels[pair[0]] not in bulk_span, "exceptional root outside bulk span")
    require(
        {i for i in range(120) if labels[i] in bulk_span} == set(bulk),
        "bulk span has no off-axis roots",
    )
    planes = Counter()
    points = tuple(r for r in roots if r not in g.frame_lines())
    for a, b in combinations(roots, 2):
        if not g.dot(a, b):
            size = sum(bool(g.dot(a, r) or g.dot(b, r)) for r in points)
            planes[size] += 1
            if size == 82:
                for first, second in ((a, b), (b, a)):
                    fiber = tuple(
                        r for r in roots if g.dot(first, r) and not g.dot(second, r)
                    )
                    punctures = tuple(r for r in fiber if r not in points)
                    require(
                        len(fiber) == 33 and len(punctures) == 4,
                        "union82 has four frame punctures per axis",
                    )
                    require(
                        all(not g.dot(x, y) for x, y in combinations(punctures, 2)),
                        "orthogonal puncture premise",
                    )
    require(
        dict(planes) == {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28},
        "all fixed-frame plane union types",
    )
    return dict(sorted(planes.items()))


def parabolic_receipt(coordinates):
    five = tuple(
        sum(all(c[i] == 0 for i in omitted) for c in coordinates)
        for omitted in combinations(range(8), 3)
    )
    six = tuple(
        sum(all(c[i] == 0 for i in omitted) for c in coordinates)
        for omitted in combinations(range(8), 2)
    )
    require(
        max(five) == 20 and {n for n in six if n >= 27} == {30, 36},
        "normalization at twenty-seven zeros",
    )
    require(max(n for n in six if n < 27) == 21, "other rank-six parabolics")
    return {"rank5_max": max(five), "rank6_large": [30, 36], "other_rank6_max": 21}


def compute():
    g = geometry()
    roots, _, _, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    pair = 0, next(j for j, r in enumerate(roots) if not g.dot(roots[0], r))
    a, b = (roots[j] for j in pair)
    axis = tuple(i for i, r in enumerate(roots) if g.dot(a, r) and not g.dot(b, r))
    planes = model_receipt(g, roots, labels, pair, axis)
    five, n5 = axis_closures(labels, axis, 5)
    six, n6 = axis_closures(labels, axis, 6)
    high = tuple(mask for mask in six if mask.bit_count() > 16)
    require(
        len(high) == 16 and {x.bit_count() for x in high} == {20},
        "all high rank-six sections",
    )
    require(max(x.bit_count() for x in five) == 12, "axis rank-five capacity")
    maximum = max((left | right).bit_count() for left in five for right in high)
    require(maximum == 28, "rank-five plus high rank-six union")
    # The other rank-six closures have <=16, so their union is <=12+16.
    require(
        max(x.bit_count() for x in six if x not in high) == 16,
        "remaining rank-six capacity",
    )
    return {
        "status": "PASS_MIXED566_CUT33",
        "cut": 33,
        "axis_pair_union": maximum,
        "axis_five_spaces": n5,
        "axis_six_spaces": n6,
        "distinct_five_closures": len(five),
        "distinct_six_closures": len(six),
        "high_six_closures": len(high),
        "pair_comparisons": len(five) * len(high),
        "ordered_axis_orbit": orbit_receipt(g, roots, labels, pair),
        "plane_union_counts": planes,
        "parabolic_counts": parabolic_receipt(coordinates),
        "D6_union82": {"required": 49, "coverage_upper": 48},
        "D6_union84": {"required": 51, "coverage_upper": 48},
        "D6_union85": {"required": 52, "coverage_upper": 48},
        "E6": {"required_twice": 90, "incidence_upper": 86},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.loads(json.dumps(compute()))
    if args.output:
        require(
            not args.output.resolve().is_relative_to(PACKAGE.parents[1]),
            "external output only",
        )
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(
            json.dumps(result, sort_keys=True)
            == json.dumps(read_json(PACKAGE / "RESULT.json"), sort_keys=True),
            "result receipt including schema types",
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
