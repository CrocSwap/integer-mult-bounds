"""Check actual mixed-rank P112 cut40 coefficients. Nick Petalas, Apache-2.0."""

import json
from itertools import combinations

from sources import PACKAGE, authenticate, load_geometry, read_json, require


def binary_rank(values):
    require(len(values) <= 112, "rank input bound")
    basis = [0] * 9
    for value in values:
        require(type(value) is int and 0 < value < 512, "nine-bit label")
        for bit in range(8, -1, -1):
            if value >> bit & 1:
                if basis[bit]:
                    value ^= basis[bit]
                else:
                    basis[bit] = value
                    break
    return sum(bool(x) for x in basis)


def validate_shape(witness):
    require(type(witness) is dict, "witness object")
    require(
        set(witness)
        == {
            "schema_version",
            "coordinate_order",
            "directions",
            "cut",
            "pieces",
            "combination_matrix",
        },
        "witness schema",
    )
    require(
        type(witness["schema_version"]) is int and witness["schema_version"] == 1,
        "witness version",
    )
    require(witness["coordinate_order"] == "pinned-geometry.points", "point order")
    cut, pieces, directions = (witness[k] for k in ("cut", "pieces", "directions"))
    require(isinstance(cut, list) and len(cut) == 40, "cut40 length")
    require(all(type(j) is int and 0 <= j < 112 for j in cut), "cut indices")
    require(cut == sorted(set(cut)), "cut distinct and sorted")
    require(isinstance(pieces, list) and len(pieces) == 3, "three pieces")
    require(all(isinstance(r, list) and len(r) == 112 for r in pieces), "piece width")
    require(
        all(type(x) is int and abs(x) <= 8 for r in pieces for x in r),
        "bounded exact integer coefficients",
    )
    require(isinstance(directions, list) and len(directions) == 2, "two directions")
    require(
        all(isinstance(r, list) and len(r) == 8 for r in directions),
        "direction dimension",
    )
    require(
        all(type(x) is int and abs(x) <= 2 for r in directions for x in r),
        "bounded root directions",
    )
    require(
        witness["combination_matrix"] == [[1, 1, 0], [0, 0, 1]],
        "fixed codeword combinations",
    )


def verify(witness, g):
    validate_shape(witness)
    roots, points, labels, _ = g.root_data()
    a, b = map(tuple, witness["directions"])
    require(a in roots and b in roots and g.dot(a, b) == 0, "orthogonal roots")
    cut, pieces = witness["cut"], witness["pieces"]
    supports = [[j for j, value in enumerate(row) if value] for row in pieces]
    require([len(s) for s in supports] == [12, 12, 20], "support sizes")
    ranks = [binary_rank([labels[j] for j in s]) for s in supports]
    require(ranks == [5, 5, 6], "actual binary ranks")
    union = set().union(*map(set, supports))
    require(len(union) == 44 and not union.intersection(cut), "disjoint44 union")
    values = [(g.dot(a, r), g.dot(b, r)) for r in points]
    active = {j for j, pair in enumerate(values) if any(pair)}
    require(len(active) == 84 and sorted(active - union) == cut, "actual common cut")
    retained = [j for j in range(112) if j not in cut]
    for j in retained:
        require(pieces[0][j] + pieces[1][j] == values[j][0], "first codeword equation")
        require(pieces[2][j] == values[j][1], "second codeword equation")
    minors = [
        values[i][0] * values[j][1] - values[i][1] * values[j][0]
        for i, j in combinations(retained, 2)
    ]
    require(any(minors), "independent restricted codewords")
    return {
        "status": "PASS_P112_MIXED_CUT40_COUNTEREXAMPLE",
        "cut": 40,
        "code_union": 84,
        "support_sizes": [12, 12, 20],
        "binary_ranks": ranks,
        "support_union": 44,
        "intersection_at_least": 2,
        "retained_equations": 144,
        "maximum_absolute_minor": max(map(abs, minors)),
        "sufficient39": "inherited PR3278; proof and receipt authenticated, not rerun",
    }


def main():
    authenticate()
    result = verify(read_json(PACKAGE / "WITNESS.json"), load_geometry())
    require(result == read_json(PACKAGE / "RESULT.json"), "result receipt")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
