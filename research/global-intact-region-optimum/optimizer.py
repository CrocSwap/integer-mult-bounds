"""Exact all-exponent minimization of a bounded binary chart problem.

Krzysztof Wojt, with substantial OpenAI Codex assistance. Apache-2.0.
The source graph/model is due to Cinna Davis and the credited PR4971 lineage.
No floating-point comparison is used.
"""
from collections import Counter
from functools import lru_cache
from itertools import product
from math import gcd


def require(condition, message):
    if not condition:
        raise ValueError(message)


def span(vectors):
    elements = {0}
    for vector in vectors:
        elements |= {element ^ vector for element in tuple(elements)}
    return sum(1 << element for element in elements)


@lru_cache(None)
def basis(space):
    require(isinstance(space, int) and space > 0 and space & 1, "Subspace contains zero")
    generated, result = {0}, []
    for vector in range(1, space.bit_length()):
        if space >> vector & 1 and vector not in generated:
            result.append(vector)
            generated |= {element ^ vector for element in tuple(generated)}
    require(sum(1 << element for element in generated) == space, "Closed binary subspace")
    return tuple(result)


def dim(space):
    return len(basis(space))


def apply(vector, matrix):
    result = 0
    for index, column in enumerate(matrix):
        if vector >> index & 1:
            result ^= column
    return result


@lru_cache(None)
def image(space, matrix):
    return span(apply(vector, matrix) for vector in basis(space))


@lru_cache(None)
def inverse(matrix):
    size = 1 << len(matrix)
    require(all(type(column) is int and 0 <= column < size for column in matrix), "Matrix column domain")
    lookup = {apply(vector, matrix): vector for vector in range(size)}
    require(len(lookup) == size, "Invertible edge map")
    return tuple(lookup[1 << index] for index in range(len(matrix)))


@lru_cache(None)
def join(left, right):
    return span(basis(left) + basis(right))


def validate(labels, fixed, edges, ambient):
    require(type(ambient) is int and 1 <= ambient <= 9, "Declared ambient dimension")
    require(set(fixed) <= set(labels), "Known fixed vertices")
    full = (1 << (1 << ambient)) - 1
    for space in labels.values():
        require(space & full == space, "Subspace ambient domain")
        basis(space)
    balance = Counter()
    for source, target, matrix in edges:
        require(source in labels and target in labels, "Known edge endpoints")
        require(len(matrix) == ambient, "Map ambient dimension")
        inverse(matrix)
        transported = image(labels[source], matrix)
        require(transported & labels[target] == transported, "Source edge containment")
        balance[source] -= 1
        balance[target] += 1
    require(all(balance[node] == 0 for node in labels if node not in fixed), "Balanced free vertices")


def close_bounds(labels, fixed, edges, ambient):
    """Every feasible chart lies between the returned necessary bounds."""
    full = (1 << (1 << ambient)) - 1
    lower = {node: labels[node] if node in fixed else 1 for node in labels}
    upper = {node: labels[node] if node in fixed else full for node in labels}
    for iteration in range(1, 2 * ambient * len(labels) + 2):
        changed = False
        for source, target, matrix in edges:
            new_lower = join(lower[target], image(lower[source], matrix))
            new_upper = upper[source] & image(upper[target], inverse(matrix))
            require(target not in fixed or new_lower == labels[target], "Fixed lower boundary")
            require(source not in fixed or new_upper == labels[source], "Fixed upper boundary")
            if new_lower != lower[target]:
                lower[target] = new_lower
                changed = True
            if new_upper != upper[source]:
                upper[source] = new_upper
                changed = True
        for node in labels:
            require(lower[node] & labels[node] == lower[node] and labels[node] & upper[node] == labels[node],
                    "Original feasible chart remains in bounds")
        if not changed:
            return lower, upper, iteration
    raise ValueError("Finite-height propagation did not terminate")


def histogram(labels, edges, ambient):
    counts = [0] * (ambient + 1)
    for source, target, matrix in edges:
        transported = image(labels[source], matrix)
        require(transported & labels[target] == transported, "Assignment edge containment")
        rank = dim(labels[target]) - dim(labels[source])
        require(0 <= rank <= ambient, "Charged rank domain")
        counts[rank] += 1
    return tuple(counts)


def plus(left, right):
    require(len(left) == len(right), "Histogram dimensions")
    return tuple(a + b for a, b in zip(left, right))


# Normalized NEW minus OLD histograms, including the zero-rank coefficient.
# Their positive all-exponent proofs are in PROOF.md. The first three are
# credited to PR4997; the last two close the global elimination comparisons.
POWER_CERTIFICATES = {
    (0, -1, 3, -3, 1): "third_difference",
    (-1, 3, -2, -1, 1): "four_three_two",
    (-4, 12, -9, 1, -3, 3): "five_four_three_two",
    (-1, 3, -2, -2, 3, -1): "four_three_two_plus_concavity",
    (-4, 7, -3, 5, -9, 4): "decreasing_curvature",
}


def certify(old, new):
    """Certify price(old) <= price(new) for every 0<t<1, or return None."""
    require(len(old) == len(new) and all(type(x) is int and x >= 0 for x in old + new), "Nonnegative histograms")
    require(sum(old) == sum(new), "Same owned edge count")
    require(sum(rank * (b - a) for rank, (a, b) in enumerate(zip(old, new))) == 0,
            "Same rank mass at a fixed separator")
    if old == new:
        return "equal"
    # Integer hinge points suffice: every rank is an integer and the hinge
    # sums are piecewise linear between those points. Equal sums/counts plus
    # these inequalities are the standard majorization criterion.
    if all(sum(max(rank - threshold, 0) * (a - b)
               for rank, (a, b) in enumerate(zip(old, new))) >= 0
           for threshold in range(len(old))):
        return "majorization"
    difference = tuple(b - a for a, b in zip(old, new))
    divisor = 0
    for coefficient in difference:
        divisor = gcd(divisor, abs(coefficient))
    normalized = tuple(coefficient // divisor for coefficient in difference)
    while normalized and normalized[-1] == 0:
        normalized = normalized[:-1]
    return POWER_CERTIFICATES.get(normalized)


def _components(variables, edges):
    adjacency = {node: set() for node in variables}
    for source, target, _ in edges:
        if source != target and source in variables and target in variables:
            adjacency[source].add(target)
            adjacency[target].add(source)
    unseen, counts = set(variables), Counter()
    while unseen:
        pending, found = [min(unseen)], set()
        while pending:
            node = pending.pop()
            if node not in found:
                found.add(node)
                pending.extend(adjacency[node] - found)
        unseen -= found
        counts[len(found)] += 1
    return counts


def solve(labels, fixed, edges, ambient=9):
    """Exact elimination. Refuse wider chart intervals or uncertified costs.

    No model assumption turns an unknown comparison into a tie. Histograms
    retain zero edges, and each factor owns disjoint original edge IDs.
    """
    edges = [(u, v, tuple(matrix)) for u, v, matrix in edges]
    fixed = set(fixed)
    validate(labels, fixed, edges, ambient)
    lower, upper, iterations = close_bounds(labels, fixed, edges, ambient)
    gaps = {node: dim(upper[node]) - dim(lower[node]) for node in labels}
    require(all(gap in (0, 1) for gap in gaps.values()), "Residual interval is not binary")
    variables = {node for node, gap in gaps.items() if gap == 1}
    require(not variables & fixed, "No fixed binary variable")
    initial_variables = set(variables)
    zero = (0,) * (ambient + 1)
    grouped = {}
    for edge_id, (source, target, matrix) in enumerate(edges):
        scope = tuple(sorted({source, target} & variables))
        if scope not in grouped:
            grouped[scope] = ({bits: zero for bits in product((0, 1), repeat=len(scope))}, set())
        table, owned = grouped[scope]
        owned.add(edge_id)
        for bits, old in list(table.items()):
            if old is None:
                continue
            assignment = dict(zip(scope, bits))
            before = (upper if assignment.get(source, 0) else lower)[source]
            after = (upper if assignment.get(target, 0) else lower)[target]
            transported = image(before, matrix)
            if transported & after != transported:
                table[bits] = None
                continue
            rank = dim(after) - dim(before)
            require(0 <= rank <= ambient, "Initial factor rank")
            table[bits] = plus(old, tuple(int(index == rank) for index in range(ambient + 1)))
    factors = [(scope, table, owned) for scope, (table, owned) in grouped.items()]
    comparisons, trace = Counter(), []
    maximum_separator = 0
    while variables:
        neighbors = {node: set() for node in variables}
        for scope, _, _ in factors:
            for node in scope:
                neighbors[node].update(set(scope) - {node})
        node = min(variables, key=lambda candidate: (len(neighbors[candidate]), candidate))
        variables.remove(node)
        separator = tuple(sorted(neighbors[node]))
        maximum_separator = max(maximum_separator, len(separator))
        require(len(separator) <= 8, "Declared bounded separator budget")
        bucket = [factor for factor in factors if node in factor[0]]
        factors = [factor for factor in factors if node not in factor[0]]
        owned = set()
        for _, _, edge_ids in bucket:
            require(not owned & edge_ids, "Disjoint factor edge ownership")
            owned |= edge_ids
        table, states = {}, []
        for bits in product((0, 1), repeat=len(separator)):
            assignment, candidates = dict(zip(separator, bits)), []
            for choice in (0, 1):
                assignment[node] = choice
                total = zero
                for scope, entry_table, _ in bucket:
                    entry = entry_table[tuple(assignment[vertex] for vertex in scope)]
                    if entry is None:
                        total = None
                        break
                    total = plus(total, entry)
                if total is not None:
                    require(sum(total) == len(owned), "Factor accounts for every owned edge")
                candidates.append(total)
            if candidates == [None, None]:
                choice, certificate = None, "infeasible"
            elif candidates[0] is None:
                choice, certificate = 1, "forced"
            elif candidates[1] is None:
                choice, certificate = 0, "forced"
            else:
                certificate = certify(candidates[0], candidates[1])
                if certificate is not None:
                    choice = 0
                else:
                    certificate = certify(candidates[1], candidates[0])
                    require(certificate is not None, "Uncertified all-exponent comparison: " + str(candidates))
                    choice = 1
            comparisons[certificate] += 1
            table[bits] = None if choice is None else candidates[choice]
            states.append({"bits": list(bits), "candidates": candidates,
                           "choice": choice, "certificate": certificate})
        trace.append({"node": node, "separator": list(separator),
                      "owned_edges": len(owned), "states": states})
        factors.append((separator, table, owned))
    total, owned = zero, set()
    for scope, table, edge_ids in factors:
        require(not scope and table[()] is not None, "Feasible terminal factor")
        require(not owned & edge_ids, "Disjoint terminal ownership")
        owned |= edge_ids
        total = plus(total, table[()])
    require(owned == set(range(len(edges))), "Every original edge owned exactly once")
    choices = {}
    for step in reversed(trace):
        bits = [choices[node] for node in step["separator"]]
        matches = [state for state in step["states"] if state["bits"] == bits]
        require(len(matches) == 1 and matches[0]["choice"] is not None, "Feasible back substitution")
        choices[step["node"]] = matches[0]["choice"]
    assignment = {node: (upper[node] if choices.get(node, 0) else lower[node]) for node in labels}
    require(histogram(assignment, edges, ambient) == total, "Reconstructed minimizing assignment")
    require(all(assignment[node] == labels[node] for node in fixed), "Restored fixed charts")
    return {
        "histogram": list(total), "assignment": assignment,
        "bounds": {node: [lower[node], upper[node]] for node in labels},
        "stats": {
            "vertices": len(labels), "edges": len(edges), "fixed_regions": len(fixed),
            "free_regions": len(labels) - len(fixed), "binary_regions": len(initial_variables),
            "forced_free_regions": len(labels) - len(fixed) - len(initial_variables),
            "closure_iterations": iterations,
            "variable_components": dict(sorted(_components(initial_variables, edges).items())),
            "maximum_separator": maximum_separator,
            "elimination_steps": len(trace), "comparisons": dict(sorted(comparisons.items())),
        },
        "trace": trace,
    }
