"""Signed one-read CK coefficient routes. Apache-2.0; see README.md.

Joseph / AmazedBot, with substantial OpenAI Codex assistance.
No pending PR implementation is imported. The original binary-Horner
convention is the retained icekylinx / PR622 / PR626 scalar interface.
"""

from fractions import Fraction as Q
from functools import lru_cache

WORK = ("W", 0)
LIMIT = 16


def require(ok, message):
    if not ok:
        raise ValueError(message)


def exponent(q):
    """Integer e if q=2**e>0, otherwise None (exact rational arithmetic)."""
    if q <= 0:
        return None
    a, b = q.numerator, q.denominator
    if a & (a - 1) or b & (b - 1):
        return None
    return a.bit_length() - b.bit_length()


def magnitude(op):
    q = Q(op[3], op[4])
    require(q != 0 and exponent(Q(q.denominator)) is not None,
            "nonzero dyadic required")
    return abs(q)


def shifts(register, e):
    return [("double" if e > 0 else "halve", register)] * abs(e)


def prepare(source, q):
    """Original cleared-work binary-Horner preparation, fully charged."""
    require(q > 0 and exponent(Q(q.denominator)) is not None,
            "positive dyadic required")
    word = [("clear", WORK)]
    for i, digit in enumerate(bin(q.numerator)[2:]):
        if i:
            word.append(("double", WORK))
        if digit == "1":
            word.append(("add", WORK, source))
    return word + shifts(WORK, -(q.denominator.bit_length() - 1))


def reference(op):
    tag, target = op[0], tuple(op[1])
    require(target != WORK, "private work used as macro target")
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        source = tuple(op[2])
        require(source != WORK, "private work used as macro source")
        return [("copy", target, source)]
    if tag == "scale":
        q = Q(op[2], op[3])
        e = exponent(abs(q))
        require(e is not None, "scale must be signed power of two")
        return shifts(target, e) + ([("negate", target)] if q < 0 else [])
    require(tag == "add", "unknown scalar macro")
    source = tuple(op[2])
    require(source not in (target, WORK), "source aliases target or work")
    q = magnitude(op)
    sign = "add" if Q(op[3], op[4]) > 0 else "subtract"
    return prepare(source, q) + [(sign, target, WORK), ("clear", WORK)]


def copy_prepare(source, q):
    """PR696's accepted copy initialization; no clean-work assumption."""
    return [("copy", WORK, source)] + prepare(source, q)[2:]


def copy_reference(op):
    """Independently implement Sagar Thakrar's PR696 copy/unit baseline."""
    if op[0] != "add":
        return reference(op)
    word = reference(op)  # also validates aliases and coefficient domain
    source, target = tuple(op[2]), tuple(op[1])
    if magnitude(op) == 1:
        return [("add" if Q(op[3], op[4]) > 0 else "subtract", target, source),
                ("clear", WORK)]
    return [("copy", WORK, source)] + word[2:]


def eligible(event):
    if event[0] != "scalar" or event[1][0] != "add":
        return None
    op = event[1]
    q = magnitude(op)
    require(tuple(op[1]) != tuple(op[2]), "source aliases target")
    if q == 1:
        return None
    return tuple(op[2]), event[2]


def partitions(events):
    """Maximal contiguous nonunit runs; every non-scalar event is a barrier."""
    i = 0
    while i < len(events):
        key = eligible(events[i])
        j = i + 1
        if key is not None:
            while j < len(events) and eligible(events[j]) == key:
                j += 1
        yield i, j
        i = j


@lru_cache(None)
def route(a, b, mode="signed"):
    """Minimum charged route in a finite class, with deterministic ties.

    Result: (cost, kind, u, v, epsilon). Powers are not bounded; one-read
    exponents are in [-16,16]. Reset uses PR696 copy-initialized Horner.
    """
    require(mode in ("power", "positive", "signed"), "unknown route mode")
    require(a > 0 and b > 0, "positive route endpoints required")
    choices = [(len(copy_prepare(("S", 0), b)), "reset", 0, 0, 0)]
    e = exponent(b / a)
    if e is not None:
        choices.append((abs(e), "power", e, 0, 0))
    signs = () if mode == "power" else (1,) if mode == "positive" else (1, -1)
    for sign in signs:
        for u in range(-LIMIT, LIMIT + 1):
            middle = a * Q(2) ** u + sign
            if middle <= 0:
                continue
            v = exponent(b / middle)
            if v is not None and -LIMIT <= v <= LIMIT:
                choices.append((abs(u) + abs(v) + 1, "read", u, v, sign))
    return min(choices)


def route_word(source, b, choice):
    cost, kind, u, v, sign = choice
    if kind == "reset":
        word = copy_prepare(source, b)
    elif kind == "power":
        word = shifts(WORK, u)
    elif kind == "read":
        require(sign in (-1, 1) and abs(u) <= LIMIT and abs(v) <= LIMIT,
                "invalid signed route")
        word = shifts(WORK, u)
        word += [("add" if sign == 1 else "subtract", WORK, source)]
        word += shifts(WORK, v)
    else:
        raise ValueError("unknown route kind")
    require(len(word) == cost, "route undercharged")
    return word


def block_word(events, mode="signed"):
    require(len(events) >= 2, "run needs two additions")
    key = eligible(events[0])
    require(key is not None and all(eligible(e) == key for e in events),
            "run crosses a source, frame, unit or non-scalar barrier")
    source, _ = key
    require(source != WORK and all(tuple(e[1][1]) != WORK for e in events),
            "private work alias")
    previous = None
    word = []
    for event in events:
        op = event[1]
        q = magnitude(op)
        if previous is None:
            word.extend(copy_prepare(source, q))
        else:
            word.extend(route_word(source, q, route(previous, q, mode)))
        word.append(("add" if Q(op[3], op[4]) > 0 else "subtract",
                     tuple(op[1]), WORK))
        previous = q
    word.append(("clear", WORK))
    return word
