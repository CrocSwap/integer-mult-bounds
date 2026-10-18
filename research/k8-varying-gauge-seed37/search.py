"""Paid time-varying dyadic gauge. Sagar Thakrar with OpenAI Codex, Apache-2.0."""
from copy import deepcopy
from fractions import Fraction as Q


def require(ok, message):
    if not ok:
        raise ValueError(message)


def power(k):
    return Q(2 ** k) if k >= 0 else Q(1, 2 ** -k)


def parts(q):
    a, d = abs(q.numerator), q.denominator
    require(a > 0 and d & (d - 1) == 0, "nonzero dyadic coefficient")
    v = (a & -a).bit_length() - 1
    return a >> v, v - (d.bit_length() - 1)


def price(q):
    # PR696 copy initialization, including its isolated unit-coefficient discount.
    p, e = parts(q)
    return 1 + p.bit_length() + p.bit_count() + abs(e) - int(p == 1 and e == 0)


def eligible(word, programs):
    excluded = set(word["centers"])
    for events in programs.values():
        for event in events:
            if event[0] == "residual_adapter":
                excluded.add(event[2])
            if event[0] == "scalar" and event[1][0] in ("copy", "clear"):
                for r in event[1][1:]:
                    if isinstance(r, list) and r[0] == "L":
                        excluded.add(r[1])
    return [h for h in range(224, 704) if h not in excluded
            and word["start"][h] == 0 and word["final"][h] == 1]


def incident(events, helper):
    result = []
    for i, event in enumerate(events):
        if event[0] == "scalar" and event[1][0] == "add":
            g = event[1]
            sign = int(g[1] == ["L", helper]) - int(g[2] == ["L", helper])
            if sign:
                result.append((i, Q(g[3], g[4]), sign))
    require(bool(result), "helper has no incident ADD")
    return result


def optimize(terms):
    breaks = [0] + [-s * parts(q)[1] for _, q, s in terms]
    lo, hi = min(breaks), max(breaks)
    # Ties prefer fewer inserted SCALE macros, then smaller exponents.
    dp = {0: (0, 0, 0, ())}
    for _, q, sign in terms:
        next_row = {}
        for k in range(lo, hi + 1):
            delta = price(q * power(sign * k)) - price(q)
            next_row[k] = min((v[0] + abs(k - j) + delta,
                               v[1] + int(k != j), v[2] + abs(k), v[3] + (k,))
                              for j, v in dp.items())
        dp = next_row
    best = min((v[0] + abs(k), v[1] + int(k != 0), v[2], v[3])
               for k, v in dp.items())
    constant = min((2 * abs(k) + sum(price(q * power(s * k)) - price(q)
                                    for _, q, s in terms), abs(k), k)
                   for k in range(lo, hi + 1))
    return {"domain": [lo, hi], "incident_adds": len(terms),
            "delta_real": best[0], "scale_macros": best[1],
            "constant_delta_real": constant[0], "constant_exponent": constant[2],
            "schedule": [[term[0], k] for term, k in zip(terms, best[3])]}


def transform(events, word, helper, schedule):
    require([i for i, _ in schedule] == [i for i, _, _ in incident(events, helper)],
            "schedule covers exactly every incident ADD")
    require(all(type(k) is int for _, k in schedule), "integer gauge exponents")
    require(word["start"][helper] == 0 and word["final"][helper] == 1,
            "cold/FULL helper boundary")
    require(events[-1] == ["phase", "done"], "terminal phase")
    by_index = dict(schedule)
    result, k = [], 0
    for i, original in enumerate(events):
        event = deepcopy(original)
        if i in by_index:
            new_k = by_index[i]
            if new_k != k:
                q = power(new_k - k)
                result.append(["scalar", ["scale", ["L", helper],
                                           q.numerator, q.denominator], event[2]])
            k = new_k
            g = event[1]
            sign = int(g[1] == ["L", helper]) - int(g[2] == ["L", helper])
            q = Q(g[3], g[4]) * power(sign * k)
            g[3:5] = [q.numerator, q.denominator]
        if i == len(events) - 1 and k:
            q = power(-k)
            result.append(["scalar", ["scale", ["L", helper],
                                       q.numerator, q.denominator], 1])
        result.append(event)
    return result
