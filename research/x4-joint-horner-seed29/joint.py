"""Two-source binary Horner circuits; Ross Richardson / OpenAI Codex.

Apache-2.0. Baseline primitive vocabulary follows icekylinx and PR696.
No repository state, stored witness, or search result is imported here.
"""
from fractions import Fraction

WORK = ("W", 0)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def coefficient(op):
    require(len(op) == 5 and op[0] == "add", "expected ADD")
    require(type(op[3]) is int and type(op[4]) is int and op[4] > 0,
            "invalid rational encoding")
    q = Fraction(op[3], op[4])
    require(q != 0 and q.denominator & (q.denominator - 1) == 0,
            "nonzero dyadic required")
    return q


def compatible(first, second):
    if first[0] != "scalar" or second[0] != "scalar":
        return False
    if first[2] != second[2] or first[2] == 0:
        return False
    a, b = first[1], second[1]
    if a[0] != "add" or b[0] != "add" or a[1] != b[1]:
        return False
    regs = (tuple(a[1]), tuple(a[2]), tuple(b[2]))
    return len(set(regs)) == 3 and WORK not in regs


def lower_pair(a, b):
    """(T,S1,S2,W) -> (T+a*S1+b*S2,S1,S2,0), arbitrary input W.

    All returned operations must be hosted at the two original common frames.
    Frame compatibility is checked by the caller on the complete events.
    """
    qs = [coefficient(a), coefficient(b)]
    target, sources = tuple(a[1]), [tuple(a[2]), tuple(b[2])]
    require(a[1] == b[1] and len({target, *sources, WORK}) == 4,
            "pair register alias")
    k = max(q.denominator.bit_length() - 1 for q in qs)
    nums = [q.numerator * ((1 << k) // q.denominator) for q in qs]
    bits = max(abs(x).bit_length() for x in nums)
    word = []
    sign = None
    for bit in range(bits - 1, -1, -1):
        if sign is not None:
            word.append(("double", WORK))
        for n, source in zip(nums, sources):
            if (abs(n) >> bit) & 1:
                direction = 1 if n > 0 else -1
                if sign is None:
                    sign = direction
                    word.append(("copy", WORK, source))
                else:
                    word.append(("add" if sign == direction else "subtract", WORK, source))
    word.extend([("halve", WORK)] * k)
    word.extend([("add" if sign == 1 else "subtract", target, WORK), ("clear", WORK)])
    expected = bits + sum(abs(x).bit_count() for x in nums) + k + 1
    require(len(word) == expected, "joint cost formula")
    return word


def plan(events, baseline_lower):
    """Maximum total saving among disjoint strictly arithmetic-saving pairs.

    Delta must exceed one, so every retained pair improves on deleting only
    one redundant coefficient-work clear. Ties skip the earlier pair (seed 29).
    """
    census, options = [], {}
    for i in range(len(events) - 1):
        a, b = events[i:i + 2]
        if not compatible(a, b):
            continue
        word = lower_pair(a[1], b[1])
        before = len(baseline_lower(a[1])) + len(baseline_lower(b[1]))
        delta = before - len(word)
        row = {"event": i, "frame": a[2], "coefficients": [str(coefficient(a[1])), str(coefficient(b[1]))],
               "before": before, "after": len(word), "saving": delta}
        census.append(row)
        if delta > 1:
            options[i] = row
    scores = [0] * (len(events) + 2)
    take = set()
    for i in range(len(events) - 1, -1, -1):
        scores[i] = scores[i + 1]
        if i in options and options[i]["saving"] + scores[i + 2] > scores[i]:
            scores[i] = options[i]["saving"] + scores[i + 2]
            take.add(i)
    selected, i = [], 0
    while i < len(events):
        if i in take:
            selected.append(i)
            i += 2
        else:
            i += 1
    require(sum(options[i]["saving"] for i in selected) == scores[0], "path optimum")
    return census, selected, scores
