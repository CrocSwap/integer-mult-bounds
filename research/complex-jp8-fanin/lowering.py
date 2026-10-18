"""One-stream reverse-Horner batching for full-frame JP8 cleanup.

Sagar Thakrar with OpenAI Codex assistance. Apache-2.0.
Related forward coefficient sharing: ellipsi2, PR #722.
"""
from fractions import Fraction

WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def key(event):
    if len(event) != 3 or event[0] != "scalar" or event[2] != 1:
        return None
    op = event[1]
    if op[0] != "add":
        return None
    target, source = tuple(op[1]), tuple(op[2])
    if target[0] != "L" or source[0] != "L":
        return None
    q = Fraction(op[3], op[4])
    require(target != source, "source aliases target")
    require(q and q.denominator & (q.denominator - 1) == 0,
            "coefficient must be nonzero and dyadic")
    return (target, abs(q)) if abs(q) != 1 else None


def groups(events):
    """Maximal literal runs; every non-scalar event is a hard boundary."""
    i, phase = 0, None
    while i < len(events):
        event = events[i]
        if event[0] == "phase":
            phase = event[1]
        group_key = key(event) if phase == "full_frame_cleanup" else None
        if group_key is None:
            i += 1
            continue
        end = i + 1
        while end < len(events) and key(events[end]) == group_key:
            end += 1
        if end - i >= 2:
            yield i, end
        i = end


def lower(block):
    """Emit clear, signed add, doubling and halving primitives."""
    require(len(block) >= 2, "batch needs at least two additions")
    group_key = key(block[0])
    require(group_key is not None and all(key(e) == group_key for e in block),
            "batch must share its target, magnitude and full frame")
    target, q = group_key
    program = [("clear", WORK)]
    for event in block:
        op = event[1]
        sign = 1 if Fraction(op[3], op[4]) > 0 else -1
        program.append(("add", WORK, tuple(op[2]), sign))
    program.extend(("half", WORK) for _ in range(q.denominator.bit_length() - 1))
    bits = bin(q.numerator)[2:][::-1]
    for index, bit in enumerate(bits):
        if bit == "1":
            program.append(("add", target, WORK, 1))
        if index + 1 < len(bits):
            program.append(("double", WORK))
    program.append(("clear", WORK))
    return program


def original_cost(op):
    """Real-component cost of the selected binary-Horner scalar macro."""
    if op[0] in ("clear", "copy"):
        return 2
    q = Fraction(op[3], op[4]) if op[0] == "add" else Fraction(op[2], op[3])
    n, d = abs(q.numerator), q.denominator
    require(n and d & (d - 1) == 0, "non-dyadic scalar")
    if op[0] == "scale":
        require(n & (n - 1) == 0, "scale must be a signed power of two")
        return 2 * (abs(n.bit_length() - d.bit_length()) + int(q < 0))
    require(op[0] == "add", "unknown scalar operation")
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)
