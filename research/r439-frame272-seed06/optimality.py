"""Independent exact minimum for a six-register positive ADD transfer.

Flat-matrix method adapted from research/r439-frame267-seed01/optimality.py,
authored by Ross Richardson with substantial OpenAI Codex assistance (PR925),
Apache-2.0. Current frame-272 adaptation: @woklerx with substantial OpenAI
Codex assistance. It applies backward breadth-first enumeration with stricter
input validation and a hard state budget. The augmented reverse-prefix BFS
is new. Neither checker imports search.py or uses the searcher's recurrence,
gate nominations, or stored distances.

Only gates r[d] += r[s], d != s, on these same six labelled registers are in
scope. Every forward intermediate matrix is entrywise at least the identity.
Removing a possible last gate therefore subtracts one whole row and retains
only matrices entrywise at least the identity. Every valid circuit reverses
to such a path, and every path to identity reverses to a valid circuit. Each
edge decreases the entry sum, so the graph is finite. Breadth-first distance
to identity proves the minimum without a single-write restriction. The claim
does not extend to XOR circuits with another positive transfer or extra wires.
"""


def check_minimum(matrix, claimed, *, max_states=1_000_000):
    """Return a completed BFS receipt, or reject an incorrect/unproved claim.

    Budget exhaustion raises ValueError; it can never certify a minimum.
    The 23-gate ceiling is the selected frame-272 baseline length.
    """
    if type(claimed) is not int or not 0 <= claimed <= 23:
        raise ValueError("invalid claimed distance")
    if type(max_states) is not int or not 1 <= max_states <= 1_000_000:
        raise ValueError("invalid state budget")
    if not isinstance(matrix, (list, tuple)) or len(matrix) != 6:
        raise ValueError("matrix shape")
    if any(not isinstance(row, (list, tuple)) or len(row) != 6 for row in matrix):
        raise ValueError("matrix shape")
    if any(type(x) is not int or not 0 <= x <= 255 for row in matrix for x in row):
        raise ValueError("matrix entries")
    if any(matrix[i][i] < 1 for i in range(6)):
        raise ValueError("matrix is not entrywise at least identity")
    target = bytes(x for row in matrix for x in row)
    identity = bytes(int(i == j) for i in range(6) for j in range(6))
    frontier, seen, layers = {target}, {target}, [1]
    edges = 0
    for depth in range(claimed + 1):
        if identity in frontier:
            if depth != claimed:
                raise ValueError("claimed minimum exceeds independent distance")
            return {
                "minimum": depth,
                "layers": layers,
                "visited_states": len(seen),
                "edges_from_completed_layers": edges,
                "completed_expansion_depths": list(range(depth)),
            }
        if depth == claimed:
            raise ValueError("claimed minimum is below independent distance")
        following = set()
        for state in frontier:
            for destination in range(0, 36, 6):
                for source in range(0, 36, 6):
                    if destination == source:
                        continue
                    reduced = []
                    for column in range(6):
                        entry = state[destination + column] - state[source + column]
                        if entry < int(column == destination // 6):
                            break
                        reduced.append(entry)
                    if len(reduced) != 6:
                        continue
                    edges += 1
                    previous = state[:destination] + bytes(reduced) + state[destination + 6:]
                    if previous not in seen:
                        if len(seen) == max_states:
                            raise ValueError("independent state budget exceeded; no minimum certified")
                        seen.add(previous)
                        following.add(previous)
        frontier = following
        layers.append(len(frontier))
        if not frontier:
            raise ValueError("target has no positive ADD factorization")
    raise ValueError("unreachable")


def check_reverse_guard_exclusion(matrix, reverse_cap, through=11, *, max_states=1_000_000):
    """Prove no factorization of length at most ``through`` meets the cap.

    A state stores both the remaining transfer and the accumulated positive
    reverse prefix, as 72 bytes. Removing a last forward gate also appends the
    first available reverse gate. The reverse prefix can only grow entrywise,
    so any entry above reverse_cap makes every completion impossible. Apart
    from this necessary condition, all legal last gates are enumerated. This
    checker uses no distances, nominations, or recurrence from search.py.

    Reaching identity is a counterexample and raises ValueError. Exhausting
    the budget also raises ValueError and is never reported as exclusion.
    """
    if type(through) is not int or not 0 <= through <= 23:
        raise ValueError("invalid exclusion depth")
    if type(max_states) is not int or not 1 <= max_states <= 1_000_000:
        raise ValueError("invalid state budget")
    for value in (matrix, reverse_cap):
        if not isinstance(value, (list, tuple)) or len(value) != 6:
            raise ValueError("matrix shape")
        if any(not isinstance(row, (list, tuple)) or len(row) != 6 for row in value):
            raise ValueError("matrix shape")
        if any(type(x) is not int or not 0 <= x <= 255 for row in value for x in row):
            raise ValueError("matrix entries")
        if any(value[i][i] < 1 for i in range(6)):
            raise ValueError("matrix is not entrywise at least identity")
    target = bytes(x for row in matrix for x in row)
    cap = bytes(x for row in reverse_cap for x in row)
    identity = bytes(int(i == j) for i in range(6) for j in range(6))
    start = target + identity
    frontier, seen, layers = {start}, {start}, [1]
    subtraction_edges = guard_prunes = 0
    completed = []
    for depth in range(through + 1):
        if any(state[:36] == identity for state in frontier):
            raise ValueError("reverse-compatible factorization exists at depth " + str(depth))
        if depth == through or not frontier:
            return {
                "excluded_gate_counts": list(range(through + 1)),
                "layers": layers,
                "visited_states": len(seen),
                "valid_subtraction_edges": subtraction_edges,
                "guard_pruned_edges": guard_prunes,
                "completed_expansion_depths": completed,
            }
        following = set()
        for state in frontier:
            remaining, reverse = state[:36], state[36:]
            for destination in range(0, 36, 6):
                for source in range(0, 36, 6):
                    if destination == source:
                        continue
                    reduced = []
                    for column in range(6):
                        entry = remaining[destination + column] - remaining[source + column]
                        if entry < int(column == destination // 6):
                            break
                        reduced.append(entry)
                    if len(reduced) != 6:
                        continue
                    subtraction_edges += 1
                    extended = [reverse[destination + col] + reverse[source + col]
                                for col in range(6)]
                    if any(entry > cap[destination + col] for col, entry in enumerate(extended)):
                        guard_prunes += 1
                        continue
                    next_remaining = remaining[:destination] + bytes(reduced) + remaining[destination + 6:]
                    next_reverse = reverse[:destination] + bytes(extended) + reverse[destination + 6:]
                    previous = next_remaining + next_reverse
                    if previous not in seen:
                        if len(seen) == max_states:
                            raise ValueError("independent state budget exceeded; no exclusion certified")
                        seen.add(previous)
                        following.add(previous)
        completed.append(depth)
        frontier = following
        layers.append(len(frontier))
    raise ValueError("unreachable")
