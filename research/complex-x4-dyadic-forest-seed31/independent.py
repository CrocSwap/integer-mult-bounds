#!/usr/bin/env python3
"""Independent integer/Horner census for the finite X4 dyadic forest domain.

Only Python's standard library is required. This file does not import the search
implementation. Costs use explicit old binary-Horner words, while coefficient
pair histograms avoid revisiting every helper for every edge. Fraction is used
only by the separate arbitrary-input endpoint controls, not the cost census.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path
import tarfile


ARCHIVE_SHA256 = "70dfdfcf2ff95352c6020ee9dfca6dca9032b33c10daed3f3dc574c014f4e2cb"
MEMBER = "native/local/CANONICAL-WORD.json.gz"
WORD_SHA256 = "1c0e9da767d4418f70016af599e4a447a3f7777acabe930318459c0fbbd260aa"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def reduced_dyadic(numerator, denominator):
    require(denominator > 0 and denominator & (denominator - 1) == 0,
            "denominator is not a positive power of two")
    if numerator == 0:
        return 0, 1
    while denominator > 1 and numerator % 2 == 0:
        numerator //= 2
        denominator //= 2
    return numerator, denominator


@lru_cache(None)
def horner_word(numerator, denominator):
    """Literal clear/double/add/half/accumulate/clear lowering of one shear."""
    numerator, denominator = reduced_dyadic(numerator, denominator)
    if not numerator:
        return ()
    bits = []
    remaining = abs(numerator)
    while remaining:
        remaining, bit = divmod(remaining, 2)
        bits.append(bit)
    word = [("clear", "W")]
    for index, bit in enumerate(reversed(bits)):
        if index:
            word.append(("double", "W"))
        if bit:
            word.append(("add", "W", "S"))
    while denominator != 1:
        word.append(("half", "W"))
        denominator //= 2
    word.extend([("add" if numerator > 0 else "sub", "T", "W"), ("clear", "W")])
    return tuple(word)


def horner_cost(numerator, denominator):
    return len(horner_word(numerator, denominator))


def coefficients(domain="complete"):
    if domain == "complete":
        result = sorted({reduced_dyadic(tick, 8) for tick in range(-543, 544) if tick})
        require(len(result) == 1086, "complete core is not exactly 1086 coefficients")
        return result
    result = []
    for sign in (-1, 1):
        for odd in range(1, 32, 2):
            for exponent in range(-5, 6):
                numerator, denominator = reduced_dyadic(
                    sign * odd * (2 ** max(exponent, 0)), 2 ** max(-exponent, 0))
                if abs(numerator) == denominator:
                    continue
                result.append((numerator, denominator))
    require(len(result) == len(set(result)) == 350, "coefficient domain is not exactly 350")
    # Canonical order is the pair (reduced signed numerator, denominator).
    return sorted(result)


def read_rows(path):
    require(hashlib.sha256(path.read_bytes()).hexdigest() == ARCHIVE_SHA256,
            "archive SHA-256 mismatch")
    with tarfile.open(path, "r:gz") as archive:
        stream = archive.extractfile(MEMBER)
        require(stream is not None, "canonical word is absent")
        payload = gzip.decompress(stream.read())
    require(hashlib.sha256(payload).hexdigest() == WORD_SHA256,
            "decompressed canonical word SHA-256 mismatch")
    word = json.loads(payload)
    sparse = {}
    for operation in word["compensation"]:
        require(len(operation) == 6, "unexpected compensation operation shape")
        tag, target, source, numerator, denominator, frame = operation
        require(tag == "add" and frame == 0 and numerator != 0,
                "compensation is not a nonzero zero-frame shear")
        require(denominator > 0 and (4 * numerator) % denominator == 0,
                "compensation coefficient is not a quarter integer")
        require(source not in sparse.get(target, {}), "duplicate compensation coefficient")
        sparse.setdefault(target, {})[source] = 4 * numerator // denominator
    targets = sorted(sparse)
    helpers = sorted(set().union(*(set(row) for row in sparse.values())))
    require(len(targets) == 112, "unexpected number of target rows")
    require(not set(targets).intersection(helpers), "targets and helpers alias")
    require(all(word["start"][register] == 0 for register in targets + helpers),
            "forest register does not start in the zero frame")
    require(all(op[-1] == 0 for op in word["precondition"]),
            "precondition does not retain the zero frame")
    dense = [[sparse[target].get(helper, 0) for helper in helpers] for target in targets]
    return targets, helpers, dense


def canonical_line(value):
    return (json.dumps(value, separators=(",", ":"), ensure_ascii=True) + "\n").encode("ascii")


def signed_unit_prim(targets, root_costs, pairs, groups, unit_prices):
    """Independent dense Prim on super-root plus undirected signed unit edges."""
    grouped_prices = [min(2 * horner_cost(1, 1) + sum(prices[index] * count for index, count in histogram)
                         for prices in unit_prices) for _, histogram in groups]
    adjacency = {(child, parent): grouped_prices[group] for child, parent, group in pairs}
    require(all(price == adjacency[parent, child] for (child, parent), price in adjacency.items()),
            "signed unit edge weights are not symmetric")
    remaining = set(range(len(targets)))
    distance = list(root_costs)
    parents = [-1] * len(targets)
    selected = []
    while remaining:
        vertex = min(remaining, key=lambda item: (distance[item], targets[item]))
        remaining.remove(vertex)
        selected.append([targets[vertex], -1 if parents[vertex] == -1 else targets[parents[vertex]], distance[vertex]])
        for other in remaining:
            price = adjacency[other, vertex]
            if price < distance[other]:
                distance[other] = price
                parents[other] = vertex
    return {"cost": sum(edge[2] for edge in selected),
            "roots": sum(edge[1] == -1 for edge in selected), "edges": selected}


def census(targets, rows, domain="complete"):
    root_costs = [sum(horner_cost(a, 4) for a in row) for row in rows]
    pair_histograms = []
    symbols = set()
    for child, child_row in enumerate(rows):
        for parent, parent_row in enumerate(rows):
            if child == parent:
                continue
            histogram = Counter(zip(child_row, parent_row))
            histogram.pop((0, 0), None)
            symbols.update(histogram)
            pair_histograms.append((child, parent, tuple(sorted(histogram.items()))))
    require(len(pair_histograms) == 112 * 111, "ordered pair coverage failure")
    symbol_list = sorted(symbols)
    symbol_indices = {symbol: index for index, symbol in enumerate(symbol_list)}
    groups = []
    group_indices = {}
    packed = []
    for child, parent, histogram in pair_histograms:
        compact = tuple((symbol_indices[pair], count) for pair, count in histogram)
        if compact not in group_indices:
            group_indices[compact] = len(groups)
            groups.append((root_costs[child], compact))
        group = group_indices[compact]
        require(groups[group][0] == root_costs[child], "histogram grouping lost root price")
        packed.append((child, parent, group))
    aggregate = hashlib.sha256()
    records = []
    unit_prices = [[horner_cost(a - sign * b, 4) for a, b in symbol_list] for sign in (-1, 1)]
    dominance_baseline = [min(0, *(2 * horner_cost(1, 1) + sum(prices[index] * count for index, count in histogram) - root_cost
                                  for prices in unit_prices))
                          for root_cost, histogram in groups]
    unit_forest = signed_unit_prim(targets, root_costs, packed, groups, unit_prices)
    for numerator, denominator in coefficients(domain):
        residual_prices = [horner_cost(a * denominator - b * numerator, 4 * denominator)
                           for a, b in symbol_list]
        shear_cost = 2 * horner_cost(numerator, denominator)
        digest = hashlib.sha256()
        minimum = None
        maximum = None
        witness = None
        negatives = 0
        zeroes = 0
        dominance_minimum = None
        dominance_witness = None
        dominance_negative = 0
        dominance_zeroes = 0
        margins = [shear_cost + sum(residual_prices[index] * count for index, count in histogram) - root_cost
                   for root_cost, histogram in groups]
        for child, parent, group in packed:
            margin = margins[group]
            line = f"[{targets[child]},{targets[parent]},{numerator},{denominator},{margin}]\n".encode("ascii")
            digest.update(line)
            aggregate.update(line)
            if minimum is None or margin < minimum:
                minimum = margin
                witness = [targets[child], targets[parent]]
            if maximum is None or margin > maximum:
                maximum = margin
            negatives += margin < 0
            zeroes += margin == 0
            dominance_margin = margin - dominance_baseline[group]
            if dominance_minimum is None or dominance_margin < dominance_minimum:
                dominance_minimum = dominance_margin
                dominance_witness = [targets[child], targets[parent]]
            dominance_negative += dominance_margin < 0
            dominance_zeroes += dominance_margin == 0
        records.append({"numerator": numerator, "denominator": denominator,
                        "min_margin": minimum, "max_margin": maximum, "witness": witness,
                        "negative_edges": negatives, "zero_edges": zeroes,
                        "min_dominance_margin": dominance_minimum,
                        "dominance_witness": dominance_witness,
                        "strict_improvement_dominance": dominance_negative,
                        "dominance_zero_edges": dominance_zeroes,
                        "census_sha256": digest.hexdigest()})
    return {"root_costs": [[target, cost] for target, cost in zip(targets, root_costs)],
            "signed_unit_prim": unit_forest,
            "root_total": sum(root_costs), "ordered_pairs_per_coefficient": len(packed),
            "coefficient_count": len(records), "edge_count": len(packed) * len(records),
            "histogram_symbols": len(symbol_list), "unique_pair_histograms": len(groups),
            "census_sha256": aggregate.hexdigest(), "coefficients": records,
            "minimum_margin": min(record["min_margin"] for record in records),
            "minimum_nonunit_margin": min(record["min_margin"] for record in records
                                          if abs(record["numerator"]) != record["denominator"]),
            "nonunit_negative_edges": sum(record["negative_edges"] for record in records
                                          if abs(record["numerator"]) != record["denominator"]),
            "nonunit_zero_edges": sum(record["zero_edges"] for record in records
                                      if abs(record["numerator"]) != record["denominator"]),
            "minimum_nonunit_dominance_margin": min(record["min_dominance_margin"] for record in records
                                                    if abs(record["numerator"]) != record["denominator"]),
            "nonunit_strict_improvement_dominance": sum(record["strict_improvement_dominance"] for record in records
                                                        if abs(record["numerator"]) != record["denominator"]),
            "nonunit_dominance_zero_edges": sum(record["dominance_zero_edges"] for record in records
                                                if abs(record["numerator"]) != record["denominator"]),
            "negative_edges": sum(record["negative_edges"] for record in records),
            "zero_edges": sum(record["zero_edges"] for record in records)}


def add_scaled(row, source, scale):
    result = dict(row)
    for key, value in source.items():
        result[key] = result.get(key, Fraction(0)) + scale * value
        if result[key] == 0:
            del result[key]
    return result


def replay(operations, registers, backward=False):
    # Identity columns include all target dirt and all independent helper inputs.
    state = {register: {register: Fraction(1)} for register in registers}
    for target, source, coefficient in operations:
        if backward:
            target, source, coefficient = source, target, -coefficient
        require(target != source, "aliased endpoint shear")
        state[target] = add_scaled(state[target], state[source], coefficient)
    return state


def endpoint_control(rows, edges):
    """Check one topologically ordered forest with arbitrary initial target dirt."""
    registers = set(rows).union(*(set(row) for row in rows.values()))
    parents = {child: (parent, coefficient) for child, parent, coefficient in edges}
    order = list(rows)
    for child, parent, _ in edges:
        require(order.index(parent) < order.index(child), "control order is not topological")
    prepare = [(child, parent, -coefficient) for child, parent, coefficient in reversed(edges)]
    inject = []
    for child, row in rows.items():
        residual = dict(row)
        if child in parents:
            parent, coefficient = parents[child]
            residual = add_scaled(residual, rows[parent], -coefficient)
        inject.extend((child, helper, coefficient) for helper, coefficient in sorted(residual.items()))
    restore = list(edges)
    controls = []
    for backward in (False, True):
        expected = {register: {register: Fraction(1)} for register in registers}
        for target, row in rows.items():
            for source, coefficient in row.items():
                if backward:
                    expected[source][target] = -coefficient
                else:
                    expected[target][source] = coefficient
        require(replay(prepare + inject + restore, registers, backward) == expected,
                "arbitrary-input endpoint control failed")
        for label, mutant in (("omit_prepare", inject + restore),
                              ("omit_restore", prepare + inject),
                              ("wrong_prepare_sign", [(t, s, -q) for t, s, q in prepare] + inject + restore)):
            require(replay(mutant, registers, backward) != expected,
                    "negative endpoint control was accepted: " + label)
            controls.append(("backward:" if backward else "forward:") + label)
    return {"arbitrary_input_columns": len(registers), "orientations": ["forward", "backward"],
            "negative_controls_rejected": controls}


def primitive_controls(domain):
    domain_coefficients = sorted(set(coefficients(domain) + [(0, 1), (1, 1), (-1, 1)]))
    for numerator, denominator in domain_coefficients:
        state = {name: {name: Fraction(1)} for name in ("S", "T", "W")}
        for tag, target, *source in horner_word(numerator, denominator):
            if tag == "clear":
                state[target] = {}
            elif tag in ("double", "half"):
                factor = Fraction(2) if tag == "double" else Fraction(1, 2)
                state[target] = {key: factor * value for key, value in state[target].items()}
            else:
                state[target] = add_scaled(state[target], state[source[0]], 1 if tag == "add" else -1)
        if numerator:
            expected = {"S": {"S": Fraction(1)}, "T": {"T": Fraction(1), "S": Fraction(numerator, denominator)}, "W": {}}
        else:
            expected = {name: {name: Fraction(1)} for name in ("S", "T", "W")}
        require(state == expected, "literal Horner primitive endpoint failed")
    return len(domain_coefficients)


def run_controls(targets, helpers, rows, result, domain):
    # A true gain exists in this finite domain on other input matrices.
    parent_row = {0: Fraction(1), 1: Fraction(1), 2: Fraction(1)}
    child_row = {helper: Fraction(3, 2) for helper in parent_row}
    positive_margin = 2 * horner_cost(3, 2) - 3 * horner_cost(3, 2)
    require(positive_margin == -7, "synthetic 3/2 gain control failed")
    positive = endpoint_control({10: parent_row, 11: child_row}, [(11, 10, Fraction(3, 2))])
    positive.update({"coefficient": [3, 2], "margin": positive_margin,
                     "root_child_cost": 21, "edge_child_cost": 14})
    # A depth-two chain catches incorrect prepare/restore traversal order.
    chain = endpoint_control({10: parent_row, 11: child_row,
                              12: {0: Fraction(-15, 8), 1: Fraction(1, 4), 2: Fraction(7, 4)}},
                             [(11, 10, Fraction(3, 2)), (12, 11, Fraction(-5, 4))])
    selected = next(record for record in result["coefficients"]
                    if (record["numerator"], record["denominator"]) == (3, 2))
    child, parent = selected["witness"]
    indexed = dict(zip(targets, rows))
    actual_rows = {target: {helper: Fraction(value, 4) for helper, value in zip(helpers, indexed[target]) if value}
                   for target in (parent, child)}
    actual = endpoint_control(actual_rows, [(child, parent, Fraction(3, 2))])
    actual.update({"coefficient": [3, 2], "witness": [child, parent]})
    return {"literal_primitive_coefficients": primitive_controls(domain),
            "positive_gain_synthetic_pair": positive, "synthetic_depth_two_chain": chain,
            "actual_source_pair": actual}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=Path(__file__).resolve().parents[1] /
                        "community-frontier799-audit/integrated799-replay.tar.gz")
    parser.add_argument("--out", type=Path, help="Write JSON only when explicitly requested; otherwise print it")
    parser.add_argument("--domain", choices=("complete", "odd31"), default="complete",
                        help="complete: all nonzero multiples of 1/8 with abs<68, including units; odd31: original 350 nonunits")
    args = parser.parse_args()
    targets, helpers, rows = read_rows(args.archive)
    result = census(targets, rows, args.domain)
    result.update({"status": "PASS_INDEPENDENT_DYADIC_EDGE_CENSUS", "targets": len(targets),
                   "helpers": len(helpers), "archive_sha256": ARCHIVE_SHA256,
                   "canonical_word_sha256": WORD_SHA256,
                   "method": "Quarter integers; literal Horner words; ordered-pair coefficient histograms",
                   "digest_format": "SHA256 of ASCII JSON [child,parent,numerator,denominator,margin] LF lines; coefficient order (numerator,denominator), then child,parent ascending",
                   "domain": args.domain,
                   "scope": "Finite dyadic single-parent edge census only; no global circuit or kappa claim."})
    result["controls"] = run_controls(targets, helpers, rows, result, args.domain)
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out is None:
        print(rendered, end="")
    else:
        args.out.write_text(rendered, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
