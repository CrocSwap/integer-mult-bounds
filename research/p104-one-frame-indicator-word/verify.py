#!/usr/bin/env python3
"""Host one P104 frame-indicator row and charge its new monomials.

The row is frame 0 of the 104-by-13 factorisation witness. A legal letter is a
root-line pairing. The shortest product of such letters that equals the
indicator on every root line has length 4, and every such product expands to
the same 48 monomials in the simple-root chart. Forty of those monomials have
degree at least 2. The other twelve frames are not expanded.

Standard library only. Checks are need() failures, so python -O still runs them.
"""
import hashlib
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
FRAMES_SHA256 = "c75915c18fc06ac19cc90fb9911209517c071862fdf401b998d5075efc0cda0d"
ANF_SHA256 = "26803d29aa3141a357da4aa551195fe6378d3f2e1cba0c4291a4dedbce6ded2a"
CANONICAL_PORTS = (11, 21, 38, 140)
DEGREE_COUNTS = {0: 1, 1: 7, 2: 17, 3: 17, 4: 6}
CENSUS = {4: 56, 5: 56, 6: 28, 7: 8, 8: 1}
DEGREE1_MASKS = (1, 2, 4, 16, 32, 64, 128)


def need(condition, message):
    if not condition:
        raise SystemExit(message)


def parity(value):
    return value.bit_count() & 1


def e8_roots():
    roots = []
    for left, right in combinations(range(8), 2):
        for sign_left in (1, -1):
            for sign_right in (1, -1):
                vector = [0] * 8
                vector[left] = 2 * sign_left
                vector[right] = 2 * sign_right
                roots.append(tuple(vector))
    for signs in product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            roots.append(tuple(signs))
    return roots


def simple_basis():
    basis = [
        (1, -1, -1, -1, -1, -1, -1, 1),
        (2, 2, 0, 0, 0, 0, 0, 0),
        (-2, 2, 0, 0, 0, 0, 0, 0),
    ]
    for index in range(1, 6):
        vector = [0] * 8
        vector[index] = -2
        vector[index + 1] = 2
        basis.append(tuple(vector))
    return basis


def dot(left, right):
    return sum(a * b for a, b in zip(left, right)) // 4


def cartan_mod2(basis):
    return [[dot(basis[i], basis[j]) & 1 for j in range(8)] for i in range(8)]


def solve_coordinates(matrix, target):
    rows = [[Fraction(entry) for entry in matrix[i]] + [Fraction(target[i])] for i in range(8)]
    for column in range(8):
        pivot = next(row for row in range(column, 8) if rows[row][column])
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = 1 / rows[column][column]
        rows[column] = [entry * scale for entry in rows[column]]
        for row in range(8):
            if row != column and rows[row][column]:
                factor = rows[row][column]
                rows[row] = [rows[row][col] - factor * rows[column][col] for col in range(9)]
    solution = [rows[i][8] for i in range(8)]
    need(all(entry.denominator == 1 for entry in solution), "root coordinates are not integral")
    return tuple(int(entry) for entry in solution)


def pairing(form, left, right):
    value = 0
    for i in range(8):
        if (left >> i) & 1:
            for j in range(8):
                if (right >> j) & 1 and form[i][j]:
                    value ^= 1
    if (left >> 8) & 1 and (right >> 8) & 1:
        value ^= 1
    return value


def label_of(root, matrix):
    coordinates = solve_coordinates(matrix, root)
    bits = 0
    for index, value in enumerate(coordinates):
        if value & 1:
            bits |= 1 << index
    return bits | (1 << 8)


def negate(vector):
    return tuple(-entry for entry in vector)


def root_lines():
    lines = []
    seen = set()
    for root in e8_roots():
        key = root if root > negate(root) else negate(root)
        if key not in seen:
            seen.add(key)
            lines.append(root)
    need(len(lines) == 120, "expected 120 root lines")
    return lines


def f2_rank(rows):
    basis = {}
    for row in rows:
        value = row
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def polynomial_multiply(left, right):
    product = {}
    for left_exp, left_coeff in left.items():
        for right_exp, right_coeff in right.items():
            exponent = left_exp | right_exp
            product[exponent] = (product.get(exponent, 0) + left_coeff * right_coeff) & 1
    return {exponent: coeff for exponent, coeff in product.items() if coeff}


def linear_factor(mask, constant):
    factor = {0: constant}
    for index in range(8):
        if (mask >> index) & 1:
            factor[1 << index] = 1
    return factor


def letter_form(label, form):
    mask = 0
    for index in range(8):
        if pairing(form, label, 1 << index):
            mask |= 1 << index
    return mask, pairing(form, label, 1 << 8)


def evaluate(polynomial, point):
    value = 0
    for exponent in polynomial:
        if (exponent & point) == exponent:
            value ^= 1
    return value


def monomial_name(exponent):
    if exponent == 0:
        return "1"
    return "*".join("x{0}".format(index) for index in range(8) if (exponent >> index) & 1)


def load_inputs():
    frame_bytes = (ROOT / "data" / "frames.json").read_bytes()
    need(hashlib.sha256(frame_bytes).hexdigest() == FRAMES_SHA256, "frames.json sha256 mismatch")
    frames = json.loads(frame_bytes.decode())["frames"]
    need(len(frames) == 13 and all(len(frame) == 8 for frame in frames), "expected 13 frames of size 8")
    ports = json.loads((REPO / "research/p104-port-window-haemers/data/ports_p104.json").read_text())["ports"]
    line_map = json.loads((REPO / "research/p104-port-window-haemers/data/e8_line_map.json").read_text())
    vector_to_root = {vector: tuple(root) for vector, root in zip(line_map["vectors"], line_map["roots2"])}
    need(len(ports) == 104 and len(set(ports)) == 104, "expected 104 distinct P104 ports")
    return frames, set(ports), vector_to_root


def build_labels(form, matrix, lines):
    labels = [label_of(root, matrix) for root in lines]
    need(len(set(labels)) == 120, "root-line labels are not distinct")
    need(all((label >> 8) & 1 for label in labels), "a label is missing the ninth coordinate")
    index = {}
    for position, root in enumerate(lines):
        index[root] = position
        index[negate(root)] = position
    mismatches = 0
    for left in range(120):
        for right in range(120):
            expected = (dot(lines[left], lines[right]) + 1) & 1
            if pairing(form, labels[left], labels[right]) != expected:
                mismatches += 1
    need(mismatches == 0, "simple-root chart does not reproduce the label pairing")
    return labels, index


def frame_geometry(frame, ports, vector_to_root, index):
    need(set(frame) <= ports, "frame 0 is not contained in P104")
    need(len(set(frame)) == 8, "frame 0 has a repeated port")
    for left, right in combinations(frame, 2):
        need((left & right).bit_count() & 1, "frame 0 is not an odd-graph clique")
        need(dot(vector_to_root[left], vector_to_root[right]) == 0, "frame 0 roots are not pairwise orthogonal")
    positions = [index[vector_to_root[port]] for port in frame]
    need(len(set(positions)) == 8, "frame 0 does not use eight root lines")
    return positions


def product_values(rows, mask):
    values = [1] * 120
    for letter, row in enumerate(rows):
        if (mask >> letter) & 1:
            for point in range(120):
                values[point] &= row[point]
    return values


def census(rows, frame_positions):
    target = tuple(1 if point in set(frame_positions) else 0 for point in range(120))
    counts = Counter()
    shortest = []
    for mask in range(1, 256):
        if tuple(product_values(rows, mask)) == target:
            length = mask.bit_count()
            counts[length] += 1
            if length == 4:
                shortest.append(mask)
    need(dict(counts) == CENSUS, "product census counts changed: {0}".format(dict(counts)))
    need(sum(counts[length] for length in range(1, 4)) == 0, "a product shorter than 4 hosts the row")
    need(len(shortest) == 56, "expected 56 length-4 words")
    return min(shortest), shortest, target


def expand_mask(mask, forms):
    polynomial = {0: 1}
    for letter in range(8):
        if (mask >> letter) & 1:
            polynomial = polynomial_multiply(polynomial, linear_factor(*forms[letter]))
    return polynomial


def simplified_polynomial():
    factors = (
        {0: 1, 1: 1},
        {0: 1, 1 << 1: 1, 1 << 2: 1, 1 << 4: 1},
        {0: 1, 1 << 5: 1},
        {0: 1, 1 << 6: 1, 1 << 7: 1},
    )
    polynomial = {0: 1}
    for factor in factors:
        polynomial = polynomial_multiply(polynomial, factor)
    return polynomial


def admissible_letters(labels, form, frame_positions):
    admissible = []
    for position, label in enumerate(labels):
        if all(pairing(form, label, labels[point]) == 1 for point in frame_positions):
            admissible.append(position)
    return admissible


def run_controls(letter_rows, frame_positions, canonical, polynomial, value_at):
    target = tuple(1 if point in set(frame_positions) else 0 for point in range(120))
    dropped_bit = 1 << (canonical.bit_length() - 1)
    need(tuple(product_values(letter_rows, canonical ^ dropped_bit)) != target,
         "deleting one canonical letter still hosts the row")
    successes = {
        mask for mask in range(256)
        if mask.bit_count() == 4 and tuple(product_values(letter_rows, mask)) == target
    }
    need(len(successes) == 56, "length-4 success count drifted inside the control")
    need(sum(1 for mask in range(256) if mask.bit_count() == 4) - len(successes) == 14,
         "length-4 failure count is not 14")
    without_constant = {exponent: coeff for exponent, coeff in polynomial.items() if exponent}
    need(any(evaluate(without_constant, point) != evaluate(polynomial, point) for point in range(256)),
         "deleting the constant monomial did not change the chart function")
    outside = next(point for point in range(120) if point not in set(frame_positions))
    need(any(value_at(outside, point) == 0 for point in frame_positions),
         "a non-frame label is 1 on every frame line")
    need(any(value_at(outside, point) == 0 and target[point] == 1 for point in frame_positions),
         "multiplying by a non-frame label would not destroy a frame value")


def main():
    frames, ports, vector_to_root = load_inputs()
    basis = simple_basis()
    matrix = list(zip(*basis))
    form = cartan_mod2(basis)
    lines = root_lines()
    labels, index = build_labels(form, matrix, lines)
    frame = frames[0]
    positions = frame_geometry(frame, ports, vector_to_root, index)
    admissible = admissible_letters(labels, form, positions)
    need(set(admissible) == set(positions), "the letters equal to 1 on the frame are not exactly the frame")
    letter_rows = [[pairing(form, labels[source], labels[point]) for point in range(120)] for source in positions]
    forms = [letter_form(labels[source], form) for source in positions]
    canonical, shortest, _target = census(letter_rows, positions)
    ports_used = tuple(frame[letter] for letter in range(8) if (canonical >> letter) & 1)
    need(ports_used == CANONICAL_PORTS, "canonical word ports changed: {0}".format(ports_used))
    expansions = [expand_mask(mask, forms) for mask in shortest]
    need(all(polynomial == expansions[0] for polynomial in expansions),
         "the 56 length-4 words do not share one expansion")
    polynomial = expansions[0]
    simplified = simplified_polynomial()
    need(polynomial == simplified, "the label product does not equal the disjoint-variable form")
    need(all(evaluate(polynomial, point) == evaluate(simplified, point) for point in range(256)),
         "chart evaluation disagrees with the factored form")
    exponents = tuple(sorted(polynomial))
    payload = ",".join(str(exponent) for exponent in exponents)
    need(hashlib.sha256(payload.encode()).hexdigest() == ANF_SHA256, "ANF sha256 mismatch")
    degrees = dict(Counter(exponent.bit_count() for exponent in exponents))
    need(degrees == DEGREE_COUNTS, "degree counts changed: {0}".format(degrees))
    degree1 = tuple(exponent for exponent in exponents if exponent.bit_count() == 1)
    need(degree1 == DEGREE1_MASKS, "degree-1 monomials changed")
    chart_support = [point for point in range(256) if evaluate(polynomial, point)]
    label_hits = [point for point in range(120) if evaluate(polynomial, labels[point] & 255)]
    need(len(chart_support) == 16, "chart support is not the 16-point flat")
    need(label_hits == sorted(positions), "on root lines the word is not the frame indicator")
    port_of = {root: port for port, root in vector_to_root.items()}
    port_of.update({negate(root): port for port, root in vector_to_root.items()})
    p104_hits = [
        point for point in range(120)
        if port_of[lines[point]] in ports and evaluate(polynomial, labels[point] & 255)
    ]
    need(sorted(p104_hits) == sorted(positions), "on P104 the word is not the frame indicator")
    direct = product_values(letter_rows, canonical)
    need(all(direct[point] == (1 if point in set(positions) else 0) for point in range(120)),
         "direct product disagrees with the indicator")
    run_controls(
        letter_rows,
        positions,
        canonical,
        polynomial,
        lambda source, point: pairing(form, labels[source], labels[point]),
    )
    new_monomials = [exponent for exponent in exponents if exponent.bit_count() >= 2]
    need(len(new_monomials) == 40, "new monomial count is not 40")
    support_rows = []
    for left in range(8):
        mask = 0
        for right, point in enumerate(positions):
            if letter_rows[left][point]:
                mask |= 1 << right
        support_rows.append(mask)
    need(support_rows == [0xFF] * 8, "the frame pairing is not the all-ones matrix")
    need(f2_rank(support_rows) == 1, "the frame support does not have pairing rank 1")
    print(
        "PASS_P104_ONE_FRAME_INDICATOR word={word} monomials=48 new=40 "
        "constant=1 degree1=7 census=4:56,5:56,6:28,7:8,8:1 support_pairing_rank=1".format(
            word=",".join(str(port) for port in ports_used)
        )
    )
    print("MONOMIALS " + " ".join(monomial_name(exponent) for exponent in exponents))
    print("NEW_MONOMIALS " + " ".join(monomial_name(exponent) for exponent in new_monomials))


if __name__ == "__main__":
    main()
