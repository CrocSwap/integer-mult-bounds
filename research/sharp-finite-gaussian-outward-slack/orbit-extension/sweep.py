#!/usr/bin/env python3
"""Exact W(D4)-orbit sweep on only radii 6, 7, 9, and 11 at error one."""

from __future__ import annotations

import itertools
import json
from collections import deque
from functools import cmp_to_key
from math import factorial


H = (
    (1, 1, 1, 1),
    (1, -1, 1, -1),
    (1, 1, -1, -1),
    (1, -1, -1, 1),
)
RADIUS_TARGETS = {
    6: (21, 19),
    7: (43, 39),
    9: (73, 67),
    11: (111, 103),
}


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise RuntimeError(explanation)


def norm_squared(point):
    return sum(value * value for value in point)


def orbit_key(point):
    pattern = tuple(sorted(abs(value) for value in point))
    if 0 in point:
        return pattern, None
    product = 1
    for value in point:
        product *= 1 if value > 0 else -1
    return pattern, product


def orbit_capacity(key):
    pattern, sign_class = key
    multiplicities = {}
    for value in pattern:
        multiplicities[value] = multiplicities.get(value, 0) + 1
    zero_count = multiplicities.pop(0, 0)
    denominator = factorial(zero_count)
    for multiplicity in multiplicities.values():
        denominator *= factorial(multiplicity)
    placements = factorial(4) // denominator
    sign_choices = 1 << (4 - zero_count)
    if zero_count == 0:
        require(sign_class in (-1, 1), "nonzero orbit needs a product-sign class")
        sign_choices //= 2
    else:
        require(sign_class is None, "zero-containing orbit has no sign-product class")
    return placements * sign_choices


def canonical_rep(key):
    pattern, sign_class = key
    if sign_class is None:
        return pattern
    if sign_class == 1:
        return pattern
    return (-pattern[0], pattern[1], pattern[2], pattern[3])


def matrix_multiply(left, right):
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(4))
              for j in range(4))
        for i in range(4)
    )


def matrix_transpose(matrix):
    return tuple(tuple(matrix[i][j] for i in range(4)) for j in range(4))


def is_signed_permutation(matrix):
    return (
        len(matrix) == 4
        and all(len(row) == 4 for row in matrix)
        and all(sum(abs(value) for value in row) == 1 for row in matrix)
        and all(sum(abs(matrix[i][j]) for i in range(4)) == 1
                for j in range(4))
    )


def signed_permutations(even_signs_only=False):
    result = []
    for permutation in itertools.permutations(range(4)):
        for signs in itertools.product((-1, 1), repeat=4):
            if even_signs_only and signs[0] * signs[1] * signs[2] * signs[3] != 1:
                continue
            matrix = [[0] * 4 for _ in range(4)]
            for row, column in enumerate(permutation):
                matrix[row][column] = signs[row]
            result.append(tuple(tuple(row) for row in matrix))
    return result


def graph_group_check():
    w_d4 = set(signed_permutations(even_signs_only=True))
    all_signed = set(signed_permutations(even_signs_only=False))
    ht = matrix_transpose(H)
    pairs = []
    input_projection = set()
    output_projection = set()
    for a in sorted(all_signed):
        numerator = matrix_multiply(matrix_multiply(H, a), ht)
        if not all(value % 4 == 0 for row in numerator for value in row):
            continue
        b = tuple(tuple(value // 4 for value in row) for row in numerator)
        if not is_signed_permutation(b):
            continue
        require(matrix_multiply(b, H) == matrix_multiply(H, a),
                "paired action fails B H=H A")
        pairs.append((a, b))
        input_projection.add(a)
        output_projection.add(b)
    require(len(w_d4) == 192 and len(all_signed) == 384,
            "signed-permutation group cardinality changed")
    require(input_projection == w_d4,
            "complete paired input projection is not exactly W(D4)")
    require(output_projection == w_d4,
            "complete paired output projection is not exactly W(D4)")
    require(len(pairs) == 192,
            "complete paired signed-permutation graph group is not W(D4)")
    return {
        "W4_order": len(all_signed),
        "paired_group_order": len(pairs),
        "input_projection_order": len(w_d4),
        "output_projection_order": len(output_projection),
    }


def input_orbits(radius):
    patterns = {
        tuple(sorted(values))
        for values in itertools.product(range(radius + 1), repeat=4)
        if sum(value * value for value in values) <= radius * radius
    }
    orbits = []
    for pattern in sorted(patterns):
        if 0 in pattern:
            keys = [(pattern, None)]
        else:
            keys = [(pattern, 1), (pattern, -1)]
        for key in keys:
            capacity = orbit_capacity(key)
            rep = canonical_rep(key)
            require(norm_squared(rep) <= radius * radius,
                    "input representative is outside the radius ball")
            orbits.append({
                "key": key,
                "representative": rep,
                "capacity": capacity,
                "norm_squared": norm_squared(rep),
            })
    return orbits


def error_one_candidates(point):
    hx = tuple(sum(H[i][j] * point[j] for j in range(4)) for i in range(4))
    parity = sum(point) & 1
    require(all((value & 1) == parity for value in hx),
            "Hadamard image coordinates do not have common parity")
    if parity == 0:
        center = tuple(value // 2 for value in hx)
        candidates = {center}
        for coordinate in range(4):
            for sign in (-1, 1):
                output = list(center)
                output[coordinate] += sign
                candidates.add(tuple(output))
        require(len(candidates) == 9, "integer image must have nine neighbors")
    else:
        lower = tuple(value // 2 for value in hx)
        candidates = {
            tuple(lower[i] + bits[i] for i in range(4))
            for bits in itertools.product((0, 1), repeat=4)
        }
        require(len(candidates) == 16, "half-integer image must have sixteen neighbors")
    for output in candidates:
        error_num = sum((2 * output[i] - hx[i]) ** 2 for i in range(4))
        require(error_num <= 4, "candidate violates error cap one")
        if parity:
            require(error_num == 4, "half-integer neighbor has nonunit error")
    return sorted(candidates), parity


def sum_sqrt_le(a, b, c, d):
    """Exact decision for sqrt(a)+sqrt(b) <= sqrt(c)+sqrt(d)."""
    require(min(a, b, c, d) >= 0, "negative square-root radicand")
    k = c + d - a - b
    p = a * b
    q = c * d
    if k >= 0:
        if p <= q:
            return True
        if k == 0:
            return False
        e = 4 * (p - q) - k * k
        if e <= 0:
            return True
        return e * e <= 16 * k * k * q
    r = -k
    e = 4 * (q - p) - r * r
    if e < 0:
        return False
    return e * e >= 16 * r * r * p


def compare_gaps(m, n, a, b):
    """Sign of (sqrt(m)-sqrt(n))-(sqrt(a)-sqrt(b))."""
    left_le = sum_sqrt_le(m, b, a, n)
    right_le = sum_sqrt_le(a, n, m, b)
    require(left_le or right_le, "exact gap comparison is inconsistent")
    if left_le and right_le:
        return 0
    return -1 if left_le else 1


def gap_label(pair):
    m, n = pair
    return f"sqrt({m})-sqrt({n})"


def compare_pair(left, right):
    return compare_gaps(left[0], left[1], right[0], right[1])


def prepare_radius(radius):
    inputs = input_orbits(radius)
    input_index = {orbit["key"]: i for i, orbit in enumerate(inputs)}
    output_caps = {}
    pair_degrees = {}
    pair_gaps = {}
    all_gaps = []
    total_error_edges = 0
    total_strict_edges_at_half = 0
    representative_candidate_total = 0
    representative_parity_counts = {"integer": 0, "half_integer": 0}
    representatives = []

    for i, orbit in enumerate(inputs):
        rep = orbit["representative"]
        candidates, parity = error_one_candidates(rep)
        representative_parity_counts["integer" if parity == 0 else "half_integer"] += 1
        representative_candidate_total += len(candidates)
        total_error_edges += orbit["capacity"] * len(candidates)
        degrees = {}
        gaps = {}
        for output in candidates:
            key = orbit_key(output)
            capacity = orbit_capacity(key)
            if key in output_caps:
                require(output_caps[key] == capacity,
                        "output orbit capacity is inconsistent")
            output_caps[key] = capacity
            jgap = (norm_squared(output), orbit["norm_squared"])
            all_gaps.append(jgap)
            pair_key = (i, key)
            if pair_key in gaps:
                require(gaps[pair_key] == jgap,
                        "one output orbit produced incompatible norm gaps")
            degrees[key] = degrees.get(key, 0) + 1
            gaps[pair_key] = jgap
        for output_key, degree in degrees.items():
            # Output orbit indices are assigned after collecting all keys.
            pair_degrees[(i, output_key)] = degree
            pair_gaps[(i, output_key)] = gaps[(i, output_key)]
        representatives.append({
            "input_orbit_index": i,
            "input_key": orbit["key"],
            "representative": rep,
            "orbit_capacity": orbit["capacity"],
            "candidate_count": len(candidates),
            "image_parity": "integer" if parity == 0 else "half_integer",
        })

    output_keys = sorted(output_caps)
    output_index = {key: j for j, key in enumerate(output_keys)}
    output_orbits = [
        {"key": key, "capacity": output_caps[key],
         "norm_squared": sum(value * value for value in key[0])}
        for key in output_keys
    ]
    quotient_edges = []
    pair_degree_indexed = {}
    pair_gap_indexed = {}
    for (i, key), degree in sorted(pair_degrees.items(), key=lambda item: (item[0][0], output_index[item[0][1]])):
        j = output_index[key]
        gap = pair_gaps[(i, key)]
        pair_degree_indexed[(i, j)] = degree
        pair_gap_indexed[(i, j)] = gap
        quotient_edges.append((i, j))
        lhs = inputs[i]["capacity"] * degree
        output_capacity = output_orbits[j]["capacity"]
        require(lhs % output_capacity == 0,
                "paired orbit relation is not biregular")

    total_inputs = sum(orbit["capacity"] for orbit in inputs)
    total_outputs = sum(orbit["capacity"] for orbit in output_orbits)
    require(total_inputs == sum(
        orbit["capacity"] for orbit in inputs
    ), "input orbit capacities fail their sum")
    return {
        "radius": radius,
        "inputs": inputs,
        "input_index": input_index,
        "outputs": output_orbits,
        "output_index": output_index,
        "pair_degree": pair_degree_indexed,
        "pair_gap": pair_gap_indexed,
        "quotient_edges": quotient_edges,
        "all_gaps": all_gaps,
        "total_inputs": total_inputs,
        "total_outputs": total_outputs,
        "error_edge_count": total_error_edges,
        "representative_candidate_total": representative_candidate_total,
        "representative_parity_counts": representative_parity_counts,
        "representatives": representatives,
    }


class Dinic:
    def __init__(self, node_count):
        self.graph = [[] for _ in range(node_count)]

    def add_edge(self, source, target, capacity):
        forward = [target, capacity, len(self.graph[target])]
        reverse = [source, 0, len(self.graph[source])]
        self.graph[source].append(forward)
        self.graph[target].append(reverse)
        return forward

    def max_flow(self, source, sink):
        flow = 0
        count = len(self.graph)
        while True:
            level = [-1] * count
            level[source] = 0
            queue = deque([source])
            while queue:
                node = queue.popleft()
                for target, capacity, _ in self.graph[node]:
                    if capacity > 0 and level[target] < 0:
                        level[target] = level[node] + 1
                        queue.append(target)
            if level[sink] < 0:
                return flow
            next_edge = [0] * count

            def push(node, available):
                if node == sink:
                    return available
                while next_edge[node] < len(self.graph[node]):
                    index = next_edge[node]
                    target, capacity, reverse_index = self.graph[node][index]
                    if capacity > 0 and level[target] == level[node] + 1:
                        sent = push(target, min(available, capacity))
                        if sent:
                            self.graph[node][index][1] -= sent
                            self.graph[target][reverse_index][1] += sent
                            return sent
                    next_edge[node] += 1
                return 0

            while True:
                sent = push(source, 1 << 60)
                if not sent:
                    break
                flow += sent

    def residual_reachable(self, source):
        found = {source}
        queue = deque([source])
        while queue:
            node = queue.popleft()
            for target, capacity, _ in self.graph[node]:
                if capacity > 0 and target not in found:
                    found.add(target)
                    queue.append(target)
        return found

    def maximal_source_side(self, sink):
        reverse_residual = [[] for _ in self.graph]
        for source, edges in enumerate(self.graph):
            for target, capacity, _ in edges:
                if capacity > 0:
                    reverse_residual[target].append(source)
        can_reach_sink = {sink}
        queue = deque([sink])
        while queue:
            node = queue.popleft()
            for previous in reverse_residual[node]:
                if previous not in can_reach_sink:
                    can_reach_sink.add(previous)
                    queue.append(previous)
        return set(range(len(self.graph))) - can_reach_sink


def flow_at(data, threshold, inclusive=True, need_cut=True,
            include_flow_certificate=False):
    input_count = len(data["inputs"])
    output_count = len(data["outputs"])
    source = 0
    input_offset = 1
    output_offset = input_offset + input_count
    sink = output_offset + output_count
    network = Dinic(sink + 1)
    inf = data["total_inputs"] + data["total_outputs"] + 1
    source_edges = []
    for i, orbit in enumerate(data["inputs"]):
        edge = network.add_edge(source, input_offset + i, orbit["capacity"])
        source_edges.append((i, orbit["capacity"], edge))
    active_pairs = []
    pair_edges = []
    for i, j in data["quotient_edges"]:
        gap = data["pair_gap"][(i, j)]
        comparison = compare_pair(gap, threshold)
        if comparison < 0 or (inclusive and comparison == 0):
            active_pairs.append((i, j))
            edge = network.add_edge(input_offset + i, output_offset + j, inf)
            pair_edges.append((i, j, edge))
    sink_edges = []
    for j, orbit in enumerate(data["outputs"]):
        edge = network.add_edge(output_offset + j, sink, orbit["capacity"])
        sink_edges.append((j, orbit["capacity"], edge))

    value = network.max_flow(source, sink)
    feasible = value == data["total_inputs"]
    result = {
        "threshold_pair": list(threshold),
        "threshold": gap_label(threshold),
        "edge_rule": "gap<=threshold" if inclusive else "gap<threshold",
        "flow": value,
        "input_capacity": data["total_inputs"],
        "cut_capacity": value,
        "deficiency": data["total_inputs"] - value,
        "feasible": feasible,
        "active_quotient_adjacencies": len(active_pairs),
    }
    if include_flow_certificate:
        input_supplies = [capacity - edge[1]
                          for _, capacity, edge in source_edges]
        output_loads = [capacity - edge[1]
                        for _, capacity, edge in sink_edges]
        pair_flows = []
        row_sums = [0] * input_count
        column_sums = [0] * output_count
        for i, j, edge in pair_edges:
            amount = inf - edge[1]
            if amount:
                pair_flows.append([i, j, amount])
                row_sums[i] += amount
                column_sums[j] += amount
        require(row_sums == input_supplies,
                "quotient flow violates input-orbit conservation")
        require(column_sums == output_loads,
                "quotient flow violates output-orbit conservation")
        require(sum(input_supplies) == value == sum(output_loads),
                "quotient flow does not conserve total value")
        require(all(load <= data["outputs"][j]["capacity"]
                    for j, load in enumerate(output_loads)),
                "quotient flow exceeds an output-orbit capacity")
        if feasible:
            require(input_supplies == [orbit["capacity"]
                                       for orbit in data["inputs"]],
                    "feasible quotient flow does not saturate every input orbit")
        result["flow_certificate"] = {
            "positive_orbit_pair_flows": pair_flows,
            "input_supplies": input_supplies,
            "output_loads": output_loads,
        }
    if not need_cut:
        return result

    source_side = network.maximal_source_side(sink)
    reachable = network.residual_reachable(source)
    require(sink not in reachable, "augmenting path remains after max flow")
    selected_i = {
        i for i in range(input_count) if input_offset + i in source_side
    }
    selected_o = {
        j for j in range(output_count) if output_offset + j in source_side
    }
    actual_neighbor_o = {
        j for i, j in active_pairs if i in selected_i
    }
    require(actual_neighbor_o == selected_o,
            "maximal min-cut output side is not exactly its neighborhood")
    input_cut = sum(data["inputs"][i]["capacity"]
                    for i in range(input_count) if i not in selected_i)
    output_cut = sum(data["outputs"][j]["capacity"] for j in selected_o)
    require(input_cut + output_cut == value,
            "explicit minimum cut differs from flow value")
    selected_input_capacity = sum(data["inputs"][i]["capacity"] for i in selected_i)
    selected_output_capacity = sum(data["outputs"][j]["capacity"] for j in selected_o)
    require(selected_input_capacity - selected_output_capacity
            == data["total_inputs"] - value,
            "cut lift has inconsistent Hall deficiency")
    result["maximal_hall_cut"] = {
        "input_count": selected_input_capacity,
        "neighbor_count": selected_output_capacity,
        "deficiency": selected_input_capacity - selected_output_capacity,
        "cut_input_side_capacity": input_cut,
        "cut_output_side_capacity": output_cut,
        "input_orbit_count": len(selected_i),
        "output_orbit_count": len(selected_o),
        "input_orbits": [
            {"key": encode_key(data["inputs"][i]["key"]),
             "capacity": data["inputs"][i]["capacity"]}
            for i in sorted(selected_i)
        ],
        "output_orbits": [
            {"key": encode_key(data["outputs"][j]["key"]),
             "capacity": data["outputs"][j]["capacity"]}
            for j in sorted(selected_o)
        ],
    }
    return result


def encode_key(key):
    pattern, sign = key
    return [list(pattern), sign]


def distinct_sorted_gaps(values):
    ordered = sorted(values, key=cmp_to_key(compare_pair))
    result = []
    for value in ordered:
        if not result or compare_pair(result[-1], value) != 0:
            result.append(value)
    return result


def binary_optimum(data, gaps):
    require(bool(gaps), "no error-one edge gap values exist")
    probes = []
    low = -1
    high = len(gaps) - 1
    high_result = flow_at(data, gaps[high], inclusive=True, need_cut=False)
    probes.append({"index": high, **high_result})
    if not high_result["feasible"]:
        return {"exists": False, "probes": probes, "gap_count": len(gaps)}
    while high - low > 1:
        mid = (low + high) // 2
        result = flow_at(data, gaps[mid], inclusive=True, need_cut=False)
        probes.append({"index": mid, **result})
        if result["feasible"]:
            high = mid
        else:
            low = mid
    optimum = gaps[high]
    upper = flow_at(data, optimum, inclusive=True, need_cut=False,
                    include_flow_certificate=True)
    strict_lower = flow_at(data, optimum, inclusive=False, need_cut=True)
    require(upper["feasible"], "binary-search optimum is not feasible")
    require(not strict_lower["feasible"] and strict_lower["deficiency"] > 0,
            "strict predecessor graph lacks a Hall obstruction")
    require(high == 0 or not flow_at(data, gaps[high - 1], inclusive=True,
                                     need_cut=False)["feasible"],
            "previous attainable gap unexpectedly feasible")
    return {
        "exists": True,
        "gap_count": len(gaps),
        "optimum_gap_index": high,
        "optimum_pair": list(optimum),
        "optimum_expression": gap_label(optimum),
        "binary_flow_probes": probes,
        "upper_flow": upper,
        "strict_lower_cut": strict_lower,
    }


def target_threshold_tests(data, target):
    inclusive = flow_at(data, target, inclusive=True, need_cut=True,
                        include_flow_certificate=True)
    strict = flow_at(data, target, inclusive=False, need_cut=True,
                     include_flow_certificate=True)
    return {"inclusive": inclusive, "strict": strict}


def build_radius_record(radius, group_receipt):
    data = prepare_radius(radius)
    strict_edges = 0
    target = RADIUS_TARGETS[radius]
    for (i, j), gap in data["pair_gap"].items():
        if compare_pair(gap, target) < 0:
            strict_edges += data["inputs"][i]["capacity"] * data["pair_degree"][(i, j)]
    gaps = distinct_sorted_gaps(data["all_gaps"])
    target_tests = target_threshold_tests(data, target)
    optimum = binary_optimum(data, gaps)
    return {
        "radius": radius,
        "threshold_family_index": (radius - 1) // 2,
        "threshold_interpretation": (
            "inherited beta_2 from the R5 finite theorem"
            if radius == 6 else "beta_a with a=(R-1)/2"
        ),
        "target_threshold": gap_label(target),
        "target_pair": list(target),
        "domain_and_graph": {
            "input_count": data["total_inputs"],
            "input_orbit_count": len(data["inputs"]),
            "error_one_candidate_output_count": data["total_outputs"],
            "output_candidate_orbit_count": len(data["outputs"]),
            "error_one_edge_count": data["error_edge_count"],
            "strict_target_edge_count": strict_edges,
            "strict_quotient_adjacencies": sum(
                compare_pair(gap, target) < 0 for gap in data["pair_gap"].values()
            ),
            "all_quotient_adjacencies": len(data["quotient_edges"]),
            "representative_count": len(data["inputs"]),
            "representative_error_one_candidate_total": data["representative_candidate_total"],
            "representative_image_parities": data["representative_parity_counts"],
        },
        "target_threshold_tests": target_tests,
        "attainable_gap_count": len(gaps),
        "exact_finite_optimum": optimum,
        "orbit_capacity_tables": {
            "inputs": [
                {"key": encode_key(o["key"]), "representative": list(o["representative"]),
                 "capacity": o["capacity"], "norm_squared": o["norm_squared"]}
                for o in data["inputs"]
            ],
            "candidate_outputs": [
                {"key": encode_key(o["key"]), "capacity": o["capacity"],
                 "norm_squared": o["norm_squared"]}
                for o in data["outputs"]
            ],
        },
    }


def main():
    group = graph_group_check()
    records = [build_radius_record(radius, group) for radius in (6, 7, 9, 11)]
    print(json.dumps({
        "status": "PASS",
        "scope": "only radii 6, 7, 9, 11 at error cap one for H4/2",
        "operator": [list(row) for row in H],
        "group": {
            **group,
            "identified_as": "W(D4): signed permutations with even sign changes",
        },
        "construction_and_feasibility_argument": {
            "input_and_output_universes": "generated by W(D4) sorted-absolute-coordinate/product-sign orbit representatives and exact capacities; no expansion to all points times 192",
            "candidate_neighbors": "9 for integer Ux, 16 for half-integer Ux",
            "orbit_pair_adjacency": "paired action makes the bipartite relation biregular on every adjacent orbit pair",
            "saturated_flow_lift": "uniform flow on each orbit-pair edge set gives a fractional matching; input degree 1 and output degree at most 1, hence an integral injection exists by bipartite matching polytope integrality",
            "lower_bound": "the maximal source side of an exact min cut lifts to a complete union-of-orbits neighborhood with the recorded capacity deficiency",
        },
        "completed_radii": records,
        "untouched_radii": "all other radii, including 8 and 10, were not evaluated",
        "limits": "finite evidence only; no inference about all radii or global maps",
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
