"""Bounded fan-in Horner words, extending Ross Richardson's PR945 pair method.

Prepared for ToikY with substantial OpenAI Codex assistance. Apache-2.0.
Primitive vocabulary and copy/unit lowering credit icekylinx and PR696.
"""
from fractions import Fraction as Q

WORK = ("W", 0)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def coefficient(op):
    need(len(op) == 5 and op[0] == "add", "expected ADD")
    need(type(op[3]) is int and type(op[4]) is int and op[4] > 0, "rational encoding")
    q = Q(op[3], op[4])
    need(q and q.denominator & (q.denominator - 1) == 0, "nonzero dyadic required")
    return q


def lower(op):
    """PR696 baseline, including the per-ADD private clear."""
    tag, target = op[0], tuple(op[1])
    need(target != WORK, "work alias")
    if tag == "clear":
        return [("clear", target)]
    if tag == "copy":
        source = tuple(op[2]); need(source != WORK, "work source")
        return [("copy", target, source)]
    if tag == "scale":
        q = Q(op[2], op[3]); a, d = abs(q.numerator), q.denominator
        need(a > 0 and a & (a-1) == 0 and d & (d-1) == 0, "nonbinary scale")
        shift = a.bit_length() - d.bit_length()
        return [("double" if shift > 0 else "halve", target)] * abs(shift) + ([("negate", target)] if q < 0 else [])
    q = coefficient(op); source = tuple(op[2])
    need(len({target, source, WORK}) == 3, "ADD alias")
    accumulate = "add" if q > 0 else "subtract"
    if abs(q) == 1:
        return [(accumulate, target, source), ("clear", WORK)]
    result = [("copy", WORK, source)]
    for bit in bin(abs(q.numerator))[3:]:
        result.append(("double", WORK))
        if bit == "1":
            result.append(("add", WORK, source))
    result += [("halve", WORK)] * (q.denominator.bit_length() - 1)
    return result + [(accumulate, target, WORK), ("clear", WORK)]


def compatible(window):
    if not 2 <= len(window) <= 4:
        return False
    if any(len(e) != 3 or e[0] != "scalar" or e[1][0] != "add" or
           type(e[2]) is not int or e[2] <= 0 for e in window):
        return False
    if len({e[2] for e in window}) != 1 or len({tuple(e[1][1]) for e in window}) != 1:
        return False
    regs = [tuple(window[0][1][1]), WORK] + [tuple(e[1][2]) for e in window]
    return len(set(regs)) == len(regs)


def joint(window):
    need(compatible(window), "incompatible joint window")
    qs = [coefficient(e[1]) for e in window]
    target = tuple(window[0][1][1]); sources = [tuple(e[1][2]) for e in window]
    k = max(q.denominator.bit_length() - 1 for q in qs)
    ns = [q.numerator * ((1 << k) // q.denominator) for q in qs]
    height = max(abs(n).bit_length() for n in ns)
    word, sign = [], None
    for bit in range(height - 1, -1, -1):
        if sign is not None:
            word.append(("double", WORK))
        for n, source in zip(ns, sources):
            if abs(n) >> bit & 1:
                direction = 1 if n > 0 else -1
                if sign is None:
                    sign = direction
                    word.append(("copy", WORK, source))
                else:
                    word.append(("add" if direction == sign else "subtract", WORK, source))
    word += [("halve", WORK)] * k
    word += [("add" if sign == 1 else "subtract", target, WORK), ("clear", WORK)]
    need(len(word) == height + sum(abs(n).bit_count() for n in ns) + k + 1, "joint bill")
    return word


def census(events):
    rows = []
    for start in range(len(events)):
        for length in (2, 3, 4):
            w = events[start:start+length]
            if len(w) != length or not compatible(w):
                continue
            before = sum(len(lower(e[1])) for e in w)
            after = len(joint(w))
            rows.append(dict(start=start, length=length, frame=w[0][2],
                             coefficients=[str(coefficient(e[1])) for e in w],
                             before=before, after=after, saving=before-after))
    return rows


def choose(events, rows, limit=4):
    """Exact interval DP; ties skip, then prefer the shorter first window."""
    options = {}
    for r in rows:
        if r["length"] <= limit and r["saving"] > r["length"] - 1:
            options.setdefault(r["start"], []).append(r)
    scores = [0] * (len(events) + 5); take = {}
    for i in range(len(events)-1, -1, -1):
        scores[i] = scores[i+1]
        for r in options.get(i, []):
            score = r["saving"] + scores[i+r["length"]]
            if score > scores[i]:
                scores[i] = score; take[i] = r["length"]
    selected, i = [], 0
    while i < len(events):
        if i in take:
            selected.append([i, take[i]]); i += take[i]
        else:
            i += 1
    return selected, scores[0]


def emitted(events, recipe):
    lookup = dict(recipe)
    need(len(lookup) == len(recipe) and recipe == sorted(recipe), "duplicate or unsorted recipe")
    i = 0
    while i < len(events):
        e = events[i]
        if i in lookup:
            length = lookup[i]; window = events[i:i+length]
            need(type(length) is int and len(window) == length and compatible(window), "recipe window")
            need(not any(j in lookup for j in range(i+1, i+length)), "overlapping recipe")
            for op in joint(window):
                yield ["primitive", list(op), e[2]]
            i += length
        else:
            if e[0] == "scalar":
                for op in lower(e[1]):
                    yield ["primitive", list(op), e[2]]
            else:
                yield e
            i += 1
    need(all(type(start) is int and 0 <= start < len(events) for start in lookup), "recipe index")
