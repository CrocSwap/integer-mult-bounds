"""Separate edge-by-edge oracle; no model imports. Same AI-assisted author.

Hanson Sun, with OpenAI Codex assistance. Apache-2.0.
"""
import heapq


def parity(reader, mask, d):
    return sum(((reader // (2 ** j)) % 2) * ((mask // (2 ** j)) % 2)
               for j in range(d)) % 2


def graph_edges(d, conditions, weights, output_prices, state):
    stage, bits = state
    for j in range(d):
        yield (stage, bits ^ (2 ** j)), weights[j]
    if stage < len(conditions):
        a, b = conditions[stage]
        defect = b ^ parity(a, bits, d)
        if not defect or output_prices is not None:
            yield (stage + 1, bits), defect * output_prices[stage] if defect else 0


def shortest(d, conditions, weights, output_prices=None):
    """Dijkstra over individual paid XOR edges and free/paid observation edges."""
    distances = {(0, 0): 0}
    heap = [(0, (0, 0))]
    while heap:
        price, state = heapq.heappop(heap)
        if distances[state] != price:
            continue
        for target, charge in graph_edges(d, conditions, weights, output_prices, state):
            trial = price + charge
            if target not in distances or trial < distances[target]:
                distances[target] = trial
                heapq.heappush(heap, (trial, target))
    goal = (len(conditions), 0)
    if goal not in distances:
        raise ValueError("unreachable observation endpoint")
    dual = [[distances.get((t, k)) for k in range(2 ** d)]
            for t in range(len(conditions) + 1)]
    return distances[goal], dual


def validate_dual(d, conditions, weights, output_prices, dual, expected):
    """Check a lower bound through local potential inequalities, without search."""
    if len(dual) != len(conditions) + 1 or any(len(row) != 2 ** d for row in dual):
        raise ValueError("invalid dual shape")
    if any(type(value) is not int for row in dual for value in row):
        raise ValueError("invalid dual values")
    if dual[0][0] != 0 or dual[-1][0] != expected:
        raise ValueError("dual endpoint mismatch")
    edges = 0
    for t, row in enumerate(dual):
        for k, value in enumerate(row):
            for (nt, nk), cost in graph_edges(d, conditions, weights, output_prices, (t, k)):
                if dual[nt][nk] > value + cost:
                    raise ValueError("invalid lower-bound edge")
                edges += 1
    return edges


def run_array(spec, word, initial, L=1, backwards=False, check_cuts=True):
    """Literal Boolean array interpreter, independent of packed symbolic rows."""
    d = spec["width"]
    a = [row[:] for row in initial]
    if len(a) != word["registers"] or any(len(row) != L for row in a):
        raise ValueError("array shape")
    cut_lookup = {n: i for i, n in enumerate(word["cuts"])}
    gates = list(reversed(word["gates"])) if backwards else word["gates"]
    observed = 0
    for pos, (target, source, _) in enumerate(gates, 1):
        for j in range(L):
            a[target][j] = (a[target][j] + a[source][j]) % 2
        if check_cuts and not backwards and pos in cut_lookup:
            t = cut_lookup[pos]
            expected = direct(spec, initial, L, upto=t + 1)
            visible = list(range(d + 1)) + list(range(2 * d + 1, 2 * d + 2 + t)) + [len(a) - 1]
            if any(a[i] != expected[i] for i in visible):
                raise ValueError("literal observation mismatch")
            observed += 1
    return a, observed


def direct(spec, initial, L=1, upto=None):
    """Evaluate the requested map by nested matrix sums, without any repair word."""
    d = spec["width"]
    a = [row[:] for row in initial]
    upto = len(spec["readers"]) if upto is None else upto
    for t in range(upto):
        row = spec["steps"][t]
        a[row] = [(x + y) % 2 for x, y in zip(a[row], a[d])]
        bx = [[sum(((spec["B"][j] // 2 ** k) % 2) * a[k][p] for k in range(d)) % 2
               for p in range(L)] for j in range(d)]
        out = 2 * d + 1 + t
        for p in range(L):
            a[out][p] = (a[out][p] + sum(((spec["readers"][t] // 2 ** j) % 2) * bx[j][p]
                                        for j in range(d))) % 2
    return a


def literal_invoice(word, L):
    moves = 0
    accesses = 0
    instructions = 0
    for target, source, _ in word["gates"]:
        for j in range(L):
            source_cell = source * L + j + 1
            target_cell = target * L + j + 1
            cursor = 0
            for cell in (source_cell, target_cell, 0):
                moves += abs(cursor - cell)
                cursor = cell
            accesses += 3  # two reads and one write
            instructions += 2  # XOR and dispatch
    return {"head_steps": moves, "online_tariff": moves + accesses + instructions}
