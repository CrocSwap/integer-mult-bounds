"""Separate coordinate recurrence and span-set witness check. Apache-2.0.

The simple-root coordinate convention is credited to the pinned root-simplex
geometry. This implementation does not import that geometry or verify.py.
"""

from itertools import combinations, product

from sources import PACKAGE, authenticate, read_json, require


def model():
    roots = []
    for i in range(8):
        for j in range(i + 1, 8):
            for sign in (-2, 2):
                row = [0] * 8
                row[i], row[j] = 2, sign
                roots.append(tuple(row))
    roots.extend(
        (1,) + tail for tail in product((-1, 1), repeat=7) if tail.count(-1) % 2 == 0
    )
    frame = set()
    for i in (0, 2, 4, 6):
        for sign in (-2, 2):
            row = [0] * 8
            row[i], row[i + 1] = 2, sign
            frame.add(tuple(row))
    points = sorted(set(roots) - frame)
    require(len(roots) == 120 and len(points) == 112, "independent root inventory")
    return points


def label(row):
    c = [0] * 8
    c[0] = row[7]
    c[7] = (row[6] + c[0]) // 2
    for i in range(6, 2, -1):
        c[i] = (row[i - 1] + c[0]) // 2 + c[i + 1]
    c[1] = (row[0] + row[1] + 2 * c[3]) // 4
    c[2] = c[1] - (row[0] - c[0]) // 2
    rebuilt = [c[0] + 2 * c[1] - 2 * c[2], -c[0] + 2 * c[1] + 2 * c[2] - 2 * c[3]]
    rebuilt.extend(-c[0] + 2 * c[i] - 2 * c[i + 1] for i in range(3, 7))
    rebuilt.extend((-c[0] + 2 * c[7], c[0]))
    require(tuple(rebuilt) == tuple(row), "integral coordinate recurrence")
    return 1 | sum((x % 2) << (j + 1) for j, x in enumerate(c))


def span_size(labels):
    require(len(labels) <= 20, "independent support bound")
    generated = {0}
    for x in labels:
        require(type(x) is int and 0 < x < 512, "independent label range")
        generated |= {x ^ y for y in generated}
    require(len(generated) <= 512, "independent memory bound")
    return len(generated)


def check(witness):
    points = model()
    labels = [label(r) for r in points]
    rows, cut, directions = (witness[k] for k in ("pieces", "cut", "directions"))
    require(len(rows) == 3 and all(len(row) == 112 for row in rows), "row shape")
    require(len(cut) == len(set(cut)) == 40, "independent cut count")
    require(all(type(j) is int and 0 <= j < 112 for j in cut), "independent cut range")
    require(len(directions) == 2 and all(len(r) == 8 for r in directions), "directions")
    require(all(type(x) is int for row in rows for x in row), "exact coefficients")
    supports = [{j for j in range(112) if row[j] != 0} for row in rows]
    require([len(s) for s in supports] == [12, 12, 20], "independent sizes")
    require(
        [span_size([labels[j] for j in s]) for s in supports] == [32, 32, 64],
        "independent binary spans",
    )
    values = [[sum(r[k] * d[k] for k in range(8)) for r in points] for d in directions]
    active = {j for j in range(112) if values[0][j] or values[1][j]}
    union = supports[0] | supports[1] | supports[2]
    require(len(active) == 84 and len(union) == 44, "independent unions")
    require(set(cut) == active - union and not set(cut) & union, "independent cut")
    retained = sorted(set(range(112)) - set(cut))
    require(
        all(rows[0][j] + rows[1][j] == values[0][j] for j in retained),
        "independent first codeword",
    )
    require(
        all(rows[2][j] == values[1][j] for j in retained), "independent second codeword"
    )
    minors = [
        values[0][i] * values[1][j] - values[1][i] * values[0][j]
        for i, j in combinations(retained, 2)
    ]
    require(any(minors), "independent dimension")
    return {
        "span_sizes": [32, 32, 64],
        "cut": 40,
        "union": 44,
        "maximum_absolute_minor": max(map(abs, minors)),
    }


def main():
    authenticate()
    result = check(read_json(PACKAGE / "WITNESS.json"))
    require(result["maximum_absolute_minor"] == 16, "independent minor receipt")
    print("PASS_INDEPENDENT_MIXED_CUT40", result)


if __name__ == "__main__":
    main()
