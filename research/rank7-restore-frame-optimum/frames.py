# SPDX-License-Identifier: Apache-2.0
"""Exact frame accounting and finite restore-frame factorization.

The accounting contract follows Jeremy Kothe's retained preload_move.py.
This implementation uses explicit vector sets and imports no predecessor code.
"""

from collections import Counter, defaultdict
from itertools import product
from math import prod

Space = frozenset[int]
FULL = frozenset(range(512))
ZERO = frozenset({0})


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def space(vectors) -> Space:
    need(isinstance(vectors, (list, tuple)) and len(vectors) <= 9, "frame generators")
    result = ZERO
    for vector in vectors:
        need(type(vector) is int and 0 < vector < 512, "nine-bit frame vector")
        result = result | frozenset(x ^ vector for x in result)
    return result


def rank(frame: Space) -> int:
    need(0 < len(frame) <= 512 and len(frame) & (len(frame) - 1) == 0, "frame size")
    return len(frame).bit_length() - 1


def registers(gate) -> tuple[int, ...]:
    need(isinstance(gate, list) and len(gate) in (5, 6), "scalar gate shape")
    need(gate[0] in ("add", "scale"), "scalar gate operation")
    add = gate[0] == "add"
    need(len(gate) == 5 + add, "scalar gate arity")
    result = tuple(gate[1:3] if add else gate[1:2])
    need(all(type(r) is int and 0 <= r < 704 for r in result), "register range")
    need(len(set(result)) == len(result), "distinct ADD registers")
    numerator, denominator = gate[-3:-1]
    need(type(numerator) is int and type(denominator) is int
         and numerator != 0 and denominator != 0, "nonzero rational coefficient")
    return result


def climb(current, paid, register, target):
    previous = current[register]
    need(previous <= target, "nonmonotone frame")
    difference = rank(target) - rank(previous)
    if difference:
        paid[difference] += 1
    current[register] = target


def step(current, paid, gate):
    if gate[0] == "warp":
        need(len(gate) == 5 and type(gate[1]) is int
             and 0 <= gate[1] < 704, "A warp shape")
        need(current[gate[1]] == space(gate[3]), "A warp preimage")
        current[gate[1]] = space(gate[4])
        return
    target = space(gate[-1])
    for register in registers(gate):
        climb(current, paid, register, target)


def centre_charges(word, current, paid):
    need(len(word["centers"]) == len(word["center_frames"]) == 8, "eight centres")
    need(len(word["cut"]) <= 224, "centre cut bound")
    for register, vectors in zip(word["centers"], word["center_frames"], strict=True):
        previous = space(vectors)
        need(current[register] == previous, "centre entry frame")
        levels = {space(word["target_levels"].get(str(g[1] - 112), []))
                  for g in word["cut"] if g[2] == register}
        for target in sorted(levels, key=lambda f: (-rank(f), tuple(sorted(f)))):
            need(target <= previous, "centre descending chain")
            if target != previous:
                paid[rank(previous) - rank(target)] += 1
            previous = target


def boundaries(word):
    """Replay the fixed prefix, including centre charges and every fixed warp."""
    ports = word["ports"]
    need(len(ports) == 112 and len(set(ports)) == 112, "112 distinct ports")
    current = [space([p]) for p in ports] + [ZERO] * 592
    end = [FULL] * 112 + [frozenset(x for x in range(512)
        if (x & p).bit_count() % 2 == 0) for p in ports] + [FULL] * 480
    for register, vectors in word["start_extra"].items():
        need(0 <= int(register) < 704, "entrance register")
        current[int(register)] = space(vectors)
    start = current.copy()
    for register, vectors in word["helper_final"].items():
        need(224 <= int(register) < 704, "helper endpoint register")
        end[int(register)] = space(vectors)
    need(len(word["A"]) <= 5000 and len(word["B"]) <= 2500, "prefix size")
    paid = Counter()
    for gate in word["A"]:
        step(current, paid, gate)
    centre_charges(word, current, paid)
    warps = defaultdict(list)
    need(len(word["warps"]) <= 100, "fixed warp bound")
    for record in word["warps"]:
        need(len(record) == 5 and 0 <= record[0] <= len(word["B"]), "B warp address")
        warps[record[0]].append(record)
    for index in range(len(word["B"]) + 1):
        for _, register, _, before, after in warps[index]:
            need(current[register] == space(before), "B warp preimage")
            current[register] = space(after)
        if index < len(word["B"]):
            step(current, paid, word["B"][index])
    removed = set(word["removed"])
    need(len(removed) == 72 and all(224 <= r < 704 for r in removed), "removed helpers")
    live = set(range(704)) - removed
    widths = Counter(rank(end[r]) - rank(start[r]) for r in sorted(live) if r >= 224)
    return current, end, live, paid, widths


def problem(word):
    entry, end, live, paid, widths = boundaries(word)
    gates = word["restore"]
    need(len(gates) == 212, "212 restore gates")
    traces = defaultdict(list)
    current = entry.copy()
    for index, gate in enumerate(gates):
        target = space(gate[-1])
        for register in registers(gate):
            need(register in live, "restore uses a live register")
            traces[register].append((index, target))
            climb(current, paid, register, target)
    for register in sorted(live):
        climb(current, paid, register, end[register])
    for register, events in traces.items():
        traces[register] = [(-1, entry[register]), *events, (len(gates), end[register])]
    need(dict(paid) == {int(r): n for r, n in word["report"]["local_profile"].items()},
         "complete declared local profile")
    need(dict(widths) == {int(r): n for r, n in word["report"]["width_inventory"].items()},
         "declared helper widths")
    return traces, dict(sorted(paid.items())), dict(sorted(widths.items()))


def bounds(gates, traces):
    """Least forward joins and greatest backward meets bound every legal schedule."""
    need(1 <= len(gates) <= 212 and len(traces) <= 424, "restore problem bound")
    current = {r: events[0][1] for r, events in traces.items()}
    lower = []
    for gate in gates:
        operands = registers(gate)
        target = ZERO
        for register in operands:
            target = frozenset(a ^ b for a in target for b in current[register])
        lower.append(target)
        for register in operands:
            current[register] = target
    current = {r: events[-1][1] for r, events in traces.items()}
    upper = [ZERO] * len(gates)
    for index in reversed(range(len(gates))):
        operands = registers(gates[index])
        target = FULL
        for register in operands:
            target = target & current[register]
        upper[index] = target
        for register in operands:
            current[register] = target
    for low, high in zip(lower, upper, strict=True):
        need(low <= high and rank(high) - rank(low) <= 2, "frame interval bound")
    return lower, upper


def domain(lower: Space, upper: Space) -> tuple[Space, ...]:
    need(lower <= upper and 0 <= rank(upper) - rank(lower) <= 2, "domain quotient")
    choices = {lower}
    for _ in range(rank(upper) - rank(lower)):
        additions = {frame | frozenset(x ^ v for x in frame)
                     for frame in choices for v in upper - frame}
        choices |= additions
    need(len(choices) <= 5, "at most five interval subspaces")
    return tuple(sorted(choices, key=lambda f: (len(f), tuple(sorted(f)))))


def factors(gates, traces, lower, upper):
    variable = {i for i in range(len(gates)) if lower[i] != upper[i]}
    need(len(variable) <= 32, "at most 32 variable frames")
    graph = {i: set() for i in variable}
    edges = []
    for register, events in sorted(traces.items()):
        need(len(events) <= len(gates) + 2, "register trace bound")
        for (i, before), (j, after) in zip(events[:-1], events[1:], strict=True):
            edges.append((register, i, before, j, after))
            if i in variable and j in variable:
                graph[i].add(j)
                graph[j].add(i)
    seen = set()
    components = []
    for root in sorted(variable):
        if root in seen:
            continue
        pending = [root]
        component = {root}
        seen.add(root)
        for _ in range(len(variable)):
            if not pending:
                break
            for neighbour in sorted(graph[pending.pop()]):
                if neighbour not in seen:
                    component.add(neighbour)
                    seen.add(neighbour)
                    pending.append(neighbour)
        need(not pending, "bounded component traversal completed")
        components.append(tuple(sorted(component)))
    return components, edges


def edge_profile(edges, assignment):
    paid = Counter()
    need(len(edges) <= 848, "transition-edge bound")
    for _, i, before, j, after in edges:
        before, after = assignment.get(i, before), assignment.get(j, after)
        if not before <= after:
            return None
        difference = rank(after) - rank(before)
        if difference:
            paid[difference] += 1
    return paid


def enumerate_component(component, edges, lower, upper, gates):
    owned = [edge for edge in edges if edge[1] in component or edge[3] in component]
    choices = [domain(lower[i], upper[i]) for i in component]
    attempts = prod(map(len, choices))
    need(attempts <= 4096, "bounded component product")
    baseline = edge_profile(owned, {})
    need(baseline is not None, "legal source transitions")
    deltas = Counter()
    equal_changes = []
    for values in product(*choices):
        paid = edge_profile(owned, dict(zip(component, values, strict=True)))
        if paid is None:
            continue
        paid.subtract(baseline)
        delta = tuple((r, n) for r, n in sorted(paid.items()) if n)
        need(sum(r * n for r, n in delta) == 0, "unchanged telescoping rank mass")
        deltas[delta] += 1
        if not delta:
            changes = []
            for i, frame in zip(component, values, strict=True):
                if frame != space(gates[i][-1]):
                    endpoint = "lower" if frame == lower[i] else (
                        "upper" if frame == upper[i] else "interior")
                    changes.append({"gate": i, "operation": gates[i][0],
                                    "rank": rank(frame), "endpoint": endpoint})
            equal_changes.append(changes)
    need(deltas, "nonempty legal component")
    return {"gates": list(component), "domain_sizes": list(map(len, choices)),
            "attempts": attempts, "legal": sum(deltas.values()),
            "equal_profile_changes": equal_changes,
            "deltas": [{"profile": dict(delta), "count": count}
                       for delta, count in sorted(deltas.items())]}


def census(gates, traces):
    lower, upper = bounds(gates, traces)
    for index, gate in enumerate(gates):
        need(lower[index] <= space(gate[-1]) <= upper[index], "source in frame interval")
    components, edges = factors(gates, traces, lower, upper)
    rows = [enumerate_component(c, edges, lower, upper, gates) for c in components]
    return {"gates": len(gates), "forced": len(gates) - sum(map(len, components)),
            "variables": sum(map(len, components)), "edges": len(edges),
            "component_attempts": sum(row["attempts"] for row in rows),
            "global_legal": prod(row["legal"] for row in rows), "components": rows}
