"""Compile the fixed PR924 factory with unit additions and binary scales.

Prepared for Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0. See SOURCES.json and README.md for predecessor credit.
"""
from fractions import Fraction as Q


def need(condition, message):
    if not condition:
        raise ValueError(message)


def exponent(q):
    q = abs(q)
    need(q and q.numerator & (q.numerator - 1) == 0
         and q.denominator & (q.denominator - 1) == 0,
         "coefficient is not a signed power of two")
    return q.numerator.bit_length() - q.denominator.bit_length()


def normalize(word):
    """Move the original diagonal factors to the output."""
    magnitudes, signs, additions = [0] * 8, [1] * 8, []
    for op in word:
        tag, target = op[:2]
        need(type(target) is int and 0 <= target < 8, "invalid target")
        if tag == "scale":
            q = Q(op[2], op[3])
            magnitudes[target] += exponent(q)
            signs[target] *= -1 if q < 0 else 1
        else:
            need(tag == "add", "invalid factory operation")
            source = op[2]
            need(type(source) is int and 0 <= source < 8 and source != target,
                 "invalid source")
            q = Q(op[3], op[4])
            additions.append((target, source,
                              exponent(q) + magnitudes[source] - magnitudes[target],
                              (-1 if q < 0 else 1) * signs[source] * signs[target]))
    return additions, magnitudes, signs


def edges(additions, final):
    """Build the scale-distance terms on the eight register paths."""
    prior, result = [(-1, 0)] * 8, []
    for index, (target, source, power, _) in enumerate(additions):
        for register, offset in ((target, 0), (source, power)):
            previous, previous_offset = prior[register]
            result.append((previous, index, previous_offset - offset, register))
            prior[register] = (index, offset)
    for register, (previous, offset) in enumerate(prior):
        result.append((previous, -1, offset - final[register], register))
    return result


def compile_factory(word, certificate):
    need(certificate["format"] == "exact-unit-add-factory-v1", "certificate format")
    additions, final, signs = normalize(word)
    levels, flow = certificate["levels"], certificate["dual_flow"]
    need(len(additions) == 26 and len(levels) == 26, "wrong addition count")
    need(all(type(x) is int for x in levels + flow), "noninteger certificate")
    terms = edges(additions, final)
    need(len(flow) == len(terms), "wrong dual length")
    divergence = [0] * len(additions)
    lower_bound = 0
    shift_count = 0
    value = lambda i: levels[i] if i >= 0 else 0
    for (a, b, offset, _), f in zip(terms, flow):
        need(abs(f) <= 1, "dual capacity")
        if a >= 0:
            divergence[a] -= f
        if b >= 0:
            divergence[b] += f
        lower_bound -= f * offset
        shift_count += abs(value(b) - value(a) - offset)
    need(not any(divergence), "dual conservation")
    need(shift_count == lower_bound == 9, "scale optimum certificate")
    physical, result = [0] * 8, []
    for index, (target, source, power, sign) in enumerate(additions):
        for register, goal in ((target, levels[index]), (source, levels[index] + power)):
            tag = "double" if goal > physical[register] else "halve"
            result.extend([(tag, register)] * abs(goal - physical[register]))
            physical[register] = goal
        result.append(("add" if sign > 0 else "subtract", target, source))
    for register in range(8):
        tag = "double" if final[register] > physical[register] else "halve"
        result.extend([(tag, register)] * abs(final[register] - physical[register]))
        if signs[register] < 0:
            result.append(("negate", register))
    need(len(result) == 37, "wrong primitive count")
    supplied = certificate["primitives"]
    need(all(type(op) is list and type(op[0]) is str
             and all(type(r) is int for r in op[1:]) for op in supplied),
         "primitive certificate types")
    need([list(x) for x in result] == supplied, "certificate word")
    return result


def variants(word, primitive=False):
    def invert(op):
        op = list(op)
        if primitive:
            op[0] = {"add": "subtract", "subtract": "add", "double": "halve",
                     "halve": "double", "negate": "negate"}[op[0]]
        elif op[0] == "add":
            op[3] = -op[3]
        else:
            op[2], op[3] = op[3], op[2]
        return op

    def dual(op):
        result = invert(op)
        if result[0] in ("add", "subtract"):
            result[1], result[2] = result[2], result[1]
        return result

    inverse = [invert(op) for op in reversed(word)]
    return {"main": [list(op) for op in word], "cleanup": inverse,
            "dual_main": [dual(op) for op in word],
            "dual_cleanup": [dual(op) for op in inverse]}


def step(rows, op):
    tag, target = op[:2]
    if tag == "clear":
        rows[target] = {}
    elif tag == "copy":
        rows[target] = rows[op[2]].copy()
    elif tag in ("double", "halve", "negate"):
        factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[tag]
        rows[target] = {j: factor * x for j, x in rows[target].items()}
    else:
        need(tag in ("add", "subtract") and target != op[2], "invalid primitive")
        row = rows[target]
        for j, value in list(rows[op[2]].items()):
            value = row.get(j, Q(0)) + (value if tag == "add" else -value)
            if value:
                row[j] = value
            else:
                row.pop(j, None)


def macro_step(rows, op):
    tag, target = op[:2]
    if tag == "scale":
        factor = Q(op[2], op[3])
        rows[target] = {j: factor * x for j, x in rows[target].items()}
    else:
        source, factor = op[2], Q(op[3], op[4])
        for j, value in list(rows[source].items()):
            value = rows[target].get(j, Q(0)) + factor * value
            if value:
                rows[target][j] = value
            else:
                rows[target].pop(j, None)


def reference(word, reuse=False):
    """Use PR696 or a stronger cleared-once coefficient-cache comparator."""
    result, rows, work = [], {i: {i: Q(1)} for i in range(9)}, 8
    for op in word:
        tag, target = op[:2]
        if tag == "scale":
            q = Q(op[2], op[3])
            power = exponent(q)
            part = [("double" if power > 0 else "halve", target)] * abs(power)
            if q < 0:
                part.append(("negate", target))
        else:
            source, q = op[2], Q(op[3], op[4])
            power = exponent(q)
            if power == 0:
                part = [("add" if q > 0 else "subtract", target, source)]
            else:
                part = [("copy", work, source)]
                part += [("double" if power > 0 else "halve", work)] * abs(power)
                sign = 1 if q > 0 else -1
                desired = {j: abs(q) * v for j, v in rows[source].items()}
                cached = rows[work]
                if reuse and cached and cached.keys() == desired.keys():
                    pivot = next(iter(cached))
                    ratio = desired[pivot] / cached[pivot]
                    if all(desired[j] == ratio * cached[j] for j in cached):
                        try:
                            shift = exponent(ratio)
                        except ValueError:
                            pass
                        else:
                            route = [("double" if shift > 0 else "halve", work)] * abs(shift)
                            if len(route) < len(part):
                                part = route
                                sign *= -1 if ratio < 0 else 1
                part.append(("add" if sign > 0 else "subtract", target, work))
            if not reuse:
                part.append(("clear", work))
        for primitive in part:
            step(rows, primitive)
        result.extend(part)
    if reuse:
        result.append(("clear", work))
    return result


def local_check(word, primitives):
    expected = {i: {i: Q(1)} for i in range(9)}
    for op in word:
        macro_step(expected, op)
    expected[8] = {}
    rows = {i: {i: Q(1)} for i in range(9)}
    peak, depth, reads = Q(1), 0, 0
    for op in primitives:
        step(rows, op)
        peak = max(peak, *(sum(map(abs, row.values())) for row in rows.values()))
        depth = max(depth, *(v.denominator.bit_length() - 1
                             for row in rows.values() for v in row.values()))
        reads += 2 if op[0] in ("add", "subtract") else int(op[0] != "clear")
    need(rows == expected, "exact factory boundary or work clearing")
    return {"primitives": len(primitives), "peak_row_l1": str(peak),
            "fractional_depth": depth, "operand_reads": reads}
