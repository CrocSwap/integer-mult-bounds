"""Joint bounded temporal gauges. Sagar Thakrar / OpenAI Codex, Apache-2.0.

Extends the single-helper recurrence of Sagar Thakrar PR1259 and the zero-boundary
contract of Philipp/mightyOil PR1270. Coefficient price is the retained PR696 one.
"""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product


def require(ok, message):
    if not ok:
        raise ValueError(message)


def power(k):
    return Q(2) ** k


def price(q):
    a, d = abs(q.numerator), q.denominator
    require(a > 0 and d & (d - 1) == 0, "nonzero dyadic coefficient")
    v = (a & -a).bit_length() - 1
    odd, exponent = a >> v, v - (d.bit_length() - 1)
    return 1 + odd.bit_length() + odd.bit_count() + abs(exponent) - int(odd == 1 and exponent == 0)


def eligible(word, programs):
    excluded = set(word["centers"])
    for events in programs.values():
        for e in events:
            if e[0] == "residual_adapter":
                excluded.add(e[2])
            if e[0] == "scalar" and e[1][0] in ("copy", "clear"):
                excluded.update(r[1] for r in e[1][1:] if isinstance(r, list) and r[0] == "L")
    return [h for h in range(224, 704) if h not in excluded
            and word["start"][h] == 0 and word["final"][h] == 1]


def pairs(programs, helpers):
    result = set()
    for e in programs["forward"]:
        if e[0] == "scalar" and e[1][0] == "add":
            a, b = e[1][1:3]
            if a[0] == b[0] == "L" and a[1] in helpers and b[1] in helpers:
                result.add(tuple(sorted((a[1], b[1]))))
    return sorted(result)


def segments(events, pair):
    result, current = [], []
    for i, e in enumerate(events):
        if e[0] != "scalar":
            if current:
                result.append(current)
                current = []
        elif e[1][0] == "add":
            g = e[1]
            signs = tuple(int(g[1] == ["L", h]) - int(g[2] == ["L", h]) for h in pair)
            if any(signs):
                current.append((i, Q(g[3], g[4]), signs))
    if current:
        result.append(current)
    return result


def distance(a, b):
    return sum(abs(x - y) for x, y in zip(a, b))


def optimize(blocks, domains=((-4, 4), (-4, 4))):
    states = list(product(*(range(lo, hi + 1) for lo, hi in domains)))
    require((0, 0) in states, "zero belongs to both gauge domains")
    schedule, total = [], 0
    for block in blocks:
        dp = {s: distance(s, (0, 0)) for s in states}
        parents = []
        for _, q, signs in block:
            # Separable exact L1 distance transform, retaining the predecessor.
            best = {s: (v, s) for s, v in dp.items()}
            for axis in range(2):
                for order, step in ((states, 1), (list(reversed(states)), -1)):
                    for s in order:
                        t = list(s)
                        t[axis] -= step
                        t = tuple(t)
                        if t in best:
                            best[s] = min(best[s], (best[t][0] + 1, best[t][1]))
            dp = {s: best[s][0] + price(q * power(sum(a * b for a, b in zip(s, signs)))) - price(q)
                  for s in states}
            parents.append({s: best[s][1] for s in states})
        cost, state = min((v + distance(s, (0, 0)), s) for s, v in dp.items())
        total += cost
        path = []
        for parent in reversed(parents):
            path.append(state)
            state = parent[state]
        schedule.extend([[term[0], *s] for term, s in zip(block, reversed(path))])
    return {"delta_real": total, "schedule": schedule}


def schedule_cost(blocks, schedule):
    require([r[0] for r in schedule] == [t[0] for b in blocks for t in b], "exact schedule coverage")
    states = {i: (a, b) for i, a, b in schedule}
    cost = 0
    for block in blocks:
        old = (0, 0)
        for i, q, signs in block:
            new = states[i]
            cost += distance(old, new) + price(q * power(sum(a * b for a, b in zip(new, signs)))) - price(q)
            old = new
        cost += distance(old, (0, 0))
    return cost


def tied_single_minimum(blocks, bound=4):
    """Cheapest joint path among ALL separately optimal paths, including ties."""
    values = list(range(-bound, bound + 1))
    total = 0
    for block in blocks:
        allowed = []
        for axis in range(2):
            costs = [{k: price(q * power(signs[axis] * k)) - price(q) for k in values}
                     for _, q, signs in block]
            forward = [{0: 0}]
            for c in costs:
                forward.append({k: min(v + abs(k - j) for j, v in forward[-1].items()) + c[k]
                                for k in values})
            optimum = min(v + abs(k) for k, v in forward[-1].items())
            backward = [None] * (len(block) + 1)
            backward[-1] = {k: abs(k) for k in values}
            for i in range(len(block) - 1, -1, -1):
                backward[i] = {j: min(abs(k - j) + costs[i][k] + backward[i + 1][k] for k in values)
                               for j in values}
            allowed.append([{k: [j for j, v in forward[i].items()
                                 if v + abs(k - j) + costs[i][k] + backward[i + 1][k] == optimum]
                             for k in values} for i in range(len(block))])
        dp = {(0, 0): 0}
        for i, (_, q, signs) in enumerate(block):
            new = {}
            for a, b in product(values, repeat=2):
                predecessors = [(x, y) for x in allowed[0][i][a] for y in allowed[1][i][b] if (x, y) in dp]
                if predecessors:
                    new[a, b] = min(dp[t] + distance((a, b), t) for t in predecessors)
                    new[a, b] += price(q * power(a * signs[0] + b * signs[1])) - price(q)
            dp = new
        require(bool(dp), "nonempty tied optimum paths")
        total += min(v + distance(s, (0, 0)) for s, v in dp.items())
    return total


def transform(events, word, pair, schedule):
    blocks = segments(events, pair)
    schedule_cost(blocks, schedule)
    require(all(type(k) is int and -4 <= k <= 4 for row in schedule for k in row[1:]), "bounded integer exponents")
    by_index = {i: (a, b) for i, a, b in schedule}
    current, frames, result = [0, 0], [word["start"][h] for h in pair], []
    inserted = 0

    def move(new):
        nonlocal inserted
        for j, h in enumerate(pair):
            if new[j] != current[j]:
                q = power(new[j] - current[j])
                result.append(["scalar", ["scale", ["L", h], q.numerator, q.denominator], frames[j]])
                inserted += 1
                current[j] = new[j]

    for i, original in enumerate(events):
        e = deepcopy(original)
        if e[0] != "scalar":
            move((0, 0))
        if i in by_index:
            move(by_index[i])
            g = e[1]
            k = sum(current[j] * (int(g[1] == ["L", h]) - int(g[2] == ["L", h])) for j, h in enumerate(pair))
            q = Q(g[3], g[4]) * power(k)
            g[3:5] = [q.numerator, q.denominator]
        result.append(e)
        if e[0] == "climb" and e[2] in pair:
            j = pair.index(e[2])
            require(frames[j] == e[3], "frame chronology")
            frames[j] = e[4]
    move((0, 0))
    return result, inserted
