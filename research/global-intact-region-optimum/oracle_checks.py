"""Independent exhaustive checks for the small ambient-two optimizer cases.

Prepared for Krzysztof Wojt by a separate OpenAI Codex supporting agent.
Apache-2.0; substantial AI assistance disclosed in TASK.json and README.md.

This module deliberately represents subspaces as explicit sets of vectors and
checks matrix images by applying columns to each vector. It does not import
optimizer.py or reuse its subspace operations.
"""

from itertools import product


def _need(condition, message):
    if not condition:
        raise AssertionError(message)


def _all_subspaces_f2_2():
    """Enumerate subspaces by testing all subsets of the four explicit vectors."""
    vectors = (0, 1, 2, 3)
    spaces = []
    for subset_bits in range(1 << len(vectors)):
        candidate = frozenset(
            vector for index, vector in enumerate(vectors)
            if subset_bits & (1 << index)
        )
        if 0 not in candidate:
            continue
        if all((left ^ right) in candidate for left in candidate for right in candidate):
            spaces.append(candidate)
    spaces.sort(key=lambda space: (len(space), tuple(sorted(space))))
    _need(len(spaces) == 5, "F2^2 has exactly five explicitly enumerated subspaces")
    return tuple(spaces)


_SPACES = _all_subspaces_f2_2()
_ZERO = frozenset({0})
_LINE_A = frozenset({0, 1})
_LINE_B = frozenset({0, 2})
_LINE_C = frozenset({0, 3})
_FULL = frozenset({0, 1, 2, 3})
_SPACE_TO_MASK = {space: sum(1 << vector for vector in space) for space in _SPACES}


def _encode(space):
    return _SPACE_TO_MASK[frozenset(space)]


def _decode(mask, ambient=2):
    limit = (1 << (1 << ambient)) - 1
    _need(type(mask) is int and mask >= 0 and mask & limit == mask,
          "Subspace mask is in the ambient vector domain")
    space = frozenset(vector for vector in range(1 << ambient) if mask & (1 << vector))
    _need(bool(space) and 0 in space, "Subspace mask contains the zero vector")
    _need(all((left ^ right) in space for left in space for right in space),
          "Subspace mask is closed under vector addition")
    return space


def _dimension(space):
    size = len(space)
    _need(size in (1, 2, 4), "Ambient-two subspace has power-of-two size")
    return size.bit_length() - 1


def _apply(vector, matrix, ambient=2):
    output = 0
    for coordinate in range(ambient):
        if vector & (1 << coordinate):
            output ^= matrix[coordinate]
    return output


def _image(space, matrix, ambient=2):
    return frozenset(_apply(vector, matrix, ambient) for vector in space)


def _matrix_is_invertible(matrix, ambient=2):
    if len(matrix) != ambient:
        return False
    largest_vector = (1 << ambient) - 1
    if any(type(column) is not int or column < 0 or column > largest_vector
           for column in matrix):
        return False
    images = {_apply(vector, matrix, ambient) for vector in range(1 << ambient)}
    return len(images) == (1 << ambient)


def _histogram(assignment, edges, ambient=2):
    counts = [0] * (ambient + 1)
    for source, target, matrix in edges:
        before = assignment[source]
        after = assignment[target]
        transported = _image(before, matrix, ambient)
        _need(transported <= after, "Literal image containment on every edge")
        rank = _dimension(after) - _dimension(before)
        _need(0 <= rank <= ambient, "Nonnegative charged edge rank")
        counts[rank] += 1
    return tuple(counts)


def _check_original_labels(labels, edges, ambient=2):
    for source, target, matrix in edges:
        _need(_matrix_is_invertible(matrix, ambient), "Fixture map is invertible")
        _need(_image(_decode(labels[source], ambient), matrix, ambient)
              <= _decode(labels[target], ambient),
              "Original source labels satisfy every fixture edge")


def _enumerate_feasible(labels, fixed, edges, ambient=2):
    """Enumerate all assignments, ignoring original labels at free vertices."""
    _check_original_labels(labels, edges, ambient)
    nodes = tuple(sorted(labels))
    domains = [(_decode(labels[node], ambient),) if node in fixed else _SPACES
               for node in nodes]
    feasible = []
    examined = 0
    for choices in product(*domains):
        examined += 1
        assignment = dict(zip(nodes, choices))
        if all(_image(assignment[source], matrix, ambient) <= assignment[target]
               for source, target, matrix in edges):
            feasible.append(assignment)
    _need(feasible, "Fixture has at least one feasible assignment")
    return feasible, examined


def _fixture(name, labels, fixed, edges):
    return {
        "name": name,
        "labels": labels,
        "fixed": set(fixed),
        "edges": list(edges),
        "ambient": 2,
    }


def _fixtures():
    identity = (1, 2)
    swap = (2, 1)
    shear_a = (1, 3)  # e0 -> e0; e1 -> e0 + e1
    shear_b = (3, 2)  # e0 -> e0 + e1; e1 -> e1
    lines = (_LINE_A, _LINE_B, _LINE_C)
    fixtures = []

    # Chains give a free vertex exactly the two assignments {0, L} or {L, F}.
    # Across these six fixtures every F2^2 subspace occurs as an allowed value.
    for index, line in enumerate(lines):
        line_mask = _encode(line)
        fixtures.append(_fixture(
            "zero_to_line_%d" % index,
            {0: _encode(_ZERO), 1: line_mask, 2: line_mask},
            {0, 2},
            [(0, 1, identity), (1, 2, identity)],
        ))
        fixtures.append(_fixture(
            "line_to_full_%d" % index,
            {0: line_mask, 1: _encode(_FULL), 2: _encode(_FULL)},
            {0, 2},
            [(0, 1, identity), (1, 2, identity)],
        ))

    # Four free variables form two interacting two-state pairs. Fixed zero,
    # line, and full boundaries give each variable a binary interval; swap maps
    # couple both pairs, while each u_i -> v_i edge can carry rank two.
    labels = {
        0: _encode(_ZERO), 1: _encode(_ZERO),
        2: _encode(_LINE_A), 3: _encode(_LINE_B),
        4: _encode(_LINE_A), 5: _encode(_LINE_B),
        6: _encode(_FULL), 7: _encode(_FULL),
        8: _encode(_LINE_A), 9: _encode(_LINE_B),
        10: _encode(_FULL), 11: _encode(_FULL),
    }
    fixed = set(range(8))
    edges = []
    for u, v, upper, lower, upper_map, lower_map, full in (
        (8, 10, 2, 4, shear_a, shear_a, 6),
        (9, 11, 3, 5, shear_b, shear_b, 7),
    ):
        # Parallel boundary edges make each free node balanced by edge count.
        edges.extend([(0, u, identity), (1, u, swap)])
        edges.append((u, upper, upper_map))
        edges.append((u, v, identity))
        edges.append((lower, v, lower_map))
        edges.extend([(v, full, swap), (v, full, identity)])
    edges.extend([
        (8, 9, swap), (9, 8, swap),
        (10, 11, swap), (11, 10, swap),
    ])
    fixtures.append(_fixture("four_free_coupled_parallel_cycle", labels, fixed, edges))
    return fixtures


def _verify_fixture(solve, fixture):
    labels = fixture["labels"]
    fixed = fixture["fixed"]
    edges = fixture["edges"]
    ambient = fixture["ambient"]
    feasible, examined = _enumerate_feasible(labels, fixed, edges, ambient)
    _need(all(sum(1 for source, _, _ in edges if source == node)
              == sum(1 for _, target, _ in edges if target == node)
              for node in labels if node not in fixed),
          "Each free fixture vertex is balanced, counting parallel edges")

    histograms = [_histogram(assignment, edges, ambient) for assignment in feasible]
    rank_masses = {
        sum(rank * count for rank, count in enumerate(histogram))
        for histogram in histograms
    }
    _need(len(rank_masses) == 1,
          "Balanced free vertices give fixed total rank mass in each fixture")
    best_rank_two = max(histogram[2] for histogram in histograms)

    result = solve(labels, fixed, edges, ambient=ambient)
    assignment_masks = result.get("assignment")
    _need(isinstance(assignment_masks, dict) and set(assignment_masks) == set(labels),
          "Solver returns one subspace for every vertex")
    assignment = {node: _decode(mask, ambient) for node, mask in assignment_masks.items()}
    _need(all(assignment[node] == _decode(labels[node], ambient) for node in fixed),
          "Returned assignment preserves fixed source labels")
    _need(all(_image(assignment[source], matrix, ambient) <= assignment[target]
              for source, target, matrix in edges),
          "Returned assignment satisfies every original edge")

    literal_histogram = _histogram(assignment, edges, ambient)
    returned_histogram = result.get("histogram")
    _need(isinstance(returned_histogram, list)
          and len(returned_histogram) == ambient + 1
          and all(type(value) is int and value >= 0 for value in returned_histogram),
          "Solver returns a nonnegative histogram including rank zero")
    _need(tuple(returned_histogram) == literal_histogram,
          "Returned histogram counts every literal edge rank, including parallels")
    _need(sum(returned_histogram) == len(edges),
          "Returned histogram owns every edge occurrence exactly once")
    _need(literal_histogram[2] == best_rank_two,
          "Returned assignment maximizes rank-two edges among all feasible assignments")
    _need(literal_histogram in histograms,
          "Returned histogram is attained by a feasible enumerated assignment")

    bounds = result.get("bounds")
    _need(isinstance(bounds, dict) and set(bounds) == set(labels),
          "Solver returns lower and upper closure bounds for every vertex")
    for node, pair in bounds.items():
        _need(isinstance(pair, (list, tuple)) and len(pair) == 2,
              "Each closure bound has a lower and upper mask")
        lower, upper = (_decode(pair[0], ambient), _decode(pair[1], ambient))
        _need(lower <= upper, "Returned closure interval is ordered by containment")
        _need(_dimension(upper) - _dimension(lower) <= 1,
              "Fixture exercises only residual binary intervals")
        for candidate in feasible:
            _need(lower <= candidate[node] <= upper,
                  "Every allowed assignment lies inside every returned closure interval")

    nonidentity = sum(matrix != (1, 2) for _, _, matrix in edges)
    parallel_count = len(edges) - len({(u, v) for u, v, _ in edges})
    return {
        "name": fixture["name"],
        "vertices": len(labels),
        "free_vertices": len(labels) - len(fixed),
        "edges": len(edges),
        "assignments_examined": examined,
        "feasible_assignments": len(feasible),
        "best_rank_two_edges": best_rank_two,
        "histogram": list(literal_histogram),
        "nonidentity_map_occurrences": nonidentity,
        "repeated_parallel_occurrences": parallel_count,
    }


def _expect_value_error(name, callback):
    try:
        callback()
    except ValueError:
        return name
    except Exception as error:
        raise AssertionError("%s raised %s instead of ValueError" %
                             (name, type(error).__name__)) from error
    raise AssertionError("%s was not refused" % name)


def run_checks(solve):
    """Run exhaustive, independent ambient-two checks against ``solve``.

    The optimizer is supplied as a callable to keep this oracle's subspace,
    image, containment, and histogram calculations independent.
    """
    _need(callable(solve), "A callable optimizer solve function is required")
    subspace_masks = sorted(_encode(space) for space in _SPACES)
    _need(len(set(subspace_masks)) == 5, "All five ambient-two subspaces are distinct")

    fixtures = _fixtures()
    fixture_results = [_verify_fixture(solve, fixture) for fixture in fixtures]
    seen_assignments = {
        mask
        for fixture in fixtures
        for assignment in _enumerate_feasible(
            fixture["labels"], fixture["fixed"], fixture["edges"], fixture["ambient"]
        )[0]
        for mask in (_encode(space) for space in assignment.values())
    }
    _need(set(subspace_masks) <= seen_assignments,
          "Every ambient-two subspace occurs in an allowed fixture assignment")

    # Sensitivity probes make an omitted coupled edge and a one-rank histogram
    # mutation observably fail the same independent conditions used above.
    coupled = fixtures[-1]
    full_feasible, _ = _enumerate_feasible(
        coupled["labels"], coupled["fixed"], coupled["edges"], coupled["ambient"]
    )
    coupling_edge = (10, 11, (2, 1))
    coupling_index = coupled["edges"].index(coupling_edge)
    without_edge = coupled["edges"][:coupling_index] + coupled["edges"][coupling_index + 1:]
    omitted_feasible, _ = _enumerate_feasible(
        coupled["labels"], coupled["fixed"], without_edge, coupled["ambient"]
    )
    _need(len(omitted_feasible) > len(full_feasible),
          "Omitting a coupling edge expands the independently enumerated feasible set")

    coupled_result = solve(coupled["labels"], coupled["fixed"], coupled["edges"], ambient=2)
    coupled_assignment = {
        node: _decode(mask, 2) for node, mask in coupled_result["assignment"].items()
    }
    coupled_histogram = _histogram(coupled_assignment, coupled["edges"], 2)
    rank_mutation = list(coupled_histogram)
    _need(rank_mutation[0] > 0, "Coupled optimum has a zero-rank edge for mutation probe")
    rank_mutation[0] -= 1
    rank_mutation[1] += 1
    _need(sum(rank_mutation) == sum(coupled_histogram)
          and sum(rank * count for rank, count in enumerate(rank_mutation))
          != sum(rank * count for rank, count in enumerate(coupled_histogram)),
          "Changing one edge rank preserves edge count but violates fixed rank mass")
    _need(list(coupled_histogram) != rank_mutation,
          "Literal histogram equality detects a one-edge rank mutation")

    bad_interval = _fixture(
        "refusal_residual_gap_two",
        {0: _encode(_ZERO)}, set(), [],
    )
    fixed_conflict = _fixture(
        "refusal_fixed_label_conflict",
        {0: _encode(_LINE_A), 1: _encode(_LINE_B)}, {0, 1},
        [(0, 1, (1, 2))],
    )
    malformed_shape = _fixture(
        "refusal_malformed_map_shape",
        {0: _encode(_ZERO), 1: _encode(_ZERO)}, {0, 1},
        [(0, 1, (1,))],
    )
    singular_map = _fixture(
        "refusal_singular_map",
        {0: _encode(_ZERO), 1: _encode(_ZERO)}, {0, 1},
        [(0, 1, (1, 1))],
    )
    refusal_names = [
        _expect_value_error("residual_gap_two", lambda: solve(
            bad_interval["labels"], bad_interval["fixed"], bad_interval["edges"], ambient=2
        )),
        _expect_value_error("fixed_label_conflict", lambda: solve(
            fixed_conflict["labels"], fixed_conflict["fixed"],
            fixed_conflict["edges"], ambient=2
        )),
        _expect_value_error("malformed_map_shape", lambda: solve(
            malformed_shape["labels"], malformed_shape["fixed"],
            malformed_shape["edges"], ambient=2
        )),
        _expect_value_error("singular_map", lambda: solve(
            singular_map["labels"], singular_map["fixed"],
            singular_map["edges"], ambient=2
        )),
    ]

    return {
        "status": "PASS_INDEPENDENT_SMALL_GRAPH_ORACLE",
        "ambient": 2,
        "explicit_subspaces": len(_SPACES),
        "subspaces_seen_in_feasible_assignments": len(set(subspace_masks) & seen_assignments),
        "fixture_count": len(fixture_results),
        "free_vertex_counts": sorted({row["free_vertices"] for row in fixture_results}),
        "assignments_examined": sum(row["assignments_examined"] for row in fixture_results),
        "feasible_assignments": sum(row["feasible_assignments"] for row in fixture_results),
        "nonidentity_map_occurrences": sum(row["nonidentity_map_occurrences"]
                                           for row in fixture_results),
        "parallel_edge_occurrences": sum(row["repeated_parallel_occurrences"]
                                         for row in fixture_results),
        "rank_two_objective": "maximized at fixed total rank mass",
        "mutation_detectors": {
            "omitted_coupling_edge_feasible_assignments": {
                "complete_graph": len(full_feasible),
                "after_omission": len(omitted_feasible),
            },
            "single_edge_rank_change_detected": True,
        },
        "refusals": refusal_names,
        "fixtures": fixture_results,
    }
