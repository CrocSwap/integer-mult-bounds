"""One-work-register dyadic lowering and adjacent coefficient reuse.

Apache-2.0. Prepared for @taizaki69 with substantial OpenAI Codex assistance.
The copy-initialized per-macro baseline follows the mechanism of PR696;
the new step retains its work value across adjacent eligible scalar events.
"""

from fractions import Fraction

WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def coefficient(op):
    offset = 3 if op[0] == "add" else 2
    numerator, denominator = op[offset:offset + 2]
    require(type(numerator) is int and type(denominator) is int,
            "integer coefficient fields required")
    # Inverse-transpose scale macros can put the sign in the denominator.
    require(denominator != 0, "nonzero denominator required")
    q = Fraction(numerator, denominator)
    require(q != 0 and q.denominator & (q.denominator - 1) == 0,
            "nonzero dyadic coefficient required")
    return q


def prepare(source, magnitude, original=False):
    """Return paid primitives making WORK = magnitude * source."""
    bits = bin(magnitude.numerator)[2:]
    if original:
        out = [("clear", WORK), ("add", WORK, source)]
    else:
        out = [("copy", WORK, source)]
    for bit in bits[1:]:
        out.append(("double", WORK))
        if bit == "1":
            out.append(("add", WORK, source))
    out.extend(("half", WORK) for _ in range(magnitude.denominator.bit_length() - 1))
    return out


def lower_scalar(op, original=False):
    tag, target = op[0], tuple(op[1])
    require(target[0] in ("L", "C"), "logical target required")
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        source = tuple(op[2])
        require(source[0] in ("L", "C"), "logical source required")
        return [("copy", target, source)]
    require(tag in ("scale", "add"), "unsupported scalar")
    q = coefficient(op)
    if tag == "scale":
        n = abs(q.numerator)
        require(n & (n - 1) == 0, "scale must be a signed power of two")
        exponent = n.bit_length() - q.denominator.bit_length()
        return ([("double" if exponent >= 0 else "half", target)] * abs(exponent)
                + ([("negate", target)] if q < 0 else []))
    source = tuple(op[2])
    require(source[0] in ("L", "C") and source != target,
            "distinct logical source and target required")
    accumulate = "add" if q > 0 else "sub"
    if abs(q) == 1 and not original:
        return [(accumulate, target, source), ("clear", WORK)]
    return prepare(source, abs(q), original) + [(accumulate, target, WORK), ("clear", WORK)]


def reuse_key(event):
    if event[0] != "scalar" or event[1][0] != "add":
        return None
    op = event[1]
    q = coefficient(op)
    source, target = tuple(op[2]), tuple(op[1])
    require(source != target and source[0] in ("L", "C")
            and target[0] in ("L", "C"), "aliased or private logical register")
    if abs(q) == 1:
        return None
    return source, abs(q), event[2]


def lower_run(events):
    """Fuse only same-source, same-magnitude, same-frame adjacent adds."""
    require(len(events) >= 2, "reuse needs at least two scalar events")
    key = reuse_key(events[0])
    require(key is not None and all(reuse_key(e) == key for e in events),
            "reuse crosses a source, coefficient, frame or event boundary")
    source, magnitude, _ = key
    out = prepare(source, magnitude)
    for event in events:
        op = event[1]
        out.append(("add" if coefficient(op) > 0 else "sub", tuple(op[1]), WORK))
    out.append(("clear", WORK))
    return out


def chunks(events, reuse=True):
    """Yield (start, stop, primitives); non-scalar events are unchanged."""
    start = 0
    while start < len(events):
        event = events[start]
        stop = start + 1
        if event[0] != "scalar":
            yield start, stop, None
        else:
            key = reuse_key(event) if reuse else None
            if key is not None:
                while stop < len(events) and reuse_key(events[stop]) == key:
                    stop += 1
            ops = lower_run(events[start:stop]) if stop > start + 1 else lower_scalar(event[1])
            yield start, stop, ops
        start = stop
