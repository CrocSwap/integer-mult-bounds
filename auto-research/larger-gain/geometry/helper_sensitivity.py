#!/usr/bin/env python3
"""Hypothetical arithmetic targets for eliminating helpers or adding cold axes.

The removed helper paths are measured in the actual three four-cold words.
No claim is made that their functions can be removed without replacement work.
"""

import copy
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csc_matrix

import stage_relaxation as stages


BASELINE_KAPPA = Q("0.001593134158181640")
DESTINATION = Path(__file__).resolve().parent


def helper_paths():
    words = {}
    hashes = {}
    for name in ("zero", "four", "eight"):
        path = stages.PROVIDERS / name / "FULL-WORD.json.gz"
        raw = path.read_bytes()
        hashes[str(path.relative_to(stages.ROOT))] = hashlib.sha256(raw).hexdigest()
        word = json.loads(gzip.decompress(raw))
        first = 2 * len(word["ports"])
        current = {r: len(word["start_extra"].get(str(r), [])) for r in range(first, first + word["report"]["R"])}
        widths = {r: 9 - rank for r, rank in current.items()}
        paths = {r: [] for r in current}
        for operation in word["A"] + word["B"]:
            for register in [operation[1]] + ([operation[2]] if operation[0] == "add" else []):
                if register not in current:
                    continue
                step = len(operation[-1]) - current[register]
                assert step >= 0
                if step:
                    paths[register].append(step)
                    current[register] += step
        for register in current:
            if current[register] < 9:
                paths[register].append(9 - current[register])
            assert sum(paths[register]) == widths[register]
            paths[register] = tuple(sorted(paths[register]))
        words[name] = paths, widths, word["centers"]
    common = [(register, path) for register, path in words["zero"][0].items()
              if all(widths[register] == 9 and register not in centers and paths[register] == path
                     for paths, widths, centers in words.values())]
    assert len(common) == 280
    return common, hashes


def altered(pairs, mode, count, ordered):
    columns, rhs, descriptors, metadata = stages.instance(pairs)
    for i, descriptor in enumerate(descriptors):
        if descriptor["kind"] != "provider":
            continue
        if mode == "remove_expensive_helpers":
            removed = Counter(rank for _, path in ordered[:count] for rank in path)
            for rank, multiplicity in removed.items():
                descriptor["paid"][rank] -= multiplicity
            descriptor["inventory"][9] -= count
        elif mode == "repeat_cold_relation":
            for rank, multiplicity in {1: count, 2: 2 * count, 3: -2 * count}.items():
                descriptor["paid"][rank] += multiplicity
            descriptor["inventory"][9] -= count
            descriptor["inventory"][8] += count
        else:
            raise ValueError(mode)
        assert all(value >= 0 for value in descriptor["paid"].values())
        assert all(value >= 0 for value in descriptor["inventory"].values())
        descriptor["paid"] = {rank: n for rank, n in descriptor["paid"].items() if n}
        assert sum(rank * n for rank, n in descriptor["paid"].items()) - sum(
            rank * n for rank, n in descriptor["inventory"].items()) == 1856
        columns[i] = [0] * len(metadata["capacities"]) + [-descriptor["inventory"].get(rank, 0)
                                                       for rank in stages.WIDTHS] + [1]
    return columns, rhs, descriptors, metadata


def screen(pairs, mode, percent, paths):
    target_kappa = BASELINE_KAPPA * (1 + Q(percent, 100))
    target_rate = target_kappa / (1 - target_kappa)
    dimension = 16 * pairs + 9
    rate = float(target_rate)
    path_cost = lambda path: sum(rank * math.expm1(rate * math.log(dimension / rank)) / rate for rank in path)
    ordered = sorted(paths, key=lambda item: (-path_cost(item[1]), item[0]))

    def solve(count):
        columns, rhs, descriptors, metadata = altered(pairs, mode, count, ordered)
        def cost(rank):
            return rank * math.expm1(rate * math.log(dimension / rank)) / rate
        costs = [sum(n * cost(rank) for rank, n in descriptor["paid"].items())
                 if descriptor["kind"] == "provider" else sum(cost(rank) for rank in descriptor["pad"])
                 for descriptor in descriptors]
        result = linprog(costs, A_eq=csc_matrix(np.asarray(columns, dtype=float).T),
                         b_eq=rhs, bounds=(0, None), method="highs")
        assert result.success, result.message
        return result, columns, rhs, descriptors, metadata

    maximum = 100 if mode == "remove_expensive_helpers" else 220
    solutions = {}
    found = None
    for count in range(maximum + 1):
        result, columns, rhs, descriptors, metadata = solve(count)
        if rate * result.fun < metadata["deficit"]:
            found = count
            break
    if found is None:
        return dict(pairs=pairs, mode=mode, target_gain_percent=percent,
                    target_kappa=str(target_kappa), target_rate=str(target_rate),
                    screened_through=maximum, reached=False)

    thresholds = []
    for count in (found - 1, found):
        result, columns, rhs, descriptors, metadata = solve(count)
        active = [i for i, n in enumerate(result.x) if n > 1e-7]
        primal = stages.solve_exact([[columns[i][row] for i in active] for row in range(len(rhs))], rhs, len(active))
        assert all(n >= 0 for n in primal)
        histogram = Counter()
        banks = Q(0)
        for i, n in zip(active, primal):
            descriptor = descriptors[i]
            if descriptor["kind"] == "provider":
                histogram.update({rank: multiplicity * n for rank, multiplicity in descriptor["paid"].items()})
            else:
                histogram.update({rank: multiplicity * n for rank, multiplicity in Counter(descriptor["pad"]).items()})
                if descriptor["kind"] == "bank":
                    banks += n
        live = metadata["base_live"] + banks
        denominator = math.lcm(live.denominator, *(n.denominator for n in histogram.values()))
        entries = [(rank, int(n * denominator)) for rank, n in histogram.items()]
        assert dimension * live - sum(rank * n for rank, n in histogram.items()) == metadata["deficit"]
        if count == found:
            signs = []
            for name in ("moment", "base_two_moment"):
                implementation = stages.engine(name)
                if name == "moment":
                    lower, upper = implementation.moment(dict(entries), dimension, int(live * denominator), target_rate)
                else:
                    lower, upper = implementation.moment(dimension, int(live * denominator), entries, target_rate)
                assert upper < 1
                signs.append(dict(engine=name, moment_residual_upper=str(upper - 1)))
            thresholds.append(dict(count=count, exact_relaxed_profile_accepts_target=True,
                                   banks=str(banks), live=str(live), signs=signs,
                                   profile={str(rank): str(n) for rank, n in sorted(histogram.items())}))
        else:
            costs = list(map(min, zip(*(stages.exact_costs(descriptors, dimension, target_rate, stages.engine(name))
                                        for name in ("moment", "base_two_moment")))))
            basis = active.copy()
            for i in np.argsort(result.lower.marginals):
                i = int(i)
                if len(basis) == len(rhs):
                    break
                if i not in basis and stages.exact_rank([columns[j] for j in basis + [i]]) > len(basis):
                    basis.append(i)
            dual = stages.solve_exact([columns[i] for i in basis], [costs[i] for i in basis], len(rhs))
            def violation(i):
                return sum(x * y for x, y in zip(columns[i], dual)) - costs[i]
            excess = max([Q(0)] + [violation(i) / sum(descriptor["widths"])
                                  for i, descriptor in enumerate(descriptors)
                                  if descriptor["kind"] == "bank" and sum(descriptor["widths"])])
            for row in range(len(metadata["capacities"]), len(rhs) - 1):
                dual[row] -= excess + Q(1, 10**60)
            for row, capacity in enumerate(metadata["capacities"]):
                excess = max([Q(0)] + [violation(i) for i, descriptor in enumerate(descriptors)
                                      if descriptor["kind"] == "pending" and descriptor["capacity"] == capacity])
                dual[row] -= excess + Q(1, 10**60)
            excess = max([Q(0)] + [violation(i) for i, descriptor in enumerate(descriptors)
                                  if descriptor["kind"] == "provider"])
            dual[-1] -= excess + Q(1, 10**60)
            assert all(sum(x * y for x, y in zip(column, dual)) <= cost for column, cost in zip(columns, costs))
            margin = target_rate * sum(x * y for x, y in zip(rhs, dual)) - metadata["deficit"]
            assert margin > 0
            thresholds.append(dict(count=count, exact_dual_rejects_target=True,
                                   strict_rejection_margin=str(margin), dual=list(map(str, dual))))
    return dict(pairs=pairs, dimension=dimension, mode=mode, target_gain_percent=percent,
                target_kappa=str(target_kappa), target_rate=str(target_rate), reached=True,
                first_count=found, residual_axes_released_per_call=found * (9 if mode == "remove_expensive_helpers" else 1),
                remaining_helpers=504 - found if mode == "remove_expensive_helpers" else 504,
                removed_helper_registers=[r for r, _ in ordered[:found]] if mode == "remove_expensive_helpers" else [],
                removed_paid_profile=dict(Counter(rank for _, path in ordered[:found] for rank in path))
                    if mode == "remove_expensive_helpers" else {},
                threshold_checks=thresholds)


def main():
    paths, hashes = helper_paths()
    rows = []
    for pairs in (3, 4):
        for mode in ("remove_expensive_helpers", "repeat_cold_relation"):
            for percent in (1, 5):
                row = screen(pairs, mode, percent, paths)
                rows.append(row)
                print(json.dumps({key: row[key] for key in ("pairs", "mode", "target_gain_percent", "reached")}
                                 | {key: row[key] for key in ("first_count", "remaining_helpers") if key in row}), flush=True)
    receipt = dict(status="HYPOTHETICAL_LOCAL_WORD_SENSITIVITY_WITH_EXACT_ARITHMETIC_THRESHOLDS",
                   baseline_kappa=str(BASELINE_KAPPA), source_word_sha256=hashes,
                   common_cold_noncenter_helpers=len(paths),
                   path_census={str(path): count for path, count in Counter(path for _, path in paths).items()},
                   scenarios=rows,
                   scope="Helper deletion subtracts the actual paid frame path of selected cold noncenter "
                         "helpers from every provider and removes their width9 demand. Selection uses most "
                         "expensive common measured paths first. Repeated cold relations use the already "
                         "observed delta H1+2H2-2H3 and width9 to width8, without claiming additional "
                         "relations exist. Both preserve local paid-minus-residual mass1856 and fixed "
                         "global deficit. These are arithmetic design targets in an optimistic fractional "
                         "bank/packing model, not removable-helper proofs, actual words, or supplier/outer "
                         "admissions. Replacement computation may erase all predicted benefit.")
    (DESTINATION / "HELPER-SENSITIVITY.json").write_text(json.dumps(receipt, indent=2) + "\n")


if __name__ == "__main__":
    main()
