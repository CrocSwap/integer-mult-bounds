"""Separate root/lattice construction and generated-span singleton-cap check.

Imports no primary or predecessor executable code. Every six-flat intersection
with at least six class labels has a spanning subset among the six-label tuples.
"""

import json
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
DATA = "research/one-sided-six-multisets/data/data.txt"
# E8 simple roots, in the retained doubled-coordinate convention.
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


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load_json(path):
    check(
        path.is_file() and not path.is_symlink() and path.stat().st_size < 2_000_000,
        "invalid JSON source",
    )
    return json.loads(path.read_bytes())


def root_labels():
    roots = set()
    for i, j in combinations(range(8), 2):
        for a, b in product((-2, 2), repeat=2):
            row = tuple(a if k == i else b if k == j else 0 for k in range(8))
            roots.add(max(tuple(-x for x in row), row))
    for row in product((-1, 1), repeat=8):
        if sum(row) % 4 == 0:
            roots.add(max(tuple(-x for x in row), row))
    roots = tuple(sorted(roots))
    check(len(roots) == 120, "independent root inventory")
    matrix = [
        [Fraction(SIMPLE[j][i]) for j in range(8)]
        + [Fraction(i == j) for j in range(8)]
        for i in range(8)
    ]
    for column in range(8):
        pivot = next(i for i in range(column, 8) if matrix[i][column])
        matrix[pivot], matrix[column] = matrix[column], matrix[pivot]
        factor = matrix[column][column]
        matrix[column] = [x / factor for x in matrix[column]]
        for i in range(8):
            if i != column:
                factor = matrix[i][column]
                matrix[i] = [
                    x - factor * y
                    for x, y in zip(matrix[i], matrix[column], strict=True)
                ]
    labels = []
    for root in roots:
        coordinates = [sum(row[j + 8] * root[j] for j in range(8)) for row in matrix]
        check(all(c.denominator == 1 for c in coordinates), "lattice integrality")
        labels.append(
            1 + sum((int(c) % 2) * 2 ** (i + 1) for i, c in enumerate(coordinates))
        )
    check(len(set(labels)) == 120, "independent label injectivity")
    return roots, tuple(labels)


def independent_classes(roots, labels):
    check(len(roots) == len(labels) == 120, "class input size")
    classes, counts = [[], [], []], [0, 0, 0]
    for root, label in zip(roots, labels, strict=True):
        values = (0, 2 * (root[0] + root[1]), 2 * (root[0] + root[2]))
        if values[0] == values[1] == values[2]:
            counts[0] += 1
        elif len(set(values)) == 3:
            counts[2] += 1
        else:
            counts[1] += 1
            for i in range(3):
                if (
                    values[i] != values[(i + 1) % 3]
                    and values[i] != values[(i + 2) % 3]
                ):
                    classes[i].append(label)
    check(
        counts == [36, 81, 3] and [len(c) for c in classes] == [27] * 3,
        "independent A2 classes",
    )
    return classes


def span_basis(rows):
    check(
        len(rows) <= 9 and all(type(x) is int and 0 < x < 512 for x in rows),
        "nine-bit basis input",
    )
    pivots = [0] * 9
    for value in rows:
        for bit in range(8, -1, -1):
            if value & (1 << bit):
                if pivots[bit]:
                    value ^= pivots[bit]
                else:
                    pivots[bit] = value
                    break
    for bit in range(9):
        if pivots[bit]:
            for higher in range(bit + 1, 9):
                if pivots[higher] & (1 << bit):
                    pivots[higher] ^= pivots[bit]
    return tuple(p for p in pivots if p)


def generated_span_cap(labels):
    check(len(labels) == len(set(labels)) == 27, "27 singleton labels required")
    seen, maximizing, maximum, tuples = set(), set(), 0, 0
    for chosen in combinations(labels, 6):
        tuples += 1
        basis = span_basis(chosen)
        if basis in seen:
            continue
        seen.add(basis)
        check(len(seen) <= 296_010, "generated-span capacity")
        space = {0}
        for row in basis:
            space.update(tuple(x ^ row for x in space))
            check(len(space) <= 64, "six-dimensional span capacity")
        intersection = tuple(label for label in labels if label in space)
        if len(intersection) > maximum:
            maximum, maximizing = len(intersection), {intersection}
        elif len(intersection) == maximum:
            maximizing.add(intersection)
    check(
        tuples == 296_010 and maximum == 16 and len(maximizing) == 27,
        "independent singleton cap",
    )
    return {
        "six_label_tuples": tuples,
        "generated_spans": len(seen),
        "maximum": maximum,
        "maximizers": len(maximizing),
        "maximizer_sha256": sha256(json.dumps(sorted(maximizing)).encode()).hexdigest(),
    }


def shift_controls():
    cases = 0
    for values in product(range(-2, 3), repeat=3):
        equal = len(set(values))
        for shift in range(-4, 5):
            support = tuple(v + shift != 0 for v in values)
            if equal == 2:
                singleton = next(i for i in range(3) if values.count(values[i]) == 1)
                check(
                    sum(support) >= 2 - support[singleton],
                    "nonmodal singleton inequality",
                )
            elif equal == 3:
                check(sum(support) >= 2, "three-distinct inequality")
            cases += 1
    check(cases == 1125, "shift-control domain")
    return cases


def original_caller_binding(sources, by_root, columns):
    path = PACKAGE / "vendor/bx_data.json"
    check(
        path.is_file() and not path.is_symlink() and path.stat().st_size < 32_768,
        "original caller file bound",
    )
    raw = path.read_bytes()
    check(
        len(raw) < 32_768
        and any(
            r["local_path"] == "vendor/bx_data.json"
            and r["sha256"] == sha256(raw).hexdigest()
            for r in sources["retained_files"]
        ),
        "independent original caller source",
    )
    original = json.loads(raw, parse_float=Fraction)
    check(len(columns) == len(span_basis(columns)) == 9, "invertible caller map")
    check(len(original["LAB"]) == len(original["L"]) == 112, "caller data size")
    for label, row in zip(original["LAB"], original["L"], strict=True):
        values = tuple(2 * x for x in row)
        check(
            len(values) == 8 and all(x.denominator == 1 for x in values), "caller roots"
        )
        root = tuple(map(int, values))
        root = max(root, tuple(-x for x in root))
        image = 0
        for bit in range(9):
            if label & (1 << bit):
                image ^= columns[bit]
        check(image == by_root[root], "independent caller map mismatch")
    return 112


def main():
    sources = load_json(PACKAGE / "SOURCES.json")
    data_path = ROOT / DATA
    check(
        data_path.is_file()
        and not data_path.is_symlink()
        and data_path.stat().st_size < 2_000_000,
        "invalid P112 data",
    )
    raw = data_path.read_bytes()
    check(
        any(
            r["path"] == DATA and r["sha256"] == sha256(raw).hexdigest()
            for r in sources["files"]
        ),
        "independent data source binding",
    )
    roots, labels = root_labels()
    by_root = dict(zip(roots, labels, strict=True))
    lines = raw.decode("utf-8").splitlines()
    live_roots = tuple(tuple(map(int, r.split())) for r in lines[2:114])
    check(
        tuple(map(int, lines[0].split())) == tuple(by_root[r] for r in live_roots),
        "independent live label binding",
    )
    expected = load_json(PACKAGE / "RESULT.json")
    original_caller_binding(
        sources, by_root, expected["original_label_binding"]["binary_map_columns"]
    )
    reports = [generated_span_cap(c) for c in independent_classes(roots, labels)]
    for report, primary in zip(reports, expected["singleton_hyperplanes"], strict=True):
        check(
            all(
                report[k] == primary[k]
                for k in ("maximum", "maximizers", "maximizer_sha256")
            ),
            "independent/primary singleton disagreement",
        )
    check(
        expected["support_bounds"] == {"18": 68, "21": 62, "22": 60}, "budget receipt"
    )
    check(
        expected["application"]["profile"] == [2, 2, 2, 5, 6, 6, 6, 7, 7, 7, 7]
        and expected["application"]["endpoint_lower"] == 68
        and expected["application"]["margin"] == 8,
        "caller receipt",
    )
    print(
        json.dumps(
            {"generated_span_checks": reports, "shift_controls": shift_controls()},
            sort_keys=True,
        )
    )
    print(
        "PASS_INDEPENDENT_P112_A2_SINGLETON_CAP tuples=888030 cap16 nonmodal_shifts1125"
    )


if __name__ == "__main__":
    main()
