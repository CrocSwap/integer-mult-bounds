#!/usr/bin/env python3
"""Replay the finite #8072 receiver, cut and same-value reroute certificates.

The supplied word is authenticated before use.  All elimination is over a
prime field, apart from the explicit Fraction checks of the 14 null vectors.
The optional rebuild check accepts an already installed #8072 runtime.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from pathlib import Path

# Avoid an oversubscribed BLAS pool in shared CI. Values are fixed before NumPy
# is imported. Correctness does not depend on thread count or a random search.
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
import numpy as np

HERE = Path(__file__).resolve().parent
WORD_SHA = "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
GZIP_SHA = "e5c1477c1b33c5cfe112fc0fd503f7dd01d1ccc556d229e76c11b1fbb7d01bb4"
WITNESS_SHA = "739c3acbaca7f69717f506149e13c89b8ca60a61a1019947a74c6f393fbf9751"
LAYOUT_SHA = "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
P = 65521


def check(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prime(p):
    return p >= 2 and all(p % k for k in range(2, math.isqrt(p) + 1))


@cache
def rational(q):
    return Fraction(q)


@cache
def residue(q, p=P):
    x = rational(q)
    check(x.denominator % p != 0, "a coefficient denominator is zero modulo p")
    return x.numerator * pow(x.denominator, -1, p) % p


def read_graph():
    compressed = (HERE / "word.json.gz").read_bytes()
    check(sha(compressed) == GZIP_SHA, "compressed word hash mismatch")
    raw = gzip.decompress(compressed)
    graph = json.loads(raw)
    check(raw == canonical(graph), "word is not the canonical serialized graph")
    check(sha(raw) == WORD_SHA, "canonical graph hash mismatch")
    return graph


def rank_mod(matrix, p=P):
    """Row echelon rank, with every integer intermediate bounded in int64."""
    a = matrix.copy()
    height, width = a.shape
    h = 0
    for column in range(width):
        if h == height:
            break
        possible = np.flatnonzero(a[h:, column])
        if not len(possible):
            continue
        j = h + int(possible[0])
        a[[h, j]] = a[[j, h]]
        pivot = (a[h] * pow(int(a[h, column]), -1, p)) % p
        targets = h + 1 + np.flatnonzero(a[h + 1:, column])
        if len(targets):
            a[targets] = (a[targets] - a[targets, column, None] * pivot) % p
        h += 1
    return h


def insert(space, values, p=P):
    """Insert a row in an insertion-ordered pivot basis; report dependence."""
    row = values.copy()
    for column, previous in space.items():
        coefficient = int(row[column])
        if coefficient:
            row = (row - coefficient * previous) % p
    positions = np.flatnonzero(row)
    if not len(positions):
        return False
    column = int(positions[0])
    space[column] = (row * pow(int(row[column]), -1, p)) % p
    return True


def chart_span(frame):
    values = {0}
    for element in frame:
        check(isinstance(element, int) and 0 <= element < 512, "invalid F2 frame")
        values |= {x ^ element for x in values}
    check(len(values) == 1 << len(frame), "a chart frame is dependent")
    return sum(1 << x for x in values)


def nested(a, b):
    return (a & b) == a or (a & b) == b


def evaluate(graph, p=P):
    """Evaluate all word rows and keep the full independent stock per chart."""
    check(prime(p), "the modulus is not prime")
    n = len(graph["initial"])
    check(len(graph["final"]) == n, "unequal input and output roles")
    frames = graph["frames"]
    dims = [len(f) for f in frames]
    spans = [chart_span(f) for f in frames]
    forms = graph["forms"]
    rows = dict(forms)
    check(len(rows) == len(forms), "repeated row node")
    triples = graph["moves"]
    moves = {k: (a, b) for k, a, b in triples}
    check(len(moves) == len(triples), "repeated transfer node")
    schedule = graph["schedule"]
    check(len(schedule) == len(rows) and set(schedule) == set(rows), "schedule differs from rows")
    output_nodes = {graph["first_output"] + i for i in range(n)}
    check(set(rows) == set(moves) | output_nodes and not (set(moves) & output_nodes),
          "rows must be transfers or final outputs")
    for chart in graph["initial"] + graph["final"]:
        check(isinstance(chart, int) and 0 <= chart < len(frames), "invalid endpoint chart")
    for source, target in moves.values():
        check(0 <= source < len(frames) and 0 <= target < len(frames), "invalid transfer chart")
        check(nested(spans[source], spans[target]) and dims[source] != dims[target],
              "a baseline transfer is not a proper nested chart pair")
    locations = {~i: c for i, c in enumerate(graph["initial"])}
    locations.update({node: dest for node, (_, dest) in moves.items()})
    locations.update({graph["first_output"] + i: c for i, c in enumerate(graph["final"])})
    check(len(locations) == n + len(rows), "a node name has more than one owner")
    order = {node: i for i, node in enumerate(schedule)}
    max_terms = max((len(row) for row in rows.values()), default=0)
    max_inner = max(n, max_terms) * (p - 1) ** 2
    check(max_inner + p < 2**63, "int64 accumulation bound is not safe")
    check(n * (p - 1) ** 2 < 2**53, "float64 screening bound is not exact")
    basis = defaultdict(dict)
    owners = defaultdict(list)
    vectors = {}
    ancestors = {}
    eye = np.eye(n, dtype=np.int64)
    for i, chart in enumerate(graph["initial"]):
        node = ~i
        vectors[node] = eye[i].copy()
        ancestors[node] = 0
        check(insert(basis[chart], vectors[node], p), "dependent local initial inputs")
        owners[chart].append(node)
    received = Counter()
    for node in schedule:
        source = moves[node][0] if node in moves else locations[node]
        row = rows[node]
        check(len({j for j, _ in row}) == len(row), "duplicate row coordinate")
        values = np.zeros(n, dtype=np.int64)
        dependencies = 0
        for parent, coefficient in row:
            check(parent in vectors, "row violates the saved topological order")
            check(locations[parent] == source, "a row reads a value outside its chart")
            check(rational(coefficient) != 0, "a zero term would falsify the dependency graph")
            values += residue(coefficient, p) * vectors[parent]
            if parent >= 0:
                dependencies |= ancestors[parent] | (1 << order[parent])
        values %= p
        vectors[node] = values
        ancestors[node] = dependencies
        if node in moves:
            destination = locations[node]
            received[destination] += 1
            check(insert(basis[destination], values, p),
                  f"arrival {node} is dependent at chart {destination}")
            owners[destination].append(node)
    return dict(graph=graph, n=n, p=p, rows=rows, moves=moves, locations=locations,
                basis=basis, owners=owners, received=received, vectors=vectors,
                ancestors=ancestors, order=order, spans=spans, dims=dims,
                max_terms=max_terms, max_inner=max_inner)


def local_ranks(data, witness):
    graph, p = data["graph"], data["p"]
    moves, rows, dims = data["moves"], data["rows"], data["dims"]
    groups = defaultdict(lambda: {"incoming": [], "demand": []})
    for node, (source, target) in moves.items():
        groups[target]["incoming"].append(node)
        groups[source]["demand"].append(node)
    for i, target in enumerate(graph["final"]):
        groups[target]["demand"].append(graph["first_output"] + i)
    check(witness["graph"] == WORD_SHA and witness["layout"] == LAYOUT_SHA,
          "rational witness belongs to another graph or layout")
    witnesses = {entry["chart"]: entry for entry in witness["charts"]}
    check(len(witnesses) == len(witness["charts"]) == 14, "duplicate or missing null vectors")
    deficient = {}
    total_rank = 0
    for chart, group in groups.items():
        incoming, demand = group["incoming"], group["demand"]
        columns = {node: i for i, node in enumerate(incoming)}
        mat = np.zeros((len(demand), len(incoming)), dtype=np.int64)
        for i, node in enumerate(demand):
            for src, coefficient in rows[node]:
                if src in columns:
                    mat[i, columns[src]] = residue(coefficient, p)
                else:
                    check(src < 0 and data["locations"][src] == chart,
                          "local demand has an unexpanded non-arrival dependency")
        rank = rank_mod(mat, p)
        total_rank += rank
        if rank < len(incoming):
            check(chart in witnesses, "missing rational null witness")
            w = witnesses.pop(chart)
            check((w["dimension"], w["incoming"], w["demands"], w["rank_Q"]) ==
                  (dims[chart], len(incoming), len(demand), rank), "null witness metadata differs")
            check(len(incoming) - rank == 1, "deficiency is not exactly one")
            support = {}
            source_groups = defaultdict(list)
            for term in w["support"]:
                node = term["node"]
                check(node in columns and node not in support, "null vector has invalid node")
                value = rational(term["coeff"])
                check(value != 0, "null vector has a zero support entry")
                source, target = moves[node]
                check(target == chart and term["source"] == source and
                      term["grade"] == abs(dims[source] - dims[target]),
                      "null vector source or grade differs")
                support[node] = value
                source_groups[str(source)].append(node)
            check(support and dict(source_groups) == w["source_groups"], "null support groups differ")
            for node in demand:
                exact = sum((rational(coeff) * support.get(src, 0) for src, coeff in rows[node]),
                            Fraction(0))
                check(exact == 0, f"rational null vector fails for chart {chart}")
            deficient[str(chart)] = [len(incoming), len(demand), rank]
    check(not witnesses, "an extraneous deficient-chart witness was supplied")
    return groups, total_rank, deficient


def determinant_mod(matrix, p=P):
    """Determinant of a small square matrix over the prime field."""
    a = matrix.copy()
    size = a.shape[0]
    check(a.shape == (size, size), "minor is not square")
    result = 1
    for column in range(size):
        possible = np.flatnonzero(a[column:, column])
        if not len(possible):
            return 0
        row = column + int(possible[0])
        if row != column:
            a[[column, row]] = a[[row, column]]
            result = -result
        pivot = int(a[column, column])
        result = result * pivot % p
        a[column] = (a[column] * pow(pivot, -1, p)) % p
        for j in range(column + 1, size):
            if a[j, column]:
                a[j] = (a[j] - a[j, column] * a[column]) % p
    return result % p


def sender_obstruction_595(data, groups, witness):
    """Seven arrivals cannot satisfy fixed demands using the two original stocks."""
    graph, rows, moves, p = data["graph"], data["rows"], data["moves"], data["p"]
    incoming = [95059, 95061, 95062, 95067, 96227, 96764, 96765, 97320]
    demands = [53, 97156, 97179, 97183, 97323, 98351, 98485, 100249]
    source520 = [96747, 97279, 97315]
    check(groups[595]["incoming"] == incoming and groups[595]["demand"] == demands,
          "chart 595 arrivals or fixed demands differ")
    check({moves[k][0] for k in incoming} == {3, 520}, "chart 595 sender set differs")
    check(graph["initial"].count(595) == 0, "chart 595 has a local input")
    check(graph["initial"].count(3) == 907 and graph["initial"][0] != 3 and
          not [k for k, (_, b) in moves.items() if b == 3], "chart 3 stock differs")
    check(graph["initial"].count(520) == 0 and
          [k for k, (_, b) in moves.items() if b == 520] == source520, "chart 520 stock differs")
    entry = next(x for x in witness["charts"] if x["chart"] == 595)
    null = {term["node"]: rational(term["coeff"]) for term in entry["support"]}
    check(entry["rank_Q"] == 7 and null.get(97320) == 1, "chart 595 null basis differs")
    coordinate_indices = [574, 0, 164, 262, 443, 127, 276, 32, 3, 274]
    pivot = 97320
    vectors = data["vectors"]
    cols = []
    for node in incoming:
        if node == pivot:
            continue
        scalar = residue(str(null.get(node, Fraction(0))), p)
        cols.append((vectors[node] - scalar * vectors[pivot]) % p)
    cols.extend(vectors[node] for node in source520)
    minor = np.stack([col[coordinate_indices] for col in cols], axis=1)
    determinant = determinant_mod(minor, p)
    check(determinant == 25594, "chart 595 demand/sender minor differs")
    # A separate exact-Q coordinate excludes H from the 907-coordinate stock
    # at chart 3. No modular-rank upper-bound inference is used.
    exact = {~i: Fraction(i == 0) for i in range(data["n"])}
    for node in graph["schedule"]:
        exact[node] = sum((rational(q) * exact[j] for j, q in rows[node] if exact[j]),
                          Fraction(0))
    outside = exact[95061] - null[95061] * exact[pivot]
    check(outside == -2, "chart 595 rational separating coordinate differs")
    return {"receiver": 595, "arrival_nodes": incoming, "outgoing_demand_rows": demands,
            "demand_rank_Q": 7, "existing_senders": [3, 520],
            "source_3_input_count": 907, "source_520_arrivals": source520,
            "minor_input_coordinates": coordinate_indices, "minor_mod_prime": p,
            "minor_mod_determinant": determinant, "outside_input_coordinate": 0,
            "outside_value_Q": str(outside), "source_3_intersection_dim_upper": 6,
            "source_520_intersection_dim": 0, "min_arrivals_existing_sender_stocks": 8}


def depth_cuts(data):
    graph, p = data["graph"], data["p"]
    dims, moves = data["dims"], data["moves"]
    n = data["n"]
    outputs = np.stack([data["vectors"][graph["first_output"] + i] for i in range(n)])
    cuts = []
    for level in range(1, max(dims) + 1):
        item = {"level": level}
        for high, label in ((True, "up"), (False, "down")):
            inside = lambda chart: (dims[chart] >= level) == high
            out = [i for i, c in enumerate(graph["final"]) if inside(c)]
            inp = [i for i, c in enumerate(graph["initial"]) if not inside(c)]
            lower = rank_mod(outputs[np.ix_(out, inp)], p)
            crossing = sum(not inside(a) and inside(b) for a, b in moves.values())
            check(lower <= crossing, "cut rank exceeds the supplied graph's messages")
            item[label] = {"paid": crossing, "output_rank_mod": lower, "slack": crossing - lower}
        cuts.append(item)
    paid = sum(abs(dims[a] - dims[b]) for a, b in moves.values())
    cut_total = sum(row[d]["output_rank_mod"] for row in cuts for d in ("up", "down"))
    check(sum(row[d]["paid"] for row in cuts for d in ("up", "down")) == paid,
          "crossing census does not equal directed grade")
    return cuts, paid, cut_total


def coordinates(data, chart, tasks):
    """Resolve tasks in an independent full stock, with donor coordinates."""
    p, n = data["p"], data["n"]
    local = data["owners"][chart]
    d = len(local)
    pivots = {}

    def reduce(row):
        for col, pivot in pivots.items():
            scalar = int(row[col])
            if scalar:
                row = (row - scalar * pivot) % p
        return row

    for i, node in enumerate(local):
        row = np.zeros(n + d, dtype=np.int64)
        row[:n] = data["vectors"][node]
        row[n + i] = 1
        row = reduce(row)
        indices = np.flatnonzero(row[:n])
        check(len(indices), "full stock lost independence during coordinate solve")
        column = int(indices[0])
        pivots[column] = (row * pow(int(row[column]), -1, p)) % p
    result = []
    for task in tasks:
        node = task[0]
        row = np.zeros(n + d, dtype=np.int64)
        row[:n] = data["vectors"][node]
        row = reduce(row)
        if np.any(row[:n]):
            result.append((task, None, None, None))
            continue
        terms = [(local[i], int(-row[n + i]) % p) for i in np.flatnonzero(row[n:])]
        descendant = [j for j, _ in terms if j >= 0 and
                      ((data["ancestors"][j] >> data["order"][node]) & 1)]
        later = [j for j, _ in terms if j >= 0 and data["order"][j] >= data["order"][node]]
        result.append((task, terms, descendant, later))
    return result


def reroutes(data):
    """Deterministically screen every cheaper nested source with nonempty stock."""
    n, p = data["n"], data["p"]
    keys = sorted(data["moves"])
    charts = sorted(data["basis"])
    # Three exact annihilators per chart. Random seed only chooses certificates:
    # a nonzero pairing is a proof, and every zero survivor is fully resolved.
    random = np.random.default_rng(8072)
    annihilators = {}
    for chart in charts:
        forms = data["basis"][chart]
        z = random.integers(0, p, (3, n), dtype=np.int64)
        for col, row in reversed(list(forms.items())):
            z[:, col] = (z[:, col] - z @ row) % p
        for row in forms.values():
            check(bool(np.all((z @ row) % p == 0)), "invalid full-stock annihilator")
        annihilators[chart] = z
    grouped = defaultdict(list)
    spans, dims = data["spans"], data["dims"]
    for node in keys:
        source, target = data["moves"][node]
        original = abs(dims[source] - dims[target])
        if original <= 1:
            continue
        for chart in charts:
            new = abs(dims[chart] - dims[target])
            if 0 < new < original and nested(spans[chart], spans[target]):
                grouped[chart].append([node, source, target, chart, original, new])
    candidates = sum(map(len, grouped.values()))
    survivors = []
    checked_float = False
    for chart, tasks in grouped.items():
        signals_int = np.stack([data["vectors"][row[0]] for row in tasks])
        z_int = annihilators[chart]
        # All summands are nonnegative integers.  Each product and each partial
        # sum is < 2**53, so the binary64 BLAS dot product is the exact integer.
        dot = signals_int.astype(np.float64) @ z_int.astype(np.float64).T
        if not checked_float and len(tasks):
            exact = sum(int(x) * int(y) for x, y in zip(signals_int[0], z_int[0]))
            check(dot[0, 0] == exact, "float64 dot product failed exactness control")
            checked_float = True
        ints = dot.astype(np.int64)
        ints %= p
        survivors.extend(row for row, ok in zip(tasks, np.all(ints == 0, axis=1)) if ok)
    by_chart = defaultdict(list)
    for task in survivors:
        by_chart[task[3]].append(task)
    excluded, coordinate_witnesses, false_positive, admissible = [], [], 0, []
    for chart, tasks in by_chart.items():
        for task, terms, descendant, later in coordinates(data, chart, tasks):
            if terms is None:
                false_positive += 1
            elif descendant:
                excluded.append([task, descendant[0], len(terms)])
                coordinate_witnesses.append([task, [[node, q] for node, q in terms], descendant[0]])
            else:
                admissible.append(dict(task=task, terms=terms, later=later))
    return dict(nonempty_charts=len(charts), candidates=candidates, survivors=len(survivors),
                exact_span_false_positives=false_positive, descendants=len(excluded),
                admissible=admissible, descendant_witnesses=sorted(excluded),
                descendant_coordinates=sorted(coordinate_witnesses))


def toy_controls():
    # k=10 carries x to chart 1. Chart 3 holds an independent, earlier copy of
    # x, so a cheaper same-value reroute from 3 is permitted. Chart 2 contains
    # x-y/2 and y/2; it can express x only by using node 11, a descendant of k.
    graph = dict(initial=[0, 1], final=[0, 1], first_output=20,
                 frames=[[], [1, 2, 4], [1], [1, 2]],
                 moves=[[13, 0, 3], [10, 0, 1], [11, 1, 2], [12, 1, 2]],
                 forms=[[13, [[-1, "1"]]], [10, [[-1, "1"]]],
                        [11, [[10, "1"], [-2, "-1/2"]]],
                        [12, [[-2, "1/2"]]], [20, [[-1, "1"]]],
                        [21, [[-2, "1"]]]], schedule=[13, 10, 11, 12, 20, 21])
    # The signed rational example is independent of the large graph and uses a
    # different prime. It tests both an available donor and a descendant cycle.
    toy = evaluate(graph, 65519)
    good = coordinates(toy, 3, [[10, 0, 1, 3, 3, 1]])[0]
    bad = coordinates(toy, 2, [[10, 0, 1, 2, 3, 2]])[0]
    check(good[1] == [(13, 1)] and not good[2] and not good[3], "toy legal reroute failed")
    check(bad[1] == [(11, 1), (12, 1)] and bad[2] == [11], "toy descendant was not rejected")
    matrix = np.array([[1, 2], [2, 4]], dtype=np.int64)
    check(rank_mod(matrix, 65519) == 1 and 1 * Fraction(-2) + 2 * Fraction(1) == 0,
          "toy rational null-rank control failed")
    altered = dict(graph, schedule=[10, 13, 11, 12, 20, 21])
    reordered = evaluate(altered, 65519)
    moved = coordinates(reordered, 3, [[10, 0, 1, 3, 3, 1]])[0]
    check(not moved[2] and moved[3] == [13], "toy later acyclic donor was misclassified")


def rebuild(runtime, graph):
    """Optional source comparison; source install is pinned and supplied separately."""
    runtime = runtime.resolve()
    sys.path.insert(0, str(runtime))
    from strong_complex import digest, load_changed
    rebuilt, layout = load_changed(runtime / "inputs")
    check(digest(rebuilt) == WORD_SHA and digest(layout) == LAYOUT_SHA,
          "installed source failed its graph or layout pin")
    check(canonical(rebuilt) == canonical(graph), "compressed word differs from source rebuild")
    print("PASS_PINNED_SOURCE_REBUILD", WORD_SHA, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime", type=Path, help="optional already installed pinned #8072 runtime")
    parser.add_argument("--emit-coordinates", action="store_true", help="print the full modular survivor coordinates")
    args = parser.parse_args()
    check(np.__version__ == "1.26.4", "replay requires numpy==1.26.4")
    toy_controls()
    print("PASS_SIGNED_RATIONAL_TOYS modulus=65519 available=1 descendant=1 reorder=1", flush=True)
    graph = read_graph()
    if args.runtime:
        rebuild(args.runtime, graph)
    raw_witness = (HERE / "null-sources.json").read_bytes()
    check(sha(raw_witness) == WITNESS_SHA, "rational witness hash mismatch")
    witness = json.loads(raw_witness)
    expected = json.loads((HERE / "RESULT.json").read_bytes())
    data = evaluate(graph)
    check((data["n"], len(data["moves"]), len(graph["frames"]), len(data["received"])) ==
          (1291, 5674, 1103, 977), "graph census differs")
    check(sum(data["received"].values()) == 5674, "missing received values")
    print("PASS_FULL_STOCK roles=1291 arrivals=5674 receiving_charts=977", flush=True)
    groups, local_total, deficient = local_ranks(data, witness)
    check(local_total == 5660 and deficient == expected["deficient_local"],
          "local rank summary differs")
    print("PASS_LOCAL_RANK rank=5660 rational_one_dimensional_deficits=14", flush=True)
    source595 = sender_obstruction_595(data, groups, witness)
    check(source595 == expected["chart_595"], "chart 595 sender certificate differs")
    print("PASS_FIXED_SENDERS chart=595 demand_rank=7 min_arrivals=8", flush=True)
    cuts, paid, cut_total = depth_cuts(data)
    check((paid, cut_total) == (9639, 9527) and cuts == expected["cuts"], "cut certificate differs")
    print("PASS_DIRECTED_CUT lower=9527 paid=9639", flush=True)
    result = reroutes(data)
    check((result["nonempty_charts"], result["candidates"], result["survivors"],
           result["exact_span_false_positives"], result["descendants"], result["admissible"]) ==
          (978, 140277, 171, 0, 171, []), "same-value reroute census differs")
    check(result["descendant_witnesses"] == expected["descendant_witnesses"],
          "descendant witness list differs")
    check(result["descendant_coordinates"] == expected["descendant_coordinates"],
          "descendant coordinate proofs differ")
    if args.emit_coordinates:
        print("COORDINATES_JSON=" + json.dumps(result["descendant_coordinates"], separators=(",", ":")), flush=True)
    print("PASS_SAME_VALUE_REROUTES cheaper=140277 survivors=171 descendant_required=171", flush=True)
    print(f"PASS_BOUNDS modulus={P} max_row_terms={data['max_terms']} "
          f"max_int64_accumulation={data['max_inner']} float64_dot_bound={data['n'] * (P-1)**2}", flush=True)
    print("PASS_GAUSSIAN_RECEIVER_RANK", flush=True)


if __name__ == "__main__":
    main()
