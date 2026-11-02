"""Exact finite corroboration of the new rank-one wrapper repair theorem."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduce_value(value, prime):
    return value % prime if prime else value


def identity(size):
    require(1 <= size <= 10, "identity size outside verifier capacity")
    return tuple(tuple(int(i == j) for j in range(size)) for i in range(size))


def add(left, right, prime, sign=1):
    return tuple(tuple(reduce_value(a + sign * b, prime)
                       for a, b in zip(x, y, strict=True))
                 for x, y in zip(left, right, strict=True))


def multiply(left, right, prime):
    columns = tuple(zip(*right, strict=True))
    return tuple(tuple(reduce_value(sum(a * b for a, b in zip(x, y, strict=True)), prime)
                       for y in columns) for x in left)


def outer(column, row, prime):
    return tuple(tuple(reduce_value(a * b, prime) for b in row) for a in column)


def rref(matrix, prime):
    height, width = len(matrix), len(matrix[0])
    require(1 <= height <= 5 and 1 <= width <= 10, "matrix outside verifier capacity")
    require(all(len(row) == width for row in matrix), "ragged matrix")
    require(prime in (0, 2, 3, 5, 7), "unsupported verifier field")
    rows = [list(row) for row in matrix]
    pivots = []
    for column in range(width):
        pivot = next((i for i in range(len(pivots), height) if rows[i][column]), None)
        if pivot is None:
            continue
        index = len(pivots)
        rows[index], rows[pivot] = rows[pivot], rows[index]
        scalar = pow(rows[index][column], -1, prime) if prime else 1 / Fraction(rows[index][column])
        rows[index] = [reduce_value(value * scalar, prime) for value in rows[index]]
        for i in range(height):
            if i != index:
                factor = rows[i][column]
                rows[i] = [reduce_value(a - factor * b, prime)
                           for a, b in zip(rows[i], rows[index], strict=True)]
        pivots.append(column)
        if len(pivots) == height:
            break
    return tuple(tuple(row) for row in rows), tuple(pivots)


def inverse(matrix, prime):
    size = len(matrix)
    require(1 <= size <= 5 and all(len(row) == size for row in matrix), "inverse requires a square matrix")
    augmented = tuple(row + unit for row, unit in zip(matrix, identity(size), strict=True))
    reduced, _ = rref(augmented, prime)
    if tuple(row[:size] for row in reduced) != identity(size):
        return None
    return tuple(row[size:] for row in reduced)


def factors(matrix, prime):
    reduced, pivots = rref(matrix, prime)
    return tuple((tuple(row[column] for row in matrix), reduced[i])
                 for i, column in enumerate(pivots))


def gates(first, second, prime, helpers=0):
    """Construct the literal six operations by executing each on basis vectors."""
    width = len(first)
    first_inverse, second_inverse = inverse(first, prime), inverse(second, prime)
    require(first_inverse is not None and second_inverse is not None, "singular callee")
    size = 2 * width + helpers
    require(size <= 5, "whole-state capacity exceeded")
    result = []
    for operation in range(6):
        columns = []
        for basis in identity(size):
            h, d, workspace = basis[:width], basis[width:2 * width], basis[2 * width:]
            if operation == 0:
                d = tuple(a - b for a, b in zip(d, h, strict=True))
            elif operation in (1, 3):
                forward = first if operation == 1 else second
                backward = first_inverse if operation == 1 else second_inverse
                h, d = tuple(sum(a * b for a, b in zip(row, d, strict=True)) for row in forward), tuple(
                    sum(a * b for a, b in zip(row, h, strict=True)) for row in backward)
            elif operation in (2, 5):
                d = tuple(a + b for a, b in zip(d, h, strict=True))
            else:
                d = tuple(-a for a in d)
            columns.append(tuple(reduce_value(value, prime) for value in h + d + workspace))
        result.append(tuple(zip(*columns, strict=True)))
    return tuple(result)


def endpoint(word, prime):
    state = identity(len(word[0]))
    for gate in word:
        state = multiply(gate, state, prime)
    return state


def target(width, helpers=0):
    size = 2 * width + helpers
    order = tuple(range(width, 2 * width)) + tuple(range(width)) + tuple(range(2 * width, size))
    unit = identity(size)
    return tuple(unit[i] for i in order)


def correction(column, row, prime, helpers=0):
    width = len(column)
    lifted_column = (0,) * width + column + (0,) * helpers
    lifted_row = row + (0,) * (width + helpers)
    return add(identity(2 * width + helpers), outer(lifted_column, lifted_row, prime), prime)


def construction(first, prime):
    size = len(first)
    inv = inverse(first, prime)
    require(inv is not None, "construction requires an invertible first map")
    defect = add(multiply(first, first, prime), identity(size), prime, -1)
    change = add(multiply(inv, inv, prime), identity(size), prime, -1)
    split = factors(change, prime)
    reconstructed = tuple((0,) * size for _ in range(size))
    for column, row in split:
        reconstructed = add(reconstructed, outer(column, row, prime), prime)
    require(reconstructed == change, "rank factorization failed")
    require(len(split) == len(rref(defect, prime)[1]), "defect-rank mismatch")
    original = gates(first, first, prime)
    repairs = tuple(correction(column, row, prime) for column, row in split)
    require(endpoint(original[:3] + repairs + original[3:], prime) == target(size), "repair endpoint failed")
    for omitted in range(len(repairs)):
        broken = original[:3] + repairs[:omitted] + repairs[omitted + 1:] + original[3:]
        error = add(endpoint(broken, prime), target(size), prime, -1)
        require(len(rref(error, prime)[1]) == 1, "omitted correction did not leave rank-one error")
    return len(split)


def construction_census():
    domains = ((2, 1), (3, 1), (5, 1), (2, 2), (3, 2), (5, 2))
    records = []
    for prime, width in domains:
        accepted, omissions = 0, 0
        for entries in product(range(prime), repeat=width * width):
            first = tuple(tuple(entries[i * width:(i + 1) * width]) for i in range(width))
            if inverse(first, prime) is not None:
                omissions += construction(first, prime)
                accepted += 1
        records.append({"prime": prime, "width": width, "first_maps": accepted,
                        "omitted_correction_rejections": omissions})
    return records


def arbitrary_cut_census():
    """Exhaust shorter repairs for one rank-two example with one dirty helper."""
    prime, size = 2, 5
    first = ((0, 1), (1, 1))
    require(len(rref(add(multiply(first, first, prime), identity(2), prime, -1), prime)[1]) == 2,
            "shorter-repair fixture is not rank two")
    vectors = tuple(vector for vector in product(range(prime), repeat=size) if any(vector))
    repairs = tuple(add(identity(size), outer(u, v, prime), prime)
                    for u in vectors for v in vectors if sum(a * b for a, b in zip(u, v, strict=True)) % 2 == 0)
    require(len(set(repairs)) == len(repairs), "duplicate rank-one perturbation")
    circuits, second_maps = 0, 0
    for entries in product(range(prime), repeat=4):
        second = (entries[:2], entries[2:])
        if inverse(second, prime) is None:
            continue
        second_maps += 1
        word = gates(first, second, prime, helpers=1)
        require(endpoint(word, prime) != target(2, 1), "zero-correction repair found")
        circuits += 1
        for cut in range(7):
            prefix = endpoint(word[:cut], prime) if cut else identity(size)
            suffix = endpoint(word[cut:], prime) if cut < 6 else identity(size)
            for repair in repairs:
                actual = multiply(suffix, multiply(repair, prefix, prime), prime)
                require(actual != target(2, 1), "one-correction repair found")
                circuits += 1
    return {"second_maps": second_maps, "rank_one_maps": len(repairs),
            "cuts": 7, "dirty_helpers": 1, "shorter_circuits_rejected": circuits}


def controls():
    first = ((2,),)
    original = gates(first, first, 0)
    inv = inverse(first, 0)
    change = add(multiply(inv, inv, 0), identity(1), 0, -1)
    split = factors(change, 0)
    column, row = split[0]
    wrong_sign = correction(tuple(-x for x in column), row, 0)
    require(endpoint(original[:3] + (wrong_sign,) + original[3:], 0) != target(1), "wrong sign accepted")
    repair = correction(column, row, 0)
    require(endpoint((repair,) + original, 0) != target(1), "wrong cut accepted")
    mismatched = gates(first, ((3,),), 0)
    require(endpoint(mismatched[:3] + (repair,) + mismatched[3:], 0) != target(1), "wrong second callee accepted")
    for matrix, prime in ((((0,),), 2), (((1, 0),), 3)):
        try:
            construction(matrix, prime)
        except ValueError:
            continue
        raise ValueError("invalid construction input accepted")
    return 5


def main():
    records = construction_census()
    rational = (((Fraction(2), Fraction(1)), (Fraction(0), Fraction(3))),
                ((Fraction(1), Fraction(2)), (Fraction(0), Fraction(1))))
    rational_ranks = [construction(first, 0) for first in rational]
    lower = arbitrary_cut_census()
    control_count = controls()
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        path = package / name
        require(path.stat().st_size <= 1024 * 1024, "package file exceeds one MiB capacity")
        data = path.read_bytes()
        hashes[name] = sha256(data).hexdigest()
    print(json.dumps({"status": "PASS_WRAPPER_RANK_ONE_REPAIR", "claim_type": "scoped written proof with finite corroboration",
                      "construction_domains": records, "rational_fixture_ranks": rational_ranks,
                      "arbitrary_cut_lower_bound": lower, "control_groups": control_count,
                      "package_sha256": hashes, "new_kappa": False}, sort_keys=True))


if __name__ == "__main__":
    main()
