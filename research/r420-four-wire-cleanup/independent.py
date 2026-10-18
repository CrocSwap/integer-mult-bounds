"""Independent finite CNOT distances, window maps and interval scheduling.

Prepared for Jeffrey Cox (@namredips) with substantial OpenAI Codex assistance.
Apache-2.0. No producer imports: this implementation propagates output columns
and complete Boolean inputs rather than the producer's packed matrix rows.
"""

from bisect import bisect_right
from collections import Counter, deque
from functools import lru_cache
from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _gates(gates):
    normalized = []
    for gate in gates:
        require(len(gate) == 2, "CNOT must have exactly two operands")
        target, source = gate
        require(type(target) is int and type(source) is int
                and target >= 0 and source >= 0 and target != source,
                "CNOT operands must be distinct nonnegative registers")
        normalized.append((target, source))
    return normalized


def _step(columns, target, source):
    return tuple(value ^ (((value >> source) & 1) << target) for value in columns)


@lru_cache(maxsize=3)
def _invertible_columns(width):
    """Enumerate all binary matrices; recognize independent columns by span."""
    states = set()
    for columns in product(range(1 << width), repeat=width):
        span = {0}
        for column in columns:
            if column in span:
                break
            span |= {value ^ column for value in span}
        else:
            states.add(columns)
    return frozenset(states)


@lru_cache(maxsize=3)
def _column_distances(width):
    """Fresh unweighted BFS, with CNOT acting on each output column."""
    identity = tuple(1 << i for i in range(width))
    distances, pending = {identity: 0}, deque([identity])
    while pending:
        columns = pending.popleft()
        for target in range(width):
            for source in range(width):
                if target == source:
                    continue
                child = _step(columns, target, source)
                if child not in distances:
                    distances[child] = distances[columns] + 1
                    pending.append(child)
    require(set(distances) == _invertible_columns(width),
            "independent column BFS missed an invertible matrix")
    return distances


def verify_distances(tables: dict[int, dict[tuple[int, ...], int]]) -> dict:
    """Check row-tuple certificates by converting them to output columns.

    Edge Lipschitz inequalities give lower bounds on every CNOT path. A
    descending neighbor at every nonidentity state gives matching upper bounds.
    Completeness is checked against independent exhaustive matrix enumeration.
    """
    require(set(tables) == {2, 3, 4}, "distance certificate must cover widths 2, 3, 4")
    evidence = {}
    for width, rows_table in sorted(tables.items()):
        columns_table = {}
        for rows, distance in rows_table.items():
            require(len(rows) == width and all(type(row) is int and 0 <= row < 1 << width
                                               for row in rows),
                    "malformed distance matrix")
            require(type(distance) is int and distance >= 0, "invalid distance label")
            columns = tuple(sum(((rows[i] >> j) & 1) << i for i in range(width))
                            for j in range(width))
            columns_table[columns] = distance
        require(set(columns_table) == _invertible_columns(width),
                "distance state set differs from all invertible matrices")
        identity = tuple(1 << i for i in range(width))
        require(columns_table[identity] == 0, "identity distance must be zero")
        edges = 0
        for columns, distance in columns_table.items():
            require((distance == 0) == (columns == identity),
                    "nonidentity has zero distance")
            descent = columns == identity
            for target in range(width):
                for source in range(width):
                    if target == source:
                        continue
                    child_distance = columns_table[_step(columns, target, source)]
                    require(abs(distance - child_distance) <= 1,
                            "distance edge is not one-Lipschitz")
                    descent |= child_distance == distance - 1
                    edges += 1
            require(descent, "positive distance has no descending neighbor")
        evidence[str(width)] = {
            "states": len(columns_table), "directed_edges_checked": edges,
            "diameter": max(columns_table.values()),
            "layers": {str(d): count for d, count in sorted(Counter(columns_table.values()).items())},
        }
    return evidence


def _run_input(gates, registers, value):
    state = {register: (value >> i) & 1 for i, register in enumerate(registers)}
    for target, source in gates:
        state[target] ^= state[source]
    return sum(state[register] << i for i, register in enumerate(registers))


def _integer_column(gates, registers, basis):
    """Propagate one basis input using ordinary nonnegative integer addition."""
    state = {register: int(i == basis) for i, register in enumerate(registers)}
    for target, source in gates:
        state[target] += state[source]
    return tuple(state[register] for register in registers)


def verify_windows(original: list[tuple[int, int]], windows: list[dict]) -> dict:
    """Check maps, shortest costs and positive envelopes, with no extra registers."""
    original = _gates(original)
    previous_stop = inputs = old_count = new_count = 0
    positive_columns = 0
    for window in windows:
        start, stop = window["start"], window["stop"]
        require(type(start) is int and type(stop) is int
                and 0 <= start < stop <= len(original), "window interval is out of range")
        require(start >= previous_stop, "windows overlap or are out of order")
        previous_stop = stop
        old, new = _gates(window["old"]), _gates(window["new"])
        require(old == original[start:stop], "window old gates differ from original slice")
        registers = sorted({register for gate in old for register in gate})
        require(window["registers"] == registers and 2 <= len(registers) <= 4,
                "window register declaration is incorrect")
        require(all(register in registers for gate in new for register in gate),
                "replacement uses an outside register")
        require(window["saving"] == len(old) - len(new) > 0,
                "replacement saving is incorrect or not positive")
        columns = []
        for value in range(1 << len(registers)):
            expected = _run_input(old, registers, value)
            actual = _run_input(new, registers, value)
            require(actual == expected, "replacement truth table differs from original")
            if value and value & (value - 1) == 0:
                columns.append(expected)
            inputs += 1
        require(len(new) == _column_distances(len(registers))[tuple(columns)],
                "replacement is not shortest in the stated CNOT class")
        for old_order, new_order in ((old, new), (old[::-1], new[::-1])):
            for basis in range(len(registers)):
                before = _integer_column(old_order, registers, basis)
                after = _integer_column(new_order, registers, basis)
                require(all(a <= b for a, b in zip(after, before)),
                        "replacement increases a nonnegative transfer column")
                positive_columns += 1
        old_count += len(old)
        new_count += len(new)
    return {
        "windows_checked": len(windows), "boolean_inputs_checked": inputs,
        "selected_original_gates": old_count, "selected_replacement_gates": new_count,
        "saving": old_count - new_count, "all_replacements_shortest": True,
        "nonnegative_transfer_columns_checked": positive_columns,
        "entrywise_dominance_forward_and_reverse": True,
    }


def census(original: list[tuple[int, int]], max_wires: int = 4) -> dict:
    """Exhaust original contiguous windows and independently schedule their gains.

    Register-union size is monotone, so the first oversized interval ends a
    start-index scan. Weighted interval scheduling is by increasing finish time.
    This optimum concerns disjoint windows in the original word only.
    """
    require(type(max_wires) is int and 2 <= max_wires <= 4, "unsupported window width")
    original = _gates(original)
    tables = {width: _column_distances(width) for width in range(2, max_wires + 1)}
    counts, shortenable, longest, gaps = Counter(), Counter(), Counter(), Counter()
    candidates = []
    for start in range(len(original)):
        positions, columns = {}, []
        for stop in range(start, len(original)):
            target, source = original[stop]
            for register in (target, source):
                if register not in positions:
                    positions[register] = len(positions)
                    columns.append(1 << (len(positions) - 1))
            width = len(positions)
            if width > max_wires:
                break
            columns = list(_step(columns, positions[target], positions[source]))
            length = stop - start + 1
            distance = tables[width][tuple(columns)]
            require(distance <= length, "distance exceeds an existing window circuit")
            gap = length - distance
            counts[width] += 1
            longest[width] = max(longest[width], length)
            gaps[gap] += 1
            if gap:
                shortenable[width] += 1
                candidates.append((stop + 1, start, gap))
    candidates.sort()
    finishes = [stop for stop, _, _ in candidates]
    best = [0]
    for stop, start, gain in candidates:
        predecessor_count = bisect_right(finishes, start)
        require(predecessor_count < len(best), "interval predecessor is not earlier")
        best.append(max(best[-1], best[predecessor_count] + gain))
    return {
        "binary_gates": len(original), "windows_checked": sum(counts.values()),
        "shortenable_windows": len(candidates), "maximum_single_window_saving": max(gaps, default=0),
        "optimal_disjoint_original_window_saving": best[-1],
        "by_width": {str(width): {"windows": counts[width], "shortenable": shortenable[width],
                                  "maximum_length": longest[width]}
                     for width in range(2, max_wires + 1)},
        "saving_histogram": {str(gap): count for gap, count in sorted(gaps.items())},
        "scope": "All original contiguous windows with at most the stated wires; no extra registers, free permutations or iterative rewrites.",
    }
