"""Check fixed-ambient BIT projector substitution and delayed cover routing."""

import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
from itertools import product
import json
from math import gcd
from pathlib import Path


SOURCE_PATH = Path("research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz")
SOURCE_SHA = "51203e7fc75ba10bd3ac3f8e675759f47e13d262bea66b6600d1e515095cad78"
FRAME_SHA = "b4c3f2891150c90b4092567b9124f071cb9ef3a1a751130e8b79f1af3effcc1a"
HELPER_CHARTS = (506, 507)


def check(value, label):
    if not value:
        raise ValueError(label)


def identity(size):
    return tuple(tuple(int(i == j) for j in range(size)) for i in range(size))


class Ring:
    def __init__(self, modulus):
        self.modulus = modulus

    def multiply(self, a, b):
        columns = tuple(zip(*b))
        return tuple(tuple(sum(x*y for x, y in zip(row, col) if x and y) % self.modulus
                           for col in columns) for row in a)

    def inverse(self, a):
        size = len(a)
        rows = [list(row + unit) for row, unit in zip(a, identity(size))]
        for col in range(size):
            pivot = next(i for i in range(col, size) if gcd(rows[i][col], self.modulus) == 1)
            rows[col], rows[pivot] = rows[pivot], rows[col]
            factor = pow(rows[col][col], -1, self.modulus)
            rows[col] = [x*factor % self.modulus for x in rows[col]]
            for i, row in enumerate(rows):
                if i != col and row[col]:
                    rows[i] = [(x-row[col]*y) % self.modulus for x, y in zip(row, rows[col])]
        return tuple(tuple(row[size:]) for row in rows)

    def conjugate(self, basis, matrix):
        return self.multiply(self.multiply(basis, matrix), self.inverse(basis))

    def projector(self, basis, rank):
        mask = tuple(tuple(x if j < rank else 0 for j, x in enumerate(row)) for row in basis)
        return self.multiply(mask, self.inverse(basis))

    def subtract(self, a, b):
        return tuple(tuple((x-y) % self.modulus for x, y in zip(r, s)) for r, s in zip(a, b))

    def action(self, matrix, vector):
        return tuple(sum(x*y for x, y in zip(row, vector)) % self.modulus for row in matrix)


def choose_columns(matrix, first):
    first = tuple(first)
    order = first + tuple(j for j in range(len(matrix)) if j not in first)
    return tuple(tuple(row[j] for j in order) for row in matrix)


def lift(matrix, columns, ambient):
    # The remaining axes retain their original coordinates.
    used = len(matrix)*columns
    out = [list(row) for row in identity(ambient)]
    for i in range(used):
        for j in range(used):
            out[i][j] = matrix[i//columns][j//columns] if i % columns == j % columns else 0
    return tuple(map(tuple, out))


def load_helpers(path, ring):
    packed = path.read_bytes()
    check(sha256(packed).hexdigest() == SOURCE_SHA, "canonical native word")
    word = json.loads(gzip.decompress(packed))
    frames = word["frames"]
    encoded = json.dumps(frames, sort_keys=True, separators=(",", ":")).encode()
    check(sha256(encoded).hexdigest() == FRAME_SHA, "common 636-frame table")
    owners = set(zip(word["start"][222:], word["final"][222:]))
    helpers = []
    for chart in HELPER_CHARTS:
        check((chart, 1) in owners and frames["1"]["dim"] == 8, "complete positive helper")
        frame = frames[str(chart)]
        check(frame["dim"] == 4 and len(frame["A"]) == 4, "rank-four helper")
        # The image of the helper projector is the kernel of its lower frame.
        def residue(value):
            rational = Fraction(value)
            return rational.numerator * pow(rational.denominator, -1, ring.modulus) % ring.modulus
        a_rows = tuple(tuple(map(residue, row)) for row in frame["A"])
        b_rows = tuple(tuple(map(residue, row)) for row in frame["B"])
        basis = tuple(zip(*(a_rows + b_rows)))
        lower_basis = tuple(zip(*(b_rows + a_rows)))
        check(ring.multiply(basis, ring.inverse(basis)) == identity(8), "split image and kernel")
        check(ring.projector(basis, 4) == ring.subtract(identity(8), ring.projector(lower_basis, 4)),
              "helper is the actual projector difference")
        helpers.append(basis)
    return helpers


def fixed_ambient(helpers, ring):
    ambient, grade = 25, 4
    counts = {"matches": 0, "peels": 0, "leaves": 0}
    one = identity(ambient)
    # This nonorthogonal split gives complementary paid ranks three and one.
    split = [list(row) for row in identity(8)]
    split[0][3], split[3][0], split[3][3] = 1, 1, 2
    split = tuple(map(tuple, split))

    def visit(target_basis, width, variant, cover):
        if width < grade:
            pieces = [choose_columns(target_basis, [j]) for j in range(width)]
            counts["leaves"] += width
            return [ring.conjugate(cover, ring.projector(piece, 1)) for piece in pieces]

        columns, remainder = divmod(width, grade)
        check(8*columns <= ambient, "original ambient fits this request")
        moved = grade*columns
        role = lift(helpers[variant % len(helpers)], columns, ambient)
        matcher = ring.multiply(target_basis, ring.inverse(role))
        routed = ring.multiply(cover, matcher)
        expected = ring.conjugate(cover, ring.projector(target_basis, moved))
        actual = ring.conjugate(routed, ring.projector(role, moved))
        check(actual == expected and ring.multiply(routed, ring.inverse(matcher)) == cover,
              "whole row right route and inverse")
        counts["matches"] += 1

        paid_basis = ring.multiply(role, lift(split, columns, ambient))
        pieces = []
        for j, axis_range in enumerate((range(3*columns), range(3*columns, moved))):
            piece = choose_columns(paid_basis, axis_range)
            pieces += visit(piece, len(axis_range), variant+j+1, routed)
        for index in range(moved, width):
            pieces += visit(choose_columns(target_basis, [index]), 1, variant, cover)
        counts["peels"] += remainder
        # On the address difference H-C D, the partial swap is I-2P.
        # Verifying its complete matrix checks the kernel and all spectators.
        matrix = one
        for piece in pieces:
            change = ring.multiply(piece, matrix)
            matrix = ring.subtract(ring.subtract(matrix, change), change)
        total = ring.conjugate(cover, ring.projector(target_basis, width))
        check(matrix == ring.subtract(ring.subtract(one, total), total), "all coordinate columns")
        return pieces

    shear = [list(row) for row in one]
    for i in range(ambient-1):
        shear[i][i+1] = (1+101*i) % ring.modulus
    shear = tuple(map(tuple, shear))
    for cover in (one, shear, tuple(reversed(shear))):
        for variant in range(2):
            pieces = []
            tile_width = grade*(ambient//8)
            for start in range(0, ambient, tile_width):
                tile = range(start, min(ambient, start+tile_width))
                pieces += visit(choose_columns(one, tile), len(tile), variant, cover)
            check(len(pieces) == ambient, "rank-one terminal count for the fixture")
            matrix = one
            for piece in pieces:
                change = ring.multiply(piece, matrix)
                matrix = ring.subtract(ring.subtract(matrix, change), change)
            check(matrix == ring.subtract(ring.subtract(one, one), one), "full I target")
    return counts


def complete_rows():
    ring = Ring(3)
    group = tuple(((a, b), (c, d)) for a, b, c, d in product(range(3), repeat=4)
                  if (a*d-b*c) % 3)
    addresses = tuple(product(range(3), repeat=4))
    position = {point: index for index, point in enumerate(addresses)}
    bits = len(addresses)
    target = ((1, 0), (0, 0))
    opposite = ring.subtract(identity(2), target)
    matchers = (((1, 1), (0, 1)), ((1, 0), (1, 1)))
    early = ((0, 1), (1, 0))

    def image(p, address):
        # A=diag(2,1) is one common external unit weight. Tail atoms are reversed.
        h = (2*address[0] % 3, address[1])
        d = address[2:][::-1]
        offset = ring.action(p, tuple((x-y) % 3 for x, y in zip(h, d)))
        h2 = tuple((x-z) % 3 for x, z in zip(h, offset))
        d2 = tuple((y+z) % 3 for y, z in zip(d, offset))
        return (2*h2[0] % 3, h2[1]) + d2[::-1]

    def permute(p, vector):
        result = [0]*bits
        for j, address in enumerate(addresses):
            result[position[image(p, address)]] = vector[j]
        return result

    # Each cell carries its own independent Boolean variable as a unit bit mask.
    raw = [{g: [1 << ((role*len(group)+row)*bits+j) for j in range(bits)]
            for row, g in enumerate(group)} for role in range(2)]

    def tile(inputs, projector, active_matchers):
        routed, result = [{}, {}], [{}, {}]
        for role, match in enumerate(active_matchers):
            for g in group:
                routed[role][ring.multiply(g, match)] = inputs[role][g]
            check(len(routed[role]) == len(group), "fresh cover fiber permutation")
        for h in group:
            x, y = (routed[i][h] for i in range(2))
            common = ring.conjugate(h, projector)
            coupled = permute(common, [a ^ b for a, b in zip(x, y)])
            move_y = permute(common, y)
            for role, output in enumerate(([a ^ b for a, b in zip(coupled, move_y)], move_y)):
                parent = ring.multiply(h, ring.inverse(active_matchers[role]))
                result[role][parent] = output
        return result

    correct_first = tile(raw, target, matchers)
    for role, match in enumerate(matchers):
        for g in group:
            canonical = ring.conjugate(ring.multiply(g, match), target)
            check(correct_first[role][g] == permute(canonical, raw[role][g]), "matched proper target")
    expected = [{g: permute(identity(2), raw[role][g]) for g in group} for role in range(2)]
    complete = tile(correct_first, opposite, matchers)
    check(complete == expected, "every role, row and arbitrary address label restored")
    wrong = tile(raw, target, (matchers[0], identity(2)))
    # A prematurely added cover can take this row before a proper target returns.
    premature = tile(raw, ring.conjugate(early, target), matchers)
    controls = {}
    for name, damaged in (("omitted_tile", correct_first),
                          ("wrong_matcher", tile(wrong, opposite, matchers)),
                          ("premature_cover", tile(premature, opposite, matchers))):
        mismatches = sum(a != b for role in range(2) for g in group
                         for a, b in zip(damaged[role][g], expected[role][g]))
        check(mismatches > 0, name + " accepted")
        controls[name] = mismatches
    return 2*len(group)*bits, controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, default=Path(__file__).resolve().parents[2] / SOURCE_PATH)
    args = parser.parse_args()
    ring = Ring(101**2)
    counts = fixed_ambient(load_helpers(args.word, ring), ring)
    labels, controls = complete_rows()
    print(f"PASS_DIRECT_BIT_GEOMETRY matches={counts['matches']} peels={counts['peels']} "
          f"leaves={counts['leaves']} labelled_cells={labels} "
          + " ".join(f"{k}={v}" for k, v in controls.items()))


if __name__ == "__main__":
    main()
