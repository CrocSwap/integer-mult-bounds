"""Independent five-label bases and dense witness arithmetic; no census import."""

import json
from hashlib import sha256
from itertools import combinations

from sources import PACKAGE, authenticate, require


def basis(values):
    rows = []
    for value in values:
        row = value
        for pivot in rows:
            row = min(row, row ^ pivot)
        if row:
            rows.append(row)
            rows.sort(reverse=True)
    return tuple(rows)


def contains(rows, value):
    row = value
    for pivot in rows:
        row = min(row, row ^ pivot)
    return row == 0


def check_axis(labels, fiber):
    distinct = set()
    subsets = 0
    for chosen in combinations(range(33), 5):
        subsets += 1
        rows = basis(tuple(labels[fiber[j]] for j in chosen))
        if len(rows) != 5:
            continue
        selected = tuple(j for j in range(33) if contains(rows, labels[fiber[j]]))
        if len(selected) >= 11:
            require(len(selected) == 12, "independent near capacity")
            actual = {fiber[j] for j in selected}
            closure = {j for j in range(120) if contains(rows, labels[j])}
            require(closure == actual, "independent full closure")
            distinct.add(sum(1 << j for j in selected))
    require(subsets == 237336 and len(distinct) == 120, "five-label basis coverage")
    return sha256(repr(sorted(distinct)).encode()).hexdigest()


def check_witness(points, labels, witness):
    rows = witness["twice_pieces"]
    a, b = witness["directions"]
    cut = set(witness["cut"])
    require(len(cut) == 48, "independent cut")
    supports = [tuple(j for j, x in enumerate(row) if x) for row in rows]
    require(
        [len(basis(tuple(labels[j] for j in s))) for s in supports] == [5, 5, 5],
        "dense ranks",
    )
    first = [sum(x * y for x, y in zip(a, r, strict=True)) for r in points]
    second = [sum(x * y for x, y in zip(b, r, strict=True)) for r in points]
    for j in range(112):
        if j not in cut:
            require(rows[0][j] + rows[1][j] == 2 * first[j], "dense first endpoint")
            require(rows[2][j] == 2 * second[j], "dense second endpoint")
    retained = tuple(j for j in range(112) if j not in cut)
    require(
        any(
            first[i] * second[j] - first[j] * second[i]
            for i, j in combinations(retained, 2)
        ),
        "independent endpoints",
    )


def main():
    g = authenticate()
    roots, points, live, coordinates = g.root_data()
    labels = tuple(
        1 | sum((int(x) & 1) << (j + 1) for j, x in enumerate(c)) for c in coordinates
    )
    a = roots[0]
    b = next(r for r in roots if sum(x * y for x, y in zip(a, r, strict=True)) == 0)
    expected = json.loads((PACKAGE / "RESULT.json").read_text())
    for index, (x, y) in enumerate(((a, b), (b, a))):
        fiber = tuple(
            j
            for j, r in enumerate(roots)
            if sum(u * v for u, v in zip(x, r, strict=True))
            and not sum(u * v for u, v in zip(y, r, strict=True))
        )
        digest = check_axis(labels, fiber)
        require(
            digest == expected["axes"][index]["near_sha256"], "independent mask digest"
        )
    check_witness(points, live, json.loads((PACKAGE / "WITNESS.json").read_text()))
    print(
        "PASS_P112_SHARP47_CROSSCHECK basis_subsets=474672 "
        "full_closures=240 exact_witness"
    )


if __name__ == "__main__":
    main()
