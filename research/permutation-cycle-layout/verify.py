"""Bounded exact corroboration of permutation-cycle-layout. Apache-2.0."""

import hashlib
import json
from itertools import permutations, product
from pathlib import Path
import platform
import sys

from routing import (check_layout, check_permutation, cut_profile, cycle_order,
                     make_train, train_entry, wire_frontiers)


def require(condition, message):
    if not condition:
        raise ArithmeticError(message)


def literal_output(permutation, x):
    y = [0] * len(permutation)
    for source, destination in enumerate(permutation):
        y[destination] = x[source]
    return tuple(y)


def pair_code(order, x, y, dimension):
    value = 0
    for site in order:
        value = value * dimension * dimension + y[site] * dimension + x[site]
    return value


def literal_unfolding(permutation, order, cut, dimension):
    """Enumerate all nonzero entries of the full literal permutation matrix."""
    rows = {}
    n = len(permutation)
    require(n <= 6 and dimension ** n <= 81, "literal matrix capacity")
    left, right = order[:cut], order[cut:]
    if len(left) > len(right):
        left, right = right, left
    for x in product(range(dimension), repeat=n):
        y = literal_output(permutation, x)
        row = pair_code(left, x, y, dimension)
        column = pair_code(right, x, y, dimension)
        entries = rows.setdefault(row, {})
        require(column not in entries, "duplicate physical matrix entry")
        entries[column] = 1
    return rows


def literal_gram(rows):
    """Construct H H^T by joining literal columns, without a rank formula."""
    columns = {}
    for row, entries in rows.items():
        for column, value in entries.items():
            columns.setdefault(column, []).append((row, value))
    gram = {row: {} for row in rows}
    for entries in columns.values():
        for row, a in entries:
            for column, b in entries:
                gram[row][column] = gram[row].get(column, 0) + a * b
    return gram


def multiply_sparse(a, b):
    result = {row: {} for row in a}
    for row, entries in a.items():
        for middle, value in entries.items():
            for column, other in b[middle].items():
                result[row][column] = result[row].get(column, 0) + value * other
    return result


def valid_flat_spectrum(gram, eigenvalue, rank):
    square = multiply_sparse(gram, gram)
    expected = {i: {j: eigenvalue * value for j, value in row.items()}
                for i, row in gram.items()}
    trace = sum(row.get(i, 0) for i, row in gram.items())
    return square == expected and trace == eigenvalue * rank


def verify_spectra():
    cases = entries = gram_entries = 0
    for dimension, max_sites in ((2, 6), (3, 4)):
        for n in range(1, max_sites + 1):
            for permutation in permutations(range(n)):
                natural = tuple(range(n))
                orders = tuple(dict.fromkeys((natural, cycle_order(permutation))))
                for order in orders:
                    counts, bonds = cut_profile(permutation, order, dimension)
                    for cut in range(n + 1):
                        h = literal_unfolding(permutation, order, cut, dimension)
                        gram = literal_gram(h)
                        sides = set(order[:cut])
                        crossing = sum((i in sides) != (j in sides)
                                       for i, j in enumerate(permutation))
                        rank = dimension ** crossing
                        eigenvalue = dimension ** (n - crossing)
                        require(crossing == 2 * counts[cut], "unbalanced wires")
                        require(bonds[cut] == rank, "wrong predicted bond")
                        require(valid_flat_spectrum(gram, eigenvalue, rank),
                                "literal spectrum certificate failed")
                        cases += 1
                        entries += sum(len(row) for row in h.values())
                        gram_entries += sum(len(row) for row in gram.values())
    return {"literal_unfoldings": cases, "literal_nonzero_entries": entries,
            "literal_gram_entries": gram_entries}


def subset_optimum(permutation):
    """Dynamic program over every prefix set, independently of cycle layout."""
    n = len(permutation)
    count = 1 << n
    costs = [sum(bool(mask & (1 << i)) and not bool(mask & (1 << j))
                 for i, j in enumerate(permutation)) for mask in range(count)]
    best = [n] * count
    best[0] = 0
    transitions = 0
    for mask in range(1, count):
        predecessor = n
        for site in range(n):
            if mask & (1 << site):
                predecessor = min(predecessor, best[mask ^ (1 << site)])
                transitions += 1
        best[mask] = max(costs[mask], predecessor)
    return best[-1], count, transitions


def verify_all_layouts():
    cases = subsets = transitions = 0
    for n in range(1, 8):
        natural = tuple(range(n))
        for permutation in permutations(range(n)):
            optimum, states, edges = subset_optimum(permutation)
            order = cycle_order(permutation)
            profile, _ = cut_profile(permutation, order, 2)
            frontier = wire_frontiers(permutation, order, 2)
            expected = int(permutation != natural)
            require(optimum == expected == max(profile), "nonoptimal cycle layout")
            require(all(len(f) == 2 * c for f, c in zip(frontier, profile, strict=True)),
                    "frontier does not realize the claimed dimensions")
            cases += 1
            subsets += states
            transitions += edges
    return {"permutations_with_all_order_optimum": cases,
            "prefix_subsets": subsets, "subset_transitions": transitions}


def check_train(permutation, order, dimension, complete):
    train = make_train(permutation, order, dimension)
    n = len(permutation)
    basis = tuple(product(range(dimension), repeat=n))
    count = 0
    for x in basis:
        target = literal_output(permutation, x)
        if complete:
            outputs = basis
        else:
            wrong = ((target[0] + 1) % dimension,) + target[1:]
            outputs = (target, wrong)
        for y in outputs:
            actual = train_entry(train, order, x, y)
            require(actual == int(y == target), "tensor train differs from endpoint")
            count += 1
    return count


def verify_trains():
    cases = entries = 0
    for dimension, max_sites in ((2, 4), (3, 3)):
        for n in range(1, max_sites + 1):
            natural = tuple(range(n))
            for permutation in permutations(range(n)):
                orders = tuple(dict.fromkeys((natural, cycle_order(permutation))))
                for order in orders:
                    entries += check_train(permutation, order, dimension, True)
                    cases += 1
    swap = (3, 4, 5, 0, 1, 2)
    for order in (tuple(range(6)), cycle_order(swap)):
        entries += check_train(swap, order, 2, False)
        cases += 1
    return {"explicit_trains": cases, "contracted_physical_entries": entries}


def expect_rejection(function, *args):
    try:
        function(*args)
    except ValueError:
        return 1
    raise ArithmeticError("invalid input was accepted")


def verify_controls():
    rejected = 0
    for permutation in ((), (0, 0), (1, 2), (False, 1), tuple(range(65))):
        rejected += expect_rejection(check_permutation, permutation)
    for order, d in (((0,), 2), ((0, 0), 2), ((True, 0), 2), ((1, 0), 1),
                     ((1, 0), 17), ((1, 0), True)):
        rejected += expect_rejection(check_layout, (1, 0), order, d)
    rejected += expect_rejection(make_train, tuple(range(7)), tuple(range(7)), 2)
    rejected += expect_rejection(make_train, (3, 4, 5, 0, 1, 2), tuple(range(6)), 3)
    p, natural = (2, 3, 0, 1), (0, 1, 2, 3)
    require(max(cut_profile(p, natural, 2)[1]) == 16, "natural half-swap control")
    require(max(cut_profile(p, cycle_order(p), 2)[1]) == 4, "reorder control")
    gram = literal_gram(literal_unfolding(p, natural, 2, 2))
    require(not valid_flat_spectrum(gram, 1, 4), "one-direction rank accepted")
    require(not valid_flat_spectrum(gram, 2, 16), "wrong singular value accepted")
    p, order, x = (1, 2, 0), (0, 1, 2), (0, 1, 0)
    y = literal_output(p, x)
    train = make_train(p, order, 2)
    broken = [dict(tables) for tables in train]
    table = broken[0][y[0], x[0]]
    broken[0][y[0], x[0]] = tuple(tuple(0 for _ in row) for row in table)
    require(train_entry(broken, order, x, y) != 1, "missing local factor escaped")
    broken[0][y[0], x[0]] = tuple(tuple(-v for v in row) for row in table)
    require(train_entry(broken, order, x, y) == -1, "absolute phase escaped")
    inverse = (2, 0, 1)
    require(train_entry(train, order, x, literal_output(inverse, x)) == 0,
            "inverse routing orientation escaped")
    return {"invalid_input_rejections": rejected, "semantic_controls": 7}


def receipt(counts):
    package = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "routing.py", "verify.py")
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in names}
    return {"status": "PASS_PERMUTATION_CYCLE_LAYOUT", "counts": counts,
            "source_sha256": hashes, "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "platform": platform.platform(), "machine": platform.machine(),
            "optimized": sys.flags.optimize,
            "scope": "Finite exact corroboration; universal theorem is in PROOF.md."}


def main():
    if len(sys.argv) != 1:
        raise ValueError("this finite verifier accepts no arguments")
    counts = {}
    for run in (verify_spectra, verify_all_layouts, verify_trains, verify_controls):
        report = run()
        require(not counts.keys() & report.keys(), "duplicate evidence counter")
        counts.update(report)
    print(json.dumps(receipt(counts), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
