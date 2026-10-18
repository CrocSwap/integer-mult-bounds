"""Independent exact checks for the fixed frame-281 six-wire transfer.

Matrix replay evolves one input column at a time.  Shortest-path checking peels
FIRST positive ADDs by column subtraction, independently of discovery's peeling
of LAST ADDs by row subtraction.  No search.py imports; standard library only.

The class is all finite straight-line circuits on these six labelled registers,
starting at identity, using only elementary ``x[d] += x[s]`` with d != s, and
having exactly the supplied nonnegative INTEGER transfer. Repeated writes and
arbitrary gate order are allowed. There are no additional registers, subtractions,
free permutations, or multi-source gates. This is not a minimum over all F2
equivalent circuits, and it is not a lower bound on the multiplication exponent.

Breadth-first proof idea follows PR925's frame-267 optimality.py by Ross
Richardson, with substantial OpenAI Codex assistance; this verifier uses the
opposite end of a circuit (column rather than row subtraction).
Prepared for @woklerx with substantial OpenAI Codex assistance; Apache-2.0.
"""

from collections import deque


N = 6


class Reject(ValueError):
    """A finite check failed or its explicitly bounded resources were exhausted."""


def _gates(ops):
    if not isinstance(ops, (list, tuple)):
        raise Reject("gate sequence must be a list or tuple")
    for gate in ops:
        if not isinstance(gate, (list, tuple)) or len(gate) != 2:
            raise Reject("each elementary ADD requires [destination, source]")
        d, s = gate
        if type(d) is not int or type(s) is not int or not (0 <= d < N and 0 <= s < N) or d == s:
            raise Reject("invalid elementary ADD operands")
    return ops


def matrix(ops, positive=False):
    """Return exact integer or F2 matrix using independent basis-column replay."""
    _gates(ops)
    columns = []
    for col in range(N):
        state = [int(row == col) for row in range(N)]
        for d, s in ops:
            state[d] = state[d] + state[s] if positive else state[d] ^ state[s]
        columns.append(state)
    return [[columns[col][row] for col in range(N)] for row in range(N)]


def check_truth_table(left, right):
    """Exhaustively compare all 64 six-bit inputs, separately from matrix replay."""
    _gates(left)
    _gates(right)
    for input_word in range(1 << N):
        outputs = []
        for circuit in (left, right):
            values = [(input_word >> i) & 1 for i in range(N)]
            for d, s in circuit:
                values[d] = (values[d] + values[s]) % 2
            outputs.append(values)
        if outputs[0] != outputs[1]:
            raise Reject("Boolean transfer differs at input " + str(input_word))
    return {"boolean_inputs": 1 << N}


def circuit_check(original, replacement, exact_forward=True):
    """Check Boolean transfer and monotone forward/reverse integer envelopes."""
    truth = check_truth_table(original, replacement)
    if matrix(original) != matrix(replacement):
        raise Reject("F2 matrix changed")
    result = dict(truth)
    for name, old, new in (("forward", original, replacement),
                           ("reverse", original[::-1], replacement[::-1])):
        before, after = matrix(old, True), matrix(new, True)
        if any(y > x for row_before, row_after in zip(before, after)
               for x, y in zip(row_before, row_after)):
            raise Reject(name + " positive transfer increased")
        if name == "forward" and exact_forward and before != after:
            raise Reject("fixed integer transfer changed")
        result[name] = {"original": before, "replacement": after}
    return result


def check_minimum(transfer, claimed, max_states=1_000_000):
    """Prove exact minimum by complete BFS through depth ``claimed``.

    If M = E_last ... E_first, removing first ADD d += s right-multiplies
    by I-e[d,s], thus subtracting column d from column s. Every remaining
    positive circuit is >= I entrywise. Trying all 30 ordered pairs is
    therefore exhaustive. Conversely, a path to I reverses to a circuit.
    Each edge decreases the integer sum strictly, so the graph is finite.

    Resource exhaustion raises Reject and is NEVER reported as a lower bound.
    """
    if type(claimed) is not int or not 0 <= claimed <= 21:
        raise Reject("claimed distance must be an integer from 0 through 21")
    if type(max_states) is not int or max_states < 1:
        raise Reject("invalid state budget")
    if not isinstance(transfer, (list, tuple)) or len(transfer) != N or any(
            not isinstance(row, (list, tuple)) or len(row) != N for row in transfer):
        raise Reject("transfer must be a 6 by 6 matrix")
    if any(type(x) is not int or x < int(r == c)
           for r, row in enumerate(transfer) for c, x in enumerate(row)):
        raise Reject("positive transfer must be integral and entrywise >= identity")

    # Columns are contiguous here, unlike the row-major nomination matrix.
    target = tuple(transfer[r][c] for c in range(N) for r in range(N))
    identity = tuple(int(r == c) for c in range(N) for r in range(N))
    queue = deque([target])
    seen = {target}
    layers = []
    edges = 0
    for depth in range(claimed + 1):
        width = len(queue)
        layers.append(width)
        # Check the entire layer before expanding it. A minimum claim at this
        # depth needs all shallower layers, but no expansion of this layer.
        if identity in queue:
            if depth != claimed:
                raise Reject("claimed minimum exceeds independent distance " + str(depth))
            return {"minimum": depth, "method": "first-ADD column-subtraction BFS",
                    "layers": layers, "visited_states": len(seen),
                    "edges_from_completed_layers": edges,
                    "completed_expansion_depths": list(range(depth))}
        if depth == claimed:
            raise Reject("identity absent through claimed distance " + str(claimed))
        for _ in range(width):
            state = queue.popleft()
            for d in range(N):
                subtract = state[N*d:N*(d+1)]
                for s in range(N):
                    if s == d:
                        continue
                    offset = N*s
                    reduced = tuple(state[offset+r] - subtract[r] for r in range(N))
                    if any(value < int(r == s) for r, value in enumerate(reduced)):
                        continue
                    edges += 1
                    previous = state[:offset] + reduced + state[offset+N:]
                    if previous not in seen:
                        if len(seen) >= max_states:
                            raise Reject("independent state budget exceeded; proof incomplete")
                        seen.add(previous)
                        queue.append(previous)
    raise Reject("unreachable control flow")


def negative_controls(original, replacement, minimum):
    """Small circuit controls; resource-heavy minimum mutations stay optional."""
    controls = []

    def rejected(label, operation):
        try:
            operation()
        except Reject:
            controls.append(label)
            return
        raise Reject("negative control accepted: " + label)

    def fixed_check(candidate):
        check_truth_table(original, candidate)
        if matrix(original, True) != matrix(candidate, True):
            raise Reject("fixed forward integer transfer changed")

    rejected("dropped circuit ADD", lambda: fixed_check(replacement[1:]))
    flipped = [list(gate) for gate in replacement]
    flipped[0].reverse()
    rejected("reversed ADD operands", lambda: fixed_check(flipped))
    padded = list(replacement) + [[0, 1], [0, 1]]
    check_truth_table(replacement, padded)
    rejected("F2-neutral positive-transfer inflation", lambda: fixed_check(padded))
    # A small, fully exhausted graph checks both directions of the minimum
    # comparison without repeating the frame-sized BFS several times.
    unit = matrix([[0, 1]], True)
    rejected("minimum underclaim", lambda: check_minimum(unit, 0))
    rejected("minimum overclaim", lambda: check_minimum(unit, 2))
    rejected("budget exhaustion is not a proof", lambda: check_minimum(unit, 1, 1))
    rejected("reverse-guard minimum underclaim", lambda: check_reverse_guard_minimum([[0, 1]], 0))
    rejected("reverse-guard minimum overclaim", lambda: check_reverse_guard_minimum([[0, 1]], 2))
    rejected("reverse-guard budget exhaustion is not a proof",
             lambda: check_reverse_guard_minimum([[0, 1]], 1, 1))
    if type(minimum) is not int or minimum != len(replacement):
        raise Reject("witness length does not match claimed minimum")
    return controls


def check_reverse_guard_minimum(original, claimed, max_states=1_000_000):
    """Independent shortest circuit proof with the original reverse envelope.

    Peel first gates with column subtraction. In parallel, their reverse-word
    prefix is P = E_first E_second ... E_k, updated by right multiplication,
    i.e. column ADD. Every entry of P is nondecreasing, so a prefix above the
    original reverse matrix cannot complete to an admissible circuit. Enumerate
    all surviving (residual transfer, reverse prefix) pairs breadth first.
    Equal pairs reached later have identical possible continuations and may be
    discarded. This proves a minimum in the narrower two-envelope class.
    """
    if type(claimed) is not int or not 0 <= claimed <= 21:
        raise Reject("invalid reverse-guard claimed distance")
    if type(max_states) is not int or max_states < 1:
        raise Reject("invalid reverse-guard state budget")
    target_matrix = matrix(original, True)
    bound_matrix = matrix(original[::-1], True)
    target = tuple(target_matrix[r][c] for c in range(N) for r in range(N))
    bound = tuple(bound_matrix[r][c] for c in range(N) for r in range(N))
    identity = tuple(int(r == c) for c in range(N) for r in range(N))
    queue = deque([(target, identity)])
    seen = {(target, identity)}
    layers, edges, pruned = [], 0, 0
    for depth in range(claimed + 1):
        width = len(queue)
        layers.append(width)
        if any(residual == identity for residual, _ in queue):
            if depth != claimed:
                raise Reject("reverse-guard claim exceeds independent distance " + str(depth))
            return {"minimum": depth, "method": "first-ADD paired column-subtraction and column-addition BFS",
                    "layers": layers, "visited_states": len(seen),
                    "positive_residual_edges_from_completed_layers": edges,
                    "reverse_guard_pruned_edges": pruned,
                    "completed_expansion_depths": list(range(depth))}
        if depth == claimed:
            raise Reject("no reverse-guarded witness through claimed distance " + str(claimed))
        for _ in range(width):
            residual, prefix = queue.popleft()
            for d in range(N):
                subtract = residual[N*d:N*(d+1)]
                add = prefix[N*d:N*(d+1)]
                for s in range(N):
                    if s == d:
                        continue
                    offset = N*s
                    reduced = tuple(residual[offset+r] - subtract[r] for r in range(N))
                    if any(value < int(r == s) for r, value in enumerate(reduced)):
                        continue
                    edges += 1
                    grown = tuple(prefix[offset+r] + add[r] for r in range(N))
                    if any(value > bound[offset+r] for r, value in enumerate(grown)):
                        pruned += 1
                        continue
                    previous = residual[:offset] + reduced + residual[offset+N:]
                    accumulated = prefix[:offset] + grown + prefix[offset+N:]
                    pair = (previous, accumulated)
                    if pair not in seen:
                        if len(seen) >= max_states:
                            raise Reject("reverse-guard state budget exceeded; proof incomplete")
                        seen.add(pair)
                        queue.append(pair)
    raise Reject("unreachable reverse-guard control flow")


def verify(witness):
    """Return a serializable finite proof; reverse growth is explicitly reported.

    Forward equality establishes the fixed-transfer synthesis claim. Reverse
    domination is a sufficient precision condition, not an acceptance condition
    here: any increases must be priced by the full-word auditor before deployment.
    """
    original, replacement = witness["original"], witness["replacement"]
    truth = check_truth_table(original, replacement)
    before, after = matrix(original, True), matrix(replacement, True)
    target = witness.get("integer_target", witness.get("target_matrix", before))
    if before != after or before != target:
        raise Reject("claimed fixed forward integer transfer differs")
    minimum = witness.get("minimum", len(replacement))
    if type(minimum) is not int or len(replacement) != minimum:
        raise Reject("replacement length differs from claimed minimum")
    optimum = check_minimum(target, minimum)
    guarded_optimum = check_reverse_guard_minimum(original, len(original))
    reverse_before, reverse_after = matrix(original[::-1], True), matrix(replacement[::-1], True)
    increases = [{"row": r, "column": c, "original": reverse_before[r][c],
                  "replacement": reverse_after[r][c]}
                 for r in range(N) for c in range(N)
                 if reverse_after[r][c] > reverse_before[r][c]]
    return {**truth, "F2_matrix": matrix(replacement),
            "positive_matrices": {"forward": {"original": before, "replacement": after},
                                  "reverse": {"original": reverse_before, "replacement": reverse_after}},
            "reverse_entrywise_dominated": not increases,
            "reverse_increased_entries": increases,
            "independent_minimum": optimum,
            "independent_reverse_guard_minimum": guarded_optimum,
            "controls_rejected": negative_controls(original, replacement, minimum),
            "class": "six labelled registers; elementary positive ADD only; exact integer target; no ancillas",
            "precision_scope": "reverse increases require full-word prefix and native payload pricing"}
