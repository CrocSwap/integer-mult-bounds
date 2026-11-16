#!/usr/bin/env python3
"""Host frame 1 of the P104 odd-character window and intersect its new monomials.

Frame 1 of the vendored 104-by-13 witness is hosted by a product of root-line
letters. Every hosting product equals one polynomial in the inherited
simple-root chart. That polynomial has 111 monomials of degree at least 2.
Thirty-one of them lie in the 40 monomials recorded for frame 0 by the closed
form in PR #7031. The other 80 are the additional charge of this row.

The frame-0 product census is not rerun. The recorded 40 are the degree-at
least-2 part of the published expansion, locked by its ANF hash. No kappa
change. Standard library only. Checks are need() failures, so python -O still
runs them.
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
RECORDED_ANF_SHA256 = "26803d29aa3141a357da4aa551195fe6378d3f2e1cba0c4291a4dedbce6ded2a"
FRAME1_SHA256 = "b2af6c2893e8104e3c9f54ce4db48f30f692c99f11ca877d81252ae5c36c0acd"
NEW_SHA256 = "df38586c54c752c2881df43e80653a9abffbaf5e49b9d76282919d3cf3c79765"
INTERSECTION_SHA256 = "2f7b63759f9780a1ae332df1ebbb987027c880cad97896fb39ebcb92194cc65b"
ADDITIONAL_SHA256 = "219f34e8bd473ae9927d0b6cb7d94c4b6de2b4c93f6b9c4c3b8355fdad4b13cb"
ABSENT_SHA256 = "5ca7559ebd00485c0852a0f65479f721997ae1c8aaac9bbc2e4083a29da2c7bf"
CANONICAL_PORTS = (13, 26, 131, 262)
CANONICAL_MASK = 0b10111
LENGTH_COUNTS = {1: 0, 2: 0, 3: 0, 4: 56, 5: 56, 6: 28, 7: 8, 8: 1}
DEGREE_COUNTS = {0: 1, 1: 8, 2: 27, 3: 47, 4: 37}
INTERSECTION_DEGREES = {2: 16, 3: 13, 4: 2}
ADDITIONAL_DEGREES = {2: 11, 3: 34, 4: 35}
ABSENT_DEGREES = {2: 1, 3: 4, 4: 4}
# Linear parts of the eight frame letters, in frame order. Every constant is 1.
LETTER_MASKS = (102, 108, 186, 176, 207, 197, 19, 25)
# Coordinates (p, q, r, s) of those linear parts.
LETTER_COORDINATES = (
    (0, 0, 1, 0),
    (1, 0, 1, 0),
    (1, 1, 0, 1),
    (0, 1, 0, 1),
    (1, 0, 1, 1),
    (0, 0, 1, 1),
    (0, 1, 0, 0),
    (1, 1, 0, 0),
)
FORM_MASKS = {"p": 10, "q": 19, "r": 102, "s": 163}


def need(condition, message):
    if not condition:
        raise SystemExit(message)


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


def bilinear(form, left, right):
    value = 0
    for i in range(8):
        if (left >> i) & 1:
            for j in range(8):
                if (right >> j) & 1 and form[i][j]:
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
    need(len(e8_roots()) == 240, "expected 240 roots")
    need(all(dot(root, root) == 2 for root in e8_roots()), "a root has norm squared other than 2")
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
    factor = {0: constant & 1}
    for index in range(8):
        if (mask >> index) & 1:
            factor[1 << index] = (factor.get(1 << index, 0) + 1) & 1
    return {exponent: coeff for exponent, coeff in factor.items() if coeff}


def multiply_all(factors):
    polynomial = {0: 1}
    for factor in factors:
        polynomial = polynomial_multiply(polynomial, factor)
    return polynomial


def evaluate(polynomial, point):
    value = 0
    for exponent in polynomial:
        if (exponent & point) == exponent:
            value ^= 1
    return value


def mobius_support(truth):
    """Algebraic normal form of a boolean function, via the subset Möbius transform."""
    values = [1 if truth(point) else 0 for point in range(256)]
    for index in range(8):
        bit = 1 << index
        for mask in range(256):
            if mask & bit:
                values[mask] ^= values[mask ^ bit]
    return {mask for mask, coeff in enumerate(values) if coeff}


def monomial_name(exponent):
    if exponent == 0:
        return "1"
    return "*".join("x{0}".format(index) for index in range(8) if (exponent >> index) & 1)


def digest(exponents):
    payload = ",".join(str(exponent) for exponent in sorted(exponents))
    return hashlib.sha256(payload.encode()).hexdigest()


def letter_form(label, form):
    mask = 0
    for index in range(8):
        if pairing(form, label, 1 << index):
            mask |= 1 << index
    return mask, pairing(form, label, 1 << 8)


def load_inputs():
    frame_path = ROOT / "data" / "frames.json"
    frame_bytes = frame_path.read_bytes()
    need(hashlib.sha256(frame_bytes).hexdigest() == FRAMES_SHA256, "frames.json sha256 mismatch")
    payload = json.loads(frame_bytes.decode())
    frames = payload["frames"]
    need(len(frames) == 13 and all(len(frame) == 8 for frame in frames), "expected 13 frames of size 8")
    covered = [port for frame in frames for port in frame]
    need(len(covered) == len(set(covered)) == 104, "the 13 frames do not partition 104 ports")
    ports = json.loads((REPO / "research/p104-port-window-haemers/data/ports_p104.json").read_text())["ports"]
    line_map = json.loads((REPO / "research/p104-port-window-haemers/data/e8_line_map.json").read_text())
    vector_to_root = {vector: tuple(root) for vector, root in zip(line_map["vectors"], line_map["roots2"])}
    need(len(ports) == 104 and len(set(ports)) == 104, "expected 104 distinct P104 ports")
    need(set(covered) == set(ports), "the frame partition is not the P104 port set")
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
    need(set(frame) <= ports, "frame 1 is not contained in P104")
    need(len(set(frame)) == 8, "frame 1 has a repeated port")
    for left, right in combinations(frame, 2):
        need((left & right).bit_count() & 1, "frame 1 is not an odd-graph clique")
        need(dot(vector_to_root[left], vector_to_root[right]) == 0, "frame 1 roots are not pairwise orthogonal")
    positions = [index[vector_to_root[port]] for port in frame]
    need(len(set(positions)) == 8, "frame 1 does not use eight root lines")
    return positions


def span_rank(vectors):
    return f2_rank(vectors)


def coordinate_of(mask):
    found = None
    for code in range(16):
        combined = 0
        for bit, name in enumerate(("p", "q", "r", "s")):
            if (code >> bit) & 1:
                combined ^= FORM_MASKS[name]
        if combined == mask:
            need(found is None, "a letter mask has two expressions in p, q, r, s")
            found = code
    need(found is not None, "a letter mask is outside span(p, q, r, s)")
    return tuple((found >> bit) & 1 for bit in range(4))


def predicted_hosting(coordinates):
    counts = {length: 0 for length in range(1, 9)}
    hosting = []
    for mask in range(1, 256):
        selected = [coordinates[bit] for bit in range(8) if (mask >> bit) & 1]
        # Pack coordinates as 4-bit integers, bit 0 = p through bit 3 = s.
        rows = [sum(coord << index for index, coord in enumerate(vector)) for vector in selected]
        if span_rank(rows) == 4:
            counts[mask.bit_count()] += 1
            hosting.append(mask)
    return counts, hosting


def product_values(rows, mask):
    values = [1] * 120
    for letter, row in enumerate(rows):
        if (mask >> letter) & 1:
            for point in range(120):
                values[point] &= row[point]
    return values


def expand_mask(mask, forms):
    factors = [linear_factor(*forms[letter]) for letter in range(8) if (mask >> letter) & 1]
    return multiply_all(factors)


def recorded_polynomial():
    factors = (
        linear_factor(1 << 0, 1),
        linear_factor((1 << 1) | (1 << 2) | (1 << 4), 1),
        linear_factor(1 << 5, 1),
        linear_factor((1 << 6) | (1 << 7), 1),
    )
    return multiply_all(factors)


def frame1_polynomial():
    factors = (
        linear_factor((1 << 1) | (1 << 3), 1),
        linear_factor((1 << 0) | (1 << 1) | (1 << 4), 1),
        linear_factor((1 << 1) | (1 << 2) | (1 << 5) | (1 << 6), 1),
        linear_factor((1 << 0) | (1 << 1) | (1 << 5) | (1 << 7), 1),
    )
    return multiply_all(factors)


def orthogonal_root_labels(form, labels, frame_labels):
    span = {0}
    for label in frame_labels:
        span |= {known ^ (label & 255) for known in span}
    need(len(span) == 16, "frame labels do not span a 4-dimensional space")
    need(f2_rank(label & 255 for label in frame_labels) == 4, "frame-label rank is not 4")
    orthogonal = [
        candidate for candidate in range(256)
        if all(bilinear(form, candidate, label & 255) == 0 for label in frame_labels)
    ]
    need(len(orthogonal) == 16, "the frame-label orthogonal does not have 16 vectors")
    label_set = {label & 255 for label in labels}
    return [candidate for candidate in orthogonal if candidate in label_set]


def run_controls(letter_rows, positions, polynomial, forms, outside_row, intersection, absent):
    target = tuple(1 if point in set(positions) else 0 for point in range(120))
    dropped = CANONICAL_MASK ^ (1 << (CANONICAL_MASK.bit_length() - 1))
    need(tuple(product_values(letter_rows, dropped)) != target, "deleting one canonical letter still hosts the row")
    failures = [
        mask for mask in range(256)
        if mask.bit_count() == 4 and tuple(product_values(letter_rows, mask)) != target
    ]
    need(len(failures) == 14, "length-4 failure count is not 14")
    need(tuple(product_values(letter_rows, 0b1111)) != target, "the rank-3 prefix still hosts the row")
    without_constant = {exponent: coeff for exponent, coeff in polynomial.items() if exponent}
    need(
        any(evaluate(without_constant, point) != evaluate(polynomial, point) for point in range(256)),
        "deleting the constant monomial did not change the chart function",
    )
    need(any(outside_row[point] == 0 for point in positions), "a non-frame letter is 1 on every frame line")
    canonical_values = product_values(letter_rows, CANONICAL_MASK)
    killed = [canonical_values[point] & outside_row[point] for point in range(120)]
    need(killed != list(target), "multiplying the canonical word by a non-frame letter still hosts the row")
    extended = CANONICAL_MASK | (1 << 3)
    need(expand_mask(extended, forms) == polynomial, "adding one more frame letter changed the polynomial")
    need(3 in intersection, "x0*x1 left the intersection")
    need(digest(exponent for exponent in intersection if exponent != 3) != INTERSECTION_SHA256,
         "deleting x0*x1 left the intersection hash unchanged")
    need(68 in absent and 68 not in polynomial, "x2*x6 is not an absent recorded monomial")


def main():
    frames, ports, vector_to_root = load_inputs()
    basis = simple_basis()
    matrix = list(zip(*basis))
    form = cartan_mod2(basis)
    lines = root_lines()
    labels, index = build_labels(form, matrix, lines)
    frame = tuple(frames[1])
    positions = frame_geometry(frame, ports, vector_to_root, index)
    forms = [letter_form(labels[source], form) for source in positions]
    need([mask for mask, _constant in forms] == list(LETTER_MASKS), "frame-1 letter masks changed")
    need(all(constant == 1 for _mask, constant in forms), "a frame-1 letter has constant term 0")
    coordinates = [coordinate_of(mask) for mask, _constant in forms]
    need(tuple(coordinates) == LETTER_COORDINATES, "frame-1 coordinates in p, q, r, s changed")
    need(all(vector[1] ^ vector[2] == 1 for vector in coordinates), "a frame-1 vector left the affine hyperplane")
    need(len(set(coordinates)) == 8, "the eight coordinate vectors are not distinct")
    counts, hosting = predicted_hosting(coordinates)
    need(counts == LENGTH_COUNTS, "span census counts changed: {0}".format(counts))
    need(sum(counts[length] for length in range(1, 4)) == 0, "a spanning set shorter than 4 exists")
    canonical = min(mask for mask in hosting if mask.bit_count() == 4)
    need(canonical == CANONICAL_MASK, "canonical mask changed: {0}".format(canonical))
    ports_used = tuple(frame[letter] for letter in range(8) if (canonical >> letter) & 1)
    need(ports_used == CANONICAL_PORTS, "canonical word ports changed: {0}".format(ports_used))

    letter_rows = [
        [pairing(form, labels[source], labels[point]) for point in range(120)] for source in positions
    ]
    target = tuple(1 if point in set(positions) else 0 for point in range(120))
    observed = []
    for mask in range(1, 256):
        if tuple(product_values(letter_rows, mask)) == target:
            observed.append(mask)
    need(observed == hosting, "the pairing products and the spanning subsets disagree")
    admissible = [
        position for position, label in enumerate(labels)
        if all(pairing(form, label, labels[point]) == 1 for point in positions)
    ]
    need(set(admissible) == set(positions), "the letters equal to 1 on the frame are not exactly the frame")
    orthogonal_hits = orthogonal_root_labels(form, labels, [labels[point] for point in positions])
    need(
        set(orthogonal_hits) == {labels[point] & 255 for point in positions},
        "the frame-label orthogonal meets the root labels outside the frame",
    )

    polynomial = frame1_polynomial()
    expansions = [expand_mask(mask, forms) for mask in hosting]
    need(all(expansion == polynomial for expansion in expansions), "a hosting product differs from the four-factor form")
    flat = mobius_support(lambda point: all(evaluate(linear_factor(FORM_MASKS[name], 0), point) == 0 for name in ("p", "q", "r", "s")))
    need(set(polynomial) == flat, "boolean multiplication disagrees with the Möbius transform of the flat")
    need(len([point for point in range(256) if evaluate(polynomial, point)]) == 16, "chart support is not the 16-point flat")
    label_hits = [point for point in range(120) if evaluate(polynomial, labels[point] & 255)]
    need(label_hits == sorted(positions), "on root lines the word is not the frame indicator")
    direct = product_values(letter_rows, canonical)
    need(all(direct[point] == target[point] for point in range(120)), "direct product disagrees with the indicator")
    port_of = {root: port for port, root in vector_to_root.items()}
    port_of.update({negate(root): port for port, root in vector_to_root.items()})
    p104_hits = [
        point for point in range(120)
        if port_of[lines[point]] in ports and evaluate(polynomial, labels[point] & 255)
    ]
    need(sorted(p104_hits) == sorted(positions), "on P104 the word is not the frame indicator")

    exponents = tuple(sorted(polynomial))
    need(digest(exponents) == FRAME1_SHA256, "frame-1 ANF sha256 mismatch")
    degrees = dict(Counter(exponent.bit_count() for exponent in exponents))
    need(degrees == DEGREE_COUNTS, "degree counts changed: {0}".format(degrees))
    new_monomials = [exponent for exponent in exponents if exponent.bit_count() >= 2]
    need(len(new_monomials) == 111, "new monomial count is not 111")
    need(digest(new_monomials) == NEW_SHA256, "new-monomial sha256 mismatch")
    with_x3 = [exponent for exponent in new_monomials if exponent & (1 << 3)]
    need(len(with_x3) == 51, "the x3 part of the new bill is not 51")

    recorded = recorded_polynomial()
    need(digest(sorted(recorded)) == RECORDED_ANF_SHA256, "recorded frame-0 ANF sha256 mismatch")
    need(len(recorded) == 48, "recorded expansion does not have 48 monomials")
    recorded_new = [exponent for exponent in sorted(recorded) if exponent.bit_count() >= 2]
    need(len(recorded_new) == 40, "recorded new-monomial count is not 40")
    need(all(exponent & (1 << 3) == 0 for exponent in recorded), "the recorded polynomial uses x3")
    intersection = [exponent for exponent in new_monomials if exponent in recorded]
    additional = [exponent for exponent in new_monomials if exponent not in recorded]
    absent = [exponent for exponent in recorded_new if exponent not in polynomial]
    need(len(intersection) == 31 and len(additional) == 80 and len(absent) == 9, "bill sizes changed")
    need(digest(intersection) == INTERSECTION_SHA256, "intersection sha256 mismatch")
    need(digest(additional) == ADDITIONAL_SHA256, "additional-bill sha256 mismatch")
    need(digest(absent) == ABSENT_SHA256, "absent-monomial sha256 mismatch")
    need(
        dict(Counter(exponent.bit_count() for exponent in intersection)) == INTERSECTION_DEGREES,
        "intersection degree counts changed",
    )
    need(
        dict(Counter(exponent.bit_count() for exponent in additional)) == ADDITIONAL_DEGREES,
        "additional degree counts changed",
    )
    need(dict(Counter(exponent.bit_count() for exponent in absent)) == ABSENT_DEGREES, "absent degree counts changed")
    need(set(with_x3) <= set(additional), "a monomial containing x3 met the recorded 40")
    need(len(set(new_monomials) - set(with_x3)) == 60, "the x3-free part of the new bill is not 60")
    need(len(set(new_monomials) | set(recorded_new)) == 120, "joint degree-at-least-2 bill is not 120")
    degree_one = [exponent for exponent in exponents if exponent.bit_count() == 1]
    need(degree_one == [1, 2, 4, 8, 16, 32, 64, 128], "frame 1 does not use every degree-1 variable")

    support_rows = []
    for left in range(8):
        mask = 0
        for right, point in enumerate(positions):
            if letter_rows[left][point]:
                mask |= 1 << right
        support_rows.append(mask)
    need(support_rows == [0xFF] * 8, "the frame pairing is not the all-ones matrix")
    need(f2_rank(support_rows) == 1, "the frame support does not have pairing rank 1")
    outside = next(point for point in range(120) if point not in set(positions))
    outside_row = [pairing(form, labels[outside], labels[point]) for point in range(120)]
    run_controls(letter_rows, positions, polynomial, forms, outside_row, set(intersection), set(absent))
    print(
        "PASS_P104_FRAME1_INTERSECTION word={word} monomials=120 new=111 "
        "intersection=31 additional=80 joint=120 absent_from_frame1=9 "
        "support_pairing_rank=1".format(word=",".join(str(port) for port in ports_used))
    )
    print("INTERSECTION " + " ".join(monomial_name(exponent) for exponent in intersection))
    print("ADDITIONAL " + " ".join(monomial_name(exponent) for exponent in additional))
    print("ABSENT " + " ".join(monomial_name(exponent) for exponent in absent))


if __name__ == "__main__":
    main()
