#!/usr/bin/env python3
"""Construct the maximal invariant Hall-deficient set on complete S5.

Inputs are the frozen R5 certificate and exact checker in the sibling
sharp-finite-gaussian-outward-slack package. The only flow is an exact
integer min-cut on signed-permutation orbit capacities; no matching search
or radius expansion is performed.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
from collections import deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
CERT_PATH = PACKAGE / "R5-OPTIMUM.json.gz"
VERIFY_PATH = PACKAGE / "verify.py"
PACKED_CERT_SHA256 = "d26f615aacff4b082c316e491aa1730aabc9cb6ceb377d33fb9a279b2d7f5f16"
RAW_CERT_SHA256 = "b1fe3d866d2184227f46ec73ec2021c546bba056e98077e657e9205d9db5ad8b"
VERIFY_SHA256 = "611124563b42ec1c20d4755d190a850d1deac5ed743d6f98094ec97f7d893190"


def require(condition: bool, explanation: str) -> None:
    if not condition:
        raise RuntimeError(explanation)


def load_pinned_inputs():
    packed = CERT_PATH.read_bytes()
    require(hashlib.sha256(packed).hexdigest() == PACKED_CERT_SHA256,
            "compressed certificate pin mismatch")
    raw = gzip.decompress(packed)
    require(hashlib.sha256(raw).hexdigest() == RAW_CERT_SHA256,
            "expanded certificate pin mismatch")
    source = VERIFY_PATH.read_bytes()
    require(hashlib.sha256(source).hexdigest() == VERIFY_SHA256,
            "frozen exact verifier pin mismatch")
    namespace = {"__name__": "pinned_exact_r5_verifier", "__file__": str(VERIFY_PATH)}
    exec(compile(source, str(VERIFY_PATH), "exec"), namespace)
    return json.loads(raw), namespace


def multiply(left, right):
    return tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(4))
              for j in range(4))
        for i in range(4)
    )


def transpose(matrix):
    return tuple(tuple(matrix[i][j] for i in range(4)) for j in range(4))


def is_signed_permutation(matrix):
    return (
        len(matrix) == 4
        and all(len(row) == 4 for row in matrix)
        and all(sum(abs(value) for value in row) == 1 for row in matrix)
        and all(sum(abs(matrix[i][j]) for i in range(4)) == 1
                for j in range(4))
    )


def matrix_sign_product(matrix):
    result = 1
    for row in matrix:
        result *= next(value for value in row if value)
    return result


def signed_permutations():
    for permutation in itertools.permutations(range(4)):
        for signs in itertools.product((-1, 1), repeat=4):
            matrix = [[0] * 4 for _ in range(4)]
            for i, j in enumerate(permutation):
                matrix[i][j] = signs[i]
            yield tuple(tuple(row) for row in matrix)


def action(matrix, point):
    return tuple(sum(matrix[i][j] * point[j] for j in range(4))
                 for i in range(4))


def neighborhood(points, graph):
    result = set()
    for point in points:
        result.update(graph[point])
    return result


def graph_group(h):
    """All paired signed permutations (A,B) satisfying B H=H A."""
    ht = transpose(h)
    pairs = []
    for a in signed_permutations():
        numerator = multiply(multiply(h, a), ht)
        if any(value % 4 for row in numerator for value in row):
            continue
        b = tuple(tuple(value // 4 for value in row) for row in numerator)
        if is_signed_permutation(b):
            require(multiply(b, h) == multiply(h, a),
                    "derived pair fails B H=H A")
            pairs.append((a, b))
    return pairs


def orbit_partition(points, matrices, norm):
    remaining = set(points)
    orbits = []
    point_to_orbit = {}
    while remaining:
        representative = min(remaining)
        orbit = {action(matrix, representative) for matrix in matrices}
        require(orbit <= points, "signed-permutation orbit leaves candidate universe")
        require(orbit <= remaining,
                "orbit partition produced intersecting blocks")
        index = len(orbits)
        for point in orbit:
            point_to_orbit[point] = index
        orbits.append({
            "representative": representative,
            "points": orbit,
            "capacity": len(orbit),
            "norm_squared": norm(representative),
            "key": list(orbit_key(representative)),
        })
        remaining -= orbit
    return orbits, point_to_orbit


def orbit_key(point):
    absolute = tuple(sorted(abs(value) for value in point))
    if 0 in point:
        sign_parity = None
    else:
        sign_parity = 1
        for value in point:
            sign_parity *= 1 if value > 0 else -1
    return absolute, sign_parity


def orbit_capacity_formula(point):
    from collections import Counter
    from math import factorial

    counts = Counter(abs(value) for value in point)
    zero_count = counts.pop(0, 0)
    permutation_count = factorial(4)
    permutation_count //= factorial(zero_count)
    for multiplicity in counts.values():
        permutation_count //= factorial(multiplicity)
    sign_count = 1 << (4 - zero_count)
    if zero_count == 0:
        sign_count //= 2
    return permutation_count * sign_count


class Dinic:
    """Integer-capacity Dinic flow with explicit residual reverse edges."""

    def __init__(self, node_count):
        self.graph = [[] for _ in range(node_count)]

    def add_edge(self, source, target, capacity):
        forward = [target, capacity, len(self.graph[target])]
        reverse = [source, 0, len(self.graph[source])]
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def max_flow(self, source, sink):
        flow = 0
        n = len(self.graph)
        while True:
            level = [-1] * n
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
            next_edge = [0] * n

            def send(node, amount):
                if node == sink:
                    return amount
                while next_edge[node] < len(self.graph[node]):
                    edge_index = next_edge[node]
                    target, capacity, reverse_index = self.graph[node][edge_index]
                    if capacity > 0 and level[target] == level[node] + 1:
                        sent = send(target, min(amount, capacity))
                        if sent:
                            self.graph[node][edge_index][1] -= sent
                            self.graph[target][reverse_index][1] += sent
                            return sent
                    next_edge[node] += 1
                return 0

            while True:
                sent = send(source, 1 << 60)
                if not sent:
                    break
                flow += sent

    def maximal_source_side(self, sink):
        """Complement of residual vertices that can reach sink."""
        reverse_residual = [[] for _ in self.graph]
        for source, edges in enumerate(self.graph):
            for target, capacity, _ in edges:
                if capacity > 0:
                    reverse_residual[target].append(source)
        can_reach_sink = {sink}
        queue = deque([sink])
        while queue:
            node = queue.popleft()
            for predecessor in reverse_residual[node]:
                if predecessor not in can_reach_sink:
                    can_reach_sink.add(predecessor)
                    queue.append(predecessor)
        return set(range(len(self.graph))) - can_reach_sink

    def minimal_source_side(self, source):
        """Residual vertices reachable from source; the minimal min-cut side."""
        reachable = {source}
        queue = deque([source])
        while queue:
            node = queue.popleft()
            for target, capacity, _ in self.graph[node]:
                if capacity > 0 and target not in reachable:
                    reachable.add(target)
                    queue.append(target)
        return reachable


def main():
    certificate, verify = load_pinned_inputs()
    h = tuple(tuple(row) for row in certificate["matrix_numerator"])
    require(certificate["denominator"] == 2
            and certificate["radius"] == 5
            and certificate["error_bound_squared"] == 1,
            "certificate domain changed")
    norm = verify["sqnorm"]
    points = {
        point for point in itertools.product(range(-5, 6), repeat=4)
        if norm(point) <= 25
    }
    require(len(points) == 3121, "complete S5 enumeration changed")

    pairs = graph_group(h)
    require(len(pairs) == 192, "paired signed-permutation group size changed")
    input_matrices = sorted({a for a, _ in pairs})
    output_matrices = sorted({b for _, b in pairs})
    all_signed = set(signed_permutations())
    w_d4 = {matrix for matrix in all_signed if matrix_sign_product(matrix) == 1}
    require(len(w_d4) == 192, "W(D4) sign-parity count changed")
    require(set(input_matrices) == w_d4,
            "input projection is not exactly the even-sign subgroup W(D4)")
    require(set(output_matrices) == w_d4,
            "output projection is not exactly the even-sign subgroup W(D4)")

    input_orbits, input_orbit_of = orbit_partition(points, input_matrices, norm)
    require(sum(orbit["capacity"] for orbit in input_orbits) == len(points),
            "input orbit capacities do not cover S5")
    require(len({tuple(orbit["key"][0]) + (orbit["key"][1],)
                 for orbit in input_orbits}) == len(input_orbits),
            "input signed-coordinate orbit keys are not unique")
    require(all(orbit["capacity"] == orbit_capacity_formula(orbit["representative"])
                for orbit in input_orbits),
            "input orbit capacity differs from signed-coordinate formula")

    error_outputs = set()
    strict_graph = {}
    strict_edge_count = 0
    for point in sorted(points):
        strict_neighbors = set()
        for output, _ in verify["all_error_one_outputs"](point, h):
            error_outputs.add(output)
            if verify["compare_gaps"](norm(output), norm(point), 21, 19) < 0:
                strict_neighbors.add(output)
                strict_edge_count += 1
        strict_graph[point] = strict_neighbors

    output_orbits, output_orbit_of = orbit_partition(
        error_outputs, output_matrices, norm
    )
    require(sum(orbit["capacity"] for orbit in output_orbits) == len(error_outputs),
            "output orbit capacities do not cover every error-one candidate output")
    require(len({tuple(orbit["key"][0]) + (orbit["key"][1],)
                 for orbit in output_orbits}) == len(output_orbits),
            "output signed-coordinate orbit keys are not unique")
    require(all(orbit["capacity"] == orbit_capacity_formula(orbit["representative"])
                for orbit in output_orbits),
            "output orbit capacity differs from signed-coordinate formula")

    quotient_edges = set()
    for point, outputs in strict_graph.items():
        i = input_orbit_of[point]
        for output in outputs:
            require(output in output_orbit_of,
                    "strict neighbor is outside error-one output universe")
            quotient_edges.add((i, output_orbit_of[output]))

    # Completeness of an orbit adjacency for neighborhoods: one edge (x,y)
    # and transitivity of the paired group projection imply that every x'
    # in O_x has some strict neighbor in O_y, and every y' in O_y is reached
    # from some x' in O_x. Check these statements on every quotient edge.
    for input_index, output_index in quotient_edges:
        input_orbit = input_orbits[input_index]["points"]
        output_orbit = output_orbits[output_index]["points"]
        for point in input_orbit:
            require(strict_graph[point] & output_orbit,
                    "orbit adjacency is not complete across input representatives")
        for output in output_orbit:
            require(any(output in strict_graph[point] for point in input_orbit),
                    "orbit adjacency misses an output representative")

    input_count = len(input_orbits)
    output_count = len(output_orbits)
    source = 0
    input_offset = 1
    output_offset = input_offset + input_count
    sink = output_offset + output_count
    flow_graph = Dinic(sink + 1)
    total_input_capacity = sum(orbit["capacity"] for orbit in input_orbits)
    total_output_capacity = sum(orbit["capacity"] for orbit in output_orbits)
    infinity = total_input_capacity + total_output_capacity + 1
    for i, orbit in enumerate(input_orbits):
        flow_graph.add_edge(source, input_offset + i, orbit["capacity"])
    for i, j in sorted(quotient_edges):
        flow_graph.add_edge(input_offset + i, output_offset + j, infinity)
    for j, orbit in enumerate(output_orbits):
        flow_graph.add_edge(output_offset + j, sink, orbit["capacity"])

    cut_value = flow_graph.max_flow(source, sink)
    minimal_source = flow_graph.minimal_source_side(source)
    maximal_source = flow_graph.maximal_source_side(sink)
    require(source in minimal_source and sink not in minimal_source,
            "residual reachable set is not a source-side cut")
    require(source in maximal_source and sink not in maximal_source,
            "maximal residual source side is not a cut")

    def cut_capacity(source_side):
        input_cut = sum(
            orbit["capacity"] for i, orbit in enumerate(input_orbits)
            if input_offset + i not in source_side
        )
        output_cut = sum(
            orbit["capacity"] for j, orbit in enumerate(output_orbits)
            if output_offset + j in source_side
        )
        infinite_crossings = sum(
            1 for i, j in quotient_edges
            if input_offset + i in source_side
            and output_offset + j not in source_side
        )
        require(infinite_crossings == 0,
                "minimum cut crosses an orbit-adjacency infinite edge")
        return input_cut + output_cut

    require(cut_capacity(minimal_source) == cut_value,
            "minimal source-side cut capacity differs from max flow")
    require(cut_capacity(maximal_source) == cut_value,
            "maximal source-side cut capacity differs from max flow")
    minimal_input_orbits = {
        i for i in range(input_count) if input_offset + i in minimal_source
    }
    minimal_output_orbits = {
        j for j in range(output_count) if output_offset + j in minimal_source
    }
    selected_input_orbits = {
        i for i in range(input_count) if input_offset + i in maximal_source
    }
    selected_output_orbits = {
        j for j in range(output_count) if output_offset + j in maximal_source
    }
    selected_inputs = set().union(*(
        input_orbits[i]["points"] for i in selected_input_orbits
    )) if selected_input_orbits else set()
    predicted_output_orbit_ids = {
        j for i, j in quotient_edges if i in selected_input_orbits
    }
    require(predicted_output_orbit_ids == selected_output_orbits,
            "maximal min-cut output side is not exactly the selected neighborhood")
    actual_neighbors = set().union(*(strict_graph[x] for x in selected_inputs)) \
        if selected_inputs else set()
    selected_orbit_neighbors = set().union(*(
        output_orbits[j]["points"] for j in selected_output_orbits
    )) if selected_output_orbits else set()
    require(actual_neighbors == selected_orbit_neighbors,
            "lifted orbit neighborhood differs from direct exact graph enumeration")

    minimal_inputs = set().union(*(
        input_orbits[i]["points"] for i in minimal_input_orbits
    )) if minimal_input_orbits else set()
    minimal_predicted_outputs = {
        j for i, j in quotient_edges if i in minimal_input_orbits
    }
    require(minimal_predicted_outputs == minimal_output_orbits,
            "minimal min-cut output side is not exactly the selected neighborhood")
    minimal_actual_neighbors = set().union(*(strict_graph[x] for x in minimal_inputs)) \
        if minimal_inputs else set()
    minimal_orbit_neighbors = set().union(*(
        output_orbits[j]["points"] for j in minimal_output_orbits
    )) if minimal_output_orbits else set()
    require(minimal_actual_neighbors == minimal_orbit_neighbors,
            "minimal min-cut lifted neighborhood differs from direct enumeration")

    selected_input_capacity = sum(
        input_orbits[i]["capacity"] for i in selected_input_orbits
    )
    selected_output_capacity = sum(
        output_orbits[j]["capacity"] for j in selected_output_orbits
    )
    deficiency = selected_input_capacity - selected_output_capacity
    require(deficiency > 0, "maximum invariant deficiency is not positive")
    require(deficiency == total_input_capacity - cut_value,
            "Hall deficiency does not equal total input capacity minus min-cut")

    minimal_input_capacity = sum(input_orbits[i]["capacity"]
                                 for i in minimal_input_orbits)
    minimal_output_capacity = sum(output_orbits[j]["capacity"]
                                  for j in minimal_output_orbits)
    minimal_deficiency = minimal_input_capacity - minimal_output_capacity
    require(minimal_deficiency == total_input_capacity - cut_value,
            "minimal min-cut does not attain the same maximum deficiency")
    require(minimal_input_orbits <= selected_input_orbits
            and minimal_output_orbits <= selected_output_orbits,
            "minimal and maximal min-cut source sides are improperly ordered")

    # Closed-form orbit witnesses. For W(D4), an orbit is determined by
    # sorted absolute coordinates and, with no zeros, the product of signs.
    def sign_product(point):
        product = 1
        for value in point:
            require(value != 0, "sign product requested for a zero coordinate")
            product *= 1 if value > 0 else -1
        return product

    def has_abs_pattern(point, pattern):
        return tuple(sorted(abs(value) for value in point)) == pattern

    ball19 = {point for point in points if norm(point) <= 19}
    orbit_0033 = {point for point in points if has_abs_pattern(point, (0, 0, 3, 3))}
    orbit_0133 = {point for point in points if has_abs_pattern(point, (0, 1, 3, 3))}
    orbit_2222_minus = {
        point for point in points
        if has_abs_pattern(point, (2, 2, 2, 2)) and sign_product(point) == -1
    }
    orbit_2223_plus = {
        point for point in points
        if has_abs_pattern(point, (2, 2, 2, 3)) and sign_product(point) == 1
    }
    small_t = (ball19 - orbit_0033 - orbit_0133 - orbit_2222_minus) | orbit_2223_plus
    small_n = ball19 - orbit_0033 - orbit_0133 - orbit_2222_minus
    expanded_t = small_t | orbit_2222_minus
    expanded_n = small_n | orbit_2222_minus
    require((len(ball19), len(orbit_0033), len(orbit_0133),
             len(orbit_2222_minus), len(orbit_2223_plus)) == (1897, 24, 96, 8, 32),
            "closed-form orbit capacities changed")
    require(len(small_t) == 1801 and len(small_n) == 1769,
            "base closed-form witness counts changed")
    require(len(expanded_t) == 1809 and len(expanded_n) == 1777,
            "expanded closed-form witness counts changed")
    require(small_t == minimal_inputs and small_n == minimal_actual_neighbors,
            "closed-form base witness differs from minimal min-cut")
    require(expanded_t == selected_inputs and expanded_n == actual_neighbors,
            "closed-form expanded witness differs from maximal min-cut")
    require(neighborhood(small_t, strict_graph) == small_n,
            "base closed-form strict neighborhood is incomplete or overinclusive")
    require(neighborhood(expanded_t, strict_graph) == expanded_n,
            "expanded closed-form strict neighborhood is incomplete or overinclusive")

    # Cross-check the selected cut's relation to the supplied deficient set.
    cert_t = {tuple(point) for point in certificate["hall"]["input_set"]}
    cert_n = {tuple(point) for point in certificate["hall"]["output_neighbors"]}
    require(len(cert_t) == 1692 and len(cert_n) == 1691,
            "pinned predecessor Hall witness changed")
    require(len(cert_t) - len(cert_n) == 1,
            "pinned predecessor witness is no longer deficit one")

    def orbit_table(orbits, selected_ids):
        rows = []
        for index, orbit in enumerate(orbits):
            representative = orbit["representative"]
            rows.append({
                "index": index,
                "representative": list(representative),
                "orbit_key": orbit["key"],
                "size": orbit["capacity"],
                "norm_squared": orbit["norm_squared"],
                "selected": index in selected_ids,
            })
        return rows

    print(json.dumps({
        "status": "PASS",
        "scope": "exact invariant Hall witness on complete S5 at strict beta only",
        "source_pins": {
            "base_commit": "e54523517d0f03e58352e647c403a5af3e525a57",
            "certificate_expanded_sha256": RAW_CERT_SHA256,
            "exact_verifier_sha256": VERIFY_SHA256,
        },
        "group": {
            "signed_permutation_count": len(all_signed),
            "paired_graph_automorphism_order": len(pairs),
            "projection_is_W_D4": True,
            "W_D4_definition": "signed permutation matrices whose four nonzero entries have product +1",
            "input_orbit_count": input_count,
            "output_candidate_orbit_count": output_count,
        },
        "graph": {
            "S5_input_count": len(points),
            "all_error_one_candidate_output_count": len(error_outputs),
            "strict_beta_edge_count": strict_edge_count,
            "quotient_adjacency_count": len(quotient_edges),
            "orbit_adjacency_completeness_checked": True,
        },
        "maximal_invariant_hall_set": {
            "selected_input_orbit_indices": sorted(selected_input_orbits),
            "selected_input_orbit_keys": [input_orbits[i]["key"] for i in sorted(selected_input_orbits)],
            "selected_output_orbit_indices": sorted(selected_output_orbits),
            "selected_output_orbit_keys": [output_orbits[j]["key"] for j in sorted(selected_output_orbits)],
            "input_count": selected_input_capacity,
            "complete_strict_beta_neighbor_count": selected_output_capacity,
            "deficiency": deficiency,
            "quotient_min_cut": cut_value,
            "maximal_min_cut_source_side": True,
        },
        "minimal_min_cut_witness": {
            "input_count": minimal_input_capacity,
            "complete_strict_beta_neighbor_count": minimal_output_capacity,
            "deficiency": minimal_deficiency,
            "same_min_cut_value": cut_value,
        },
        "short_closed_form_witness": {
            "definition": {
                "B19": "{x in Z^4: ||x||^2<=19}",
                "O0033": "sorted absolute coordinates (0,0,3,3)",
                "O0133": "sorted absolute coordinates (0,1,3,3)",
                "O2222minus": "sorted absolute coordinates (2,2,2,2), sign product -1",
                "O2223plus": "sorted absolute coordinates (2,2,2,3), sign product +1",
                "T0": "B19 \\ O0033 \\ O0133 \\ O2222minus union O2223plus",
                "N0": "B19 \\ O0033 \\ O0133 \\ O2222minus",
                "T1": "T0 union O2222minus = B19 \\ O0033 \\ O0133 union O2223plus",
                "N1": "N0 union O2222minus = B19 \\ O0033 \\ O0133",
            },
            "orbit_sizes": {
                "B19": len(ball19),
                "O0033": len(orbit_0033),
                "O0133": len(orbit_0133),
                "O2222minus": len(orbit_2222_minus),
                "O2223plus": len(orbit_2223_plus),
            },
            "T0_size": len(small_t),
            "N0_size": len(small_n),
            "T1_size": len(expanded_t),
            "N1_size": len(expanded_n),
            "T0_exact_neighborhood": True,
            "T1_exact_neighborhood": True,
            "added_balanced_orbit_preserves_deficiency": (
                len(expanded_t) - len(expanded_n)
                == len(small_t) - len(small_n) == 32
            ),
        },
        "previous_witness": {
            "input_count": len(cert_t),
            "neighbor_count": len(cert_n),
            "deficiency": len(cert_t) - len(cert_n),
            "provided_as_input_data_only": True,
        },
        "membership_rule": {
            "closed_form_inputs": "T1=(B19\\O0033\\O0133) union O2223plus",
            "closed_form_outputs": "N1=B19\\O0033\\O0133",
            "domain": "S5 points satisfying the closed-form T1 predicate",
            "W_D4_orbit_key": "(sorted absolute coordinates, product of coordinate signs if no coordinate is zero else null)",
            "neighbor_rule": "error-one candidate output orbit_key appears among selected_output_orbit_keys; quotient adjacency is exact",
        },
        "input_orbit_table": orbit_table(input_orbits, selected_input_orbits),
        "output_orbit_table": orbit_table(output_orbits, selected_output_orbits),
    }, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
