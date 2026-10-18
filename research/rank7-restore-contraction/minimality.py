# SPDX-License-Identifier: Apache-2.0
"""Universal two-gate exclusion over Q, not a coefficient enumeration."""

from itertools import product

from frames import require

ZERO = (0, 0, 0, 0)
ONE = (1, 0, 0, 0)
KINDS = ("add_x", "add_y", "scale_x", "scale_y")
TARGET = ((0, -1), (1, -1))


def times_variable(polynomial, variable):
    """Coefficients of 1,a,b,ab. Each of two gates has its own variable."""
    result = [0] * 4
    for mask, value in enumerate(polynomial):
        require(not value or mask & variable == 0, "multiaffine two-gate polynomial")
        if value:
            result[mask | variable] += value
    return tuple(result)


def symbolic_pair(kinds):
    require(len(kinds) == 2 and all(k in KINDS for k in kinds), "two gate kinds")
    rows = [[ONE, ZERO], [ZERO, ONE]]
    for kind, variable in zip(kinds, (1, 2), strict=True):
        target = 0 if kind.endswith("x") else 1
        source = 1 - target if kind.startswith("add") else target
        scaled = [times_variable(p, variable) for p in rows[source]]
        if kind.startswith("scale"):
            rows[target] = scaled
        else:
            rows[target] = [tuple(a + b for a, b in zip(p, q, strict=True))
                            for p, q in zip(rows[target], scaled, strict=True)]
    return rows


def exclude_two(target=TARGET):
    """Every template has a forced constant entry incompatible with target."""
    require(len(target) == 2 and all(len(row) == 2 for row in target), "2x2 target")
    witnesses = []
    for kinds in product(KINDS, repeat=2):
        rows = symbolic_pair(kinds)
        mismatch = [(i, j, rows[i][j][0]) for i in range(2) for j in range(2)
                    if rows[i][j][1:] == (0, 0, 0) and rows[i][j][0] != target[i][j]]
        require(bool(mismatch), f"no universal obstruction for {kinds}")
        i, j, value = mismatch[0]
        witnesses.append({"gates": list(kinds), "entry": [i, j],
                          "forced": value, "required": target[i][j]})
    require(len(witnesses) == 16, "all ordered pairs of gate kinds")
    return witnesses
