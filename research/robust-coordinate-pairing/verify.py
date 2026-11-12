#!/usr/bin/env python3
"""Exact clean-rectangle predictions versus complete small-field sandwiches."""

from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


def need(condition, message):
    if not condition:
        raise ValueError(message)


def norm(value, prime):
    return value % prime if prime else Fraction(value)


def eye(size):
    return tuple(tuple(int(i == j) for j in range(size)) for i in range(size))


def matrices(rows, columns, prime):
    need(1 <= rows <= 3 and 1 <= columns <= 3, "enumeration shape")
    need(prime in (2, 3) and prime ** (rows * columns) <= 512, "enumeration cap")
    return tuple(tuple(tuple(flat[i * columns:(i + 1) * columns])
                       for i in range(rows))
                 for flat in product(range(prime), repeat=rows * columns))


def multiply(left, right, prime):
    need(left and right and len(left[0]) == len(right), "product shape")
    need(max(len(left), len(right), len(right[0])) <= 5, "matrix cap")
    return tuple(tuple(norm(sum(left[i][k] * right[k][j]
                                for k in range(len(right))), prime)
                       for j in range(len(right[0])))
                 for i in range(len(left)))


def rank(matrix, prime):
    if not matrix or not matrix[0]:
        return 0
    work = [list(row) for row in matrix]
    rows, columns = len(work), len(work[0])
    need(rows <= 5 and columns <= 5, "rank shape cap")
    pivot = 0
    for column in range(columns):
        candidates = [i for i in range(pivot, rows) if work[i][column]]
        if not candidates:
            continue
        chosen = candidates[0]
        work[pivot], work[chosen] = work[chosen], work[pivot]
        value = work[pivot][column]
        reciprocal = pow(value, -1, prime) if prime else 1 / Fraction(value)
        work[pivot] = [norm(x * reciprocal, prime) for x in work[pivot]]
        for i in range(rows):
            if i != pivot:
                factor = work[i][column]
                work[i] = [norm(a - factor * b, prime)
                           for a, b in zip(work[i], work[pivot], strict=True)]
        pivot += 1
        if pivot == rows:
            break
    return pivot


def inverse(matrix, prime):
    size = len(matrix)
    need(1 <= size <= 5 and all(len(row) == size for row in matrix), "inverse shape")
    work = [list(row) + list(unit)
            for row, unit in zip(matrix, eye(size), strict=True)]
    for column in range(size):
        candidates = [i for i in range(column, size) if work[i][column]]
        need(candidates, "singular minor")
        chosen = candidates[0]
        work[column], work[chosen] = work[chosen], work[column]
        value = work[column][column]
        reciprocal = pow(value, -1, prime) if prime else 1 / Fraction(value)
        work[column] = [norm(x * reciprocal, prime) for x in work[column]]
        for i in range(size):
            if i != column:
                factor = work[i][column]
                work[i] = [norm(a - factor * b, prime)
                           for a, b in zip(work[i], work[column], strict=True)]
    result = tuple(tuple(row[size:]) for row in work)
    need(multiply(matrix, result, prime) == eye(size), "inverse endpoint")
    return result


def submatrix(matrix, rows, columns):
    return tuple(tuple(matrix[i][j] for j in columns) for i in rows)


def rectangles(matrix, prime):
    rows, columns = len(matrix), len(matrix[0])
    need(1 <= rows <= 5 and 1 <= columns <= 5, "rectangle cap")
    records = []
    for row_mask in range(1 << rows):
        chosen_rows = tuple(i for i in range(rows) if row_mask >> i & 1)
        for column_mask in range(1 << columns):
            chosen_columns = tuple(j for j in range(columns) if column_mask >> j & 1)
            mask = sum(1 << (i * columns + j)
                       for i in chosen_rows for j in chosen_columns)
            dimension = rank(submatrix(matrix, chosen_rows, chosen_columns), prime)
            records.append((dimension, mask, chosen_rows, chosen_columns))
    return tuple(records)


def prediction(records, errors):
    return max((row for row in records if not row[1] & errors), key=lambda row: row[0])


def witness(matrix, record, prime):
    dimension, _, rows, columns = record
    if dimension == 0:
        return (), tuple(() for _ in matrix[0])
    for chosen_rows in combinations(rows, dimension):
        for chosen_columns in combinations(columns, dimension):
            minor = submatrix(matrix, chosen_rows, chosen_columns)
            if rank(minor, prime) != dimension:
                continue
            inv = inverse(minor, prime)
            left = tuple(tuple(inv[a][chosen_rows.index(i)] if i in chosen_rows else 0
                               for i in range(len(matrix)))
                         for a in range(dimension))
            right = tuple(tuple(int(j == chosen_columns[b]) for b in range(dimension))
                          for j in range(len(matrix[0])))
            return left, right
    raise ValueError("missing full-rank minor")


def changed(matrix, index, prime):
    columns = len(matrix[0])
    return tuple(tuple(norm(value + int(i * columns + j == index), prime)
                       for j, value in enumerate(row))
                 for i, row in enumerate(matrix))


def check_pairing(matrix, left, right, errors, prime):
    if not left:
        return
    dimension = len(left)
    need(multiply(multiply(left, matrix, prime), right, prime) == eye(dimension),
         "nominal pairing")
    for index in range(len(matrix) * len(matrix[0])):
        if errors >> index & 1:
            alternative = changed(matrix, index, prime)
            need(multiply(multiply(left, alternative, prime), right, prime) == eye(dimension),
                 "single-entry pairing")


def literal_sandwich(left, middle_right, prime):
    """Separate oracle arithmetic: reject at the first nonidentity entry."""
    size = len(left)
    for a in range(size):
        for b in range(size):
            value = 0
            for k in range(len(middle_right)):
                value += left[a][k] * middle_right[k][b]
            if value % prime != int(a == b):
                return False
    return True


def oracle(matrix, prime):
    """Enumerate every X,Y; directly test every single-entry alternative."""
    rows, columns = len(matrix), len(matrix[0])
    capacities = [0] * (1 << (rows * columns))
    accepted, examined = 0, 0
    alternatives = tuple(changed(matrix, index, prime) for index in range(rows * columns))
    for dimension in range(1, min(rows, columns) + 1):
        all_right = matrices(columns, dimension, prime)
        right_products = tuple(multiply(matrix, right, prime) for right in all_right)
        for left in matrices(dimension, rows, prime):
            for right, middle_right in zip(all_right, right_products, strict=True):
                examined += 1
                if not literal_sandwich(left, middle_right, prime):
                    continue
                accepted += 1
                legal = 0
                for index, alternative in enumerate(alternatives):
                    alt_product = multiply(alternative, right, prime)
                    if literal_sandwich(left, alt_product, prime):
                        legal |= 1 << index
                for errors in range(1 << (rows * columns)):
                    if not errors & ~legal:
                        capacities[errors] = max(capacities[errors], dimension)
    return capacities, accepted, examined


def exhaustive_families():
    digest = sha256()
    counts = {"nominal_matrices": 0, "support_cases": 0, "sandwiches_examined": 0,
              "nominal_identity_sandwiches": 0, "attaining_pairings": 0}
    domains = ((1, 1, 2), (1, 1, 3), (2, 2, 2), (2, 2, 3),
               (2, 3, 2), (3, 2, 2), (3, 3, 2))
    for rows, columns, prime in domains:
        samples = (eye(3),) if rows == columns == 3 else matrices(rows, columns, prime)
        for matrix in samples:
            capacities, accepted, examined = oracle(matrix, prime)
            records = rectangles(matrix, prime)
            counts["nominal_matrices"] += 1
            counts["sandwiches_examined"] += examined
            counts["nominal_identity_sandwiches"] += accepted
            for errors, capacity in enumerate(capacities):
                record = prediction(records, errors)
                need(record[0] == capacity, "rectangle/oracle disagreement")
                left, right = witness(matrix, record, prime)
                check_pairing(matrix, left, right, errors, prime)
                counts["attaining_pairings"] += int(capacity > 0)
                counts["support_cases"] += 1
                digest.update(json.dumps([prime, matrix, errors, capacity], separators=(",", ":")).encode())
    counts["capacity_table_sha256"] = digest.hexdigest()
    return counts


def independent_set_size(size, errors):
    maximum = 0
    for subset in range(1 << size):
        valid = True
        for i in range(size):
            for j in range(size):
                if subset >> i & 1 and subset >> j & 1 and errors >> (i * size + j) & 1:
                    valid = False
        if valid:
            maximum = max(maximum, subset.bit_count())
    return maximum


def graph_cases():
    counts = {"graphs": 0, "cycle_instances": 0}
    for size in range(1, 4):
        records = rectangles(eye(size), 2)
        for errors in range(1 << (size * size)):
            need(prediction(records, errors)[0] == independent_set_size(size, errors),
                 "graph capacity")
            counts["graphs"] += 1
    for size in range(3, 6):
        errors = sum(1 << (i * size + (i + 1) % size) for i in range(size))
        for prime in (0, 2, 3, 5, 7):
            record = prediction(rectangles(eye(size), prime), errors)
            need(record[0] == size // 2, "cycle floor")
            check_pairing(eye(size), *witness(eye(size), record, prime), errors, prime)
            for i in range(size):
                alternative = changed(eye(size), i * size + (i + 1) % size, prime)
                need(rank(alternative, prime) == size, "invertible cycle alternative")
            counts["cycle_instances"] += 1
    return counts


def rational_cases():
    fixtures = (((Fraction(3, 2), 0), (0, Fraction(5, 8))),
                ((0, 1), (1, 0)), ((1, 1), (1, 1)),
                ((1, Fraction(1, 2), 0), (0, 1, Fraction(-3, 4))))
    checked = 0
    for matrix in fixtures:
        records = rectangles(matrix, 0)
        for errors in range(1 << (len(matrix) * len(matrix[0]))):
            record = prediction(records, errors)
            check_pairing(matrix, *witness(matrix, record, 0), errors, 0)
            checked += 1
    return {"rational_support_cases": checked}


def controls():
    left = ((0, Fraction(-1, 2), Fraction(1, 2)),
            (1, Fraction(1, 2), Fraction(-1, 2)))
    right = ((1, 1), (-1, 0), (1, 0))
    skew = ((0, 1, 1), (-1, 0, 1), (-1, -1, 0))
    need(multiply(left, right, 0) == eye(2), "correlated nominal")
    need(multiply(multiply(left, skew, 0), right, 0) == ((0, 0), (0, 0)), "correlated error")
    complete = sum(1 << (i * 3 + j) for i in range(3) for j in range(3) if i != j)
    need(prediction(rectangles(eye(3), 0), complete)[0] == 1, "independent/correlated gap")
    swap = ((0, 1), (1, 0))
    need(prediction(rectangles(swap, 0), 9)[0] == 1, "nonidentity nominal")
    need(independent_set_size(2, 9) == 0, "graph corollary nominal boundary")
    rejected = 0
    for errors in (1, 2, 4, 8):
        try:
            check_pairing(eye(2), eye(2), eye(2), errors, 2)
        except ValueError as error:
            need(str(error) == "single-entry pairing", "wrong rejection")
            rejected += 1
        else:
            raise ValueError("omitted-error mutation accepted")
    need(rank(((1, 0), (0, 0)), 2) == 1, "singular baseline rank")
    need(prediction(rectangles(eye(2), 2), 0)[0] == 2, "empty uncertainty")
    need(prediction(rectangles(eye(2), 2), 15)[0] == 0, "full uncertainty")
    return {"boundary_equalities": 8, "omitted_error_rejections": rejected}


def source_hashes():
    root = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result = {}
    for name in names:
        data = (root / name).read_bytes()
        need(len(data) <= 256 * 1024, "package-file size cap")
        result[name] = sha256(data).hexdigest()
    return result


def main():
    result = {"status": "PASS_ROBUST_COORDINATE_PAIRING", "claim_type": "scoped written proof",
              "exhaustive": exhaustive_families(), "graph": graph_cases(),
              "rational": rational_cases(), "controls": controls(),
              "source_sha256": source_hashes()}
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
