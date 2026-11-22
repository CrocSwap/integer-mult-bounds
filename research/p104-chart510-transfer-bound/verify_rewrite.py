# SPDX-License-Identifier: Apache-2.0
"""Recover the full map, its transpose and the exact agreement kernel of the rewrite."""
from collections import Counter
from functools import reduce
import gzip
from hashlib import sha256
import json
from operator import xor
from pathlib import Path


HERE = Path(__file__).resolve().parent
SHA = "74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326"
A_READERS = (2336, 2344, 2416, 2439, 2448, 2451, 2482, 2655, 2698)
B_READERS = (2359, 2362, 2372, 2394, 2397, 2408, 2416, 2419, 2425, 2431,
             2434, 2465, 2484, 2518, 2530, 2571, 2576, 2584, 2600, 2617,
             2623, 2626, 2778)


def support(mask):
    return [i for i in range(mask.bit_length()) if mask & (1 << i)]


def dots(row, vector):
    return (row & vector).bit_count() % 2


def apply(rows, vector):
    return sum(dots(row, vector) << i for i, row in enumerate(rows))


def trace(word, program, *, backwards=False):
    """In reverse, CLEAR creates a zero adjoint and an initial zero has no adjoint."""
    start, end = (word["final"], word["start"]) if backwards else (word["start"], word["final"])
    count = len(start)
    charts = dict(enumerate(start))
    forms = {i: 1 << i for i in range(count)}
    retirements = []
    for op, target, *args in (reversed(program) if backwards else program):
        if op == ("CLEAR" if backwards else "INIT"):
            assert target >= count and target not in charts
            charts[target], forms[target] = args[0], 0
        elif op == ("INIT" if backwards else "CLEAR"):
            assert target >= count and charts.pop(target) == args[0]
            retirements.append((target, args[0], forms.pop(target)))
        elif op == "ADD":
            source, chart = args
            assert charts[source] == charts[target] == chart
            if backwards:
                forms[source] ^= forms[target]
            else:
                forms[target] ^= forms[source]
        elif op == "MOVE":
            before, after = reversed(args) if backwards else args
            assert charts[target] == before
            charts[target] = after
        else:
            assert op == "SWAP"
            source, = args
            forms[target], forms[source] = forms[source], forms[target]
            charts[target], charts[source] = charts[source], charts[target]
    assert charts == dict(enumerate(end)) and set(forms) == set(range(count))
    return [forms[i] for i in range(count)], retirements


def readout(owner, donors):
    return [["INIT", owner, 1], *(["ADD", owner, donor, 1] for donor in donors)]


def rewrite(word):
    tape = word["program"]
    assert tape[10034:10040] == [
        ["INIT", 2828, 510], ["ADD", 2828, 2337, 510], ["MOVE", 2828, 510, 1],
        ["INIT", 2829, 510], ["ADD", 2829, 2335, 510], ["MOVE", 2829, 510, 1],
    ]
    return tape[:10034] + readout(2828, B_READERS) + readout(2829, A_READERS) + tape[10040:]


def paid(word, program):
    dimensions = {int(i): frame["dim"] for i, frame in word["frames"].items()}
    return Counter(abs(dimensions[row[2]] - dimensions[row[3]])
                   for row in program if row[0] == "MOVE")


def main():
    raw = (HERE / "strong-bit.json.gz").read_bytes()
    assert sha256(raw).hexdigest() == SHA
    word = json.loads(gzip.decompress(raw))
    old, new = word["program"], rewrite(word)
    baseline, old_scrub = trace(word, old)
    changed, new_scrub = trace(word, new)
    baseline_dual, _ = trace(word, old, backwards=True)
    changed_dual, _ = trace(word, new, backwards=True)
    assert len(baseline) == 630 and baseline == [
        (1 << i) ^ (1 << (i - 111) if 111 <= i < 222 else 0) for i in range(630)
    ]
    assert [(r, c) for r, c, _ in old_scrub] == [(r, c) for r, c, _ in new_scrub]
    assert len(old_scrub) == 3433
    old_ops, new_ops = (Counter(row[0] for row in tape) for tape in (old, new))
    assert new_ops - old_ops == {"ADD": 30} and old_ops - new_ops == {"MOVE": 2}
    assert paid(word, old) - paid(word, new) == {1: 2} and not (paid(word, new) - paid(word, old))

    delta = [a ^ b for a, b in zip(baseline, changed, strict=True)]
    ra, rb = delta[92], delta[63]
    sa = sum((row == ra) << i for i, row in enumerate(delta))
    sb = sum((row == rb) << i for i, row in enumerate(delta))
    assert (ra.bit_count(), rb.bit_count(), (ra | rb).bit_count()) == (29, 18, 46)
    assert all(row in (0, ra, rb) for row in delta)
    assert support(sa) == [92, 99, 231, 428, 433, 434, 435, 448, 449, 473, 516, 582]
    assert support(sb) == [63, 222, 230, 362, 367, 368, 369]
    assert all((word["start"][h], word["final"][h]) == (0, 1) for h in support(ra | rb))
    assert all(word["final"][i] == 1 for i in support(sa | sb))
    # The rank-two formula is independently read in the reverse instruction order.
    for i, (before, after) in enumerate(zip(baseline_dual, changed_dual, strict=True)):
        assert (before ^ after) == ((sa if ra & (1 << i) else 0) ^ (sb if rb & (1 << i) else 0))
    assert sum(((row & ~(ra | rb)) != 0) for row in delta) == 0
    assert apply(delta, 1 << 266) == sa and apply(delta, 1 << 254) == sb
    # M is self-inverse. The columns of M^{-1}S are two explicit collisions.
    collisions = [apply(baseline, s) for s in (sa, sb)]
    pairing = [[dots(row, v) for v in collisions] for row in (ra, rb)]
    assert pairing == [[1, 0], [0, 1]]
    assert all(apply(changed, v) == 0 for v in collisions)
    assert [apply(baseline, v) for v in collisions] == [sa, sb]
    for zeros, expected_dirty in ((ra | rb, 3344), (((1 << 630) - (1 << 222)), 2617)):
        for rows in (old_scrub, new_scrub):
            assert sum(bool(form & ~zeros) for _, _, form in rows) == expected_dirty
    print(json.dumps({
        "public_rows": 630, "agreement_dimension": 628, "changed_map_rank": 628,
        "residual_a": support(ra), "residual_b": support(rb),
        "signature_a": support(sa), "signature_b": support(sb),
        "collision_inputs": list(map(support, collisions)), "residual_collision_pairing": pairing,
        "private_clears": len(new_scrub), "paid_moves": [old_ops["MOVE"], new_ops["MOVE"]],
        "paid_grade_one": [paid(word, old)[1], paid(word, new)[1]],
        "cochart_adds": [old_ops["ADD"], new_ops["ADD"]],
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
