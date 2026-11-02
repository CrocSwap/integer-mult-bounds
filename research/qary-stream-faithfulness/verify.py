#!/usr/bin/env python3
"""Exact, bounded checks for the defining-characteristic stream interface."""

import argparse
from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Field:
    """Polynomial-basis fields for the six declared finite fixtures only."""

    def __init__(self, q, bad_modulus=False):
        specs = {2: (2, 1, (0,)), 3: (3, 1, (0,)),
                 4: (2, 2, (1, 1)), 5: (5, 1, (0,)),
                 8: (2, 3, (1, 1, 0)), 9: (3, 2, (1, 0))}
        require(q in specs, "unsupported fixture field")
        self.q = q
        self.p, self.degree, self.modulus = specs[q]
        if bad_modulus:
            require(q == 9, "bad-modulus control is defined only for q=9")
            self.modulus = (2, 0)
        self.digits = tuple(tuple((a // self.p**i) % self.p
                                  for i in range(self.degree)) for a in range(q))
        self.add = tuple(tuple(self.sum_code(a, b) for b in range(q))
                         for a in range(q))
        self.mul = tuple(tuple(self.product_code(a, b) for b in range(q))
                         for a in range(q))
        self.neg = tuple(next(b for b in range(q) if self.add[a][b] == 0)
                         for a in range(q))
        self.inv = (0,) + tuple(next((b for b in range(1, q)
                                      if self.mul[a][b] == 1), 0)
                               for a in range(1, q))
        require(all(self.inv[1:]), "modulus does not define a field")

    def sum_code(self, a, b):
        return sum(((x + y) % self.p) * self.p**i
                   for i, (x, y) in enumerate(zip(self.digits[a], self.digits[b])))

    def product_code(self, a, b):
        work = [0] * (2 * self.degree - 1)
        for i, x in enumerate(self.digits[a]):
            for j, y in enumerate(self.digits[b]):
                work[i + j] = (work[i + j] + x * y) % self.p
        for i in range(len(work) - 1, self.degree - 1, -1):
            for j, c in enumerate(self.modulus):
                at = i - self.degree + j
                work[at] = (work[at] - work[i] * c) % self.p
        return sum(work[i] * self.p**i for i in range(self.degree))


def rank(rows, field):
    basis = {}
    for original in rows:
        row = list(original)
        for i in range(len(row)):
            if row[i] == 0:
                continue
            if i not in basis:
                scale = field.inv[row[i]]
                basis[i] = tuple(field.mul[scale][x] for x in row)
                break
            scale = row[i]
            row = [field.add[x][field.neg[field.mul[scale][y]]]
                   for x, y in zip(row, basis[i])]
    return len(basis)


def field_checks(field):
    for a in range(field.q):
        require(field.add[a][0] == a and field.mul[a][1] == a, "field identities")
    for a, b, c in product(range(field.q), repeat=3):
        require(field.add[a][b] == field.add[b][a], "addition commutativity")
        require(field.mul[a][b] == field.mul[b][a], "multiplication commutativity")
        require(field.add[field.add[a][b]][c] == field.add[a][field.add[b][c]],
                "addition associativity")
        require(field.mul[field.mul[a][b]][c] == field.mul[a][field.mul[b][c]],
                "multiplication associativity")
        require(field.mul[a][field.add[b][c]] ==
                field.add[field.mul[a][b]][field.mul[a][c]], "distributivity")
    return field.q**3


def gl_order(q, d):
    answer = 1
    for j in range(d):
        answer *= q**d - q**j
    return answer


def group_fixture(field, d, affine):
    require(d in (1, 2) and field.q ** (d * d) <= 256, "group fixture bound")
    points = tuple(product(range(field.q), repeat=d))
    indices = {point: i for i, point in enumerate(points)}
    elements, actions = [], []
    offsets = points if affine else ((0,) * d,)
    for entries in product(range(field.q), repeat=d * d):
        matrix = tuple(entries[i * d:(i + 1) * d] for i in range(d))
        if rank(matrix, field) != d:
            continue
        for offset in offsets:
            permutation = []
            for point in points:
                image = list(offset)
                for i, row in enumerate(matrix):
                    for a, x in zip(row, point):
                        image[i] = field.add[image[i]][field.mul[a][x]]
                permutation.append(indices[tuple(image)])
            require(len(set(permutation)) == len(points), "not a permutation")
            elements.append((entries, offset))
            actions.append(tuple(permutation))
    expected = gl_order(field.q, d) * (field.q**d if affine else 1)
    require(len(elements) == expected == len(set(actions)), "group enumeration")
    return points, tuple(elements), tuple(actions)


def threshold(q, d, affine):
    if d >= 2:
        return d + int(affine)
    if affine:
        return 1 if q == 2 else 2
    return 0 if q == 2 else 1


def separating_tuple(points, q, d, affine):
    if threshold(q, d, affine) == 0:
        return ()
    if affine and q == 2 and d == 1:
        return (points.index((0,)),)
    basis = tuple(points.index(tuple(int(i == j) for i in range(d)))
                  for j in range(d))
    return (points.index((0,) * d),) + basis if affine else basis


def regular_images(actions, address):
    images = tuple(tuple(action[x] for x in address) for action in actions)
    require(len(set(images)) == len(actions), "tuple does not separate labels")
    return images


def annihilator(field, d, affine, elements):
    if d >= 2 or (affine and field.q == 2):
        return tuple(1 for _ in elements)
    a = 2
    return tuple(1 if matrix == (a,) else field.p - 1 if matrix == (1,)
                 else 0 for matrix, _ in elements)


def image_coefficients(actions, address, coefficients, p):
    image = Counter()
    for action, coefficient in zip(actions, coefficients):
        key = tuple(action[x] for x in address)
        image[key] = (image[key] + coefficient) % p
    return {key: value for key, value in image.items() if value}


def check_widths(field, d, affine, points, elements, actions):
    width = threshold(field.q, d, affine)
    kernel = annihilator(field, d, affine, elements)
    require(any(kernel), "annihilator must be formally nonzero")
    profiles, tuples_checked = [], 0
    for w in range(width):
        stabilizers = Counter()
        for address in product(range(len(points)), repeat=w):
            fixed = sum(all(action[x] == x for x in address) for action in actions)
            if affine and not address:
                expected = len(actions)
            else:
                vectors = tuple(points[x] for x in address)
                if affine:
                    base = vectors[0]
                    vectors = tuple(tuple(field.add[x][field.neg[y]]
                                          for x, y in zip(v, base))
                                    for v in vectors[1:])
                r = rank(vectors, field)
                expected = field.q ** (r * (d - r)) * gl_order(field.q, d - r)
            require(fixed == expected, "stabilizer formula mismatch")
            require(not image_coefficients(actions, address, kernel, field.p),
                    "proposed below-threshold element is not in the kernel")
            stabilizers[fixed] += 1
            tuples_checked += 1
        profiles.append({"width": w, "stabilizers": sorted(stabilizers.items())})
    address = separating_tuple(points, field.q, d, affine)
    images = regular_images(actions, address)
    require(len(address) == width, "wrong claimed least width")
    for shift in range(field.p):
        coefficients = tuple((i + shift) % field.p for i in range(len(actions)))
        actual = image_coefficients(actions, address, coefficients, field.p)
        expected = {image: c for image, c in zip(images, coefficients) if c}
        require(actual == expected, "regular-orbit coefficient recovery")
    return {"q": field.q, "d": d, "affine": affine, "group_order": len(actions),
            "least_width": width, "below_threshold_tuples": tuples_checked,
            "profiles": profiles, "separating_orbit": len(images)}


def line_image_rank(field, actions):
    """Independent full permutation-matrix span at one point column."""
    rows = []
    for permutation in actions:
        row = [0] * (field.q * field.q)
        for x, y in enumerate(permutation):
            row[y * field.q + x] = 1
        rows.append(row)
    return rank(rows, Field(field.p))


def inverse_permutation(permutation):
    inverse = [0] * len(permutation)
    for x, y in enumerate(permutation):
        inverse[y] = x
    return tuple(inverse)


def alias_program(elements, actions):
    program = []
    identity = tuple(range(len(actions[0])))
    for (matrix, _), action in zip(elements, actions):
        coefficient = 1 if matrix == (2,) else -1
        if action != identity:
            program.append(("address", inverse_permutation(action)))
        program.append(("add", coefficient))
        if action != identity:
            program.append(("address", action))
    return tuple(program)


def literal_endpoint(program, w):
    addresses = tuple(product(range(3), repeat=w))
    index = {address: i for i, address in enumerate(addresses)}
    n = len(addresses)
    rows = [[int(i == j) for j in range(2 * n)] for i in range(2 * n)]
    for kind, operand in program:
        if kind == "address":
            moved = [None] * n
            for x, address in enumerate(addresses):
                y = index[tuple(operand[t] for t in address)]
                moved[y] = rows[x]
            rows[:n] = moved
        else:
            require(kind == "add" and operand in (-1, 1), "invalid literal event")
            rows[:n] = [[(a + operand * b) % 3 for a, b in zip(x, y)]
                        for x, y in zip(rows[:n], rows[n:])]
    return rows


def formal_endpoint(program):
    identity = tuple(range(3))
    own, borrowed = {identity: 1}, {}
    for kind, operand in program:
        if kind == "address":
            own = {tuple(operand[x] for x in g): c for g, c in own.items()}
            borrowed = {tuple(operand[x] for x in g): c for g, c in borrowed.items()}
        else:
            borrowed[identity] = (borrowed.get(identity, 0) + operand) % 3
            borrowed = {g: c for g, c in borrowed.items() if c}
    require(own == {identity: 1}, "formal own-input endpoint")
    return borrowed


def changed_columns(rows):
    return tuple(j for j in range(len(rows))
                 if any(rows[i][j] != int(i == j) for i in range(len(rows))))


def reject(operation, *args):
    try:
        operation(*args)
    except ValueError:
        return 1
    raise ValueError("negative control was accepted")


def source_bytes(row, data):
    require(hashlib.sha256(data).hexdigest() == row["sha256"], "source digest drift")


def source_checks(package):
    manifest = json.loads((package / "SOURCES.json").read_text())
    controls = 0
    for row in manifest["files"]:
        if row["usage"] == "input":
            data = (package.parents[1] / row["path"]).read_bytes()
            source_bytes(row, data)
            controls += reject(source_bytes, row, data + b"\ncorruption")
    require(controls == 1, "exactly one predecessor documentation input is declared")
    return controls


def semantic_controls(fixtures, program):
    actions = fixtures[(3, 2, False)][3]
    controls = reject(regular_images, actions, (0,))
    f, _, els, acts = fixtures[(3, 1, True)]
    controls += reject(regular_images, acts, (0,))
    require(line_image_rank(f, acts) < len(acts), "affine-line exception lost")
    require(image_coefficients(actions, (1,), (1,) * len(actions), 5),
            "wrong-characteristic norm control failed")
    controls += 1
    kernel = list(annihilator(f, 1, True, els))
    kernel[0] = (kernel[0] + 1) % 3
    require(image_coefficients(acts, (0,), kernel, 3), "missing coset term hidden")
    controls += 1
    controls += reject(Field, 6) + reject(Field, 9, True)
    omitted = 0
    for i, event in enumerate(program):
        if event[0] == "add":
            require(changed_columns(literal_endpoint(program[:i] + program[i + 1:], 1)),
                    "omitted scalar ADD was accepted")
            omitted += 1
    require(omitted == 6, "scalar omission domain")
    controls += omitted
    wide = literal_endpoint(program, 2)
    require(all(j >= 9 for j in changed_columns(wide)), "own dirty role changed")
    require(len(changed_columns(wide)) == 6, "borrowed dirty role was not tested")
    return controls + 1


def run(package):
    controls = source_checks(package)
    cases = [(q, 1, affine) for q in (2, 3, 4, 5, 8, 9) for affine in (False, True)]
    cases += [(3, 2, False), (3, 2, True), (4, 2, False)]
    fields = {q: Field(q) for q in (2, 3, 4, 5, 8, 9)}
    axioms = sum(field_checks(field) for field in fields.values())
    fixtures, results, line_ranks = {}, [], []
    for q, d, affine in cases:
        field = fields[q]
        points, elements, actions = group_fixture(field, d, affine)
        fixtures[(q, d, affine)] = (field, points, elements, actions)
        results.append(check_widths(field, d, affine, points, elements, actions))
        if d == 1:
            line_ranks.append({"q": q, "affine": affine,
                               "rank": line_image_rank(field, actions), "labels": len(actions)})
    field, _, elements, actions = fixtures[(3, 1, True)]
    program = alias_program(elements, actions)
    formal = formal_endpoint(program)
    expected = {action: c for action, c in zip(actions, annihilator(field, 1, True, elements)) if c}
    require(formal == expected and len(formal) == 6, "formal coset-shear endpoint")
    narrow, wide = literal_endpoint(program, 1), literal_endpoint(program, 2)
    require(not changed_columns(narrow), "one-column alias failed")
    require(len(changed_columns(wide)) == 6, "two-column detection failed")
    controls += semantic_controls(fixtures, program)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(package.iterdir()) if p.is_file()}
    return {"status": "PASS_QARY_STREAM_FAITHFULNESS", "cases": results,
            "field_triples": axioms, "line_action_ranks": line_ranks,
            "literal_alias": {"address_events": sum(k == "address" for k, _ in program),
                              "scalar_adds": sum(k == "add" for k, _ in program),
                              "dirty_basis_columns": len(narrow) + len(wide),
                              "w2_changed_columns": len(changed_columns(wide)),
                              "formal_nonzero_coefficients": len(formal)},
            "controls": controls, "source_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    result = run(Path(__file__).resolve().parent)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
