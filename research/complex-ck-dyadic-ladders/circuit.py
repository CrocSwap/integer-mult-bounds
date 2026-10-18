"""Finite same-source dyadic ladders. Apache-2.0; see NOTICE.md."""

from fractions import Fraction

WORK = ("W", 0)


def power_of_two(n):
    return n > 0 and n & (n - 1) == 0


def magnitude(op):
    return abs(Fraction(op[3], op[4]))


def prepare(source, value):
    """The selected emitter's original cleared-work binary Horner recipe."""
    value = abs(value)
    a, b = value.numerator, value.denominator
    if not a or not power_of_two(b):
        raise ValueError("coefficient must be a nonzero dyadic rational")
    out = [("clear", WORK)]
    for i, bit in enumerate(bin(a)[2:]):
        if i:
            out.append(("double", WORK))
        if bit == "1":
            out.append(("add", WORK, source, 1))
    out.extend([("half", WORK)] * (b.bit_length() - 1))
    return out


def reference(op):
    tag, target = op[0], tuple(op[1])
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        return [("copy", target, tuple(op[2]))]
    if tag == "scale":
        q = Fraction(op[2], op[3])
        if not power_of_two(abs(q.numerator)) or not power_of_two(q.denominator):
            raise ValueError("scale must be a signed power of two")
        exponent = abs(q.numerator).bit_length() - q.denominator.bit_length()
        out = [("double" if exponent > 0 else "half", target)] * abs(exponent)
        return out + ([("negate", target)] if q < 0 else [])
    if tag != "add":
        raise ValueError("unknown scalar operation")
    source = tuple(op[2])
    if target == source or WORK in (target, source):
        raise ValueError("source, target and work must be distinct")
    q = Fraction(op[3], op[4])
    return prepare(source, q) + [("add", target, WORK, 1 if q > 0 else -1),
                                ("clear", WORK)]


def run_key(event):
    if event[0] != "scalar" or event[1][0] != "add":
        return None
    op = event[1]
    if op[1] == op[2] or op[1][0] != "L" or op[2][0] != "L":
        return None
    q = magnitude(op)
    if not q or q == 1 or not power_of_two(q.denominator):
        return None
    odd = q.numerator // (q.numerator & -q.numerator)
    return tuple(op[2]), event[2], odd


def transition(source, previous, following, equal_only=False):
    ratio = following / previous
    if not power_of_two(ratio.numerator) or not power_of_two(ratio.denominator):
        raise ValueError("transition ratio must be a power of two")
    exponent = ratio.numerator.bit_length() - ratio.denominator.bit_length()
    reset = [("clear", WORK)] + prepare(source, following)
    shift = [("double" if exponent > 0 else "half", WORK)] * abs(exponent)
    if (not equal_only or previous == following) and len(shift) < len(reset):
        return shift
    return reset


def lower_block(events, equal_only=False):
    if len(events) < 2 or run_key(events[0]) is None:
        raise ValueError("a ladder needs at least two eligible additions")
    key = run_key(events[0])
    if any(run_key(e) != key for e in events):
        raise ValueError("ladder crosses a source, frame, ratio or event boundary")
    source = key[0]
    out = prepare(source, magnitude(events[0][1]))
    previous = None
    for event in events:
        op = event[1]
        value = magnitude(op)
        if previous is not None:
            out.extend(transition(source, previous, value, equal_only))
        out.append(("add", tuple(op[1]), WORK, 1 if Fraction(op[3], op[4]) > 0 else -1))
        previous = value
    out.append(("clear", WORK))
    return out


def select_blocks(events):
    """Exhaust maximal eligible runs; select only useful varying-magnitude runs."""
    blocks = []
    i = 0
    while i < len(events):
        key = run_key(events[i])
        j = i + 1
        if key is None:
            i = j
            continue
        while j < len(events) and run_key(events[j]) == key:
            j += 1
        if j - i > 1:
            group = events[i:j]
            original = sum(len(reference(e[1])) for e in group)
            candidate = len(lower_block(group))
            equal_only = len(lower_block(group, equal_only=True))
            if candidate < equal_only <= original:
                blocks.append((i, j))
        i = j
    return blocks
