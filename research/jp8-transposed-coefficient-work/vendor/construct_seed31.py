"""Finite positive one-read routes for fixed-order JP8 cleanup.

Ryan Haines, with substantial OpenAI Codex assistance. Apache-2.0.
Original binary-Horner contract: attributed #626/#622 emitter.
Power-of-two comparator: Jeffrey Cox (@namredips), PR #739; no code imported.
"""

from fractions import Fraction as Q
from functools import lru_cache

WORK = 724
LIMIT = 16


def require(condition, message):
    if not condition:
        raise ValueError(message)


def register(pair):
    tag, index = pair
    require(isinstance(index, int), "noninteger register")
    require((tag == "L" and 0 <= index < 716)
            or (tag == "C" and 0 <= index < 8), "unknown register")
    return index if tag == "L" else 716 + index


def exponent(q):
    a, b = q.numerator, q.denominator
    if a > 0 and a & (a - 1) == 0 and b & (b - 1) == 0:
        return a.bit_length() - b.bit_length()
    return None


def coefficient(op):
    q = Q(op[3], op[4])
    require(q and exponent(Q(1, q.denominator)) is not None,
            "nonzero dyadic coefficient required")
    return q


def preparation_cost(q):
    a, b = abs(q.numerator), q.denominator
    return a.bit_length() + a.bit_count() + b.bit_length() - 1


def shift(target, power):
    return [["double" if power > 0 else "halve", target]
            for _ in range(abs(power))]


def prepare(source, magnitude):
    require(magnitude > 0, "positive magnitude required")
    a, b = magnitude.numerator, magnitude.denominator
    require(b & (b - 1) == 0, "nondyadic preparation")
    result = [["clear", WORK], ["add", WORK, source]]
    for bit in bin(a)[3:]:
        result.append(["double", WORK])
        if bit == "1":
            result.append(["add", WORK, source])
    return result + shift(WORK, 1 - b.bit_length())


def lower_macro(op):
    tag, target = op[0], register(op[1])
    if tag == "clear":
        return [["clear", target]]
    if tag == "copy":
        return [["copy", target, register(op[2])]]
    if tag == "scale":
        q = Q(op[2], op[3])
        k = exponent(abs(q))
        require(k is not None, "scale is not a signed power of two")
        return shift(target, k) + ([["neg", target]] if q < 0 else [])
    require(tag == "add", "unknown macro")
    source, q = register(op[2]), coefficient(op)
    require(target != source, "source/target alias")
    return (prepare(source, abs(q))
            + [["add" if q > 0 else "sub", target, WORK], ["clear", WORK]])


@lru_cache(None)
def one_read_routes(a, b):
    """Enumerate all feasible (u,v) in the claimed square, using unique v.

    For each u, (a*2**u+1)*2**v=b determines v. Positive coefficients
    make the maximum below an exact coefficient-work L1 envelope.
    """
    cap = max(a, Q(b.numerator))
    routes = []
    for u in range(-LIMIT, LIMIT + 1):
        middle = a * Q(2)**u + 1
        v = exponent(b / middle)
        if (v is not None and -LIMIT <= v <= LIMIT
                and max(a, middle, b) <= cap):
            routes.append((abs(u) + 1 + abs(v), u, v))
    return tuple(sorted(routes))


def select_route(a, b, additive):
    """Strict improvement over reset; ties keep the earlier/simpler choice."""
    cost, route = 1 + preparation_cost(b), None
    k = exponent(b / a)
    if k is not None and abs(k) < cost:
        cost, route = abs(k), ["shift", k]
    if additive:
        candidates = one_read_routes(a, b)
        if candidates and candidates[0][0] < cost:
            cost, u, v = candidates[0]
            route = ["read", u, v]
    return cost, route


def eligible(event, phase):
    if (phase != "full_frame_cleanup" or event[0] != "scalar"
            or event[2] != 1 or event[1][0] != "add"):
        return None
    op = event[1]
    q = coefficient(op)
    if (op[1][0] != "L" or op[2][0] != "L" or op[1] == op[2]
            or abs(q) == 1):
        return None
    return register(op[2]), abs(q)


def plan(events, additive):
    phase, previous = None, None
    edges = {}
    for index, event in enumerate(events):
        if event[0] == "phase":
            phase = event[1]
        current = eligible(event, phase)
        if previous and current and previous[0] == current[0]:
            _, route = select_route(previous[1], current[1], additive)
            if route is not None:
                edges[index] = route
        previous = current
    blocks = []
    for index, route in edges.items():
        if blocks and blocks[-1]["stop"] == index:
            blocks[-1]["stop"] = index + 1
            blocks[-1]["routes"].append(route)
        else:
            blocks.append({"start": index - 1, "stop": index + 1,
                           "routes": [route]})
    return blocks


def lower_block(events, block):
    start, stop, routes = block["start"], block["stop"], block["routes"]
    require(0 <= start < stop <= len(events) and stop - start >= 2,
            "invalid block span")
    require(len(routes) == stop - start - 1, "route count mismatch")
    phase = next((e[1] for e in reversed(events[:start + 1])
                  if e[0] == "phase"), None)
    data = [eligible(e, phase) for e in events[start:stop]]
    require(all(data), "block crossed phase/frame or ineligible operation")
    source = data[0][0]
    require(all(item[0] == source for item in data), "block changes source")
    result = prepare(source, data[0][1])
    for j, event in enumerate(events[start:stop]):
        if j:
            route = routes[j - 1]
            a, b = data[j - 1][1], data[j][1]
            if route[0] == "shift":
                require(len(route) == 2 and exponent(b / a) == route[1],
                        "invalid rescaling route")
                result.extend(shift(WORK, route[1]))
            else:
                require(route[0] == "read" and len(route) == 3,
                        "unknown route")
                u, v = route[1:]
                require((abs(u) + 1 + abs(v), u, v) in one_read_routes(a, b),
                        "invalid one-read route or prefix excursion")
                result.extend(shift(WORK, u))
                result.append(["add", WORK, source])
                result.extend(shift(WORK, v))
        q = coefficient(event[1])
        result.append(["add" if q > 0 else "sub", register(event[1][1]), WORK])
    return result + [["clear", WORK]]
