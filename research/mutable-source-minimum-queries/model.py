"""Exact construction of the minimum-query slice. Arham Tahir / Codex, Apache-2.0."""
from collections import Counter


def need(ok, message):
    if not ok:
        raise ValueError(message)


def slots(n, mask):
    # q_t=2^t-1. The nonzero q_t form a triangular basis.
    coefficients = [mask & 1]
    coefficients += [((mask >> (t - 1)) ^ (mask >> t)) & 1 for t in range(1, n + 1)]
    return [t for t, c in enumerate(coefficients) if c]


def minimum_word(n):
    need(type(n) is int and 1 <= n <= 9, "fixture dimension outside 1..9")
    reads = {m: slots(n, m) for m in range(1, 1 << n)}
    word = []
    for t in range(n + 1):
        word += [["R", m] for m, positions in reads.items() if t in positions]
        if t < n:
            word.append(["Q", t])
    # The first n queries add all original sources. Compute their sum at x0,
    # query it once to restore z, then restore x0. Every XOR is paid.
    word += [["X", j, 0] for j in range(1, n)]
    word.append(["Q", 0])
    word += [["X", j, 0] for j in reversed(range(1, n))]
    return word


def path_word(points):
    """Lower an attributed closed prefix path by restored source shears."""
    need(points[0] == points[-1] == 0, "path is not closed")
    readouts = {}
    for m in range(1, 32):
        pair = next(((s, t) for s in range(len(points)) for t in range(s + 1, len(points))
                     if points[s] ^ points[t] == m), None)
        need(pair is not None, "path does not cover all masks")
        readouts[m] = pair
    word = []
    for s, point in enumerate(points):
        word += [["R", m] for m, pair in readouts.items() if s in pair]
        if s + 1 < len(points):
            delta = point ^ points[s + 1]
            need(delta != 0, "zero query edge")
            target = (delta & -delta).bit_length() - 1
            donors = [j for j in range(5) if j != target and delta >> j & 1]
            word += [["X", j, target] for j in donors]
            word.append(["Q", target])
            word += [["X", j, target] for j in reversed(donors)]
    return word


def root_ops(word, n):
    out = []
    for event in word:
        need(type(event) is list and event, "invalid event")
        kind = event[0]
        if kind == "Q":
            need(len(event) == 2 and type(event[1]) is int and 0 <= event[1] < n, "invalid Q")
            out.append(["B", f"x{event[1]}", "z"])
        elif kind == "R":
            need(len(event) == 2 and type(event[1]) is int and 0 < event[1] < (1 << n), "invalid R")
            out.append([f"A{event[1]}", "z", f"y{event[1]}"])
        elif kind == "X":
            need(len(event) == 3 and all(type(i) is int and 0 <= i < n for i in event[1:])
                 and event[1] != event[2], "invalid source XOR")
            out.append(["", f"x{event[1]}", f"x{event[2]}"])
        else:
            raise ValueError("unknown root operation")
    return out


def roles(n, private=True):
    return [f"x{j}" for j in range(n)] + [f"y{m}" for m in range(1, 1 << n)] + ["z"] + (
        [f"w{j}" for j in range(3)] if private else [])


def interpret(operations, names, initial=None):
    state = {r: {(r,)} for r in names} if initial is None else {r: set(p) for r, p in initial.items()}
    for coefficient, source, target in operations:
        need(source in state and target in state and source != target, "invalid or aliased port")
        terms = state[source] if coefficient == "" else {(coefficient,) + term for term in state[source]}
        state[target].symmetric_difference_update(terms)
    return state


def expected(n, expanded=False):
    state = {r: {(r,)} for r in roles(n)}
    for m in range(1, 1 << n):
        for j in range(n):
            if m >> j & 1:
                coefficients = (f"A{m}",) + (tuple(f"B{k}" for k in reversed(range(5))) if expanded else ("B",))
                state[f"y{m}"].symmetric_difference_update({coefficients + (f"x{j}",)})
    return state


def check_identity(word, n):
    ops = root_ops(word, n)
    target = expected(n)
    result = interpret(ops, roles(n))
    need(result == target, "dirty root map or restoration failed")
    need(interpret(ops[::-1], roles(n), result) == {r: {(r,)} for r in roles(n)}, "root inverse failed")
    return Counter(event[0] for event in word)


def echo(factors, source, target, depth=0):
    if len(factors) == 1:
        return [[factors[0], source, target]], 0
    need(depth < 3, "fixture private scratch overflow")
    mid = len(factors) // 2
    scratch = f"w{depth}"
    right, nr = echo(factors[:mid], source, scratch, depth + 1)
    left, nl = echo(factors[mid:], scratch, target, depth + 1)
    return right + left + right[::-1] + left[::-1], 1 + 2 * nr + 2 * nl


def lower(word):
    operations, nodes = [], 0
    for coefficient, source, target in root_ops(word, 5):
        if coefficient == "B":
            child, count = echo([f"B{k}" for k in range(5)], source, target)
            operations += child
            nodes += count
        else:
            operations.append([coefficient, source, target])
    return operations, nodes


def invoice(word):
    counts = Counter(e[0] for e in word)
    leaves = 28 * counts["Q"] + counts["R"]
    nodes = 9 * counts["Q"]
    dispatch = len(word)
    return {"Q": counts["Q"], "R": counts["R"], "X": counts["X"],
            "map_leaves": leaves, "echo_nodes": nodes, "root_dispatches": dispatch,
            "borrowed_dirty_rows": 4,
            "tariff": leaves + nodes + counts["X"] + dispatch}


def build(old):
    words = {"minimum_queries": minimum_word(5),
             "four_X_ten_Q": path_word([0, 4, 5, 1, 3, 7, 6, 14, 28, 16, 0])}
    for name in ("five_extra_source", "five_extra_output"):
        words[name] = [["Q" if kind == "B" else "R", j if kind == "B" else j + 1]
                       for kind, j in old["schedules"][name]["word"]]
    schedules = {}
    for name, word in words.items():
        expanded, nodes = lower(word)
        need(nodes == invoice(word)["echo_nodes"], "node recurrence mismatch")
        schedules[name] = {"word": word, "leaf_word": expanded, "invoice": invoice(word)}
    return {"schema_version": 1, "n": 5,
            "scope": "minimum Q and minimum R at that Q; X count attained, not optimized",
            "readout_slots": {str(m): slots(5, m) for m in range(1, 32)},
            "prefixes": [(1 << t) - 1 for t in range(6)] + [0],
            "complete_tariff": {"Q": 38, "R": 2, "X": 2},
            "schedules": schedules}
