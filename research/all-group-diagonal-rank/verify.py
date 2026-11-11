"""Exact coefficient-image corroboration, produced by Nick Petalas. Apache-2.0."""

import hashlib
import itertools
import json
from pathlib import Path
import platform
import random


def need(condition, message):
    if not condition:
        raise ValueError(message)


def zeros(rows, cols):
    return [[0] * cols for _ in range(rows)]


def identity(size):
    return [[int(i == j) for j in range(size)] for i in range(size)]


def add(left, right, prime, sign=1):
    return [[(x + sign * y) % prime for x, y in zip(a, b)]
            for a, b in zip(left, right)]


def multiply(left, right, prime):
    need(len(left[0]) == len(right), "incompatible matrix shapes")
    return [[sum(x * y for x, y in zip(row, col)) % prime
             for col in zip(*right)] for row in left]


def rank(matrix, prime):
    work = [row[:] for row in matrix]
    pivot = 0
    for col in range(len(work[0])):
        found = next((i for i in range(pivot, len(work)) if work[i][col]), None)
        if found is None:
            continue
        work[pivot], work[found] = work[found], work[pivot]
        scale = pow(work[pivot][col], -1, prime)
        work[pivot] = [(x * scale) % prime for x in work[pivot]]
        for i in range(len(work)):
            if i != pivot:
                factor = work[i][col]
                work[i] = [(x - factor * y) % prime
                           for x, y in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def concatenate(matrices):
    return [list(itertools.chain.from_iterable(rows)) for rows in zip(*matrices)]


def rowspace_rank(matrix, prime):
    need(1 <= len(matrix) <= 3, "row-space oracle bound")
    span = {tuple(sum(c * row[j] for c, row in zip(coefficients, matrix)) % prime
                  for j in range(len(matrix[0])))
            for coefficients in itertools.product(range(prime), repeat=len(matrix))}
    dimensions = [d for d in range(len(matrix) + 1) if prime ** d == len(span)]
    need(len(dimensions) == 1, "row space is not a prime power")
    return dimensions[0]


def inverse(matrix, prime):
    size = len(matrix)
    work = concatenate([matrix, identity(size)])
    for col in range(size):
        found = next((i for i in range(col, size) if work[i][col]), None)
        need(found is not None, "singular change of basis")
        work[col], work[found] = work[found], work[col]
        scale = pow(work[col][col], -1, prime)
        work[col] = [(x * scale) % prime for x in work[col]]
        for i in range(size):
            if i != col:
                factor = work[i][col]
                work[i] = [(x - factor * y) % prime
                           for x, y in zip(work[i], work[col])]
    return [row[size:] for row in work]


def group_tables():
    groups = []
    for size in (4, 6):
        groups.append((f"C{size}", [[(i + j) % size for j in range(size)]
                                    for i in range(size)]))
    permutations = list(itertools.permutations(range(3)))
    table = [[permutations.index(tuple(a[b[i]] for i in range(3)))
              for b in permutations] for a in permutations]
    groups.append(("S3", table))
    return groups


def scalar(matrix):
    return {0: matrix}


def formal_multiply(left, right, table, prime):
    rows = len(next(iter(left.values())))
    cols = len(next(iter(right.values()))[0])
    result = {g: zeros(rows, cols) for g in range(len(table))}
    for g, a in left.items():
        for h, b in right.items():
            label = table[g][h]
            result[label] = add(result[label], multiply(a, b, prime), prime)
    return result


def augmentation(formal, prime):
    sample = next(iter(formal.values()))
    total = zeros(len(sample), len(sample[0]))
    for matrix in formal.values():
        total = add(total, matrix, prime)
    return total


def coefficient_rank(formal, prime):
    sample = next(iter(formal.values()))
    columns = [matrix for g, matrix in formal.items() if g != 0]
    return rank(concatenate(columns or [zeros(len(sample), 1)]), prime)


def gate(projector, label, prime):
    size = len(projector)
    need(label > 0, "paid identity label")
    need(multiply(projector, projector, prime) == projector, "not idempotent")
    return {0: add(identity(size), projector, prime, -1), label: projector}


def projector(size, chosen_rank, prime, rng):
    basis = identity(size)
    for _ in range(8):
        i, j = rng.randrange(size), rng.randrange(size)
        if i != j:
            factor = rng.randrange(prime)
            basis[i] = [(x + factor * y) % prime
                        for x, y in zip(basis[i], basis[j])]
    diagonal = [[int(i == j and i < chosen_rank) for j in range(size)]
                for i in range(size)]
    result = multiply(multiply(basis, diagonal, prime), inverse(basis, prime), prime)
    need(rank(result, prime) == chosen_rank, "projector rank")
    return result


def random_matrix(rows, cols, prime, rng):
    return [[rng.randrange(prime) for _ in range(cols)] for _ in range(rows)]


def regular_matrix(formal, table):
    sample = next(iter(formal.values()))
    rows, cols, order = len(sample), len(sample[0]), len(table)
    result = zeros(rows * order, cols * order)
    for g, matrix in formal.items():
        for i, row in enumerate(matrix):
            for j, value in enumerate(row):
                for address in range(order):
                    result[i * order + table[g][address]][j * order + address] = value
    return result


def one_circuit(table, prime, case, rng):
    length = 1 + case % 4
    widths = [rng.randrange(1, 5) for _ in range(length)]
    free = [random_matrix(3, widths[0], prime, rng)]
    free += [random_matrix(a, b, prime, rng)
             for a, b in zip(widths, widths[1:])]
    free.append(random_matrix(widths[-1], 3, prime, rng))
    value = scalar(free[0])
    literal = regular_matrix(value, table)
    prefix, images, budget = free[0], [], 0
    for j, width in enumerate(widths):
        chosen = (case + j) % (width + 1)
        coupling = projector(width, chosen, prime, rng)
        paid = gate(coupling, rng.randrange(1, len(table)), prime)
        images.append(multiply(prefix, coupling, prime))
        prefix = multiply(prefix, free[j + 1], prime)
        budget += chosen
        value = formal_multiply(value, paid, table, prime)
        value = formal_multiply(value, scalar(free[j + 1]), table, prime)
        literal = multiply(literal, regular_matrix(paid, table), prime)
        literal = multiply(literal, regular_matrix(scalar(free[j + 1]), table), prime)
    need(augmentation(value, prime) == prefix, "augmentation baseline")
    ambient = concatenate(images)
    joined = concatenate([ambient] + [a for g, a in value.items() if g])
    need(rank(joined, prime) == rank(ambient, prime), "transported-image containment")
    cost = coefficient_rank(value, prime)
    need(cost <= budget, "coefficient-image rank exceeds paid rank")
    nonidentity = concatenate([a for g, a in value.items() if g])
    need(cost == rowspace_rank(nonidentity, prime), "independent row-space rank")
    need(literal == regular_matrix(value, table), "formal/regular circuit disagreement")
    return {"circuits": 1, "paid_gates": length,
            "regular_entries": len(literal) * len(literal[0]),
            "rectangular_free_maps": sum(len(a) != len(a[0]) for a in free),
            "singular_square_free_maps": sum(len(a) == len(a[0]) and
                                             rank(a, prime) < len(a) for a in free),
            "positive_coefficient_ranks": int(cost > 0)}


def circuit_checks():
    rng = random.Random(53941919)
    counts = {}
    for _, table in group_tables():
        for prime in (2, 3, 5):
            for case in range(24):
                for key, value in one_circuit(table, prime, case, rng).items():
                    counts[key] = counts.get(key, 0) + value
    for key in ("rectangular_free_maps", "singular_square_free_maps",
                "positive_coefficient_ranks"):
        need(counts[key] > 0, "vacuous circuit checks: " + key)
    return counts


def diagonal(labels, order):
    size = len(labels)
    result = {g: zeros(size, size) for g in range(order)}
    for i, label in enumerate(labels):
        result[label][i][i] = 1
    return result


def direct_word(labels, table, prime):
    size = len(labels)
    value = diagonal([0] * size, len(table))
    used = 0
    for i, label in enumerate(labels):
        if label != 0:
            coupling = zeros(size, size)
            coupling[i][i] = 1
            value = formal_multiply(value, gate(coupling, label, prime), table, prime)
            used += 1
    return value, used


def endpoint_checks():
    counts = {"diagonal_fixtures": 0, "regular_basis_columns": 0,
              "repeated_target_fixtures": 0}
    for _, table in group_tables():
        targets = [[0, 0], [0, 1], [1, 1, 1], list(range(1, len(table))),
                   [0, 1, 2, 1, 0], [2, 2, 2]]
        for prime in (2, 3, 5):
            for labels in targets:
                # Two independent dirty roles are retained with identity labels.
                complete = labels + [0, 0]
                value, cost = direct_word(complete, table, prime)
                target = diagonal(complete, len(table))
                need(value == target, "direct all-input diagonal endpoint")
                need(coefficient_rank(target, prime) == cost, "sharp diagonal rank")
                literal = identity(len(complete) * len(table))
                for i, label in enumerate(complete):
                    if label:
                        coupling = zeros(len(complete), len(complete))
                        coupling[i][i] = 1
                        literal = multiply(literal, regular_matrix(
                            gate(coupling, label, prime), table), prime)
                wanted = regular_matrix(target, table)
                need(literal == wanted, "regular endpoint")
                counts["regular_basis_columns"] += len(literal[0])
                counts["diagonal_fixtures"] += 1
                counts["repeated_target_fixtures"] += len(set(labels)) < len(labels)
    return counts


def controls():
    table = group_tables()[2][1]
    p = 2
    target = diagonal([1, 1, 1, 1], len(table))
    need(coefficient_rank(target, p) == 4, "repeated labels lost multiplicity")
    need(sum(any(any(row) for row in a) for g, a in target.items() if g) == 1,
         "distinct-label counting control")
    high_rank = gate(identity(3), 1, p)
    need(coefficient_rank(high_rank, p) > 1, "unit-price/rank-price distinction")
    need(coefficient_rank(diagonal([1, 1], len(table)), p) > 0,
         "free address-map exclusion")
    need(coefficient_rank(scalar(zeros(3, 3)), p) == 0, "free singular map charged")
    rejected = False
    try:
        gate([[0, 1], [0, 0]], 1, p)
    except ValueError:
        rejected = True
    need(rejected, "invalid projector accepted")
    a, b = next((a, b) for a in range(1, 6) for b in range(1, 6)
                if table[a][b] != table[b][a])
    left = formal_multiply(gate([[1]], a, p), gate([[1]], b, p), table, p)
    right = formal_multiply(gate([[1]], b, p), gate([[1]], a, p), table, p)
    need(left != right, "noncommutative order control")
    direct, _ = direct_word([a, b], table, p)
    omitted, _ = direct_word([a, 0], table, p)
    need(direct != omitted, "omitted call control")
    scalar_only = formal_multiply(scalar([[1, 1]]), scalar([[1], [1]]), table, p)
    need(augmentation(scalar_only, p) == [[0]], "characteristic-two cancellation")
    need(coefficient_rank(scalar_only, p) == 0, "scalar cancellation has defect")
    return 8


def main():
    counts = circuit_checks() | endpoint_checks()
    counts["controls"] = controls()
    root = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in names}
    print(json.dumps({"status": "PASS_ALL_GROUP_DIAGONAL_RANK", "counts": counts,
                      "python": platform.python_version(), "source_sha256": hashes},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
