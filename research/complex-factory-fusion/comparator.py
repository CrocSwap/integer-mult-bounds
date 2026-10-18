"""Compare paid cache routes on the fixed factory map.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
PR1032 supplies the persistent-work comparison. PR1036 supplies the
small-integer accumulation routes. See README.md for full credit.
"""
from fractions import Fraction as Q
from itertools import product

from circuit import exponent, macro_step, need, normalize


def shifts(register, power):
    return [("double" if power > 0 else "halve", register)] * abs(power)


def cache_word(word):
    """Find a shortest route in the stated macro-by-macro cache class."""
    rows = {i: {i: Q(1)} for i in range(8)}
    states = {((8, Q(1)),): []}
    for op in word:
        tag, target = op[:2]
        if tag == "scale":
            q = Q(op[2], op[3])
            part = shifts(target, exponent(q)) + ([("negate", target)] if q < 0 else [])
            states = {cache: path + part for cache, path in states.items()}
        else:
            source, q = op[2], Q(op[3], op[4])
            power = exponent(q)
            add = "add" if q > 0 else "subtract"
            desired = {j: abs(q) * value for j, value in rows[source].items()}
            fresh = shifts(8, power)
            updated = {}
            for cache, path in states.items():
                # This route restores the source before the next macro.
                direct = shifts(source, power) + [(add, target, source)] + shifts(source, -power)
                if q.denominator == 1 and abs(q.numerator) < len(direct):
                    direct = [(add, target, source)] * abs(q.numerator)
                routes = [(cache, direct),
                          (tuple(sorted(desired.items())),
                           [("copy", 8, source)] + fresh + [(add, target, 8)])]
                cached = dict(cache)
                if cached and cached.keys() == desired.keys():
                    pivot = next(iter(cached))
                    ratio = desired[pivot] / cached[pivot]
                    if ratio and all(desired[j] == ratio * cached[j] for j in cached):
                        try:
                            shift = exponent(ratio)
                        except ValueError:
                            pass
                        else:
                            sign = (1 if q > 0 else -1) * (1 if ratio > 0 else -1)
                            end = tuple(sorted((j, value * abs(ratio)) for j, value in cached.items()))
                            routes.append((end, shifts(8, shift) +
                                           [("add" if sign > 0 else "subtract", target, 8)]))
                for end, part in routes:
                    candidate = path + part
                    if end not in updated or len(candidate) < len(updated[end]):
                        updated[end] = candidate
            states = updated
        macro_step(rows, op)
    return min(states.values(), key=len) + [("clear", 8)]


def gauge_census(word):
    """Check all one-scale magnitude placements with a source-version cache."""
    additions, final, signs = normalize(word)
    uses = [0] * 8
    for target, source, _, _ in additions:
        uses[target] += 1
        uses[source] += 1
    wires = [r for r in range(8) if final[r]]
    placements, best, winners = 0, None, []
    fixed_cost = sum(abs(e) + int(s < 0) for e, s in zip(final, signs)) + 1
    for slots in product(*(range(uses[r] + 1) for r in wires)):
        placements += 1
        scheduled = dict(zip(wires, slots))
        seen, level, power = [0] * 8, [0] * 8, [0] * 8
        version = list(range(8))
        states = {(-1, 0): 0}
        for index, (target, source, e, _) in enumerate(additions):
            for r in (target, source):
                if scheduled.get(r, -1) == seen[r]:
                    level[r] = final[r]
                    power[r] += final[r]
            e += level[target] - level[source]
            desired = (version[source], power[source] + e)
            updated = {}
            for cache, cost in states.items():
                prep = 1 + abs(e)
                if cache[0] == desired[0]:
                    prep = min(prep, abs(cache[1] - desired[1]))
                updated[desired] = min(updated.get(desired, 10**9), cost + prep + 1)
                direct = 2 * abs(e) + 1
                if e >= 0:
                    direct = min(direct, 2**e)
                updated[cache] = min(updated.get(cache, 10**9), cost + direct)
            states = updated
            version[target], power[target] = 8 + index, 0
            seen[target] += 1
            seen[source] += 1
        cost = min(states.values()) + fixed_cost
        if best is None or cost < best:
            best, winners = cost, []
        if cost == best:
            winners.append(list(slots))
    need(placements == 39424 and best == 44, "extended gauge comparison")
    return {"placements": placements, "minimum": best, "wires": wires,
            "winning_magnitude_slots": winners,
            "cache_rule": "same_source_version_up_to_binary_scale",
            "scope": "one_net_magnitude_scale_per_nonunit_wire"}
