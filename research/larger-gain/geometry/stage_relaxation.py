#!/usr/bin/env python3
"""Fractional stage-count upper bounds with arbitrary auxiliary bank patterns.

SciPy nominates a basis; --verify uses only the standard library and the two
unchanged rational moment engines. This drops all chronology and whole-owner
conflicts, and is not a supplier or physical admission.
"""

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
PROVIDERS = ROOT / "research/larger-gain/providers/words"
ENGINE_ROOT = Path(os.environ.get('GAIN_PR564_SOURCE', ROOT / 'research/complex-allcold')).resolve() / 'engines'
WIDTHS = (4, 5, 8, 9)


def engine(name):
    spec = importlib.util.spec_from_file_location(name, ENGINE_ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def instance(pairs, extra_providers=()):
    stages, replicas, ports = 2 * pairs + 1, 8, 112
    dimension = 16 * pairs + 9
    live = 2 * pairs * replicas * ports
    deficit = replicas * (2 * pairs * ports - stages * 64)
    capacities = {8: 2 * (pairs - 1) * ports * replicas}
    capacities.update({16 * j: 4 * ports * replicas for j in range(1, pairs)})
    rank_limit = math.isqrt((dimension * dimension - 1) // 2)
    columns, descriptors = [], []
    provider_paths = [(name, PROVIDERS / name / "CONSTRUCTION.json")
                      for name in ("zero", "four", "eight")]
    provider_paths.extend((Path(path).parent.name, ROOT / path) for path in extra_providers)
    assert len({name for name, _ in provider_paths}) == len(provider_paths)
    source_hashes, providers = {}, []
    for name, path in provider_paths:
        construction = json.loads(path.read_text())
        source_hashes[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        paid = {int(rank): count for rank, count in construction["profile_after"].items()}
        inventory = {int(rank): count for rank, count in construction["widths_after"].items()}
        assert sum(inventory.values()) == 504
        assert all(0 < rank <= dimension and count >= 0 for rank, count in inventory.items())
        assert all(0 < rank <= rank_limit and count >= 0 for rank, count in paid.items())
        assert sum(rank * count for rank, count in paid.items()) - sum(
            rank * count for rank, count in inventory.items()) == 1856
        providers.append((name, paid, inventory))
    widths = tuple(sorted({rank for _, _, inventory in providers for rank in inventory}))

    def pad(remainder):
        count, tail = divmod(remainder, rank_limit)
        return [rank_limit] * count + ([tail] if tail else [])

    def patterns(capacity, index=0, counts=()):
        if index == len(widths):
            yield counts, capacity
            return
        for count in range(capacity // widths[index] + 1):
            yield from patterns(capacity - count * widths[index], index + 1, counts + (count,))

    for capacity in capacities:
        for counts, remainder in patterns(capacity):
            columns.append([int(capacity == rank) for rank in capacities] + list(counts) + [0])
            descriptors.append(dict(kind="pending", capacity=capacity, widths=list(counts),
                                    pad=pad(remainder)))
    for counts, remainder in patterns(dimension):
        columns.append([0] * len(capacities) + list(counts) + [0])
        descriptors.append(dict(kind="bank", capacity=dimension, widths=list(counts),
                                pad=pad(remainder)))
    for name, paid, inventory in providers:
        columns.append([0] * len(capacities) + [-inventory.get(rank, 0) for rank in widths] + [1])
        descriptors.append(dict(kind="provider", provider=name, paid=paid, inventory=inventory))
    rhs = list(capacities.values()) + [0] * len(widths) + [stages * replicas]
    assert sum(rank * count for rank, count in capacities.items()) + stages * replicas * 1856 == dimension * live - deficit
    metadata = dict(pairs=pairs, dimension=dimension, stages=stages, replicas=replicas, ports=ports,
                    base_live=live, deficit=deficit, calls=stages * replicas,
                    capacities=capacities, max_paid_rank=rank_limit, source_sha256=source_hashes)
    if extra_providers:
        metadata.update(extra_provider_constructions=list(extra_providers), width_alphabet=list(widths))
    return columns, rhs, descriptors, metadata


def exact_costs(descriptors, dimension, rate, implementation):
    ranks = {rank for descriptor in descriptors for rank in
             (descriptor["paid"] if descriptor["kind"] == "provider" else descriptor["pad"])}
    values = {}
    for rank in ranks:
        if hasattr(implementation, "logarithm"):
            lower, upper = implementation.logarithm(Q(dimension, rank))
            exponential = implementation.exponential(rate * lower, rate * upper)[0]
        else:
            lower, _ = implementation.log_bounds(Q(dimension, rank))
            exponential = implementation.exp_bounds(rate * lower)[0]
        values[rank] = rank * (exponential - 1) / rate
    return [sum(count * values[rank] for rank, count in descriptor["paid"].items())
            if descriptor["kind"] == "provider" else sum(values[rank] for rank in descriptor["pad"])
            for descriptor in descriptors]


def solve_exact(matrix, rhs, variables, free=None):
    rows = [list(map(Q, row)) + [Q(value)] for row, value in zip(matrix, rhs)]
    pivots = []
    for column in range(variables):
        pivot = next((j for j in range(len(pivots), len(rows)) if rows[j][column]), None)
        if pivot is None:
            continue
        position = len(pivots)
        rows[position], rows[pivot] = rows[pivot], rows[position]
        factor = rows[position][column]
        rows[position] = [x / factor for x in rows[position]]
        for j in range(len(rows)):
            if j != position and rows[j][column]:
                factor = rows[j][column]
                rows[j] = [x - factor * y for x, y in zip(rows[j], rows[position])]
        pivots.append(column)
    assert all(any(row[:variables]) or row[-1] == 0 for row in rows)
    result = [Q(0)] * variables if free is None else list(map(Q, free))
    for i, column in enumerate(pivots):
        result[column] = rows[i][-1] - sum(rows[i][j] * result[j]
                                         for j in range(variables) if j not in pivots)
    assert all(sum(Q(a) * x for a, x in zip(row, result)) == value for row, value in zip(matrix, rhs))
    return result


def exact_rank(matrix):
    basis = {}
    for row in matrix:
        row = list(map(Q, row))
        for pivot, old in sorted(basis.items()):
            if row[pivot]:
                factor = row[pivot]
                row = [a - factor * b for a, b in zip(row, old)]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is not None:
            factor = row[pivot]
            basis[pivot] = [value / factor for value in row]
    return len(basis)


def verify(receipt):
    columns, rhs, descriptors, metadata = instance(receipt["pairs"], receipt.get("extra_provider_constructions", ()))
    for key, value in metadata.items():
        if key == "capacities":
            assert {int(rank): count for rank, count in receipt[key].items()} == value
        else:
            assert receipt[key] == value
    assert len(columns) == receipt["columns"]
    rate = Q(receipt["rejected_rate"])
    assert Q(receipt["kappa_upper_bound"]) == rate / (1 + rate)
    dual = list(map(Q, receipt["dual"]))
    assert len(dual) == len(rhs)
    for name in ("moment", "base_two_moment"):
        costs = exact_costs(descriptors, metadata["dimension"], rate, engine(name))
        assert all(sum(a * b for a, b in zip(column, dual)) <= cost
                   for column, cost in zip(columns, costs))
    value = sum(a * b for a, b in zip(rhs, dual))
    assert rate * value > metadata["deficit"]
    assert str(rate * value - metadata["deficit"]) == receipt["strict_rejection_margin"]
    # Independently reconstruct the exact relaxed primal and its bank stock.
    active = [(int(row["column"]), Q(row["multiplicity"])) for row in receipt["exact_primal"]]
    assert all(count >= 0 for _, count in active)
    assert all(sum(columns[index][i] * count for index, count in active) == target
               for i, target in enumerate(rhs))
    histogram = Counter()
    banks = Q(0)
    for index, count in active:
        descriptor = descriptors[index]
        if descriptor["kind"] == "provider":
            histogram.update({rank: n * count for rank, n in descriptor["paid"].items()})
        else:
            histogram.update({rank: n * count for rank, n in Counter(descriptor["pad"]).items()})
            if descriptor["kind"] == "bank":
                banks += count
    assert {str(rank): str(count) for rank, count in sorted(histogram.items())} == receipt["relaxed_profile"]
    assert str(banks) == receipt["relaxed_bank_count"]
    live = metadata["base_live"] + banks
    assert Q(receipt["relaxed_live"]) == live
    assert metadata["dimension"] * live - sum(rank * count for rank, count in histogram.items()) == metadata["deficit"]
    denominator = math.lcm(live.denominator, *(count.denominator for count in histogram.values()))
    entries = [(rank, int(count * denominator)) for rank, count in histogram.items()]
    lower = Q(receipt["relaxed_profile_root"]["lower"])
    assert rate == Q(receipt["relaxed_profile_root"]["upper"]) == lower + Q(1, 10**24)
    independent = engine("base_two_moment")
    assert independent.moment(metadata["dimension"], int(live * denominator), entries, lower)[1] < 1
    assert independent.moment(metadata["dimension"], int(live * denominator), entries, rate)[0] > 1
    return dict(status="PASS_EXACT_FRACTIONAL_STAGE_AND_BANK_UPPER_BOUND", columns=len(columns),
                rejected_rate=str(rate), strict_rejection_margin=str(rate * value - metadata["deficit"]))


def nominate(pairs, extra_providers=()):
    import numpy as np
    import scipy
    from scipy.optimize import linprog
    from scipy.sparse import csc_matrix
    columns, rhs, descriptors, metadata = instance(pairs, extra_providers)
    matrix = csc_matrix(np.asarray(columns, dtype=float).T)
    dimension = metadata["dimension"]

    def solve(rate):
        def cost(rank):
            return rank * math.expm1(rate * math.log(dimension / rank)) / rate
        costs = [sum(count * cost(rank) for rank, count in descriptor["paid"].items())
                 if descriptor["kind"] == "provider" else sum(cost(rank) for rank in descriptor["pad"])
                 for descriptor in descriptors]
        result = linprog(costs, A_eq=matrix, b_eq=rhs, bounds=(0, None), method="highs")
        assert result.success, result.message
        return result

    lower, upper = 0.0, 0.003
    for _ in range(45):
        rate = (lower + upper) / 2
        result = solve(rate)
        if rate * result.fun < metadata["deficit"]:
            lower = rate
        else:
            upper = rate
    result = solve(upper)
    active = [i for i, count in enumerate(result.x) if count > 1e-7]
    primal = solve_exact([[columns[index][row] for index in active] for row in range(len(rhs))],
                         rhs, len(active))
    assert all(count >= 0 for count in primal)
    histogram = Counter()
    banks = Q(0)
    mixture = {}
    for index, count in zip(active, primal):
        descriptor = descriptors[index]
        if descriptor["kind"] == "provider":
            histogram.update({rank: n * count for rank, n in descriptor["paid"].items()})
            mixture[descriptor["provider"]] = str(count)
        else:
            histogram.update({rank: n * count for rank, n in Counter(descriptor["pad"]).items()})
            if descriptor["kind"] == "bank":
                banks += count
    live = metadata["base_live"] + banks
    denominator = math.lcm(live.denominator, *(count.denominator for count in histogram.values()))
    integer_profile = {rank: int(count * denominator) for rank, count in histogram.items()}
    root = engine("moment").certify(integer_profile, dimension, int(live * denominator), False)
    rate = Q(root["upper"])
    costs = list(map(min, zip(*(exact_costs(descriptors, dimension, rate, engine(name))
                                for name in ("moment", "base_two_moment")))))
    # A degenerate optimum can have fewer positive primal variables than
    # equality rows. Complete the basis using zero-reduced-cost columns;
    # floating dual coordinates are never used in the final certificate.
    dual_basis = active.copy()
    for index in np.argsort(result.lower.marginals):
        index = int(index)
        if len(dual_basis) == len(rhs):
            break
        if index not in dual_basis and exact_rank([columns[i] for i in dual_basis + [index]]) > len(dual_basis):
            dual_basis.append(index)
    assert len(dual_basis) == len(rhs)
    dual = solve_exact([columns[index] for index in dual_basis], [costs[index] for index in dual_basis], len(rhs))

    def violation(index):
        return sum(a * b for a, b in zip(columns[index], dual)) - costs[index]

    # Optional banks have no fixed capacity coefficient. Lower all width
    # potentials enough to admit every bank column before correcting the
    # fixed-capacity and provider potentials.
    excess = max([Q(0)] + [violation(i) / sum(descriptor["widths"])
                          for i, descriptor in enumerate(descriptors)
                          if descriptor["kind"] == "bank" and sum(descriptor["widths"])])
    for row in range(len(metadata["capacities"]), len(rhs) - 1):
        dual[row] -= excess + Q(1, 10**70)
    for row, capacity in enumerate(metadata["capacities"]):
        excess = max([Q(0)] + [violation(i) for i, descriptor in enumerate(descriptors)
                              if descriptor["kind"] == "pending" and descriptor["capacity"] == capacity])
        dual[row] -= excess + Q(1, 10**70)
    excess = max([Q(0)] + [violation(i) for i, descriptor in enumerate(descriptors)
                          if descriptor["kind"] == "provider"])
    dual[-1] -= excess + Q(1, 10**70)
    value = sum(a * b for a, b in zip(rhs, dual))
    receipt = dict(metadata, status="EXACT_STAGE_CEILING_PENDING_SELF_CHECK", columns=len(columns),
                   rejected_rate=str(rate), kappa_upper_bound=str(rate / (1 + rate)),
                   approximate_relaxed_root=(lower + upper) / 2,
                   approximate_kappa_ceiling=upper / (1 + upper),
                   relaxed_bank_count=str(banks), relaxed_live=str(live), provider_counts=mixture,
                   relaxed_profile={str(rank): str(count) for rank, count in sorted(histogram.items())},
                   relaxed_profile_root=root, dual=list(map(str, dual)),
                   exact_primal=[dict(column=index, multiplicity=str(count)) for index, count in zip(active, primal)],
                   nominated_dual_basis=dual_basis,
                   active_patterns=[dict(descriptor=descriptors[index], multiplicity=str(count))
                                    for index, count in zip(active, primal)],
                   strict_rejection_margin=str(rate * value - metadata["deficit"]),
                   optimizer=dict(name="scipy.optimize.linprog/highs", version=scipy.__version__, role="nomination only"),
                   scope="All source-bound provider costs and helper widths are charged. "
                         "Fractional provider and pattern counts, mixed-width auxiliary banks, "
                         "and all pending owner capacities are allowed. All windows, same-call "
                         "conflicts, spectators and integer restrictions are dropped. Paid pads "
                         "are split optimistically at floor(m/sqrt(2)); all finite invoice, "
                         "phase, controller and outer assembly admission remain separate. "
                         "Native complex model, not a bit-side or complete kappa admission.")
    receipt["verification"] = verify(receipt)
    receipt["status"] = receipt["verification"]["status"]
    return receipt


if __name__ == "__main__":
    assert not sys.flags.optimize, "Assertions required"
    sys.dont_write_bytecode = True
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, choices=(2, 3, 4, 5))
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify", type=Path)
    parser.add_argument("--provider", action="append", default=[], type=Path,
                        help="Additional CONSTRUCTION.json; default zero/four/eight providers remain available")
    arguments = parser.parse_args()
    if arguments.verify:
        result = verify(json.loads(arguments.verify.read_text()))
    else:
        assert arguments.pairs and arguments.out and not arguments.out.exists()
        extra_providers = [str(path.resolve().relative_to(ROOT)) for path in arguments.provider]
        result = nominate(arguments.pairs, extra_providers)
        arguments.out.write_text(json.dumps(result, indent=2) + "\n")
        result = {key: result[key] for key in ("status", "pairs", "approximate_relaxed_root",
                                             "approximate_kappa_ceiling", "relaxed_bank_count", "provider_counts")}
    print(json.dumps(result))
