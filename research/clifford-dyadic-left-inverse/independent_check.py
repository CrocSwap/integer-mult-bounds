#!/usr/bin/env python3
"""Independent finite calibration of the Clifford interpolation construction.

Enumerates one-qubit operators by their entries, not by generator closure.
Expands ordered coordinate words, not commutative polynomial monomials.
No primary checker or predecessor implementation is imported. These finite
checks corroborate PROOF.md; they do not enumerate the four-qubit alphabet.

apoursh, with substantial OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction as F
from itertools import product
import json


def require(condition, message):
    if not condition:
        raise ValueError(message)


def g(real=0, imag=0):
    return (F(real), F(imag))


ZERO, ONE, I = g(), g(1), g(0, 1)
UNITS = (ONE, I, g(-1), g(0, -1))


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def neg(a):
    return (-a[0], -a[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def conj(a):
    return (a[0], -a[1])


def times(a, scalar):
    return (a[0] * scalar, a[1] * scalar)


def total(values):
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


def power(a, exponent):
    result = ONE
    for _ in range(exponent):
        result = mul(result, a)
    return result


def mm(a, b):
    return tuple(total(mul(a[2 * r + k], b[2 * k + c])
                       for k in range(2))
                 for r in range(2) for c in range(2))


def star(a):
    return (conj(a[0]), conj(a[2]), conj(a[1]), conj(a[3]))


def mscale(a, scalar):
    return tuple(mul(scalar, x) for x in a)


def det(a):
    return add(mul(a[0], a[3]), neg(mul(a[1], a[2])))


def adj(a):
    return (a[3], neg(a[1]), neg(a[2]), a[0])


def tr(a):
    return add(a[0], a[3])


ID = (ONE, ZERO, ZERO, ONE)
X = (ZERO, ONE, ONE, ZERO)
Y = (ZERO, neg(I), I, ZERO)
Z = (ONE, ZERO, ZERO, g(-1))
PAULIS = (X, Y, Z) + tuple(mscale(a, g(-1)) for a in (X, Y, Z))


def canonical(a):
    return min(mscale(a, phase) for phase in UNITS)


def operators():
    """Enumerate all axis/flat one-qubit entries; verify all Pauli images."""
    alphabet = (ZERO,) + UNITS + tuple(g(F(a, 2), F(b, 2))
                                      for a in (-1, 1) for b in (-1, 1))
    columns = [c for c in product(alphabet, repeat=2)
               if total(mul(conj(z), z) for z in c) == ONE]
    raw = []
    for left, right in product(columns, repeat=2):
        if total(mul(conj(a), b) for a, b in zip(left, right)) != ZERO:
            continue
        a = (left[0], right[0], left[1], right[1])
        require(mm(star(a), a) == ID, "entry enumeration lost unitarity")
        require(det(a) in UNITS, "determinant is not a Gaussian unit")
        require(all(mm(mm(a, p), star(a)) in PAULIS for p in (X, Y, Z)),
                "enumerated operator does not normalize Paulis")
        raw.append(a)
    require(len(raw) == len(set(raw)) == 96, "wrong entry enumeration")
    reps = sorted(set(canonical(a) for a in raw))
    require(len(reps) == 24, "wrong projective alphabet size")
    images = {(mm(mm(a, X), star(a)), mm(mm(a, Z), star(a))) for a in reps}
    require(len(images) == 24, "Pauli images do not distinguish cosets")
    # There are precisely 6*4 ordered anticommuting signed axes.
    all_images = {(p, q) for p in PAULIS for q in PAULIS
                  if mm(p, q) == mscale(mm(q, p), g(-1))}
    require(images == all_images, "one-qubit calibration is not complete")
    return raw, reps


def scalar_detector(target, value, mode="correct"):
    determinant = det(value)
    answer = ONE
    for p in ((X,) if mode == "omit_generator" else (X, Z)):
        q = mm(mm(target, p), star(target))
        t = times(tr(mm(mm(mm(q, value), p), adj(value))), F(1, 2))
        if mode == "unsigned":
            term = mul(t, t)
        elif mode == "omit_determinant":
            term = times(add(mul(t, t), t), F(1, 2))
        else:
            term = times(add(mul(t, t), mul(t, determinant)), F(1, 2))
        answer = mul(answer, term)
    return answer


def merge_term(poly, word, value):
    value = add(poly.get(word, ZERO), value)
    if value == ZERO:
        poly.pop(word, None)
    else:
        poly[word] = value


def word_add(a, b):
    result = dict(a)
    for word, value in b.items():
        merge_term(result, word, value)
    return result


def word_times(a, scalar):
    return {w: times(z, scalar) for w, z in a.items() if z != ZERO}


def word_mul(a, b):
    result = {}
    for wa, ca in a.items():
        for wb, cb in b.items():
            merge_term(result, wa + wb, mul(ca, cb))
    return result


def ordered_row(target):
    """Expand straight-line products by concatenation; never symmetrize."""
    determinant = {(0, 3): ONE, (1, 2): g(-1)}
    # adj(X)_(l,i) is a signed coordinate of the generic 2-by-2 X.
    adj_coordinates = ((3, 1), (1, -1), (2, -1), (0, 1))
    result = {(): ONE}
    for p in (X, Z):
        q = mm(mm(target, p), star(target))
        t = {}
        # Tr(Q X P adj(X)) = sum_(i,j,k,l) Q_ij X_jk P_kl adj(X)_li.
        for i, j, k, ell in product(range(2), repeat=4):
            coordinate, sign = adj_coordinates[2 * ell + i]
            coefficient = times(mul(q[2 * i + j], p[2 * k + ell]),
                                F(sign, 2))
            merge_term(t, (2 * j + k, coordinate), coefficient)
        h = word_times(word_add(word_mul(t, t), word_mul(t, determinant)), F(1, 2))
        result = word_mul(result, h)
    require(result and all(len(w) == 8 for w in result), "wrong ordered degree")
    for coefficient in result.values():
        require(all(z.denominator & (z.denominator - 1) == 0 for z in coefficient),
                "ordered coefficient has an odd denominator")
    return result


def tensor_coordinate(word):
    """Coordinate in row-major vec(U tensor ... tensor U)."""
    row = col = 0
    for position in word:
        row = 2 * row + position // 2
        col = 2 * col + position % 2
    return row * (2 ** len(word)) + col


def coordinate_word(index, width):
    """Independently unpack a row-major tensor coordinate."""
    row, col = divmod(index, 2 ** width)
    return tuple(2 * ((row >> bit) & 1) + ((col >> bit) & 1)
                 for bit in range(width - 1, -1, -1))


def evaluate_word(value, word):
    answer = ONE
    for position in word:
        answer = mul(answer, value[position])
    return answer


def check():
    raw, reps = operators()
    phase_cases = 0
    negative_local_factors = 0
    for target in reps:
        for value in raw:
            expected = ONE if canonical(value) == target else ZERO
            interpolated = scalar_detector(target, value)
            require(interpolated == expected,
                    "entry-enumerated interpolation failed")
            if expected == ONE and det(value) in (I, neg(I)):
                negative_local_factors += 1
            ell = times(tr(mm(star(target), value)), F(1, 2))
            for width in (8, 9, 11):
                actual = mul(interpolated, power(ell, width - 8))
                # At a matching phase lift, ell is precisely that scalar phase.
                wanted = power(ell, width) if expected == ONE else ZERO
                require(actual == wanted, "phase-covariant padding failed")
                phase_cases += 1
    require(negative_local_factors == 48, "phase cancellation control absent")

    rows = [ordered_row(a) for a in reps]
    coordinates = {tensor_coordinate(w) for row in rows for w in row}
    words = {w for row in rows for w in row}
    require(len(words) == len(coordinates), "ordered tensor coordinates collide")
    require(all(coordinate_word(tensor_coordinate(w), 8) == w for w in words),
            "tensor word/coordinate convention disagrees")
    # Width-eight one-qubit normalization is d^(f/2)=16.
    columns = [{w: times(evaluate_word(a, coordinate_word(tensor_coordinate(w), 8)),
                        F(1, 16)) for w in words} for a in reps]
    for i, row in enumerate(rows):
        for j, column in enumerate(columns):
            value = total(mul(times(c, 16), column[w]) for w, c in row.items())
            require(value == (ONE if i == j else ZERO),
                    "ordered tensor left inverse failed")

    faults = {}
    for mode in ("unsigned", "omit_generator", "omit_determinant"):
        faults[mode] = any(scalar_detector(a, b, mode) != (ONE if i == j else ZERO)
                           for i, a in enumerate(reps) for j, b in enumerate(reps))
        require(faults[mode], "detector fault escaped: " + mode)
    faults["missing_normalization"] = any(
        total(mul(c, columns[i][w]) for w, c in row.items()) != ONE
        for i, row in enumerate(rows))
    require(faults["missing_normalization"], "normalization fault escaped")
    faults["transpose_tensor_entry"] = any(
        scalar_detector(a, (b[0], b[2], b[1], b[3])) != (ONE if i == j else ZERO)
        for i, a in enumerate(reps) for j, b in enumerate(reps))
    require(faults["transpose_tensor_entry"], "coordinate transpose fault escaped")

    # Non-Clifford unitary control: CCZ at three qubits is Gaussian dyadic,
    # unitary and determinant -1, but its X-generator correlations are 1/2.
    signs = (1,) * 7 + (-1,)
    correlations = [F(sum(signs[x] * signs[x ^ (1 << j)] for x in range(8)), 8)
                    for j in range(3)]
    require(correlations == [F(1, 2)] * 3, "CCZ correlation control changed")
    ccz_value = F(1)
    for u in correlations + [F(1)] * 3:
        ccz_value *= (u * u + u) / 2
    require(ccz_value == F(27, 512), "non-Clifford scope control changed")
    return {
        "status": "PASS_INDEPENDENT_CLIFFORD_DYADIC_LEFT_INVERSE",
        "entry_enumerated_matrices": len(raw),
        "projective_one_qubit_operators": len(reps),
        "scalar_interpolation_pairs": len(raw) * len(reps),
        "phase_padding_cases": phase_cases,
        "matched_lifts_with_negative_local_factors": negative_local_factors,
        "ordered_tensor_identity_entries": len(reps) ** 2,
        "ordered_row_terms": sum(len(row) for row in rows),
        "distinct_tensor_coordinates": len(coordinates),
        "rejected_faults": sorted(faults),
        "non_clifford_control": str(ccz_value),
        "scope": "Independent one-qubit ordered-word calibration and three-qubit scope control; no four-qubit enumeration or physical cost claim.",
    }


if __name__ == "__main__":
    print(json.dumps(check(), indent=2, sort_keys=True))
