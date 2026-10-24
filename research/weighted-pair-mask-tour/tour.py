"""Exact weighted borrowed-anchor pair tours. Produced by Nick Petalas; Apache-2.0."""
from fractions import Fraction
from itertools import combinations

MAX_SOURCES = 64
MAX_COPIES = 8


def require(condition, message):
    if not condition:
        raise ValueError(message)


def prices(values):
    require(isinstance(values, (list, tuple)), "prices must be a list or tuple")
    require(2 <= len(values) <= MAX_SOURCES, "source count must be in [2,64]")
    require(all(type(x) is int or type(x) is Fraction for x in values),
            "prices must be exact integers or Fractions, excluding booleans")
    require(all(x > 0 for x in values), "prices must be positive")
    return tuple(Fraction(x) for x in values)


def minimum_cost(values):
    weights = sorted(prices(values), reverse=True)
    return 2 * weights[0] + 2 * sum(
        i * weight for i, weight in enumerate(weights[1:], 1))


def pair_order(values):
    weights = prices(values)
    order = sorted(range(len(weights)), key=lambda i: (-weights[i], i))
    return tuple((order[i], order[j]) for i in range(len(order) - 1)
                 for j in range(len(order) - 1, i, -1))


def transitions(start, end, n):
    """Shortest mask path; each returned integer selects one toggle source."""
    return tuple(i for i in range(n) if ((start ^ end) >> i) & 1)


def tour_events(values):
    """Events are ('toggle', source index) or ('visit', two-bit mask)."""
    weights = prices(values)
    current = 0
    events = []
    for i, j in pair_order(weights):
        target = (1 << i) | (1 << j)
        events.extend(("toggle", k) for k in transitions(current, target, len(weights)))
        events.append(("visit", target))
        current = target
    events.extend(("toggle", k) for k in transitions(current, 0, len(weights)))
    return tuple(events)


def checked_tour_cost(values, events):
    """Validate a complete possibly nonminimal tour and return its literal bill."""
    weights = prices(values)
    require(isinstance(events, (list, tuple)) and len(events) <= 100_000,
            "events must be a bounded sequence")
    required = {(1 << i) | (1 << j) for i, j in combinations(range(len(weights)), 2)}
    visited = set()
    current = 0
    cost = Fraction(0)
    for event in events:
        require(isinstance(event, tuple) and len(event) == 2, "bad event")
        kind, value = event
        require(type(value) is int, "event value must be an integer")
        if kind == "toggle":
            require(0 <= value < len(weights), "unknown toggle source")
            current ^= 1 << value
            cost += weights[value]
        else:
            require(kind == "visit" and value == current and value in required,
                    "visit is not its required current pair mask")
            visited.add(value)
    require(current == 0, "anchor not restored")
    require(visited == required, "missing pair mask")
    return cost


def circuit(values, copies=2):
    """A is row 0, B_i is row i+1; targets follow in lexicographic pair order."""
    weights = prices(values)
    require(type(copies) is int and 1 <= copies <= MAX_COPIES,
            "copies must be an integer in [1,8]")
    pairs = tuple(combinations(range(len(weights)), 2))
    targets = {(1 << i) | (1 << j): tuple(
        len(weights) + 1 + p * copies + k for k in range(copies))
        for p, (i, j) in enumerate(pairs)}
    gates = []
    for kind, value in tour_events(weights):
        if kind == "toggle":
            gates.append((0, value + 1))
        else:
            gates.extend((target, 0) for target in targets[value])
    return tuple(gates), len(weights) + 1 + copies * len(pairs)


def execute(gates, rows):
    """Literal XOR execution on arbitrary-width dirty row values."""
    require(isinstance(rows, (list, tuple)) and 1 <= len(rows) <= 17_000,
            "bad row bank")
    require(all(type(x) is int and x >= 0 for x in rows), "rows must be unsigned integers")
    require(isinstance(gates, (list, tuple)) and len(gates) <= 100_000, "bad gate count")
    state = list(rows)
    for gate in gates:
        require(isinstance(gate, tuple) and len(gate) == 2, "bad gate")
        dst, src = gate
        require(type(dst) is int and type(src) is int and dst != src
                and 0 <= dst < len(state) and 0 <= src < len(state), "bad row reference")
        state[dst] ^= state[src]
    return tuple(state)
