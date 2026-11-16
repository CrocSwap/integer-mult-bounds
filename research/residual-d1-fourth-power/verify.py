#!/usr/bin/env python3
"""D1^4 = I does not kill the residual word Q^{-1} C1 Q^2 C1 C3 D1 D3.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
The predecessor group algebra is imported unchanged. Checks are explicit
need failures, so the optimized run still executes them.
"""
from fractions import Fraction
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
RESIDUAL = (-1, 2, 1, 1, 2, 3)
TARGET = (-1, 2)
PINS = {
    "research/coded-active-feedback/search.py":
        "1383010827af29a1b0e595e2c1aa2ffad461b266ffc9f936efce1603ff9f5eb6",
    "research/coded-native-caller/gauge.py":
        "390391d291353741c89daea999d483660ca185987ed96a15b82576280c487cad",
    "research/coded-active-feedback/PROOF.md":
        "c6233d2759811190c7ea1be455c9351b61c29f6a8afc8584e7bc0dfbc00f3a3d",
    "research/coded-native-caller/PHYSICAL.md":
        "4321b159ff8d3fe705419adaaa1beef75606e869e34341bda553f17d598a6078",
    "research/moving-stage-restoration-tariff/PROOF.md":
        "36d3b13ab3919559fde46b1c33f856379cd5b2bab06d835ddf7e177c96868712",
    "certificates/selected-result.json":
        "9b8d0eea95b3bf0dfcb7938a732a6439b87a2685dec2a5ab9e525b3b34debbfa",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_search():
    path = ROOT / "research/coded-active-feedback/search.py"
    spec = importlib.util.spec_from_file_location("active_feedback_search_pinned", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def gadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def gmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def matmul(left, right):
    size = len(left)
    out = [[(0, 0)] * size for _ in range(size)]
    for i in range(size):
        for k in range(size):
            if left[i][k] == (0, 0):
                continue
            for j in range(size):
                if right[k][j] != (0, 0):
                    out[i][j] = gadd(out[i][j], gmul(left[i][k], right[k][j]))
    return out


def matpow(matrix, exponent):
    size = len(matrix)
    out = [[(1 if i == j else 0, 0) for j in range(size)] for i in range(size)]
    while exponent:
        if exponent & 1:
            out = matmul(out, matrix)
        matrix = matmul(matrix, matrix)
        exponent >>= 1
    return out


def eye(size):
    return [[(1 if i == j else 0, 0) for j in range(size)] for i in range(size)]


def same(left, right):
    return all(left[i][j] == right[i][j]
               for i in range(len(left)) for j in range(len(left)))


def residue(element):
    """Coset sums for the central quotient by D1^4 = I. D3 is not reduced."""
    totals = {}
    for (word, degree), value in element.items():
        key = (word, (degree[0] % 4, degree[1]))
        totals[key] = totals.get(key, Fraction(0)) + value
        if totals[key] == 0:
            del totals[key]
    return totals


def q_parity(element):
    total = Fraction(0)
    for (word, degree), value in element.items():
        need(degree == (0, 0), "parity character left the D-exponent-0 line")
        sign = -1 if sum(1 for letter in word if abs(letter) == 1) % 2 else 1
        total += value * sign
    return total


def one_axis_gaussian():
    """(2A)^2 = 4X and (2A)^4 = 16 I for A = [[a, b], [b, a]]."""
    two = [[(1, 1), (1, -1)], [(1, -1), (1, 1)]]
    square = matmul(two, two)
    fourth = matmul(square, square)
    need(square == [[(0, 0), (4, 0)], [(4, 0), (0, 0)]],
         "One-axis Gaussian square is not 4X")
    need(fourth == [[(16, 0), (0, 0)], [(0, 0), (16, 0)]],
         "One-axis Gaussian fourth power is not 16 I")


def separating_representation(algebra, qi, c1, q, c3, d1, d3):
    """Monomial 8-dimensional image. Also satisfies D3^4 = I, which is extra."""
    identity = eye(8)
    phase = (0, 1)

    def diagonal(bit):
        matrix = eye(8)
        for index in range(8):
            if (index >> bit) & 1:
                matrix[index][index] = phase
        return matrix

    def swap(bit_a, bit_b):
        matrix = [[(0, 0)] * 8 for _ in range(8)]
        for index in range(8):
            bits = [(index >> bit) & 1 for bit in range(3)]
            bits[bit_a], bits[bit_b] = bits[bit_b], bits[bit_a]
            destination = bits[0] + 2 * bits[1] + 4 * bits[2]
            matrix[destination][index] = (1, 0)
        return matrix

    q_matrix = diagonal(0)
    d1_matrix = diagonal(1)
    d3_matrix = diagonal(2)
    c1_matrix = swap(0, 1)
    c3_matrix = swap(0, 2)
    q_inverse = matpow(q_matrix, 3)
    need(same(matpow(q_matrix, 4), identity), "Representation lost Q^4 = I")
    need(same(matmul(c1_matrix, c1_matrix), identity), "Representation lost C1^2 = I")
    need(same(matmul(c3_matrix, c3_matrix), identity), "Representation lost C3^2 = I")
    need(same(matpow(d1_matrix, 4), identity), "Representation lost D1^4 = I")
    need(same(matpow(d3_matrix, 4), identity),
         "Representation was expected to satisfy the extra equation D3^4 = I")
    braid = c1_matrix
    for factor in (c3_matrix, c1_matrix, c3_matrix, c1_matrix, c3_matrix):
        braid = matmul(braid, factor)
    need(same(braid, identity),
         "Representation was expected to satisfy the extra equation (C1 C3)^3 = I")
    need(same(matmul(d1_matrix, q_matrix), matmul(q_matrix, d1_matrix)),
         "Representation lost [D1, Q] = 0")
    need(same(matmul(d3_matrix, q_matrix), matmul(q_matrix, d3_matrix)),
         "Representation lost [D3, Q] = 0")
    need(same(matmul(d1_matrix, d3_matrix), matmul(d3_matrix, d1_matrix)),
         "Representation lost [D1, D3] = 0")
    need(same(matmul(d1_matrix, c3_matrix), matmul(c3_matrix, d1_matrix)),
         "Representation lost [D1, C3] = 0")
    need(same(matmul(d3_matrix, c1_matrix), matmul(c1_matrix, d3_matrix)),
         "Representation lost [D3, C1] = 0")
    need(not same(matmul(c1_matrix, q_matrix), matmul(q_matrix, c1_matrix)),
         "Representation collapsed [C1, Q]")
    conjugated = matmul(q_inverse, matmul(c1_matrix, matmul(q_matrix, d1_matrix)))
    need(same(matmul(d1_matrix, c1_matrix), conjugated),
         "Representation lost the D1 conjugation rule")
    conjugated = matmul(q_inverse, matmul(c3_matrix, matmul(q_matrix, d3_matrix)))
    need(same(matmul(d3_matrix, c3_matrix), conjugated),
         "Representation lost the D3 conjugation rule")

    def letter_matrix(letter):
        if letter == 1:
            return q_matrix
        if letter == -1:
            return q_inverse
        if letter == 2:
            return c1_matrix
        if letter == 3:
            return c3_matrix
        raise ValueError("unexpected formal letter")

    def image(element):
        """Normal form is the free-product word on the left and the D monomial on the right."""
        total = [[(0, 0)] * 8 for _ in range(8)]
        for (word, degree), value in element.items():
            need(degree[0] >= 0 and degree[1] >= 0, "image expects a nonnegative D degree")
            matrix = matmul(matpow(d1_matrix, degree[0]), matpow(d3_matrix, degree[1]))
            for letter in reversed(word):
                matrix = matmul(letter_matrix(letter), matrix)
            scale = (int(value), 0) if value.denominator == 1 else None
            need(scale is not None, "representation expected an integer coefficient")
            for row in range(8):
                for column in range(8):
                    total[row][column] = gadd(total[row][column], gmul(scale, matrix[row][column]))
        return total

    def monomial_and_bijective(matrix):
        rows = set()
        for column in range(8):
            support = [row for row in range(8) if matrix[row][column] != (0, 0)]
            need(len(support) == 1, "image column is not monomial")
            rows.add(support[0])
        need(len(rows) == 8, "image is singular")

    residual = algebra.mul(qi, c1, q, q, c1, c3, d1, d3)
    target = algebra.mul(qi, c1)
    explicit = q_inverse
    for factor in (c1_matrix, q_matrix, q_matrix, c1_matrix, c3_matrix, d1_matrix, d3_matrix):
        explicit = matmul(explicit, factor)
    residual_image = image(residual)
    target_image = image(target)
    need(same(residual_image, explicit),
         "normal-form image disagrees with the generator product")
    monomial_and_bijective(residual_image)
    monomial_and_bijective(target_image)
    need(not same(residual_image, target_image),
         "representation identified the residual with Q^{-1} C1")
    need(not same(residual_image, [[(0, 0)] * 8 for _ in range(8)]),
         "representation killed the residual")
    images = {}
    images["residual_nonzero"] = True
    images["target_nonzero"] = True
    images["images_distinct"] = True
    images["extra_relations_in_this_representation"] = ["D3^4 = I", "(C1 C3)^3 = I"]
    return images


def main():
    for name, digest in PINS.items():
        blob = (ROOT / name).read_bytes()
        need(sha256(blob).hexdigest() == digest, "source pin changed: " + name)
    feedback = (ROOT / "research/coded-active-feedback/PROOF.md").read_text(encoding="utf-8")
    physical = (ROOT / "research/coded-native-caller/PHYSICAL.md").read_text(encoding="utf-8")
    tariff = (ROOT / "research/moving-stage-restoration-tariff/PROOF.md").read_text(encoding="utf-8")
    need("D^4=I and other additional physical source relations are not" in feedback,
         "omitted-relation sentence missing")
    need("Let Q be the central C gate, D the product of the other eight C gates" in physical,
         "stage-Gaussian sentence missing")
    need("`D^2=X` and `D^4=I`" in tariff, "one-axis fourth-power sentence missing")
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    need(selected["kappa"] == "781451/250000000", "selected frontier kappa changed")

    one_axis_gaussian()
    algebra = load_search().algebra()
    q, c1, c3 = algebra.gen(1), algebra.gen(2), algebra.gen(3)
    d1, d3 = algebra.D(0), algebra.D(1)
    qi = algebra.inv(q)
    residual = algebra.mul(qi, c1, q, q, c1, c3, d1, d3)
    target = algebra.mul(qi, c1)
    need(residual == algebra.term(RESIDUAL, (1, 1)), "residual normal form changed")
    need(target == algebra.term(TARGET, (0, 0)), "Q^{-1} C1 normal form changed")

    fourth = algebra.mul(d1, d1, d1, d1)
    need(fourth == algebra.term((), (4, 0)), "D1^4 is not the degree-(4, 0) monomial")
    need(fourth != algebra.one, "D1^4 is already I in the predecessor algebra")
    for name, generator in (("Q", q), ("C1", c1), ("C3", c3), ("D1", d1), ("D3", d3)):
        need(algebra.mul(fourth, generator) == algebra.mul(generator, fourth),
             "D1^4 failed to commute with " + name)
    shifted = algebra.term(RESIDUAL, (5, 1))
    need(algebra.mul(fourth, residual) == shifted, "left D1^4 did not shift only the exponent")
    need(algebra.mul(residual, fourth) == shifted, "right D1^4 did not shift only the exponent")

    residual_class = {(RESIDUAL, (1, 1)): Fraction(1)}
    target_class = {(TARGET, (0, 0)): Fraction(1)}
    need(residue(residual) == residual_class, "residual coset sum is not 1")
    need(residue(target) == target_class, "Q^{-1} C1 coset sum is not 1")
    need(residual_class != target_class, "quotient identified the two words")
    need(q_parity(target) == -1, "parity character collapsed Q^{-1} C1")
    need(residue(algebra.add(fourth, algebra.neg(algebra.one))) == {},
         "quotient failed to impose D1^4 = I")
    fifth = algebra.mul(d1, d1, d1, d1, d1)
    inverse_cube = algebra.mul(algebra.inv(d1), algebra.inv(d1), algebra.inv(d1))
    need(residue(fifth) == residue(d1), "D1^5 did not reduce to D1")
    need(residue(inverse_cube) == residue(d1), "D1^{-3} did not reduce to D1")
    need(residue(d1) != residue(algebra.one), "D1 collapsed to I")
    witness = separating_representation(algebra, qi, c1, q, c3, d1, d3)

    receipt = {
        "relation": "D1^4 = I",
        "residual_class": [list(RESIDUAL), [1, 1], 1],
        "target_class": [list(TARGET), [0, 0], 1],
        "residual_is_zero": False,
        "target_is_zero": False,
        "classes_distinct": True,
        "target_q_parity": -1,
        "witness": witness,
        "evidence_class": "proof",
        "selected_kappa": selected["kappa"],
        "new_kappa": None,
    }
    print(json.dumps(receipt, sort_keys=True))
    print("PASS_RESIDUAL_D1_FOURTH_POWER")


if __name__ == "__main__":
    main()
