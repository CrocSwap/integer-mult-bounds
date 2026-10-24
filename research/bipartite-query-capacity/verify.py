#!/usr/bin/env python3
"""Exact finite corroboration for the bipartite block-fitting theorem.

Nick Petalas. Apache-2.0.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(left, right, edges, widths):
    require(type(left) is int and type(right) is int, "integer partition sizes")
    require(0 <= left <= 7 and 0 <= right <= 7, "partition capacity")
    require(len(widths) == left + right, "width count")
    require(
        all(type(d) is int and d >= 0 and d.bit_length() <= 4096 for d in widths),
        "nonnegative bounded integer widths",
    )
    require(len(edges) <= left * right, "edge capacity")
    require(len(set(edges)) == len(edges), "duplicate edge")
    require(
        all(
            type(i) is int
            and type(j) is int
            and 0 <= i < left
            and left <= j < left + right
            for i, j in edges
        ),
        "bipartite edge",
    )


def reachable(capacity, source):
    size = len(capacity)
    parent = [-1] * size
    parent[source] = source
    queue = [source]
    for head in range(size):
        if head == len(queue):
            break
        i = queue[head]
        for j in range(size):
            if capacity[i][j] > 0 and parent[j] == -1:
                parent[j] = i
                queue.append(j)
    return parent


def construct(left, right, edges, widths):
    validate(left, right, edges, widths)
    size = left + right + 2
    source, sink = size - 2, size - 1
    total = sum(widths)
    capacity = [[0] * size for _ in range(size)]
    for i in range(left):
        capacity[source][i] = widths[i]
    for j in range(left, left + right):
        capacity[j][sink] = widths[j]
    for i, j in edges:
        capacity[i][j] = total + 1
    flow = 0
    # Edmonds-Karp has at most V*E augmentations; E <= V**2.
    for _ in range(size**3 + 1):
        parent = reachable(capacity, source)
        if parent[sink] == -1:
            break
        path = []
        vertex = sink
        for _ in range(size):
            if vertex == source:
                break
            previous = parent[vertex]
            path.append((previous, vertex))
            vertex = previous
        require(vertex == source, "bounded augmenting path")
        amount = min(capacity[i][j] for i, j in path)
        require(amount > 0, "positive augmentation")
        for i, j in path:
            capacity[i][j] -= amount
            capacity[j][i] += amount
        flow += amount
    else:
        raise ValueError("augmentation bound exhausted")
    counts = tuple(capacity[j][i] for i, j in edges)
    private = list(widths)
    for (i, j), count in zip(edges, counts, strict=True):
        private[i] -= count
        private[j] -= count
    cover = tuple(i for i in range(left) if parent[i] == -1) + tuple(
        j for j in range(left, left + right) if parent[j] != -1
    )
    require(all(d >= 0 for d in private), "endpoint capacities")
    require(sum(counts) == flow == sum(widths[i] for i in cover), "flow cut equality")
    require(all(i in cover or j in cover for i, j in edges), "vertex cover")
    return counts, tuple(private), cover, total - flow


def independent_optimum(edges, widths):
    best = 0
    for mask in range(1 << len(widths)):
        if all(not (mask >> i & 1 and mask >> j & 1) for i, j in edges):
            best = max(best, sum(d for i, d in enumerate(widths) if mask >> i & 1))
    return best


def matrix_from_recipe(edges, widths, counts, private):
    total = sum(widths)
    require(total <= 16, "dense matrix capacity")
    offsets = [sum(widths[:i]) for i in range(len(widths))]
    used = [0] * len(widths)
    matrix = [[0] * total for _ in range(total)]
    for (i, j), count in zip(edges, counts, strict=True):
        for _ in range(count):
            a, b = offsets[i] + used[i], offsets[j] + used[j]
            for row in (a, b):
                for column in (a, b):
                    matrix[row][column] = 1
            used[i] += 1
            used[j] += 1
    for i, count in enumerate(private):
        for _ in range(count):
            a = offsets[i] + used[i]
            matrix[a][a] = 1
            used[i] += 1
    require(tuple(used) == tuple(widths), "all coordinates allocated once")
    return matrix


def rank_mod(matrix, prime):
    rows = [[value % prime for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows)):
        pivot = next((i for i in range(rank, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, prime)
        rows[rank] = [x * inverse % prime for x in rows[rank]]
        for i in range(rank + 1, len(rows)):
            factor = rows[i][column]
            rows[i] = [
                (a - factor * b) % prime
                for a, b in zip(rows[i], rows[rank], strict=True)
            ]
        rank += 1
    return rank


def check_fit(matrix, edges, widths):
    owners = [i for i, count in enumerate(widths) for _ in range(count)]
    allowed = set(edges) | {(j, i) for i, j in edges}
    for a, i in enumerate(owners):
        for b, j in enumerate(owners):
            if i == j:
                require(matrix[a][b] == int(a == b), "identity diagonal block")
            elif (i, j) not in allowed:
                require(matrix[a][b] == 0, "forbidden ordered block")


def weighted_cases():
    count = 0
    digest = hashlib.sha256()
    possibilities = tuple(itertools.product(range(2), range(2, 5)))
    for mask in range(64):
        edges = tuple(edge for bit, edge in enumerate(possibilities) if mask >> bit & 1)
        for widths in itertools.product(range(3), repeat=5):
            counts, private, cover, optimum = construct(2, 3, edges, widths)
            require(
                optimum == independent_optimum(edges, widths), "independent-set oracle"
            )
            matrix = matrix_from_recipe(edges, widths, counts, private)
            check_fit(matrix, edges, widths)
            for prime in (2, 3, 101):
                require(rank_mod(matrix, prime) == optimum, "actual constructed rank")
            digest.update(
                json.dumps(
                    [mask, widths, counts, private, cover, optimum],
                    separators=(",", ":"),
                ).encode()
            )
            count += 1
    return count, digest.hexdigest()


def exhaustive_binary():
    count = 0
    possibilities = tuple(itertools.product(range(2), range(2, 4)))
    for mask in range(16):
        edges = tuple(edge for bit, edge in enumerate(possibilities) if mask >> bit & 1)
        for widths in itertools.product(range(2), repeat=4):
            total = sum(widths)
            owners = [i for i, width in enumerate(widths) if width]
            allowed = set(edges) | {(j, i) for i, j in edges}
            slots = [
                (a, b)
                for a, i in enumerate(owners)
                for b, j in enumerate(owners)
                if (i, j) in allowed
            ]
            best = total
            for values in itertools.product(range(2), repeat=len(slots)):
                matrix = [[int(a == b) for b in range(total)] for a in range(total)]
                for (a, b), value in zip(slots, values, strict=True):
                    matrix[a][b] = value
                best = min(best, rank_mod(matrix, 2))
                count += 1
            require(
                best == independent_optimum(edges, widths), "all directed binary fits"
            )
    return count


def controls():
    invalid = [
        (-1, 1, (), ()),
        (1, 1, (), (1,)),
        (1, 1, (), (True, 1)),
        (1, 1, (), (-1, 1)),
        (1, 1, ((0, 0),), (1, 1)),
        (1, 1, ((0, 1), (0, 1)), (1, 1)),
        (8, 0, (), (0,) * 8),
        (1, 0, (), (1 << 4096,)),
    ]
    for args in invalid:
        try:
            construct(*args)
        except ValueError:
            continue
        raise ValueError("invalid input admitted")
    edges, widths = ((0, 1), (0, 2), (0, 3)), (4, 1, 1, 1)
    recipe = construct(1, 3, edges, widths)
    require(recipe[-1] == 4 and sum(recipe[0]) == 3, "unequal star fixture")
    huge = (1 << 4095) + 17
    require(
        construct(1, 1, ((0, 1),), (huge, huge))[-1] == huge, "compressed large widths"
    )
    path_edges = ((0, 2), (1, 2), (1, 3))
    require(
        construct(2, 2, path_edges, (4, 1, 1, 4))[-1] == 8,
        "larger side total can be too small",
    )
    for mutant in ([[0, 1], [1, 1]], [[1, 1], [0, 1]]):
        try:
            check_fit(mutant, (), (1, 1))
        except ValueError:
            continue
        raise ValueError("invalid fitting matrix admitted")
    return len(invalid) + 5


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="create an external new receipt")
    args = parser.parse_args()
    weighted, stream = weighted_cases()
    binary = exhaustive_binary()
    control_count = controls()
    here = Path(__file__).resolve().parent
    names = (
        "README.md",
        "PROOF.md",
        "TASK.json",
        "SOURCES.json",
        "VERIFY.json",
        "verify.py",
    )
    receipt = {
        "weighted_cases": weighted,
        "constructed_field_ranks": weighted * 3,
        "directed_binary_matrices": binary,
        "controls": control_count,
        "recipe_sha256": stream,
        "source_sha256": {
            name: hashlib.sha256((here / name).read_bytes()).hexdigest()
            for name in names
        },
    }
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        require(
            not args.receipt.resolve().is_relative_to(here.parents[1]),
            "receipt destination outside the checkout",
        )
        with args.receipt.open("x", encoding="utf-8") as destination:
            require(
                destination.write(encoded) == len(encoded), "complete receipt write"
            )
    print(encoded, end="")
    print("PASS_BIPARTITE_QUERY_CAPACITY")


if __name__ == "__main__":
    main()
