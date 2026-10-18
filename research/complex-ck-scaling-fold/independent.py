#!/usr/bin/env python3
"""Independent finite CK search and boundary check. Apache-2.0.

Prepared for @thakrarsagar with substantial OpenAI Codex assistance.
Credits the selected #626 CK construction and icekylinx's Horner accounting.
Uses dyadic valuations and integer matrices; imports no construction/verifier.
"""
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "research/community-k492-audit/pr626/replay/mixed-global/base/providers/ck/CANONICAL-WORD.json.gz"
SOURCE_SHA256 = "9bbc75dede090cfd7a0a0252424ea9d9f6211e2350d2a801d4e4f2f0784167c7"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def valuation(n):
    n = abs(n)
    need(n > 0, "zero coefficient")
    return (n & -n).bit_length() - 1


def exponent(numerator, denominator):
    need(denominator > 0 and denominator & (denominator - 1) == 0, "non-dyadic denominator")
    return valuation(numerator) - valuation(denominator)


def scan(ops):
    # For a = odd * 2**e, Horner cost is 2 + bits(odd) + popcount(odd) + abs(e).
    best, minimizers, candidates, shortest = 0, 0, 0, None
    for i, scale in enumerate(ops):
        if scale[0] != "scale":
            continue
        _, register, numerator, denominator, _ = scale
        need(abs(numerator) & (abs(numerator) - 1) == 0, "nonbinary scale")
        shift = exponent(numerator, denominator)
        deltas = [0] * len(ops)
        for direction in (-1, 1):
            delta = 0
            stop = -1 if direction < 0 else len(ops)
            for j in range(i + direction, stop, direction):
                e = ops[j]
                if e[0] == "add":
                    power = exponent(e[3], e[4])
                    change = shift * ((e[2] == register) - (e[1] == register)) * direction
                    delta += abs(power + change) - abs(power)
                deltas[j] = delta
        candidates += len(deltas)
        for j, delta in enumerate(deltas):
            if delta < best:
                best, minimizers, shortest = delta, 0, None
            if delta == best:
                minimizers += 1
                choice = (abs(j - i), i, j)
                shortest = choice if shortest is None else min(shortest, choice)
    return candidates, best, minimizers, shortest


def dual(e):
    if e[0] == "add":
        return ["add", e[2], e[1], -e[3], e[4], e[-1]]
    return ["scale", e[1], e[3], e[2], e[-1]]


def integer_matrix(word, registers, backward):
    # Sixteenths cover this pinned 38-gate interval and all four mutations.
    # Every division is checked, so insufficient precision fails explicitly.
    rows = {r: {r: 16} for r in registers}
    for raw in word:
        e = dual(raw) if backward else raw
        target = e[1]
        if e[0] == "add":
            for column, value in rows[e[2]].items():
                product = e[3] * value
                need(product % e[4] == 0, "integer matrix lost precision")
                rows[target][column] = rows[target].get(column, 0) + product // e[4]
            rows[target] = {c: v for c, v in rows[target].items() if v}
        else:
            for column, value in rows[target].items():
                product = e[2] * value
                need(product % e[3] == 0, "integer matrix lost precision")
                rows[target][column] = product // e[3]
    return rows


def main():
    raw = gzip.decompress((ROOT / SOURCE).read_bytes())
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "native source hash mismatch")
    word = json.loads(raw)
    ops = word["cleanup"]
    need(len(ops) == 8309 and sum(e[0] == "scale" for e in ops) == 123, "search domain changed")
    for e in ops:
        need(e[0] in ("add", "scale") and e[-1] == 1, "invalid cleanup operation/frame")
        registers = e[1:3] if e[0] == "add" else e[1:2]
        need(all(word["final"][r] == 1 for r in registers), "non-FULL terminal frame")
        if e[0] == "add":
            need(e[1] != e[2], "self-addition")
    result = scan(ops)
    need(result == (1022007, -31, 644, (37, 4832, 4869)), "independent search mismatch")

    before = ops[4832:4870]
    need(before[0] == ["scale", 97, 2, 1, 1], "unexpected selected scale")
    need(all(e[0] == "add" and e[2] == 97 for e in before[1:]), "interval is not source fanout")
    need(len({e[1] for e in before[1:]}) == 37, "fanout targets repeat")
    after = []
    for original in before[1:]:
        e = original.copy()
        divisor = gcd(2 * e[3], e[4])
        e[3], e[4] = 2 * e[3] // divisor, e[4] // divisor
        after.append(e)
    after.append(before[0].copy())
    registers = sorted({r for e in before for r in (e[1:3] if e[0] == "add" else e[1:2])})
    need(len(registers) == 38, "boundary register count")
    controls = 0
    for backward in (False, True):
        expected = integer_matrix(before, registers, backward)
        need(expected == integer_matrix(after, registers, backward), "boundary map differs")
        mutations = [after[:-1]]
        unadjusted = [e.copy() for e in after]
        unadjusted[0] = before[1].copy()
        mutations.append(unadjusted)
        wrong_scale = [e.copy() for e in after]
        wrong_scale[-1][2] = 4
        mutations.append(wrong_scale)
        wrong_sign = [e.copy() for e in after]
        wrong_sign[0][3] *= -1
        mutations.append(wrong_sign)
        for mutation in mutations:
            need(expected != integer_matrix(mutation, registers, backward), "negative control accepted")
            controls += 1
    need(controls == 8, "missing negative controls")
    print("PASS_INDEPENDENT_CK_SCALE positions=1022007 min_delta=-31 minimizers=644 columns=38/38 controls=8")


if __name__ == "__main__":
    main()
