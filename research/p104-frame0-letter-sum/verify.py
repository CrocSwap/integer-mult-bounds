#!/usr/bin/env python3
"""No F2 sum of root-line letters hosts the #7031 frame-0 indicator.

The explicit sum is λ_11 + λ_21 + λ_38 + λ_56. In the inherited simple-root
chart those four letters cancel, so the sum is the zero polynomial: no
monomials at all, and therefore no monomial of degree at least 2. The zero
polynomial is 0 on the eight frame lines, so this sum does not host the row.

Every F2 sum of the 120 letters is affine, and the letters span all 512
affine functions. Ports 478, 11, 14 and 475 lie in P104 and their augmented
labels sum to 0, while the indicator sums to 1 on those four lines. No affine
function hosts the row on the 104 P104 lines, nor on all 120 root lines.

This does not rerun the #7031 product census and does not change kappa.
Checks are need() failures, so python -O still runs them.
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
FRAME = (11, 21, 38, 56, 140, 146, 161, 191)
EXPLICIT_SUM = (11, 21, 38, 56)
FRAME_LETTERS = {
    11: (54, 1),
    21: (55, 1),
    38: (23, 1),
    56: (22, 1),
    140: (225, 1),
    146: (224, 1),
    161: (192, 1),
    191: (193, 1),
}
CANCEL_FOURS = (
    (11, 21, 38, 56),
    (11, 21, 140, 146),
    (11, 21, 161, 191),
    (11, 38, 140, 161),
    (11, 38, 146, 191),
    (11, 56, 140, 191),
    (11, 56, 146, 161),
    (21, 38, 140, 191),
    (21, 38, 146, 161),
    (21, 56, 140, 161),
    (21, 56, 146, 191),
    (38, 56, 140, 146),
    (38, 56, 161, 191),
    (140, 146, 161, 191),
)
OBSTRUCTION = (478, 11, 14, 475)
OBSTRUCTION_BITS = {478: 12, 11: 26, 14: 175, 475: 185}
SECOND_OBSTRUCTION = (21, 13, 493, 501)
SECOND_BITS = {21: 28, 13: 58, 493: 30, 501: 56}
DISTANCE_120 = {8: 1, 48: 7, 56: 248, 64: 248, 72: 7, 112: 1}
DISTANCE_104 = {8: 1, 36: 3, 44: 12, 48: 199, 52: 82, 56: 199, 60: 12, 68: 3, 96: 1}
WEIGHT4_OBSTRUCTIONS = 7168
WEIGHT4_OBSTRUCTIONS_P104 = 4384
LETTER_SYZYGIES_SIZE4 = 32130


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


def letter_form(label, form):
    mask = 0
    for index in range(8):
        if pairing(form, label, 1 << index):
            mask |= 1 << index
    return mask, pairing(form, label, 1 << 8)


def monomials(mask, constant):
    exponents = []
    if constant:
        exponents.append(0)
    for index in range(8):
        if (mask >> index) & 1:
            exponents.append(1 << index)
    return tuple(exponents)


def new_monomials(mask, constant):
    return tuple(exponent for exponent in monomials(mask, constant) if exponent.bit_count() >= 2)


def evaluate_affine(mask, constant, bits):
    return constant ^ ((bits & mask).bit_count() & 1)


def f2_rank(vectors):
    basis = {}
    for vector in vectors:
        value = vector
        while value:
            pivot = value.bit_length() - 1
            if pivot in basis:
                value ^= basis[pivot]
            else:
                basis[pivot] = value
                break
    return len(basis)


def load_geometry():
    frame_path = ROOT / "data" / "frames.json"
    frame_bytes = frame_path.read_bytes()
    need(hashlib.sha256(frame_bytes).hexdigest() == FRAMES_SHA256, "frames.json sha256 mismatch")
    frames = json.loads(frame_bytes.decode())["frames"]
    need(len(frames) == 13 and all(len(frame) == 8 for frame in frames), "expected 13 frames of size 8")
    need(tuple(frames[0]) == FRAME, "frame 0 ports changed")
    ports = json.loads((REPO / "research/p104-port-window-haemers/data/ports_p104.json").read_text())["ports"]
    line_map = json.loads((REPO / "research/p104-port-window-haemers/data/e8_line_map.json").read_text())
    vector_to_root = {vector: tuple(root) for vector, root in zip(line_map["vectors"], line_map["roots2"])}
    need(len(ports) == 104 and len(set(ports)) == 104, "expected 104 distinct P104 ports")
    port_set = set(ports)
    basis = simple_basis()
    matrix = list(zip(*basis))
    form = cartan_mod2(basis)
    lines = root_lines()
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
    root_to_port = {}
    for vector, root in vector_to_root.items():
        root_to_port[root] = vector
        root_to_port[negate(root)] = vector
    return frames, port_set, vector_to_root, form, lines, labels, index, root_to_port


def position_of(port, vector_to_root, index):
    root = vector_to_root[port]
    if root not in index:
        root = negate(root)
    return index[root]


def main():
    _frames, ports, vector_to_root, form, lines, labels, index, root_to_port = load_geometry()
    frame_positions = [position_of(port, vector_to_root, index) for port in FRAME]
    need(len(set(frame_positions)) == 8, "frame 0 does not use eight root lines")
    need(set(FRAME) <= ports, "frame 0 is not contained in P104")
    for left, right in combinations(FRAME, 2):
        need((left & right).bit_count() & 1, "frame 0 is not an odd-graph clique")
        need(dot(vector_to_root[left], vector_to_root[right]) == 0, "frame 0 roots are not pairwise orthogonal")
    frame_position_set = set(frame_positions)
    p104_points = {position for position in range(120) if root_to_port[lines[position]] in ports}
    need(len(p104_points) == 104, "expected 104 P104 root lines")
    need(frame_position_set <= p104_points, "a frame line is outside P104")

    letter_vectors = []
    point_vectors = []
    point_bits = []
    for position, label in enumerate(labels):
        mask, constant = letter_form(label, form)
        need(constant == 1, "a letter does not have constant term 1")
        letter_vectors.append(mask | (constant << 8))
        bits = label & 255
        point_bits.append(bits)
        point_vectors.append(bits | (1 << 8))
    need(len(set(letter_vectors)) == 120, "letter vectors are not distinct")
    need(f2_rank(letter_vectors) == 9, "the 120 letters do not span every affine function")
    need(all(new_monomials(vector & 255, (vector >> 8) & 1) == () for vector in range(512)),
         "an affine normal form has a monomial of degree at least 2")

    forms = {}
    for port, position in zip(FRAME, frame_positions):
        forms[port] = letter_form(labels[position], form)
    need(forms == FRAME_LETTERS, "frame-letter polynomials changed: {0}".format(forms))
    explicit_mask = 0
    explicit_constant = 0
    for port in EXPLICIT_SUM:
        mask, constant = forms[port]
        explicit_mask ^= mask
        explicit_constant ^= constant
    need((explicit_mask, explicit_constant) == (0, 0), "the explicit four-letter sum is not zero")
    need(monomials(explicit_mask, explicit_constant) == (), "the zero polynomial was given a monomial")
    need(new_monomials(explicit_mask, explicit_constant) == (), "the explicit sum was charged a new monomial")
    for port in EXPLICIT_SUM:
        mask, constant = forms[port]
        rest_mask = explicit_mask ^ mask
        rest_constant = explicit_constant ^ constant
        need((rest_mask, rest_constant) != (0, 0), "dropping {0} still cancels".format(port))

    cancel_fours = []
    cancel_sizes = Counter()
    for size in range(1, 9):
        for choice in combinations(FRAME, size):
            mask = 0
            constant = 0
            for port in choice:
                bit, term = forms[port]
                mask ^= bit
                constant ^= term
            if (mask, constant) == (0, 0):
                cancel_sizes[size] += 1
                if size == 4:
                    cancel_fours.append(choice)
    need(dict(cancel_sizes) == {4: 14, 8: 1}, "frame-letter cancellations changed: {0}".format(dict(cancel_sizes)))
    need(tuple(cancel_fours) == CANCEL_FOURS, "the 14 cancelling fours changed")
    hosted_frame_sums = 0
    for size in range(1, 9):
        for choice in combinations(range(8), size):
            mask = 0
            constant = 0
            for letter_index in choice:
                bit, term = forms[FRAME[letter_index]]
                mask ^= bit
                constant ^= term
            if all(evaluate_affine(mask, constant, point_bits[position]) == 1 for position in frame_positions):
                if all(evaluate_affine(mask, constant, point_bits[position]) == 0
                       for position in range(120) if position not in frame_position_set):
                    hosted_frame_sums += 1
    need(hosted_frame_sums == 0, "a sum of frame letters hosts the row")

    def bits_of(port):
        return point_bits[position_of(port, vector_to_root, index)]

    for port, bits in OBSTRUCTION_BITS.items():
        need(bits_of(port) == bits, "label of port {0} changed".format(port))
        need(port in ports, "obstruction port {0} is outside P104".format(port))
    for port, bits in SECOND_BITS.items():
        need(bits_of(port) == bits, "label of port {0} changed".format(port))
        need(port in ports, "second obstruction port {0} is outside P104".format(port))
    need(OBSTRUCTION_BITS[478] ^ OBSTRUCTION_BITS[11] ^ OBSTRUCTION_BITS[14] ^ OBSTRUCTION_BITS[475] == 0,
         "the four obstruction labels do not sum to 0")
    need((1 << 8) ^ (1 << 8) ^ (1 << 8) ^ (1 << 8) == 0, "four constant coordinates failed to cancel")
    need(sum(1 for port in OBSTRUCTION if port in set(FRAME)) == 1, "the obstruction should meet the frame once")
    need(SECOND_BITS[21] ^ SECOND_BITS[13] ^ SECOND_BITS[493] ^ SECOND_BITS[501] == 0,
         "the second obstruction labels do not sum to 0")
    for kept in combinations(OBSTRUCTION, 3):
        total = 0
        for port in kept:
            total ^= OBSTRUCTION_BITS[port] | (1 << 8)
        need(total != 0, "a proper subset of the obstruction is already dependent")
    frame_four_bits = [bits_of(port) for port in EXPLICIT_SUM]
    need(frame_four_bits[0] ^ frame_four_bits[1] ^ frame_four_bits[2] ^ frame_four_bits[3] == 0,
         "the explicit sum's evaluation labels do not sum to 0")
    need(sum(1 for port in EXPLICIT_SUM if port in set(FRAME)) == 4, "the explicit sum left the frame")
    # All four ports lie in the frame, so this dependence has even indicator
    # parity and must not be counted as an obstruction.
    explicit_points = tuple(sorted(position_of(port, vector_to_root, index) for port in EXPLICIT_SUM))

    target = [1 if position in frame_position_set else 0 for position in range(120)]
    distances = Counter()
    distances_104 = Counter()
    hosts = 0
    hosts_104 = 0
    for coefficient in range(512):
        mask = coefficient & 255
        constant = (coefficient >> 8) & 1
        wrong = 0
        wrong_104 = 0
        for position in range(120):
            if evaluate_affine(mask, constant, point_bits[position]) != target[position]:
                wrong += 1
                if position in p104_points:
                    wrong_104 += 1
        distances[wrong] += 1
        distances_104[wrong_104] += 1
        if wrong == 0:
            hosts += 1
        if wrong_104 == 0:
            hosts_104 += 1
    need(hosts == 0, "an affine function agrees with the indicator on all 120 lines")
    need(hosts_104 == 0, "an affine function agrees with the indicator on the 104 P104 lines")
    need(dict(distances) == DISTANCE_120, "120-line distances changed: {0}".format(dict(distances)))
    need(dict(distances_104) == DISTANCE_104, "104-line distances changed: {0}".format(dict(distances_104)))
    need(distances[8] == 1, "the distance-8 sum is not unique")
    zero_wrong = sum(target)
    need(zero_wrong == 8, "the zero polynomial does not miss exactly the eight frame lines")

    small_obstructions = 0
    small_dependencies = 0
    for size in range(1, 4):
        for choice in combinations(range(120), size):
            total = 0
            parity = 0
            for position in choice:
                total ^= point_vectors[position]
                parity ^= target[position]
            if total == 0:
                small_dependencies += 1
                if parity == 1:
                    small_obstructions += 1
    need(small_dependencies == 0, "an affine dependence of fewer than four root lines exists")
    need(small_obstructions == 0, "an obstruction of fewer than four root lines exists")
    weight4 = 0
    weight4_p104 = 0
    seen_primary = False
    seen_second = False
    seen_explicit = False
    odd_frame_counts = Counter()
    primary_points = tuple(sorted(position_of(port, vector_to_root, index) for port in OBSTRUCTION))
    second_points = tuple(sorted(position_of(port, vector_to_root, index) for port in SECOND_OBSTRUCTION))
    for choice in combinations(range(120), 4):
        total = 0
        parity = 0
        frame_hits = 0
        for position in choice:
            total ^= point_vectors[position]
            parity ^= target[position]
            frame_hits += target[position]
        if total != 0 or parity != 1:
            continue
        weight4 += 1
        odd_frame_counts[frame_hits] += 1
        if all(position in p104_points for position in choice):
            weight4_p104 += 1
        ordered = tuple(sorted(choice))
        if ordered == primary_points:
            seen_primary = True
        if ordered == second_points:
            seen_second = True
        if ordered == explicit_points:
            seen_explicit = True
    need(not seen_explicit, "the even frame dependence was counted as an obstruction")
    need(weight4 == WEIGHT4_OBSTRUCTIONS, "weight-4 obstruction count changed: {0}".format(weight4))
    need(weight4_p104 == WEIGHT4_OBSTRUCTIONS_P104,
         "P104 weight-4 obstruction count changed: {0}".format(weight4_p104))
    need(dict(odd_frame_counts) == {1: WEIGHT4_OBSTRUCTIONS},
         "a weight-4 obstruction meets the frame more than once")
    need(seen_primary and seen_second, "a named obstruction was not found by the census")

    letter_small = 0
    letter_size4 = 0
    for size in range(1, 5):
        for choice in combinations(range(120), size):
            total = 0
            for position in choice:
                total ^= letter_vectors[position]
            if total == 0:
                if size < 4:
                    letter_small += 1
                else:
                    letter_size4 += 1
    need(letter_small == 0, "fewer than four letters already sum to zero")
    need(letter_size4 == LETTER_SYZYGIES_SIZE4, "four-letter syzygy count changed: {0}".format(letter_size4))

    constant_one_wrong = 0
    for position in range(120):
        if evaluate_affine(0, 1, point_bits[position]) != target[position]:
            constant_one_wrong += 1
    need(constant_one_wrong == 112, "the constant-1 function does not miss the 112 non-frame lines")
    one_letter_mask, one_letter_constant = forms[11]
    need(new_monomials(one_letter_mask, one_letter_constant) == (), "one letter acquired a new monomial")
    need(all(evaluate_affine(one_letter_mask, one_letter_constant, point_bits[position]) == 1
             for position in frame_positions), "λ_11 is not 1 on the whole frame")
    need(any(evaluate_affine(one_letter_mask, one_letter_constant, point_bits[position]) == 1
             for position in range(120) if position not in frame_position_set),
         "λ_11 does not spill outside the frame")

    print(
        "PASS_P104_FRAME0_LETTER_SUM explicit=11+21+38+56 monomials=0 new=0 "
        "hosts=0 hosts_p104=0 min_disagreements=8 closest=zero "
        "obstruction=478,11,14,475 weight4=7168 weight4_p104=4384 "
        "frame_sums=255 frame_sum_hosts=0 cancelling_fours=14"
    )
    print("MONOMIALS")
    print("NEW_MONOMIALS")
    print("ONE_LETTER port=11 monomials=1,x1,x2,x4,x5 new=0 hosts=0")


if __name__ == "__main__":
    main()
