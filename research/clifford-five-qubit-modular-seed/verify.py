"""Exact restrictions to the 64-element Bell stabilizer, using integer arithmetic."""
import argparse
from fractions import Fraction
import json
from math import prod
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SP, PLUS, MINUS = "S10(2)", "O10+(2)", "O10-(2)"
# ATLAS positions are one-based throughout the data and proof.
EXPECTED = {SP: {5: 162, 7: 187, 11: 195, 17: 192, 31: 195},
            PLUS: {3: 39}, MINUS: {3: 35}}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def recover(ordinary, sparse, count):
    """Solve D times the Brauer columns = ordinary columns; check every row."""
    require(len(ordinary) == len(sparse), "Missing ordinary reduction")
    pending = {}
    for i, encoded in enumerate(sparse):
        row = dict(encoded)
        require(len(row) == len(encoded) and row and
                all(1 <= j <= count and a > 0 for j, a in row.items()),
                "Invalid sparse decomposition entry")
        pending[i] = row
    solutions = {}
    while pending:
        before = len(pending)
        for i, row in list(pending.items()):
            unknown = row.keys() - solutions.keys()
            if len(unknown) > 1:
                continue
            known = [(a, solutions[j]) for j, a in row.items() if j in solutions]
            residual = [v-sum(a*r[t] for a, r in known) for t, v in enumerate(ordinary[i])]
            if unknown:
                j, = unknown
                a = row[j]
                require(all(v % a == 0 for v in residual), "Nonintegral Brauer entry")
                solutions[j] = [v // a for v in residual]
            else:
                require(not any(residual), "Inconsistent decomposition equation")
            del pending[i]
        require(len(pending) < before, "Decomposition system lacks a triangular pivot")
    require(len(solutions) == count, "Incomplete Brauer character coverage")
    return [solutions[j] for j in range(1, count+1)]


def restrictions(row):
    degree, lo, hi = row
    # Characters of the binary alternating-four-space are indexed by dual
    # alternating forms of ranks 0, 2 and 4. The three orbit sizes are 1,35,28.
    fourier = (degree+35*lo+28*hi, degree+3*lo-4*hi, degree-5*lo+4*hi)
    require(degree > 0 and all(v >= 0 and v % 64 == 0 for v in fourier),
            "Not a character of the elementary abelian seed")
    a, b, c = (v // 64 for v in fourier)
    require(a+35*b+28*c == degree, "Seed restriction has wrong dimension")
    return a, b, c


def ordinary_control(group, rows):
    sp_order = 2**25 * prod(4**i-1 for i in range(1, 6))
    order = {SP: sp_order, PLUS: sp_order // (528*2), MINUS: sp_order // (496*2)}[group]
    class_count, c2, c4 = {SP: (198, 285380444160, 1132462080),
                            PLUS: (97, 990904320, 11796480),
                            MINUS: (115, 1274019840, 35389440)}[group]
    require(len(rows) == class_count, "Missing ordinary character")
    columns = list(zip(*rows, strict=True))
    require(len(columns) == 3, "Missing class column")
    squared = [sum(x*x for x in col) for col in columns]
    require(squared == [order, c2, c4], "Wrong ordinary column norms")
    for i in range(3):
        for j in range(i):
            require(sum(a*b for a, b in zip(columns[i], columns[j], strict=True)) == 0,
                    "Ordinary columns are not orthogonal")
    return [restrictions(row)[0] for row in rows]


def quantitative_three(tables):
    plus, minus = tables[PLUS], tables[MINUS]
    # These inequalities include the zero-fixed rows, where both sides vanish.
    for d, t, u in plus:
        require(31*t+d >= 32*restrictions([d, t, u])[0], "Plus trace inequality")
    for d, t, u in minus:
        require(1309*t+67*d <= 29920*restrictions([d, t, u])[0], "Minus trace inequality")
    lower = Fraction(31*67-1309, 31*29920-1309*32)
    require(lower == Fraction(6, 6919), "Universal fixed fraction")

    # A pair of subgroup modules attains the linear relaxation on (1,c2,c4).
    pos = [168*a+223*b for a, b in zip(plus[0], plus[3], strict=True)]
    neg = [6*a+7*b for a, b in zip(minus[12], minus[6], strict=True)]
    require(pos == neg == [193732, -6076, 1060] and
            Fraction(restrictions(pos)[0], pos[0]) == lower, "Tight restriction witness")
    print("PASS universal dimension fraction 6/6919; tight on the three shared columns")


def verify(data, gap_rows=None):
    require(list(data) == list(EXPECTED), "Unexpected groups")
    if gap_rows is not None:
        external = iter(gap_rows)
    bad_three = {}
    orthogonal = {}
    for group, counts in EXPECTED.items():
        ordinary = data[group]["ordinary"]
        fixed = ordinary_control(group, ordinary)
        if group == SP:
            require(min(fixed) == fixed.count(1) == 1, "Ordinary symplectic positivity")
            require(min(Fraction(b, r[0]) for b, r in zip(fixed, ordinary, strict=True)) ==
                    Fraction(15, 5797), "Ordinary fixed fraction")
        tables = data[group]["reduction"]
        require({int(p) for p in tables} == set(counts), "Missing prime")
        for p, count in counts.items():
            matrix = tables[str(p)]
            rows = recover(ordinary, matrix, count)
            if gap_rows is not None:
                require(rows == next(external), "Mismatch against native GAP Brauer values")
            fixed = [restrictions(row)[0] for row in rows]
            if p == 3:
                orthogonal[group] = rows
                bad_three[group] = [(i, r) for i, (r, f) in enumerate(zip(rows, fixed), 1) if f == 0]
                print(f"{group} p=3  rows={count}  zero seed rows={bad_three[group]}")
            else:
                require(min(fixed) == fixed.count(1) == 1 and min(fixed[1:]) == 15,
                        "Unexpected modular fixed dimensions")
                fraction = min(Fraction(b, r[0]) for b, r in zip(fixed, rows, strict=True))
                expected = Fraction(45, 40393) if p == 7 else Fraction(15, 5797)
                require(fraction == expected and fraction > Fraction(6, 6919), "Modular fixed fraction")
                print(f"{group} p={p}  rows={count}  minimum nontrivial dimension=15  fixed fraction={fraction}")
    if gap_rows is not None:
        require(next(external, None) is None, "Extra GAP table")
    require(bad_three[PLUS] == [(4, [868,-28,4]), (10, [13888,-448,64])] and
            bad_three[MINUS] == [(7, [5236,-268,148])], "Changed characteristic-three obstructions")
    ratios = {g: {Fraction(r[1], r[0]) for _, r in bad_three[g]} for g in (PLUS, MINUS)}
    require(ratios == {PLUS: {Fraction(-1,31)}, MINUS: {Fraction(-67,1309)}} and
            ratios[PLUS].isdisjoint(ratios[MINUS]), "Restrictions do not exclude an obstruction")
    quantitative_three(orthogonal)
    print("PASS five-qubit width 15: 931 symplectic and 74 orthogonal Brauer rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gap-rows", type=Path, help="Optional numerical output from gap_rows.g")
    args = parser.parse_args()
    saved = json.loads((ROOT/"CHARACTERS.json").read_text())
    gap_rows = json.loads(args.gap_rows.read_text()) if args.gap_rows else None
    verify(saved, gap_rows)
