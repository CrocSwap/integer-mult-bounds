"""Exact private-work circuits for fixed-source dyadic cleanup blocks.

Prepared for Jeff Cox (@namredips) with substantial OpenAI Codex assistance.
Apache-2.0. The equal-magnitude comparison follows @ellipsi2's PR #722;
the original Horner circuit follows the attributed PR #626 emitter.
"""

from fractions import Fraction

WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def power_exponent(value):
    """Return k for value = 2**k, or None for other positive rationals."""
    a, b = value.numerator, value.denominator
    if a <= 0 or a & (a - 1) or b & (b - 1):
        return None
    return a.bit_length() - b.bit_length()


def coefficient(op):
    q = Fraction(op[3], op[4])
    require(q != 0 and power_exponent(Fraction(1, q.denominator)) is not None,
            "addition coefficient must be nonzero and dyadic")
    return q


def prepare_cost(q):
    a, b = abs(q.numerator), q.denominator
    return 1 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1


def shift(register, exponent):
    return [("double" if exponent > 0 else "halve", register)] * abs(exponent)


def prepare(source, q):
    """Original clear, binary Horner, then halve circuit (one real component)."""
    a, b = abs(q.numerator), q.denominator
    require(a > 0 and b & (b - 1) == 0, "non-dyadic preparation")
    ops = [("clear", WORK), ("inc", WORK, source, 1)]
    for bit in bin(a)[3:]:
        ops.append(("double", WORK))
        if bit == "1":
            ops.append(("inc", WORK, source, 1))
    ops.extend(shift(WORK, -(b.bit_length() - 1)))
    return ops


def lower_macro(op):
    tag, target = op[0], tuple(op[1])
    require(target != WORK, "work register aliases macro target")
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        source = tuple(op[2])
        require(source != WORK, "work register aliases macro source")
        return [("copy", target, source)]
    if tag == "scale":
        q = Fraction(op[2], op[3])
        exponent = power_exponent(abs(q))
        require(exponent is not None, "scale must be a signed power of two")
        return shift(target, exponent) + ([("neg", target)] if q < 0 else [])
    require(tag == "add", "unknown scalar macro")
    source, q = tuple(op[2]), coefficient(op)
    require(source != target and source != WORK, "addition register alias")
    return prepare(source, q) + [("inc", target, WORK, 1 if q > 0 else -1),
                                 ("clear", WORK)]


def block_data(events):
    require(len(events) >= 2, "block must contain at least two additions")
    source, magnitudes = None, []
    for event in events:
        require(event[0] == "scalar" and event[2] == 1 and event[1][0] == "add",
                "block must contain consecutive full-frame additions")
        op = event[1]
        target, current_source, q = tuple(op[1]), tuple(op[2]), coefficient(op)
        require(target[0] == current_source[0] == "L", "block uses non-live register")
        require(target != current_source, "block mutates its source")
        require(abs(q) != 1, "unit coefficients are outside this experiment")
        if source is None:
            source = current_source
        require(current_source == source, "block changes source")
        if magnitudes:
            require(power_exponent(abs(q) / magnitudes[-1]) is not None,
                    "block changes odd numerator")
        magnitudes.append(abs(q))
    return source, magnitudes


def lower_block(events):
    source, magnitudes = block_data(events)
    ops = prepare(source, magnitudes[0])
    for i, event in enumerate(events):
        if i:
            ops.extend(shift(WORK, power_exponent(magnitudes[i] / magnitudes[i - 1])))
        q = coefficient(event[1])
        ops.append(("inc", tuple(event[1][1]), WORK, 1 if q > 0 else -1))
    ops.append(("clear", WORK))
    return ops


def plans(events, mode):
    """All profitable adjacent merges in a fixed word; no gate reordering.

    The end-clear + next preparation saved by each edge is independent of
    other edges. Equal/negative savings are cut to keep shorter lifetimes.
    """
    require(mode in ("equal", "rescale"), "unknown planning mode")
    phase, run, result, previous = None, [], [], None
    for index, event in enumerate(events):
        if event[0] == "phase":
            phase = event[1]
        eligible = (phase == "full_frame_cleanup" and event[0] == "scalar"
                    and event[2] == 1 and event[1][0] == "add")
        current = None
        if eligible:
            op, q = event[1], coefficient(event[1])
            eligible = (abs(q) != 1 and op[1][0] == op[2][0] == "L"
                        and op[1] != op[2])
            if eligible:
                current = (tuple(op[2]), abs(q))
        merge = False
        if previous is not None and current is not None and previous[0] == current[0]:
            k = power_exponent(current[1] / previous[1])
            merge = (k is not None and (mode == "rescale" or k == 0)
                     and abs(k) < 1 + prepare_cost(current[1]))
        if not merge:
            if len(run) > 1:
                result.append((run[0], run[-1] + 1))
            run = []
        if eligible:
            run.append(index)
        previous = current
    if len(run) > 1:
        result.append((run[0], run[-1] + 1))
    return result
