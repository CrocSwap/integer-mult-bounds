"""Exact replay of an explicitly supplied, finite dyadic scalar circuit.

This checker does not import the candidate constructor or its lowering rules.
Every L, C and W register enters with its own independent dirt symbol. Sparse
integer rows with one power-of-two denominator implement the arithmetic; no
floating point or Fraction arithmetic is used here. Positive envelopes replay
the literal primitive sequence without using cancellation.

The result certifies the scalar projection of the supplied finite instruction
list. Recursive child identities, physical frames, global hosting and any
asymptotic multiplication bound remain separate inherited obligations.

Prepared for Ross with substantial OpenAI Codex assistance. Apache-2.0.
"""

from collections import Counter
import hashlib
import json


class ReplayError(ValueError):
    """A malformed circuit or an incorrect asserted endpoint."""


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


def replay(primitives, n=716, centers=8):
    """Return a JSON-serializable exact endpoint, cost and positive prefix.

    The vocabulary is clear(ref), copy(target, source), add(target, source,
    sign), double(ref), halve(ref), negate(ref), represented as JSON lists.
    Add's sign must be exactly +1 or -1. References are ["L", index],
    ["C", index], or the unique coefficient scratch ["W", 0].

    Basis symbols 0..n-1 are L inputs, n..n+centers-1 are C inputs and
    n+centers is the W input. Non-scalar events must be checked separately,
    never passed here. This function accepts an iterable so callers need not
    materialize a second copy of a long literal program.
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
            # Rows are immutable by convention: updates always allocate a row.
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
    """Check additive forward or inverse-transpose ports and erased private work.

    Forward: L[v+i] += L[i]. Backward: L[i] -= L[v+i]. All remaining
    logical columns are restored exactly, including every helper dirt input.
    This test uses explicit exceptions and remains active with Python -O.
    """
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


def check_recipe(word, recipe):
    """Independently price the finite recipe and repeat its helper census.

    Prim's algorithm checks the signed target-forest minimum, independently of
    the constructor's Kruskal implementation and tie ordering. Pricing counts
    literal binary digits and denominator halvings; it does not use bit_count
    or the constructor's price routine. The helper pairs are verified as a
    disjoint selection, without asserting their global optimality.
    """
    targets = sorted({event[1] for event in word["compensation"]})
    sources = sorted({event[2] for event in word["compensation"]})
    _require((len(targets), len(sources)) == (112, 254), "unexpected compensation shape")
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

    distances = [sum(map(price, row)) for row in matrix]
    reached, minimum = set(), 0
    for _ in targets:
        j = min((j for j in range(len(targets)) if j not in reached), key=distances.__getitem__)
        reached.add(j)
        minimum += distances[j]
        for i in range(len(targets)):
            if i not in reached:
                edge = 8 + min(sum(price(x - sign * y) for x, y in zip(matrix[i], matrix[j]))
                               for sign in (-1, 1))
                distances[i] = min(distances[i], edge)
    transformed = [row[:] for row in matrix]
    parent = {}
    for child, ancestor, sign, _depth in recipe["target_forest"]:
        _require(type(child) is int and type(ancestor) is int
                 and 0 <= child < len(targets) and 0 <= ancestor < len(targets)
                 and child != ancestor and child not in parent
                 and type(sign) is int and sign in (-1, 1), "invalid target-forest edge")
        parent[child] = ancestor
        transformed[child] = [x - sign * y for x, y in zip(transformed[child], transformed[ancestor])]
    for child in parent:
        visited = set()
        while child in parent:
            _require(child not in visited, "target forest has a cycle")
            visited.add(child)
            child = parent[child]
    forest_cost = cost(transformed) + 8 * len(parent)
    _require(forest_cost == minimum == recipe["forest_search"]["price"], "target forest is not minimum priced")
    columns = list(zip(*transformed))
    column_costs = [sum(map(price, col)) for col in columns]
    census = hashlib.sha256()
    cases = profitable = 0
    gains = {}
    for a in range(len(sources)):
        for b in range(len(sources)):
            if a == b:
                continue
            for sign in (-1, 1):
                gain = column_costs[b] - sum(price(y - sign * x) for x, y in zip(columns[a], columns[b])) - 8
                cases += 1
                profitable += gain > 0
                gains[a, b, sign] = gain
                census.update((json.dumps([a, b, sign, gain], separators=(",", ":")) + "\n").encode())
    used, total_gain = set(), 0
    for a, b, sign, gain in recipe["helper_pairs"]:
        _require(a not in used and b not in used and a != b, "helper pair collision")
        _require((a, b, sign) in gains and gain == gains[a, b, sign] and gain > 0, "incorrect selected helper gain")
        used.update((a, b))
        total_gain += gain
        for row in transformed:
            row[b] -= sign * row[a]
    helper_summary = {"cases": cases, "profitable": profitable,
                      "census_sha256": census.hexdigest(), "gain": total_gain}
    _require(helper_summary == recipe["helper_search"], "helper census mismatch")
    complete = cost(transformed) + 8 * (len(parent) + len(recipe["helper_pairs"]))
    _require(complete == minimum - total_gain == recipe["two_sided_panel_price"], "complete panel price mismatch")
    _require(cost(matrix) == recipe["baseline_panel_price"], "baseline panel price mismatch")
    return {"method": "Prim signed-forest minimum; exhaustive ordered signed helper-pair census",
            "baseline_panel_price": cost(matrix), "target_minimum": minimum,
            "helper_search": helper_summary, "complete_panel_price": complete}
