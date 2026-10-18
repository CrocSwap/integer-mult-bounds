"""D6 near-tight closure and an exact cut48 P112 shortening witness.

The echelon census follows the credited PR3266 method. This checks the new
full-E8 closure of eleven singleton labels and an actual sharpness example.
"""

import argparse
import json
from collections import Counter
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

from sources import PACKAGE, authenticate, require


def span(values):
    require(len(values) <= 120, "bounded span input")
    result = {0}
    for value in values:
        require(type(value) is int and 0 < value < 512, "nine-bit label")
        result.update(x ^ value for x in tuple(result))
    return result


def coordinate_model(labels):
    mapping = {0: 0}
    dimension = 0
    for label in labels:
        if label not in mapping:
            mapping.update(
                {x ^ label: y | (1 << dimension) for x, y in tuple(mapping.items())}
            )
            dimension += 1
    require(dimension in (7, 8), "fiber dimension")
    return tuple(mapping[x] for x in labels), dimension


def flat_masks(labels):
    """All five-spaces in a seven/eight-dimensional fiber span, once."""
    require(len(labels) in (12, 33), "D6 fiber size")
    coordinates, dimension = coordinate_model(labels)
    kernels = tuple(
        sum(1 << j for j, x in enumerate(coordinates) if (x & h).bit_count() % 2 == 0)
        for h in range(1 << dimension)
    )
    masks = []
    for pivots in combinations(range(dimension), dimension - 5):
        choices = []
        for pivot in pivots:
            free = tuple(j for j in range(pivot) if j not in pivots)
            choices.append(
                tuple(
                    kernels[
                        (1 << pivot)
                        | sum(((n >> k) & 1) << j for k, j in enumerate(free))
                    ]
                    for n in range(1 << len(free))
                )
            )
        for row_masks in product(*choices):
            intersection = (1 << len(labels)) - 1
            for mask in row_masks:
                intersection &= mask
            masks.append(intersection)
    require(len(masks) == {7: 2667, 8: 97155}[dimension], "flat count")
    return masks


def axis_check(g, roots, labels, indices):
    fiber = tuple(labels[i] for i in indices)
    masks = flat_masks(fiber)
    histogram = Counter(mask.bit_count() for mask in masks)
    near = sorted(set(mask for mask in masks if mask.bit_count() >= 11))
    require(max(histogram) == 12 and len(near) == 120, "near-tight census")
    require(histogram[11] == 0, "unexpected eleven-root intersection")
    for mask in near:
        selected = tuple(fiber[j] for j in range(33) if mask >> j & 1)
        generated = span(selected)
        require(
            {label for label in labels if label in generated} == set(selected),
            "full E8 closure leaves axis",
        )
    punctures = []
    for chosen in combinations(range(33), 4):
        if all(
            g.dot(roots[indices[i]], roots[indices[j]]) == 0
            for i, j in combinations(chosen, 2)
        ):
            removed = sum(1 << j for j in chosen)
            survivors = tuple(mask for mask in near if not mask & removed)
            require(len(survivors) == 12, "puncture survivor count")
            overlaps = Counter(
                (a & b).bit_count() for a, b in combinations(survivors, 2)
            )
            require(overlaps == {2: 12, 4: 24, 8: 30}, "puncture overlap")
            near_live = tuple(
                mask & ~removed for mask in near if (mask & ~removed).bit_count() >= 11
            )
            require(len(near_live) == 60, "near-tight puncture count")
            require(
                max((a | b).bit_count() for a, b in combinations(near_live, 2)) == 22,
                "near-tight pair union",
            )
            punctures.append(removed)
    require(len(punctures) == 120, "puncture census")
    return {
        "flats": len(masks),
        "histogram": dict(sorted(histogram.items())),
        "near_tight_sets": len(near),
        "full_root_closures": len(near),
        "orthogonal_punctures": len(punctures),
        "minimum_survivor_intersection": 2,
        "near_live_sets_per_puncture": 60,
        "maximum_near_pair_union": 22,
        "near_sha256": sha256(repr(near).encode()).hexdigest(),
    }


def normalization_check(g, roots, points, coordinates):
    qualifying = []
    for omitted in combinations(range(8), 2):
        subsystem = tuple(
            root
            for root, c in zip(roots, coordinates, strict=True)
            if all(c[j] == 0 for j in omitted)
        )
        if len(subsystem) >= 29:
            normal = tuple(r for r in roots if all(g.dot(r, s) == 0 for s in subsystem))
            require(len(normal) == {30: 2, 36: 3}[len(subsystem)], "normal type")
            qualifying.append((omitted, len(subsystem), len(normal)))
    require(len(qualifying) == 2, "six-face classification at29")
    five_max = max(
        sum(all(c[j] == 0 for j in omitted) for c in coordinates)
        for omitted in combinations(range(8), 3)
    )
    require(five_max == 20, "lower-rank parabolic bound")
    histogram = Counter()
    a2_unions = []
    for a, b in combinations(roots, 2):
        pairing = g.dot(a, b)
        if abs(pairing) == 4:
            a2_unions.append(sum(bool(g.dot(a, r) or g.dot(b, r)) for r in points))
        if pairing == 0:
            count = sum(bool(g.dot(a, r) or g.dot(b, r)) for r in points)
            histogram[count] += 1
            if count <= 83:
                removed = Counter(
                    (bool(g.dot(a, r)), bool(g.dot(b, r))) for r in g.frame_lines()
                )
                require(removed == {(True, False): 4, (False, True): 4}, "4+4 puncture")
    require(histogram == {82: 448, 84: 2688, 85: 448, 86: 168, 88: 28}, "D6 union")
    require(len(a2_unions) == 3360 and min(a2_unions) == 78, "A2 union bound")
    return {
        "five_face_max": five_max,
        "six_faces_at_least29": qualifying,
        "orthogonal_plane_unions": dict(sorted(histogram.items())),
        "a2_root_pairs": len(a2_unions),
        "a2_minimum_union": min(a2_unions),
    }


def witness_axes(g, roots, points, labels, plane):
    axes = []
    for a, b in (plane, tuple(reversed(plane))):
        full = tuple(r for r in roots if g.dot(a, r) and not g.dot(b, r))
        masks = flat_masks(tuple(labels[r] for r in full))
        survivors = []
        for mask in sorted(set(masks)):
            selected = tuple(full[j] for j in range(33) if mask >> j & 1)
            if len(selected) == 12 and all(r in points for r in selected):
                survivors.append(tuple(points.index(r) for r in selected))
        require(len(survivors) == 12, "witness axis")
        axes.append(survivors)
    return axes


def choose_witness(g, roots, points, labels):
    plane = next(
        (a, b)
        for a, b in combinations(roots, 2)
        if g.dot(a, b) == 0
        and sum(bool(g.dot(a, r) or g.dot(b, r)) for r in points) == 82
    )
    axes = witness_axes(g, roots, points, labels, plane)
    left, right = next(
        (a, b) for a, b in combinations(axes[0], 2) if len(set(a) & set(b)) == 2
    )
    supports = (left, right, axes[1][0])
    union = set().union(*map(set, supports))
    cut = tuple(
        j
        for j, r in enumerate(points)
        if (g.dot(plane[0], r) or g.dot(plane[1], r)) and j not in union
    )
    pieces = []
    for i, support in enumerate(supports):
        row = [0] * 112
        for j in support:
            value = g.dot(plane[0 if i < 2 else 1], points[j])
            row[j] = value if i < 2 and j in set(left) & set(right) else 2 * value
        pieces.append(row)
    return {"directions": plane, "cut": cut, "twice_pieces": pieces}


def verify_witness(g, points, labels, witness):
    require(set(witness) == {"directions", "cut", "twice_pieces"}, "witness schema")
    directions, cut, pieces = (
        witness[k] for k in ("directions", "cut", "twice_pieces")
    )
    require(len(directions) == 2 and all(len(r) == 8 for r in directions), "directions")
    require(
        len(cut) == len(set(cut)) == 48
        and all(type(j) is int and 0 <= j < 112 for j in cut),
        "cut48",
    )
    require(len(pieces) == 3 and all(len(r) == 112 for r in pieces), "piece dimensions")
    require(
        all(type(x) is int and abs(x) <= 16 for row in pieces for x in row),
        "coefficient domain",
    )
    supports = [tuple(j for j, x in enumerate(row) if x) for row in pieces]
    require([len(x) for x in supports] == [12, 12, 12], "support sizes")
    require(all(not set(s) & set(cut) for s in supports), "piece inside cut")
    require(
        all(len(span(tuple(labels[j] for j in s))) == 32 for s in supports),
        "support rank5",
    )
    retained = tuple(j for j in range(112) if j not in cut)
    for j in retained:
        require(
            pieces[0][j] + pieces[1][j] == 2 * g.dot(directions[0], points[j]),
            "first codeword",
        )
        require(pieces[2][j] == 2 * g.dot(directions[1], points[j]), "second codeword")
    independent = any(
        g.dot(directions[0], points[i]) * g.dot(directions[1], points[j])
        != g.dot(directions[1], points[i]) * g.dot(directions[0], points[j])
        for i, j in combinations(retained, 2)
    )
    require(independent, "restricted codewords dependent")
    return {
        "cut": 48,
        "support_sizes": [12, 12, 12],
        "binary_ranks": [5, 5, 5],
        "support_union": len(set().union(*map(set, supports))),
        "intersection_at_least": 2,
    }


def compute():
    g = authenticate()
    roots, points, live_labels, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) % 2) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    mapping = dict(zip(roots, labels, strict=True))
    require(tuple(mapping[r] for r in points) == live_labels, "live label binding")
    a = roots[0]
    b = next(r for r in roots if g.dot(a, r) == 0)
    axes = []
    for x, y in ((a, b), (b, a)):
        indices = tuple(
            j for j, r in enumerate(roots) if g.dot(x, r) and not g.dot(y, r)
        )
        axes.append(axis_check(g, roots, labels, indices))
    small_capacities = []
    for sign in (-1, 1):
        fiber = tuple(
            labels[j]
            for j, r in enumerate(roots)
            if g.dot(a, r) == sign * g.dot(b, r) != 0
        )
        small_capacities.append(max(mask.bit_count() for mask in flat_masks(fiber)))
    require(small_capacities == [8, 8], "small D6 fiber capacity")
    witness = choose_witness(g, roots, points, mapping)
    result = {
        "claim": "sharp-uniform-rank5-common-cut47-char0",
        "axes": axes,
        "normalization": normalization_check(g, roots, points, coordinates),
        "witness_summary": verify_witness(g, points, live_labels, witness),
        "a2_required": 62,
        "a2_inherited_allowance": 60,
        "d6_required_union": 35,
        "d6_maximum_union": 34,
        "small_fiber_capacities": small_capacities,
    }
    return json.loads(json.dumps(result)), json.loads(json.dumps(witness))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result, witness = compute()
    if args.output:
        require(
            not args.output.resolve().is_relative_to(PACKAGE.parents[1]),
            "external output",
        )
        args.output.mkdir(exist_ok=False)
        for name, data in (("RESULT.json", result), ("WITNESS.json", witness)):
            (args.output / name).write_text(
                json.dumps(data, indent=2, sort_keys=True) + "\n"
            )
    else:
        require(
            result == json.loads((PACKAGE / "RESULT.json").read_text()),
            "result mismatch",
        )
        require(
            witness == json.loads((PACKAGE / "WITNESS.json").read_text()),
            "witness mismatch",
        )
    print(
        "PASS_P112_SHARP47 flats=194310 closures=240 punctures=240 cut48_witness=exact"
    )


if __name__ == "__main__":
    main()
