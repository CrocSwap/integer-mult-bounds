"""Exact replay of an explicitly supplied, finite dyadic scalar circuit,
plus independent Prim and cycle-property verification of the U8 bi-forest recipe.

This checker does not import the candidate constructor or its lowering rules.
Every L, C and W register enters with its own independent dirt symbol. Sparse
integer rows with one power-of-two denominator implement the arithmetic; no
floating point or Fraction arithmetic is used here. Positive envelopes replay
the literal primitive sequence without using cancellation.

The result certifies the scalar projection of the supplied finite instruction
list and the coordinate-wise MST optimality of the target and helper forests at
the fixed point (T5, H5). Recursive child identities, physical frames, global
hosting and any asymptotic multiplication bound remain separate inherited
obligations.

Prepared by Stephan Arrington (@steph4n-gh) with substantial Google DeepMind
Antigravity assistance. Apache-2.0.
"""

from collections import Counter
import hashlib
import json


class ReplayError(ValueError):
    """A malformed circuit, recipe, or an incorrect asserted endpoint."""


def _require(condition, message):
    if not condition:
        raise ReplayError(message)


def _normal_row(terms, exponent):
    """Canonical integer numerator row divided by 2**exponent."""
    terms = {column: value for column, value in terms.items() if value}
    if not terms:
        return {}, 0
    if exponent:
        trailing = min((abs(value) & -abs(value)).bit_length() - 1
                       for value in terms.values())
        reduction = min(exponent, trailing)
        if reduction:
            terms = {column: value >> reduction for column, value in terms.items()}
            exponent -= reduction
    return terms, exponent


def _sum_rows(left, right, sign):
    left_terms, left_exponent = left
    right_terms, right_exponent = right
    exponent = max(left_exponent, right_exponent)
    result = {column: value << (exponent - left_exponent)
              for column, value in left_terms.items()}
    for column, value in right_terms.items():
        result[column] = result.get(column, 0) + sign * (value << (exponent - right_exponent))
    return _normal_row(result, exponent)


def _normal_number(numerator, exponent):
    if numerator == 0:
        return 0, 0
    reduction = min(exponent, (numerator & -numerator).bit_length() - 1)
    return numerator >> reduction, exponent - reduction


def _sum_numbers(left, right):
    exponent = max(left[1], right[1])
    numerator = ((left[0] << (exponent - left[1]))
                 + (right[0] << (exponent - right[1])))
    return _normal_number(numerator, exponent)


def _greater(left, right):
    return (left[0] << right[1]) > (right[0] << left[1])


def _serialize_row(row):
    terms, exponent = row
    return {"denominator_power": exponent,
            "terms": [[column, terms[column]] for column in sorted(terms)]}


def replay(primitives, n=728, centers=8):
    """Return a JSON-serializable exact endpoint, cost and positive prefix.

    The vocabulary is clear(ref), copy(target, source), add(target, source,
    sign), double(ref), halve(ref), negate(ref), represented as JSON lists.
    Add's sign must be exactly +1 or -1. References are ["L", index],
    ["C", index], or the unique coefficient scratch ["W", 0].

    Basis symbols 0..n-1 are L inputs, n..n+centers-1 are C inputs and
    n+centers is the W input. Non-scalar events must be checked separately,
    never passed here.
    """
    _require(type(n) is int and n > 0, "n must be a positive integer")
    _require(type(centers) is int and centers >= 0, "centers must be a nonnegative integer")
    sizes = {"L": n, "C": centers, "W": 1}
    refs = [(kind, index) for kind, size in sizes.items() for index in range(size)]
    rows = {ref: ({column: 1}, 0) for column, ref in enumerate(refs)}
    envelope = {ref: (1, 0) for ref in refs}
    prefix = (1, 0)
    prefix_at = -1
    maximum_denominator_power = 0
    counts = Counter()

    def reference(value, instruction_index):
        _require(isinstance(value, (list, tuple)) and len(value) == 2,
                 f"instruction {instruction_index}: malformed register reference")
        kind, index = value
        _require(type(kind) is str and kind in sizes and type(index) is int
                 and 0 <= index < sizes[kind],
                 f"instruction {instruction_index}: register outside declared domain")
        return kind, index

    arities = {"clear": 2, "copy": 3, "add": 4,
               "double": 2, "halve": 2, "negate": 2}
    for instruction_index, instruction in enumerate(primitives):
        _require(isinstance(instruction, (list, tuple)) and bool(instruction),
                 f"instruction {instruction_index}: malformed primitive")
        operation = instruction[0]
        _require(type(operation) is str and operation in arities,
                 f"instruction {instruction_index}: unknown primitive {operation!r}")
        _require(len(instruction) == arities[operation],
                 f"instruction {instruction_index}: wrong primitive arity")
        target = reference(instruction[1], instruction_index)
        counts[operation] += 1
        if operation == "clear":
            rows[target] = ({}, 0)
            envelope[target] = (0, 0)
        elif operation == "copy":
            source = reference(instruction[2], instruction_index)
            rows[target] = rows[source]
            envelope[target] = envelope[source]
        elif operation == "add":
            source = reference(instruction[2], instruction_index)
            sign = instruction[3]
            _require(type(sign) is int and sign in (-1, 1),
                     f"instruction {instruction_index}: add sign must be +1 or -1")
            _require(target != source,
                     f"instruction {instruction_index}: add aliases its source")
            rows[target] = _sum_rows(rows[target], rows[source], sign)
            envelope[target] = _sum_numbers(envelope[target], envelope[source])
        else:
            terms, exponent = rows[target]
            numerator, denominator_power = envelope[target]
            if operation == "negate":
                rows[target] = ({column: -value for column, value in terms.items()}, exponent)
            elif operation == "double":
                rows[target] = _normal_row({column: 2 * value for column, value in terms.items()}, exponent)
                envelope[target] = _normal_number(2 * numerator, denominator_power)
            else:
                rows[target] = _normal_row(terms, exponent + 1)
                envelope[target] = _normal_number(numerator, denominator_power + 1)
        if _greater(envelope[target], prefix):
            prefix = envelope[target]
            prefix_at = instruction_index
        maximum_denominator_power = max(maximum_denominator_power, rows[target][1])

    return {
        "arithmetic": "exact integer sparse rows over dyadic denominators",
        "input_columns": len(refs),
        "logical_registers": n,
        "center_registers": centers,
        "scratch_registers": 1,
        "primitive_count": sum(counts.values()),
        "primitive_counts": dict(sorted(counts.items())),
        "maximum_denominator_power": maximum_denominator_power,
        "positive_prefix": {
            "numerator": prefix[0],
            "denominator_power": prefix[1],
            "strict_power_of_two_bits": prefix[0].bit_length() - prefix[1],
            "first_maximum_instruction": prefix_at,
        },
        "endpoint": {kind: [_serialize_row(rows[kind, index]) for index in range(size)]
                     for kind, size in sizes.items()},
    }


def check_endpoint(result, orientation, v=112):
    """Check additive forward or inverse-transpose ports and erased private work."""
    _require(orientation in ("forward", "backward"), "unknown orientation")
    n = result["logical_registers"]
    _require(type(v) is int and 0 < 2 * v <= n, "invalid port count")
    endpoint = result["endpoint"]
    _require(len(endpoint["L"]) == n, "wrong number of logical outputs")
    for index, actual in enumerate(endpoint["L"]):
        terms = {index: 1}
        if orientation == "forward" and v <= index < 2 * v:
            terms[index - v] = 1
        elif orientation == "backward" and index < v:
            terms[v + index] = -1
        expected = _serialize_row((terms, 0))
        _require(actual == expected,
                 f"{orientation}: incorrect logical output L[{index}]")
    for kind in ("C", "W"):
        _require(len(endpoint[kind]) == result["center_registers" if kind == "C" else "scratch_registers"],
                 f"wrong number of {kind} outputs")
        for index, actual in enumerate(endpoint[kind]):
            _require(actual == _serialize_row(({}, 0)),
                     f"{orientation}: private register {kind}[{index}] is not erased")
    return True


def _verify_forest_optimality(vectors, forest_edges, price_fn, label):
    """Check forest validity, topological ordering, Prim minimum, and all cycle inequalities."""
    n = len(vectors)
    parent = {}
    depth_map = {}
    adjacency = {u: [] for u in range(-1, n)}
    previous_depth = float("inf")
    for entry in forest_edges:
        _require(isinstance(entry, (list, tuple)) and len(entry) == 4,
                 f"{label}: malformed forest edge")
        child, ancestor, sign, depth = entry
        _require(type(child) is int and type(ancestor) is int
                 and 0 <= child < n and 0 <= ancestor < n
                 and child != ancestor and child not in parent
                 and type(sign) is int and sign in (-1, 1)
                 and type(depth) is int and depth >= 1,
                 f"{label}: invalid forest edge")
        _require(depth <= previous_depth,
                 f"{label}: forest edges are not in non-increasing leaf-before-parent depth order")
        previous_depth = depth
        parent[child] = (ancestor, sign)
        depth_map[child] = depth
    for u in range(n):
        if u not in parent:
            depth_map[u] = 0
            w = sum(price_fn(x) for x in vectors[u])
            adjacency[-1].append((u, w))
            adjacency[u].append((-1, w))
    for child, (ancestor, sign) in parent.items():
        visited = set()
        cur = child
        while cur in parent:
            _require(cur not in visited, f"{label}: forest has a cycle")
            visited.add(cur)
            cur = parent[cur][0]
        _require(depth_map[child] == depth_map[ancestor] + 1,
                 f"{label}: inconsistent node depth")
        w = 8 + sum(price_fn(a - sign * b)
                    for a, b in zip(vectors[child], vectors[ancestor]))
        adjacency[ancestor].append((child, w))
        adjacency[child].append((ancestor, w))

    # Prim's algorithm from superroot -1
    distances = [sum(price_fn(x) for x in row) for row in vectors]
    best_pair = {}
    for i in range(n):
        vi = vectors[i]
        for j in range(i):
            vj = vectors[j]
            w_neg = 8 + sum(price_fn(a + b) for a, b in zip(vi, vj))
            w_pos = 8 + sum(price_fn(a - b) for a, b in zip(vi, vj))
            best_pair[i, j] = best_pair[j, i] = min(w_neg, w_pos)

    reached = set()
    prim_minimum = 0
    for _ in range(n):
        j = min((j for j in range(n) if j not in reached), key=distances.__getitem__)
        reached.add(j)
        prim_minimum += distances[j]
        for i in range(n):
            if i not in reached and best_pair[i, j] < distances[i]:
                distances[i] = best_pair[i, j]

    transformed = [v[:] for v in vectors]
    for child, (ancestor, sign) in parent.items():
        transformed[child] = [a - sign * b for a, b in zip(vectors[child], vectors[ancestor])]
    forest_cost = sum(price_fn(x) for row in transformed for x in row) + 8 * len(parent)
    _require(forest_cost == prim_minimum,
             f"{label}: forest cost {forest_cost} differs from Prim minimum {prim_minimum}")

    # Verify MST cycle-exchange inequality against all n + 2*n*(n-1)//2 edges.
    max_on_path = {}
    for start in range(-1, n):
        stack = [(start, None, 0)]
        while stack:
            u, prev, peak = stack.pop()
            max_on_path[start, u] = peak
            for v, w in adjacency[u]:
                if v != prev:
                    stack.append((v, u, max(peak, w)))
    checked_edges = 0
    for i in range(n):
        w_root = sum(price_fn(x) for x in vectors[i])
        _require(w_root >= max_on_path[-1, i],
                 f"{label}: negative cycle-exchange opportunity on root edge {i}")
        checked_edges += 1
        for j in range(i):
            _require(best_pair[i, j] >= max_on_path[j, i],
                     f"{label}: negative cycle-exchange opportunity on pair ({j}, {i})")
            checked_edges += 2
    return transformed, forest_cost, checked_edges


def check_recipe(word, recipe):
    """Independently price the finite U8 bi-forest recipe, comparator, and MST certificates."""
    targets = sorted({event[1] for event in word["compensation"]})
    sources = sorted({event[2] for event in word["compensation"]})
    _require((len(targets), len(sources)) == (112, 216), "unexpected U8 compensation shape")
    _require(targets == recipe["targets"] and sources == recipe["sources"], "recipe bank mismatch")
    _require(set(targets).isdisjoint(sources), "compensation banks overlap")
    _require(all(word["start"][r] == 0 for r in targets + sources), "nonzero compensation frame")
    _require(all(word["final"][r] == 1 for r in sources), "wrapped helper before entry adapter")
    ti, si = {r: i for i, r in enumerate(targets)}, {r: i for i, r in enumerate(sources)}
    matrix = [[0] * len(sources) for _ in targets]
    for tag, target, source, numerator, denominator, frame in word["compensation"]:
        _require(tag == "add" and frame == 0 and denominator > 0
                 and (4 * numerator) % denominator == 0, "non-quarter compensation")
        matrix[ti[target]][si[source]] += (4 * numerator) // denominator
    prices = {0: 0}

    def price(value):
        if value not in prices:
            integer, halvings = abs(value), 2
            while halvings and integer % 2 == 0:
                integer //= 2
                halvings -= 1
            digits = []
            while integer:
                digits.append(integer % 2)
                integer //= 2
            prices[value] = 3 + halvings + sum(digits) + len(digits) - 1
        return prices[value]

    def cost(rows):
        return sum(price(value) for row in rows for value in row)

    baseline_price = cost(matrix)
    _require(baseline_price == recipe["baseline_panel_price"], "baseline panel price")

    # 1. Verify initial target forest T0 on C (10,883 floor)
    D0, t0_cost, t0_edges = _verify_forest_optimality(
        matrix, recipe["initial_target_forest"], price, "initial_target_forest"
    )
    _require(t0_cost == recipe["target_only_panel_price"]
             == recipe["initial_target_search"]["price"],
             "initial target forest is not minimum priced")
    _require(t0_edges == recipe["initial_target_search"]["edges"],
             "initial target edge count")

    # 2. Verify PR917-style disjoint helper-pair comparator on D0 = T0 C
    columns0 = list(zip(*D0))
    column_costs0 = [sum(map(price, col)) for col in columns0]
    census = hashlib.sha256()
    cases = profitable = 0
    gains = {}
    for a in range(len(sources)):
        for b in range(len(sources)):
            if a == b:
                continue
            for sign in (-1, 1):
                gain = column_costs0[b] - sum(price(y - sign * x) for x, y in zip(columns0[a], columns0[b])) - 8
                cases += 1
                profitable += gain > 0
                gains[a, b, sign] = gain
                census.update((json.dumps([a, b, sign, gain], separators=(",", ":")) + "\n").encode())
    used, total_gain = set(), 0
    E_pairs = [row[:] for row in D0]
    for a, b, sign, gain in recipe["disjoint_helper_comparator"]["pairs"]:
        _require(a not in used and b not in used and a != b, "helper pair collision")
        _require((a, b, sign) in gains and gain == gains[a, b, sign] and gain > 0,
                 "incorrect selected helper gain")
        used.update((a, b))
        total_gain += gain
        for row in E_pairs:
            row[b] -= sign * row[a]
    comparator_summary = {
        "cases": cases,
        "profitable": profitable,
        "selected_pairs": len(recipe["disjoint_helper_comparator"]["pairs"]),
        "census_sha256": census.hexdigest(),
        "gain": total_gain,
        "panel_price": cost(E_pairs) + 8 * (len(recipe["initial_target_forest"]) + len(recipe["disjoint_helper_comparator"]["pairs"])),
    }
    _require(comparator_summary == {k: v for k, v in recipe["disjoint_helper_comparator"].items() if k != "pairs"},
             "disjoint helper comparator mismatch")

    # 3. Verify one-pass helper forest minimum on D0 = T0 C
    _, h1_cost_no_t0, h1_edges = _verify_forest_optimality(
        [list(col) for col in columns0],
        [],  # dummy check below replaced by Prim check on D0^T
        price,
        "empty_check",
    ) if False else (None, None, None)
    # Compute Prim minimum on D0^T directly:
    cols_D0 = [list(col) for col in columns0]
    d_h1 = [sum(map(price, col)) for col in cols_D0]
    reached_h1 = set()
    prim_h1 = 0
    for _ in range(len(sources)):
        j = min((j for j in range(len(sources)) if j not in reached_h1), key=d_h1.__getitem__)
        reached_h1.add(j)
        prim_h1 += d_h1[j]
        for i in range(len(sources)):
            if i not in reached_h1:
                edge = 8 + min(sum(price(x - sign * y) for x, y in zip(cols_D0[i], cols_D0[j]))
                               for sign in (-1, 1))
                if edge < d_h1[i]:
                    d_h1[i] = edge
    _require(prim_h1 + 8 * len(recipe["initial_target_forest"])
             == recipe["one_pass_biforest_panel_price"]
             == recipe["one_pass_helper_search"]["panel_price"],
             "one-pass helper forest price mismatch")

    # 4. Verify fixed-point bi-forest (T5, H5):
    #    - T5 is minimum spanning forest on C H5^-1 (all 12,544 target edges)
    #    - H5 is minimum spanning forest on (T5 C)^T (all 46,656 helper edges)
    C_right = [row[:] for row in matrix]
    for child, ancestor, sign, _depth in recipe["helper_forest"]:
        for i in range(len(targets)):
            C_right[i][child] = matrix[i][child] - sign * matrix[i][ancestor]
    E_from_T, t5_cost, t5_edges = _verify_forest_optimality(
        C_right, recipe["target_forest"], price, "fixed_point_target_forest"
    )

    D_left = [row[:] for row in matrix]
    for child, ancestor, sign, _depth in recipe["target_forest"]:
        D_left[child] = [a - sign * b for a, b in zip(matrix[child], matrix[ancestor])]
    cols_E_from_H, h5_cost, h5_edges = _verify_forest_optimality(
        [list(col) for col in zip(*D_left)],
        recipe["helper_forest"],
        price,
        "fixed_point_helper_forest",
    )
    E_from_H = [list(row) for row in zip(*cols_E_from_H)]
    _require(E_from_T == E_from_H, "two-sided associativity (T C) H^-1 != T (C H^-1)")

    complete_price = cost(E_from_T) + 8 * (len(recipe["target_forest"]) + len(recipe["helper_forest"]))
    _require(complete_price == t5_cost + 8 * len(recipe["helper_forest"])
             == h5_cost + 8 * len(recipe["target_forest"])
             == recipe["two_sided_biforest_panel_price"],
             "complete panel price")
    residual_additions = sum(value != 0 for row in E_from_T for value in row)
    _require(residual_additions == recipe["residual_additions"], "residual addition count")
    digest = hashlib.sha256(json.dumps(E_from_T, separators=(",", ":")).encode()).hexdigest()
    _require(digest == recipe["residual_quarters_sha256"], "residual matrix digest")
    return {
        "baseline_panel_price": baseline_price,
        "target_only_panel_price": t0_cost,
        "disjoint_pair_panel_price": comparator_summary["panel_price"],
        "one_pass_biforest_panel_price": prim_h1 + 8 * len(recipe["initial_target_forest"]),
        "two_sided_biforest_panel_price": complete_price,
        "target_cycle_edges_checked": t5_edges,
        "helper_cycle_edges_checked": h5_edges,
        "residual_additions": residual_additions,
        "residual_quarters_sha256": digest,
    }
