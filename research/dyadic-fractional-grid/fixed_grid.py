"""Independent scalar fixed-grid execution and one-column rational witnesses.

Gareth Davidson (@bitplane), substantial OpenAI Codex assistance; Apache-2.0.
Halving rounds toward minus infinity. Integer part is unbounded. This models
the scalar primitive projection, not the physical frame/phase realization.
"""

from fractions import Fraction as Q


def need(ok, message):
    if not ok:
        raise ValueError(message)


def step(op, values, integer=False):
    tag, target = op[:2]
    discarded = False
    if tag == "copy":
        values[target] = values[op[2]]
    elif tag == "clear":
        values[target] = 0 if integer else Q(0)
    elif tag == "double":
        values[target] *= 2
    elif tag == "halve":
        if integer:
            discarded = values[target] % 2 != 0
            values[target] //= 2
        else:
            values[target] /= 2
    elif tag == "negate":
        values[target] = -values[target]
    elif tag == "add":
        values[target] += values[op[2]]
    elif tag == "subtract":
        values[target] -= values[op[2]]
    else:
        raise ValueError("unknown primitive")
    return discarded


def initial(word, column, unit):
    n = 2*word["v"]+word["R"]
    registers = [("L", i) for i in range(n)] + [("C", i) for i in range(len(word["centers"]))] + [("W", 0)]
    need(type(column) is int and 0 <= column < len(registers), "bad input column")
    values = {reg: 0*unit for reg in registers}
    values[registers[column]] = unit
    return values


def check_witness(events, word, lowering, reverse, proof):
    """Direct Fraction evaluation on one independently chosen basis input."""
    values = initial(word, proof["input_column"], Q(1))
    index = 0
    for event_id, event in enumerate(events):
        if event[0] != "scalar":
            continue
        method, circuit = lowering.choose(event[1], reverse=reverse)
        for step_id, op in enumerate(circuit):
            step(op, values)
            if index == proof["primitive_index"]:
                need([event_id, step_id, list(op[1]), method] ==
                     [proof["event"], proof["step"], proof["register"], proof["method"]], "witness address mismatch")
                exact = values[op[1]]
                expected = Q(proof["odd_numerator"], 2**proof["denominator_exponent"])
                need(exact == expected, "rational witness value mismatch")
                need(expected.numerator % 2 != 0, "non-sharp witness numerator")
                need(expected.denominator == 2**proof["denominator_exponent"], "non-sharp witness denominator")
                return str(exact)
            index += 1
    raise ValueError("witness location not reached")


def program(events, word, orientation, lowering, reverse, guard, column):
    need(type(guard) is int and guard >= 0, "bad guard")
    unit = 2**guard
    values = initial(word, column, unit)
    discarded, first = 0, None
    for event_id, event in enumerate(events):
        if event[0] != "scalar":
            continue
        for step_id, op in enumerate(lowering.choose(event[1], reverse=reverse)[1]):
            if step(op, values, integer=True):
                discarded += 1
                if first is None:
                    first = {"event": event_id, "step": step_id, "register": list(op[1])}
    expected = {reg: 0 for reg in values}
    n = 2*word["v"]+word["R"]
    if column < n:
        expected["L", column] = unit
        if orientation == "forward" and column < word["v"]:
            expected["L", word["v"]+column] = unit
        elif orientation == "backward" and word["v"] <= column < 2*word["v"]:
            expected["L", column-word["v"]] = -unit
    differences = [{"register": list(reg), "error": str(Q(value-expected[reg], unit))}
                   for reg, value in values.items() if value != expected[reg]]
    return {"guard_bits": guard, "input_column": column, "discarded_halves": discarded,
            "first_discarded_half": first, "endpoint_matches": not differences,
            "endpoint_errors": differences}


def local(circuit, guard):
    values = {("S", 0): 2**guard, ("T", 0): 0, ("W", 0): 7*2**guard}
    losses = 0
    for op in circuit:
        losses += step(op, values, integer=True)
    need(values["S", 0] == 2**guard and values["W", 0] == 0, "fixed-grid source/private contract")
    return str(Q(values["T", 0], 2**guard)), losses
