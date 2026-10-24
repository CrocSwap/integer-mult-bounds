#!/usr/bin/env python3
"""Exact finite calibration for PROOF.md; no native or theorem admission.

Apache-2.0. Substantial OpenAI Codex assistance.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json
import platform
import random


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank(rows):
    if not rows:
        return 0
    a = [[F(x) for x in row] for row in rows]
    p = 0
    for j in range(len(a[0])):
        k = next((i for i in range(p, len(a)) if a[i][j]), None)
        if k is None:
            continue
        a[p], a[k] = a[k], a[p]
        z = a[p][j]
        a[p] = [x / z for x in a[p]]
        for i in range(p + 1, len(a)):
            z = a[i][j]
            a[i] = [x - z * y for x, y in zip(a[i], a[p])]
        p += 1
        if p == len(a):
            break
    return p


def functional(rows, values):
    """Solve rows times ell = values, choosing zero for free coordinates."""
    a = [[F(x) for x in row] + [F(y)] for row, y in zip(rows, values)]
    width = len(rows[0]); pivots = []; p = 0
    for j in range(width):
        k = next((i for i in range(p, len(a)) if a[i][j]), None)
        if k is None:
            continue
        a[p], a[k] = a[k], a[p]
        z = a[p][j]; a[p] = [x / z for x in a[p]]
        for i in range(len(a)):
            if i != p:
                z = a[i][j]
                a[i] = [x - z * y for x, y in zip(a[i], a[p])]
        pivots.append(j); p += 1
        if p == len(a):
            break
    need(all(any(row[:-1]) or not row[-1] for row in a), "Inconsistent separator")
    answer = [F(0)] * width
    for i, j in enumerate(pivots):
        answer[j] = a[i][-1]
    return answer


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def separator(vectors, target, width):
    m = len(vectors); r = rank(vectors)
    need(width >= m - r + 1, "Below the guaranteed separation width")
    for i in range(m):
        need(any(vectors[i]), "Zero vector")
        for j in range(i):
            need(rank([vectors[i], vectors[j]]) == 2, "Projective duplicate")
    chosen = []; basis = [vectors[target]]
    for j, v in enumerate(vectors):
        if j != target and rank(basis + [v]) > len(basis):
            chosen.append(j); basis.append(v)
    need(len(basis) == r, "Basis construction failed")
    first = functional(basis, [1] + [0] * (r - 1))
    factors = [first]
    for j, v in enumerate(vectors):
        if j != target and j not in chosen:
            factors.append(functional([vectors[target], v], [1, 0]))
    factors.extend([first] * (width - len(factors)))
    return factors


def check_separator(vectors, target, factors):
    for j, v in enumerate(vectors):
        value = F(1)
        for ell in factors:
            value *= dot(ell, v)
        need(value == int(j == target), "Invalid isolating certificate")


def exponents(total, dimensions):
    if dimensions == 1:
        yield (total,)
    else:
        for a in range(total + 1):
            for tail in exponents(total - a, dimensions - 1):
                yield (a,) + tail


def symmetric_rank(vectors, width):
    # Select one coordinate per orbit of equal tensor entries; no binomial
    # coefficient is introduced, including in positive characteristic.
    rows = []
    for powers in exponents(width, len(vectors[0])):
        row = []
        for v in vectors:
            z = F(1)
            for a, k in zip(v, powers):
                z *= a ** k
            row.append(z)
        rows.append(row)
    return rank(rows)


def separator_checks():
    rng = random.Random(1163); cases = 0; certificates = 0
    for d in range(2, 6):
        for extra in range(5):
            for _ in range(3):
                vectors = [tuple(F(int(i == j)) for j in range(d)) for i in range(d)]
                while len(vectors) < d + extra:
                    v = tuple(F(rng.randrange(-2, 3)) for _ in range(d))
                    if not any(v):
                        continue
                    scale = next(x for x in v if x)
                    v = tuple(x / scale for x in v)
                    if v not in vectors:
                        vectors.append(v)
                width = len(vectors) - rank(vectors) + 1
                for i in range(len(vectors)):
                    check_separator(vectors, i, separator(vectors, i, width))
                    certificates += 1
                need(symmetric_rank(vectors, width) == len(vectors), "Expanded rank mismatch")
                cases += 1
    moving = []
    for f in range(1, 8):
        v = [(F(1), F(j + 1, f + 2)) for j in range(f + 1)]
        for i in range(len(v)):
            check_separator(v, i, separator(v, i, f))
        moving.append({"f": f, "terms": len(v), "rank": symmetric_rank(v, f)})
    v = [(1, 0, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0),
         (1, 2, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
    need(rank(v) == 4 and symmetric_rank(v, 2) == 5 and symmetric_rank(v, 3) == 6,
         "Sharp rank-refined boundary failed")
    try:
        separator([(1, 1), (-1, -1)], 0, 2)
    except ValueError:
        pass
    else:
        raise ValueError("Proportional-letter mutation accepted")
    # Over F2, (1,1)=(1,0)+(0,1), but their tensor squares are independent.
    square_rows = [[1, 0, 1], [0, 0, 1], [0, 1, 1]]
    need(abs(determinant3(square_rows)) == 1, "F2 square-rank control")
    return {"rational_sets": cases, "dual_certificates": certificates,
            "moving_supports": moving, "rank_refined_boundary": {"m": 6, "r": 4, "rank_at_2": 5, "rank_at_3": 6},
            "projective_duplicate_rejected": True, "F2_trine_square_rank": 3}


def determinant3(a):
    return (a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
            - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
            + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0]))


def kron(a, b):
    return [[x * y for x in row_a for y in row_b] for row_a in a for row_b in b]


def tensor_power(a, f):
    out = [[1]]
    for _ in range(f):
        out = kron(out, a)
    return out


def coefficient_checks():
    identity = [[1, 0], [0, 1]]
    x = [[0, 1], [1, 0]]; z = [[1, 0], [0, -1]]
    coefficients = [[[1, 2], [0, 1]], [[0, 1], [-1, 0]], [[2, 0], [1, 1]]]
    coefficient_mass = sum(y*y for b in coefficients for row in b for y in row)
    for f in range(1, 5):
        terms = [kron(b, tensor_power(u, f)) for b, u in zip(coefficients, [identity, x, z])]
        total = [[sum(t[i][j] for t in terms) for j in range(len(terms[0]))]
                 for i in range(len(terms[0]))]
        need(sum(y*y for row in total for y in row) == 2**f * coefficient_mass,
             "Operator-coefficient Gram identity failed")
    negative_identity = [[-1, 0], [0, -1]]
    for f in [1, 2, 3, 4]:
        a, b = tensor_power(identity, f), tensor_power(negative_identity, f)
        need(all(b[i][j] == (-1)**f*a[i][j] for i in range(len(a)) for j in range(len(a))),
             "Projective phase power failed")
    return {"matrix_coefficient_orthogonal_Gram_cases": 4,
            "projective_phase_powers_checked": [1, 2, 3, 4],
            "scope": "Finite matrix-coefficient and phase calibration; no auxiliary physical implementation."}


class G:
    """Gaussian rationals, with no floating-point arithmetic."""
    def __init__(self, a=0, b=0):
        if isinstance(a, G):
            self.a, self.b = a.a, a.b
        else:
            self.a, self.b = F(a), F(b)

    def __add__(self, y):
        y = G(y); return G(self.a + y.a, self.b + y.b)
    __radd__ = __add__
    def __neg__(self):
        return G(-self.a, -self.b)
    def __sub__(self, y):
        return self + -G(y)
    def __mul__(self, y):
        y = G(y); return G(self.a * y.a - self.b * y.b, self.a * y.b + self.b * y.a)
    __rmul__ = __mul__
    def __pow__(self, k):
        need(type(k) is int and k >= 0, "Nonnegative power required")
        out = G(1); base = self
        while k:
            if k % 2:
                out = out * base
            base = base * base; k //= 2
        return out
    def __bool__(self):
        return bool(self.a or self.b)
    def norm2(self):
        return self.a * self.a + self.b * self.b


def evaluate(coeff, z):
    answer = G(0)
    for c in reversed(coeff):
        answer = answer * z + c
    return answer


def sharp_escape_checks():
    alpha = G(F(3, 5), F(4, 5)); out = []
    for f in range(1, 9):
        coeff = [G(1)]
        roots = [alpha ** k for k in range(f + 1)]
        for root in roots:
            new = [G(0)] * (len(coeff) + 1)
            for j, c in enumerate(coeff):
                new[j] = new[j] - root * c
                new[j + 1] = new[j + 1] + c
            coeff = new
        need(len(coeff) == f + 2 and all(coeff), "Sharp escape lost a term")
        need(all(not evaluate(coeff, z) for z in roots), "Annihilator failed")
        need(bool(evaluate(coeff, alpha ** (f + 1))), "Width-increment mutation accepted")
        need(bool(evaluate(coeff[:-1], G(1))), "Omitted-term mutation accepted")
        need(all(bool(roots[j] - roots[i]) for i in range(len(roots)) for j in range(i)),
             "Repeated eigenvalue")
        scale = 5 ** (f * (f + 1) // 2)
        for c in coeff:
            for x in (c.a, c.b):
                need(scale % x.denominator == 0, "Coefficient denominator bound failed")
                need(abs(x * scale) <= 2 ** (f + 1) * scale, "Numerator bound failed")
        out.append({"f": f, "terms": len(coeff), "spectrum_points": len(roots),
                    "coefficient_component_max_bits": max(max(abs(x.numerator).bit_length(), x.denominator.bit_length()) for c in coeff for x in (c.a, c.b)),
                    "exact_zero": True, "fails_at_next_width": True})
    near = []
    for f in range(1, 13):
        t = f * f; beta = G(F(t * t - 1, t * t + 1), F(2 * t, t * t + 1))
        need(beta.norm2() == 1 and bool(beta - G(1)), "Moving-unitary fixture failed")
        error2 = max((beta ** k - G(1)).norm2() for k in range(f + 1))
        need(0 < error2 <= F(4, f * f), "Approximate escape bound failed")
        near.append({"f": f, "error_squared": str(error2), "upper_squared": str(F(4, f*f))})
    return {"single_fixed_generator": "diag(1,(3+4i)/5)", "sharp_exact_identities": out,
            "two_term_approximate_escape": near,
            "scope": "Exact diagonal-spectrum calibration only; no native recoding or precision admission."}


def source_check(package, root):
    fixture = json.loads((package / "FIXTURE.json").read_text())
    if root:
        manifest = json.loads((package / "SOURCES.json").read_text())
        for pin in manifest["files"]:
            need(hashlib.sha256((root / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                 "Changed source: " + pin["path"])
        code = json.loads((root / "research/coded-native-caller/CODE.json").read_text())
        normalizers = json.loads((root / "research/coded-native-caller/NORMALIZERS.json").read_text())
        need(fixture["A"] == code["A"] and fixture["mode_columns"] == normalizers["mode_columns"],
             "Source excerpt mismatch")
        need(fixture["ports"] == [{"q": x["q"], "G_rows": x["G_rows"]} for x in normalizers["ports"]],
             "Port excerpt mismatch")
    a = [[F(x) for x in row] for row in fixture["A"]]; n = len(a)
    columns = fixture["mode_columns"]
    need(n == 112 and len(columns) == 8 and all(len(x) == n for x in columns), "Fixture shape")
    for i in range(8):
        for j in range(8):
            need(dot(columns[i], columns[j]) == 56 * int(i == j), "Mode Gram mismatch")
    for i in range(n):
        for j in range(n):
            expected = int(i == j) - F(sum(columns[k][i] * columns[k][j] for k in range(8)), 4)
            need(a[i][j] == expected, "Code factor mismatch")
        need(a[i][i] == 0, "Zero-diagonal premise failed")
    row = [sum(bool(x) for x in v) for v in a]
    col = [sum(bool(a[i][j]) for i in range(n)) for j in range(n)]
    need(set(row) == {52} and set(col) == {52}, "Code support mismatch")
    ports = fixture["ports"]; need(len(ports) == n and len({x["q"] for x in ports}) == n, "Port distinctness")
    for p in ports:
        rows = p["G_rows"]
        need(len(rows) == 9, "Binary map shape")
        for i in range(9):
            for j in range(9):
                need((rows[i] & rows[j]).bit_count() % 2 == int(i == j), "Binary orthogonality")
        need(sum((r & 1) << i for i, r in enumerate(rows)) == p["q"], "Gq convention mismatch")
    return {"owners": n, "nonzero_code_entries": sum(row), "row_support": 52, "column_support": 52,
            "terminal_multiplier": 2704, "equal_support_multiplier": 2705,
            "all_code_entries_checked": n*n, "distinct_binary_port_maps_checked": n,
            "scope": "Exact scalar factor, support and one-column port excerpt checks. No original producer, full phase, native tape, compiler or admission replay."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args(); package = Path(__file__).resolve().parent
    result = {"status": "PASS_SUPPORT_WIDTH_FINITE_CALIBRATION_NO_NEW_KAPPA",
              "python": platform.python_version(),
              "separators": separator_checks(), "sharpness_and_approximation": sharp_escape_checks(),
              "operator_coefficients": coefficient_checks(),
              "source_structure": source_check(package, args.source_root)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
