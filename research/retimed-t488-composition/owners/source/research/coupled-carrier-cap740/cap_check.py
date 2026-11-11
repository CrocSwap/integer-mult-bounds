# SPDX-License-Identifier: Apache-2.0
"""Exact PR3133 fixed-inventory cap and replica-divisibility certificate.

Adapted by Jeremy Diviney with OpenAI Codex assistance from Nick Petalas's
research/rank7-cap740/cap_proof.py (PR3024). Changes: PR3133 inventory and
local bill, residue coefficient 1323 instead of 1341; old exchange proof omitted.
The pattern catalogue and exact interval-dual argument are retained.

The caller must authenticate the root arithmetic module and bind `certificate`
to the words' actual local profile and width inventory. This module checks the
fixed chronology-free pattern relaxation. It does not prove chronological
feasibility or any scalar/native/physical/outer admission obligation.
"""

from fractions import Fraction
from itertools import product
from math import gcd

Q = Fraction
WIDTHS = (4, 5, 6, 7, 8, 9)
CAPS = (8, 16, 32, 48)
BINS = (672, 448, 448, 448)
INVENTORY = (26, 2, 18, 50, 99, 213)
LOCAL = {1: 2433, 2: 724, 3: 228, 4: 102, 5: 20, 8: 8}
Q_ROW = (-3, -6, -12, 0, 0, 0, 1, 2, 3, 4)
TIGHT = (
    (8, (8,)),
    (16, (8, 8)),
    (16, (7, 9)),
    (32, (9, 9, 9)),
    (32, (8, 8, 8, 8)),
    (32, (7, 8, 8, 9)),
    (32, (7, 7, 9, 9)),
    (32, (6, 8, 9, 9)),
    (32, (5, 9, 9, 9)),
    (32, (4, 9, 9, 9)),
    (48, ()),
    (48, (9, 9, 9, 9, 9)),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def patterns():
    """All 2,551 capacity-feasible count vectors; loops have fixed finite bounds."""
    result = []
    for capacity in CAPS:
        for counts in product(*(range(capacity // width + 1) for width in WIDTHS)):
            idle = capacity - sum(w * n for w, n in zip(WIDTHS, counts, strict=True))
            if idle >= 0:
                result.append((capacity, counts, idle))
    need(len(result) == 2551, "changed pattern domain")
    return result


def column(pattern):
    capacity, counts, _ = pattern
    return tuple(int(capacity == cap) for cap in CAPS) + counts


def inverse(matrix):
    """Gauss-Jordan inversion over Q, explicitly restricted to the 10-row model."""
    need(len(matrix) == 10 and all(len(row) == 10 for row in matrix), "matrix shape")
    rows = [
        [Q(value) for value in row] + [Q(i == j) for j in range(10)]
        for i, row in enumerate(matrix)
    ]
    for col in range(10):
        pivot = next((r for r in range(col, 10) if rows[r][col]), None)
        need(pivot is not None, "singular basis")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        divisor = rows[col][col]
        rows[col] = [value / divisor for value in rows[col]]
        for r in range(10):
            if r != col:
                multiple = rows[r][col]
                rows[r] = [
                    a - multiple * b for a, b in zip(rows[r], rows[col], strict=True)
                ]
    return [row[10:] for row in rows]


def basis_data(certificate, catalogue):
    need(
        set(certificate["inventory_per_call"]) == set(map(str, WIDTHS)),
        "inventory keys",
    )
    need(
        tuple(Q(certificate["inventory_per_call"][str(w)]) for w in WIDTHS)
        == INVENTORY,
        "wrong inventory",
    )
    need(
        {int(r): Q(n) for r, n in certificate["local_per_call"].items()} == LOCAL,
        "wrong local profile",
    )
    entries = certificate["basis_patterns"]
    need(len(entries) == 10, "wrong basis size")
    basis, amounts = [], []
    for entry in entries:
        widths = entry["widths"]
        need(len(widths) <= 12 and all(w in WIDTHS for w in widths), "basis widths")
        pattern = (
            entry["capacity"],
            tuple(widths.count(w) for w in WIDTHS),
            entry["capacity"] - sum(widths),
        )
        need(pattern in catalogue, "infeasible basis pattern")
        basis.append(pattern)
        amounts.append(Q(entry["count_per_replica"]))
    need(len(set(basis)) == 10 and all(x >= 0 for x in amounts), "basis feasibility")
    columns = [column(p) for p in basis]
    matrix = [[columns[k][r] for k in range(10)] for r in range(10)]
    rhs = BINS + tuple(9 * n for n in INVENTORY)
    need(
        all(
            sum(matrix[r][k] * amounts[k] for k in range(10)) == rhs[r]
            for r in range(10)
        ),
        "basis does not supply complete counts",
    )
    return basis, amounts, inverse(matrix), rhs


def reduced_cost(pattern, basis, basis_inverse):
    """Exact coefficients of H_r in c_p - a_p^T B^-T c_B."""
    coefficients = {pattern[2]: Q(1)} if pattern[2] else {}
    a = column(pattern)
    for k, basic in enumerate(basis):
        if basic[2]:
            amount = -sum(a[j] * basis_inverse[k][j] for j in range(10))
            coefficients[basic[2]] = coefficients.get(basic[2], Q(0)) + amount
    return {rank: value for rank, value in coefficients.items() if value}


def check_invariant(tight, rhs, amounts):
    """A residue identity isolates the only idle-rank-3 tight pattern."""
    for pattern in tight:
        value = sum(a * b for a, b in zip(Q_ROW, column(pattern), strict=True))
        is_five_nines = pattern[0] == 48 and pattern[1] == (0, 0, 0, 0, 0, 5)
        need(value == 20 * is_five_nines, "tight-pattern invariant failed")
    coefficient = sum(a * b for a, b in zip(Q_ROW, rhs, strict=True))
    need(coefficient == 1323 and gcd(coefficient, 20) == 1, "residue coefficient")
    need(
        all((20 * x).denominator == 1 for x in amounts),
        "20 replicas do not integralize the displayed basis",
    )
    return {
        "identity": "20*N_[9,9,9,9,9]@48 = 1323*T",
        "cap_requires_T_multiple_of": 20,
        "first_multiple_of_74": 74 * 20 // gcd(74, 20),
        "scope": "Pattern integrality; chronological sufficiency is not asserted.",
    }


def verify_cap(certificate, root_tools):
    """Recertify the complete relaxation and strictness on the entire root bracket."""
    catalogue = patterns()
    basis, amounts, basis_inverse, rhs = basis_data(certificate, catalogue)
    lower, upper = Q(certificate["cap_lower"]), Q(certificate["cap_upper"])
    need(
        0 < lower < upper <= Q(1, 100) and upper - lower <= Q(1, 10**25), "cap bracket"
    )
    profile = {rank: Q(9 * amount) for rank, amount in LOCAL.items()}
    idle = {}
    for pattern, amount in zip(basis, amounts, strict=True):
        if pattern[2]:
            profile[pattern[2]] = profile.get(pattern[2], Q(0)) + amount
            idle[pattern[2]] = idle.get(pattern[2], Q(0)) + amount
    need(
        {int(r): Q(n) for r, n in certificate["idle_per_replica"].items()} == idle,
        "stored idle differs from primal basis",
    )
    need(sum(r * n for r, n in profile.items()) == 65088, "rank mass")
    need(
        root_tools.moment(profile, lower, 896)[1]
        < 1
        < root_tools.moment(profile, upper, 896)[0],
        "unproved cap root bracket",
    )
    intervals = {
        rank: (root_tools.H(rank, lower)[0], root_tools.H(rank, upper)[1])
        for rank in range(1, 49)
    }
    tight, slacks = [], []
    for pattern in catalogue:
        coefficients = reduced_cost(pattern, basis, basis_inverse)
        if not coefficients:
            tight.append(pattern)
        else:
            slack = sum(
                v * intervals[r][0 if v > 0 else 1] for r, v in coefficients.items()
            )
            need(slack > 0, "reduced cost is not strictly positive on cap bracket")
            slacks.append(slack)
    named = {
        (cap, tuple(w for w, n in zip(WIDTHS, counts, strict=True) for _ in range(n)))
        for cap, counts, _ in tight
    }
    need(named == set(TIGHT) and len(slacks) == 2539, "tight domain differs")
    invariant = check_invariant(tight, rhs, amounts)
    return {
        "idle_per_replica": {str(r): str(n) for r, n in sorted(idle.items())},
        "patterns": len(catalogue),
        "strict_patterns": len(slacks),
        "tight_patterns": len(tight),
        "minimum_slack_lower": str(min(slacks)),
        "cap_lower": str(lower),
        "cap_upper": str(upper),
        "invariant": invariant,
    }

