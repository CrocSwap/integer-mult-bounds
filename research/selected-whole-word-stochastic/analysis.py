"""Exact ideal norms and signed stochastic transfers for a fixed word."""

from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt

ROUNDED = {"MOVE", "ADD", "SCALE"}


def need(ok, why):
    if not ok:
        raise ValueError(why)


def add(row, source, coefficient):
    for key, value in source.items():
        new = row.get(key, 0) + coefficient * value
        if new:
            row[key] = new
        else:
            row.pop(key, None)


def span(basis):
    result = {0}
    for vector in basis:
        need(type(vector) is int and 0 < vector < 512 and vector not in result, "frame basis")
        result |= {x ^ vector for x in tuple(result)}
    return result


def ideal(word):
    public, count = word["public"], word["public"] + word["owned_fields"]
    rows = [{r: Q(1)} if r < public else {} for r in range(count)]
    norms = [Q(bool(row)) for row in rows]
    frames = list(word["initial"]) + [None] * word["owned_fields"]
    spaces = [span(basis) for basis in word["frames"]]
    live, weights, erasures = set(), [], []
    peak = [Q(1), 0, 0]
    for step, event in enumerate(word["program"]):
        op, r = event[:2]
        need(type(r) is int and 0 <= r < count, "destination")
        a, c = norms[r], Q(1)
        if op == "MOVE":
            _, _, before, after, private = event
            need(frames[r] == before and private == (r in live), "native source/owner")
            need(spaces[after] < spaces[before] if private else spaces[before] < spaces[after], "native nesting")
            frames[r] = after
        elif op == "INIT":
            need(r >= public and r not in live, "owned allocation")
            live.add(r)
            rows[r], frames[r] = {}, event[2]
        elif op == "CLEAR":
            need(r in live and frames[r] == event[2], "owned erasure")
            erasures.append([step, r, norms[r]])
            live.remove(r)
            rows[r], frames[r] = {}, None
        else:
            need(op in {"ADD", "SCALE", "COPY"}, "known opcode")
            q = Q(event[-2])
            need(q and frames[r] == event[-1] and q.denominator & (q.denominator - 1) == 0, "scalar chart/coefficient")
            if op == "SCALE":
                a, c = abs(q) * norms[r], abs(q)
                rows[r] = {k: q * v for k, v in rows[r].items()}
            else:
                s = event[2]
                need(s != r and 0 <= s < count and frames[s] == frames[r], "common-frame operands")
                if op == "COPY":
                    need(r in live and not rows[r], "copy destination")
                    rows[r] = {k: q * v for k, v in rows[s].items()}
                else:
                    a, c = norms[r] + abs(q) * norms[s], 1 + abs(q)
                    add(rows[r], rows[s], q)
        norms[r] = sum(map(abs, rows[r].values()), Q(0))
        weights.append((a, c))
        if norms[r] > peak[0]:
            peak = [norms[r], step + 1, r]
    need(not live and frames[:public] == word["final"], "final frames/lifetimes")
    active = set(word["live"])
    for r, row in enumerate(rows):
        expected = {r: Q(1)} if r < public else {}
        if r - 112 in active:
            expected[r - 112] = Q(1)
        need(row == expected, "complete ideal endpoint")
    return weights, {"peak_ideal_norm": peak, "erasures": erasures,
                     "opcode_counts": dict(Counter(e[0] for e in word["program"]))}


def integer_weights(word):
    """Use separate integer rows and a binary denominator for each field."""
    public, count = word["public"], word["public"] + word["owned_fields"]
    rows = [{r: 1} if r < public else {} for r in range(count)]
    powers = [0] * count
    result = []
    for event in word["program"]:
        op, r = event[:2]
        norm = lambda s: Q(sum(map(abs, rows[s].values())), 1 << powers[s])
        a, c = norm(r), Q(1)
        if op in {"INIT", "CLEAR"}:
            rows[r], powers[r] = {}, 0
        elif op in {"ADD", "COPY", "SCALE"}:
            q = Q(event[-2])
            denominator_power = q.denominator.bit_length() - 1
            if op == "SCALE":
                a, c = abs(q) * norm(r), abs(q)
                rows[r] = {k: q.numerator * v for k, v in rows[r].items()}
                powers[r] += denominator_power
            else:
                s = event[2]
                if op == "COPY":
                    rows[r] = {k: q.numerator * v for k, v in rows[s].items()}
                    powers[r] = powers[s] + denominator_power
                else:
                    a, c = norm(r) + abs(q) * norm(s), 1 + abs(q)
                    level = max(powers[r], powers[s] + denominator_power)
                    old = {k: v << (level - powers[r]) for k, v in rows[r].items()}
                    for k, v in rows[s].items():
                        old[k] = old.get(k, 0) + q.numerator * (v << (level - powers[s] - denominator_power))
                    rows[r] = {k: v for k, v in old.items() if v}
                    powers[r] = level
            while powers[r] and all(v % 2 == 0 for v in rows[r].values()):
                rows[r] = {k: v // 2 for k, v in rows[r].items()}
                powers[r] -= 1
        result.append((a, c))
    return result


def coefficient_digest(row):
    return sha256("".join(f"{j}:{v};" for j, v in sorted(row.items(), reverse=True)).encode()).hexdigest()


def forward(word, weights):
    count = word["public"] + word["owned_fields"]
    rows, scores = [{} for _ in range(count)], [[Q(0)] * 4 for _ in range(count)]
    peaks = [[Q(0), 0, 0] for _ in range(4)]
    for step, event in enumerate(word["program"]):
        op, r = event[:2]
        if op in {"INIT", "CLEAR"}:
            rows[r], scores[r] = {}, [Q(0)] * 4
        elif op in {"SCALE", "COPY"}:
            q = Q(event[-2])
            source = r if op == "SCALE" else event[2]
            rows[r] = {j: q * v for j, v in rows[source].items()}
            scores[r] = [value * (q * q if i < 2 else abs(q)) for i, value in enumerate(scores[source])]
        elif op == "ADD":
            q = Q(event[-2])
            for j, value in rows[event[2]].items():
                old = rows[r].get(j, Q(0))
                new = old + q * value
                squared, absolute = new * new - old * old, abs(new) - abs(old)
                a, c = weights[j]
                delta = [squared * a * a, squared * c * c, absolute * a, absolute * c]
                scores[r] = [v + d for v, d in zip(scores[r], delta)]
                if new:
                    rows[r][j] = new
                else:
                    rows[r].pop(j, None)
        if op in ROUNDED:
            a, c = weights[step]
            rows[r][step] = Q(1)
            scores[r] = [v + d for v, d in zip(scores[r], [a*a, c*c, a, c])]
        for i, value in enumerate(scores[r]):
            if value > peaks[i][0]:
                peaks[i] = [value, step + 1, r]
    return peaks, scores, rows


def transpose(word, weights):
    count = word["public"] + word["owned_fields"]
    columns = [{r: Q(1)} for r in range(count)]
    coefficients = [{} for _ in range(count)]
    for step in reversed(range(len(word["program"]))):
        event = word["program"][step]
        op, r = event[:2]
        if op in ROUNDED:
            for output, value in columns[r].items():
                coefficients[output][step] = value
        if op in {"INIT", "CLEAR"}:
            columns[r] = {}
        elif op == "SCALE":
            q = Q(event[-2])
            columns[r] = {k: q * v for k, v in columns[r].items()}
        elif op in {"ADD", "COPY"}:
            add(columns[event[2]], columns[r], Q(event[-2]))
            if op == "COPY":
                columns[r] = {}
    scores = []
    for row in coefficients:
        score = [Q(0)] * 4
        for j, value in row.items():
            a, c = weights[j]
            parts = [value*value*a*a, value*value*c*c, abs(value)*a, abs(value)*c]
            score = [x + y for x, y in zip(score, parts)]
        scores.append(score)
    return scores, coefficients


def sqrt_upper(value):
    n = isqrt(value.numerator // value.denominator)
    return n if n*n == value else n + 1


def reverse_cut(word, cut, role):
    row, errors = {role: Q(1)}, {}
    for step in reversed(range(cut)):
        event = word["program"][step]
        op, r = event[:2]
        value = row.get(r, Q(0))
        if op in ROUNDED and value:
            errors[step] = value
        if op in {"INIT", "CLEAR"}:
            row.pop(r, None)
        elif op == "SCALE" and value:
            row[r] = value * Q(event[-2])
        elif op in {"ADD", "COPY"}:
            if value:
                add(row, {event[2]: value}, Q(event[-2]))
            if op == "COPY":
                row.pop(r, None)
    return row, errors


def guards(peaks, scores, public, stochastic):
    if stochastic:
        j, k = [Q(sqrt_upper(row[0])) for row in peaks[:2]]
        final = [(Q(sqrt_upper(row[0])), Q(sqrt_upper(row[1]))) for row in scores[:public]]
    else:
        j, k = [row[0] for row in peaks[2:]]
        final = [tuple(row[2:]) for row in scores[:public]]
    history = []
    for guard in range(64):
        z = 1 << guard
        if z <= k:
            history.append([guard, "unstable"])
            continue
        rho, role = max(((a + b * j / (z-k)) / z, r) for r, (a, b) in enumerate(final))
        history.append([guard, rho])
        if rho < 1:
            prefix_guard = next(g for g in range(64) if (1 << g) > j+k)
            return {"J": j, "K": k, "final_guard": guard, "prefix_guard": prefix_guard,
                    "final_rho": rho, "final_role": role, "prefix_at_final_guard": j/(z-k),
                    "smaller_guard_checks": history}
    raise ValueError("no bounded guard found")


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value
