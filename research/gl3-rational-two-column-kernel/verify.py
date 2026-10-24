#!/usr/bin/env python3
"""Exact characteristic-zero GL3 two-column kernel. Apache-2.0."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

N = 8
SIZE = 168
PRIME = 65537
IDENTITY = tuple(range(N))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compose(a, b):
    return tuple(a[b[x]] for x in range(N))


def from_columns(columns):
    return tuple(columns[0] * (x & 1) ^ columns[1] * ((x >> 1) & 1)
                 ^ columns[2] * ((x >> 2) & 1) for x in range(N))


def construct_group():
    candidates = (from_columns(c) for c in product(range(1, N), repeat=3))
    group = sorted(g for g in candidates if len(set(g)) == N)
    require(len(group) == SIZE and len(set(group)) == SIZE, "GL3 order")
    # A second construction starts from elementary binary row additions.
    generators = [tuple(x ^ (((x >> j) & 1) << i) for x in range(N))
                  for i in range(3) for j in range(3) if i != j]
    reached, queue = {IDENTITY}, [IDENTITY]
    for index in range(SIZE):
        require(index < len(queue), "premature generator closure")
        for generator in generators:
            value = compose(generator, queue[index])
            if value not in reached:
                reached.add(value)
                queue.append(value)
        require(len(queue) <= SIZE, "generator closure exceeded GL3")
    require(reached == set(group), "independent group constructions disagree")
    labels = {g: i for i, g in enumerate(group)}
    table = [[labels[compose(a, b)] for b in group] for a in group]
    return group, table, labels[IDENTITY]


def element_orders(table, one):
    orders = []
    for g in range(SIZE):
        current = one
        for exponent in range(1, SIZE + 1):
            current = table[current][g]
            if current == one:
                orders.append(exponent)
                break
        else:
            raise ValueError("element order exceeds group order")
    require(Counter(orders) == {1: 1, 2: 21, 3: 56, 4: 42, 7: 48},
            "unexpected order populations")
    return orders


def convolution(a, b, table):
    require(len(a) == len(b) == SIZE, "group algebra vector size")
    result = [0] * SIZE
    for i in range(SIZE):
        for j in range(SIZE):
            result[table[i][j]] += a[i] * b[j]
    return result


def action(coefficients, group, width):
    require(width in (1, 2), "full action is bounded to widths one and two")
    points = tuple(product(range(N), repeat=width))
    labels = {point: i for i, point in enumerate(points)}
    matrix = [[0] * len(points) for _ in points]
    for g, coefficient in zip(group, coefficients, strict=True):
        for column, point in enumerate(points):
            row = labels[tuple(g[x] for x in point)]
            matrix[row][column] += coefficient
    return matrix


def is_zero(matrix):
    return not any(any(row) for row in matrix)


def certify_element(coefficients, group, table):
    require(convolution(coefficients, coefficients, table)
            == [56 * c for c in coefficients], "E squared differs from 56 E")
    require(is_zero(action(coefficients, group, 2)), "nonzero two-column action")
    # Check centrality directly, independently of the order-class argument.
    for g in range(SIZE):
        left, right = [0] * SIZE, [0] * SIZE
        for h in range(SIZE):
            left[table[g][h]] += coefficients[h]
            right[table[h][g]] += coefficients[h]
        require(left == right, "E is not central")


def modular_pivots(matrix):
    require(len(matrix) == SIZE and all(len(row) == SIZE for row in matrix),
            "Gram matrix shape")
    require(all(PRIME % divisor for divisor in range(2, 257)), "modulus not prime")
    work = [[x % PRIME for x in row] for row in matrix]
    labels = list(range(SIZE))
    pivot_rows, pivot_columns = [], []
    for column in range(SIZE):
        rank = len(pivot_columns)
        pivot = next((i for i in range(rank, SIZE) if work[i][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        labels[rank], labels[pivot] = labels[pivot], labels[rank]
        pivot_rows.append(labels[rank])
        pivot_columns.append(column)
        scale = pow(work[rank][column], -1, PRIME)
        work[rank] = [(x * scale) % PRIME for x in work[rank]]
        for i in range(rank + 1, SIZE):
            factor = work[i][column]
            if factor:
                work[i] = [(a - factor * b) % PRIME
                           for a, b in zip(work[i], work[rank], strict=True)]
    return pivot_rows, pivot_columns


def minor_determinant(matrix, rows, columns):
    require(len(rows) == len(columns) == 150, "rank certificate must have order 150")
    work = [[matrix[i][j] % PRIME for j in columns] for i in rows]
    determinant = 1
    for j in range(150):
        pivot = next((i for i in range(j, 150) if work[i][j]), None)
        require(pivot is not None, "zero rank-certificate determinant")
        if pivot != j:
            work[j], work[pivot] = work[pivot], work[j]
            determinant = -determinant
        diagonal = work[j][j]
        determinant = determinant * diagonal % PRIME
        inverse = pow(diagonal, -1, PRIME)
        for i in range(j + 1, 150):
            factor = work[i][j] * inverse % PRIME
            work[i] = [(a - factor * b) % PRIME
                       for a, b in zip(work[i], work[j], strict=True)]
    require(determinant != 0, "zero minor")
    return determinant


def replay_shear(group, coefficients, width, full_basis):
    require(width in (1, 2, 3) and (not full_basis or width <= 2), "replay bound")
    points = tuple(product(range(N), repeat=width))
    labels = {point: i for i, point in enumerate(points)}
    size = len(points)
    if full_basis:
        target = [[int(i == j) for j in range(2 * size)] for i in range(size)]
        source = [[int(size + i == j) for j in range(2 * size)] for i in range(size)]
    else:
        target = [[0] for _ in points]
        source = [[int(point == (1, 2, 4))] for point in points]
    initial_source = [row[:] for row in source]
    for g, coefficient in zip(group, coefficients, strict=True):
        if coefficient == 0:
            continue
        permutation = [labels[tuple(g[x] for x in point)] for point in points]
        moved = [None] * size
        for old, new in enumerate(permutation):
            moved[new] = source[old]
        require(all(row is not None for row in moved), "source permutation")
        for i in range(size):
            target[i] = [a + coefficient * b
                         for a, b in zip(target[i], moved[i], strict=True)]
        # Undo the address map on the source after every addition.
        source = [moved[new] for new in permutation]
        require(source == initial_source, "dirty source not restored")
    if full_basis:
        expected = [[int(i == j) for j in range(2 * size)] for i in range(size)]
        require(target == expected, "shear is visible below width three")
    else:
        expected = [0] * size
        for g, coefficient in zip(group, coefficients, strict=True):
            expected[labels[(g[1], g[2], g[4])]] += coefficient
        require([row[0] for row in target] == expected, "width-three shear witness")
        require(sum(value != 0 for value in expected) == 112, "witness support")
    return 2 * size if full_basis else 1


def failure_controls(coefficients, orders, group, table):
    rejected = 0
    for order in (1, 2, 4, 7):
        changed = [0 if n == order else c
                   for c, n in zip(coefficients, orders, strict=True)]
        try:
            certify_element(changed, group, table)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("omitted class was accepted")
    norm = action([1] * SIZE, group, 2)
    require(norm[0][0] == SIZE and not is_zero(norm), "characteristic-zero norm control")
    return {"omitted_classes_rejected": rejected, "group_norm_at_fixed_pair": norm[0][0]}


def verify():
    group, table, one = construct_group()
    orders = element_orders(table, one)
    coefficients = [{1: 6, 2: -2, 3: 0, 4: 2, 7: -1}[n] for n in orders]
    certify_element(coefficients, group, table)
    require(is_zero(action(coefficients, group, 1)), "width-one action")
    regular_orbit = {(g[1], g[2], g[4]) for g in group}
    require(len(regular_orbit) == SIZE, "width three lacks a regular orbit")
    gram = [[sum(a[x] == b[x] for x in range(N)) ** 2 for b in group]
            for a in group]
    rows, columns = modular_pivots(gram)
    require(len(rows) == len(columns) == 150, "two-column Gram rank")
    determinant = minor_determinant(gram, rows, columns)
    ideal_dimension, remainder = divmod(SIZE * coefficients[one], 56)
    require(remainder == 0 and ideal_dimension == 18, "idempotent trace")
    require(150 + ideal_dimension == SIZE, "kernel/image dimensions")
    replay_columns = [replay_shear(group, coefficients, f, True) for f in (1, 2)]
    replay_shear(group, coefficients, 3, False)
    return {
        "group_order": SIZE, "order_populations": dict(sorted(Counter(orders).items())),
        "annihilator_class_coefficients": {"1": 6, "2": -2, "3": 0, "4": 2, "7": -1},
        "scale": 56, "kernel_dimension": ideal_dimension, "action_rank": 150,
        "annihilator_support": sum(c != 0 for c in coefficients),
        "minor_prime": PRIME, "minor_rows": rows, "minor_columns": columns,
        "minor_determinant_mod_prime": determinant,
        "complete_dirty_replay_columns": replay_columns,
        "width_three_witness_support": 112,
        "controls": failure_controls(coefficients, orders, group, table),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="exclusively create a hash-bound receipt")
    args = parser.parse_args()
    result = verify()
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((package / name).read_bytes()).hexdigest() for name in names}
    receipt = {"schema": "gl3-rational-two-column-kernel/v1", "result": result,
               "source_sha256": hashes}
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS_GL3_RATIONAL_TWO_COLUMN_KERNEL group=168 image=150 kernel=18 "
          "E_squared=56E support=112 dirty_columns=144 no_new_kappa")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
