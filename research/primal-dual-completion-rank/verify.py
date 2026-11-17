#!/usr/bin/env python3
"""Corroborate the paired-support formulas by complete small binary censuses."""

from functools import reduce
from hashlib import sha256
from itertools import combinations, product
import json
from operator import xor
from pathlib import Path
import platform


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    points = {0}
    for vector in vectors:
        points |= {point ^ vector for point in points}
    return frozenset(points)


def subspaces(dimension):
    nonzero = range(1, 1 << dimension)
    return sorted({
        tuple(sorted(span(vectors)))
        for size in range(dimension + 1)
        for vectors in combinations(nonzero, size)
    })


def quotient_table(covectors, order):
    basis = []
    for row in covectors:
        if row not in span(basis):
            basis.append(row)
    return tuple(
        sum(((v & row).bit_count() % 2) << i for i, row in enumerate(basis))
        for v in range(order)
    )


def dimension(points):
    count = len(points)
    require(count > 0 and count & (count - 1) == 0,
            f"invalid subspace cardinality: {count}")
    return count.bit_length() - 1


def matrix_actions(size):
    """Enumerate the literal action table of every binary square matrix."""
    order = 1 << size
    actions = []
    for columns in product(range(order), repeat=size):
        table = tuple(
            reduce(xor, (c for i, c in enumerate(columns) if x & (1 << i)), 0)
            for x in range(order)
        )
        invertible = len(set(table)) == order
        rank = dimension({x ^ value for x, value in enumerate(table)})
        actions.append((table, invertible, rank))
    return actions


def completion_minima(actions, source, pi):
    """Group enumerated matrices by the exact equations each one satisfies."""
    ordinary = {}
    invertible = {}
    quotient_size = len(set(pi))
    for table, unit, rank in actions:
        target = tuple(table[x] for x in source)
        if len(set(target)) != len(source):
            continue
        g = tuple(pi[image] for image in table)
        if len(set(g)) != quotient_size:
            continue
        contract = (target, g)
        ordinary[contract] = min(rank, ordinary.get(contract, rank))
        if unit:
            invertible[contract] = min(rank, invertible.get(contract, rank))
    require(ordinary.keys() == invertible.keys(),
            "some compatible contract has no invertible completion")
    return ordinary, invertible


def predicted_minima(source, target, pi, g):
    ambient = dimension(range(len(pi)))
    fixed = {x for x, y in zip(source, target, strict=True) if x == y}
    equalizer = {x for x in range(len(pi)) if g[x] == pi[x]}
    base = ambient - dimension(equalizer) - dimension(fixed)
    source_inside = dimension(equalizer.intersection(source))
    target_inside = dimension(equalizer.intersection(target))
    return base + source_inside, base + max(source_inside, target_inside)


def check_minima(source, target, pi, g, observed):
    expected = predicted_minima(source, target, pi, g)
    require(observed == expected,
            f"incorrect minima for {source}, {target}, {pi}, {g}: "
            f"enumerated {observed}, formula {expected}")


def census(size):
    actions = matrix_actions(size)
    spaces = subspaces(size)
    quotients = [quotient_table(space, 1 << size) for space in spaces]
    gap_counts = [0] * (size + 1)
    for source, pi in product(spaces, quotients):
        ordinary, invertible = completion_minima(actions, source, pi)
        for (target, g), free_rank in ordinary.items():
            unit_rank = invertible[target, g]
            check_minima(source, target, pi, g, (free_rank, unit_rank))
            gap_counts[unit_rank - free_rank] += 1
    return {
        "dimension": size,
        "matrices": len(actions),
        "invertible_matrices": sum(unit for _, unit, _ in actions),
        "primal_subspaces": len(spaces),
        "dual_subspaces": len(quotients),
        "contracts": sum(gap_counts),
        "counts_by_rank_increase": gap_counts,
    }


def check_gap_fixture():
    source, target = (0, 1), (0, 2)
    pi, g = (0, 0, 1, 1), (0, 1, 1, 0)
    ordinary, invertible = completion_minima(matrix_actions(2), source, pi)
    observed = ordinary[target, g], invertible[target, g]
    require(observed == (1, 2), f"unexpected two-dimensional fixture: {observed}")
    check_minima(source, target, pi, g, observed)
    try:
        check_minima(source, target, pi, g, (1, 1))
    except ValueError as error:
        require("enumerated (1, 1), formula (1, 2)" in str(error),
                "wrong reason for rejecting a missing invertibility charge")
    else:
        raise ValueError("accepted a missing invertibility charge")
    return {"relaxed": observed[0], "invertible": observed[1]}


def package_hashes():
    directory = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (directory / name).open("rb") as stream:
            raw = stream.read(65_537)
        require(0 < len(raw) <= 65_536, f"unexpected package file size: {name}")
        hashes[name] = sha256(raw).hexdigest()
    return hashes


def main():
    fixture = check_gap_fixture()
    reports = [census(size) for size in range(1, 4)]
    print(json.dumps({
        "status": "PASS_PRIMAL_DUAL_COMPLETION_RANK",
        "python": platform.python_version(),
        "censuses": reports,
        "sharp_fixture": fixture,
        "rejected_missing_invertibility_charge": 1,
        "sha256": package_hashes(),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
