"""Separate lattice reconstruction and exhaustive four-deletion oracle."""

import json
from fractions import Fraction
from itertools import combinations, permutations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
SIMPLE = (
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def lattice_inverse():
    matrix = [
        [Fraction(SIMPLE[j][i]) for j in range(8)]
        + [Fraction(i == j) for j in range(8)]
        for i in range(8)
    ]
    for pivot in range(8):
        row = next((i for i in range(pivot, 8) if matrix[i][pivot]), None)
        require(row is not None, "singular lattice basis")
        matrix[pivot], matrix[row] = matrix[row], matrix[pivot]
        scale = matrix[pivot][pivot]
        matrix[pivot] = [x / scale for x in matrix[pivot]]
        for i in range(8):
            if i != pivot:
                scale = matrix[i][pivot]
                matrix[i] = [
                    x - scale * y for x, y in zip(matrix[i], matrix[pivot], strict=True)
                ]
    return tuple(tuple(row[8:]) for row in matrix)


def root_data():
    # Doubled E8 consists of equal-parity coordinates with sum divisible by four.
    roots = set()
    for row in product(range(-2, 3), repeat=8):
        if (
            sum(x * x for x in row) == 8
            and sum(row) % 4 == 0
            and all(x % 2 == row[0] % 2 for x in row)
        ):
            roots.add(max(row, tuple(-x for x in row)))
    frame = set()
    for i in range(0, 8, 2):
        for sign in (-2, 2):
            row = tuple(2 if j == i else sign if j == i + 1 else 0 for j in range(8))
            frame.add(row)
    points = tuple(sorted(roots - frame))
    require(
        len(roots) == 120 and len(frame) == 8 and len(points) == 112,
        "root lattice inventory",
    )
    inverse = lattice_inverse()
    labels = []
    for point in points:
        coordinate = tuple(
            sum(x * y for x, y in zip(row, point, strict=True)) for row in inverse
        )
        require(all(x.denominator == 1 for x in coordinate), "nonintegral root")
        labels.append(
            1 + sum((int(x) % 2) * 2 ** (i + 1) for i, x in enumerate(coordinate))
        )
    require(len(set(labels)) == 112, "label collision")
    return points, tuple(labels)


def rank(columns):
    require(
        len(columns) <= 112 and all(type(x) is int and 0 < x < 512 for x in columns),
        "nine-bit column bounds",
    )
    basis = []
    for original in columns:
        value = original
        for row in basis:
            value = min(value, value ^ row)
        if value:
            basis.append(value)
            basis.sort(reverse=True)
    return len(basis)


def live_in_flat(label, equations):
    return all(
        sum(((label >> bit) & 1) * ((equation >> bit) & 1) for bit in range(9)) % 2 == 0
        for equation in equations
    )


def minimum_four_deletion_rank(columns):
    require(4 <= len(columns) <= 112, "four-deletion oracle bounds")
    minimum, checked = 9, 0
    for deleted in combinations(range(len(columns)), 4):
        remaining = tuple(
            column for i, column in enumerate(columns) if i not in deleted
        )
        minimum = min(minimum, rank(remaining))
        checked += 1
    return minimum, checked


def read_witness():
    witness = json.loads((PACKAGE / "WITNESS.json").read_text())
    require(
        witness["schema_version"] == 1 and len(witness["directions"]) == 3,
        "reference witness schema",
    )
    equations = [witness["first_flat_annihilator"]]
    for entry in witness["directions"]:
        h, deleted = entry["h"], entry["deleted_lines"]
        require(
            len(h) == 8
            and all(type(x) is int for x in h)
            and sum(x * x for x in h) == 8,
            "reference root direction",
        )
        require(
            len(deleted) == len(set(deleted)) == 5
            and all(type(i) is int and 0 <= i < 112 for i in deleted),
            "reference deletion indices",
        )
        equations.append(entry["second_flat_annihilator"])
    require(
        all(len(pair) == 2 and rank(pair) == 2 for pair in equations),
        "reference annihilator dimensions",
    )
    return witness


def run():
    witness = read_witness()
    points, labels = root_data()
    first = witness["first_flat_annihilator"]
    rows = []
    for entry in witness["directions"]:
        h, deleted = entry["h"], set(entry["deleted_lines"])
        second = entry["second_flat_annihilator"]
        off = tuple(
            i
            for i, point in enumerate(points)
            if sum(h[j] * point[j] for j in range(8))
        )
        outside = tuple(i for i in off if not live_in_flat(labels[i], first))
        missing = {i for i in outside if not live_in_flat(labels[i], second)}
        require(missing == deleted, "reference deletion identity")
        residual_rank = rank(tuple(labels[i] for i in outside if i not in deleted))
        minimum, checked = minimum_four_deletion_rank(tuple(labels[i] for i in outside))
        require(residual_rank == 7 and minimum == 8, "reference deletion threshold")
        rows.append(
            {
                "outside_first_flat": len(outside),
                "four_deletion_subsets_checked": checked,
                "minimum_rank_after_four_deletions": minimum,
                "rank_after_five_deletions": residual_rank,
            }
        )
    minor = [entry["h"][5:8] for entry in witness["directions"]]
    determinant = sum(
        (-1) ** sum(p[i] > p[j] for i in range(3) for j in range(i + 1, 3))
        * minor[0][p[0]]
        * minor[1][p[1]]
        * minor[2][p[2]]
        for p in permutations(range(3))
    )
    require(determinant == 16, "independent rational minor")
    result = {
        "status": "PASS_P112_FIVE_LINE_REFERENCE",
        "minor_determinant": determinant,
        "directions": rows,
        "reconstructed_live_labels": len(labels),
    }
    require(
        result == json.loads((PACKAGE / "REFERENCE.json").read_text()),
        "committed reference result differs",
    )
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
