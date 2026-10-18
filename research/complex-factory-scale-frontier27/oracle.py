#!/usr/bin/env python3
"""Separate exhaustive primitive execution on an exact fixed binary grid.

Does not import verify.py, its tables, cost formula, constructor or interpreter.
Ross Richardson with substantial OpenAI Codex assistance, Apache-2.0.
"""
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GRID = 1 << 128


def check(ok, message):
    if not ok:
        raise ValueError(message)


def signed_power(n, d):
    sign = 1 if n * d > 0 else -1
    n, d = abs(n), abs(d)
    check(n > 0 and d > 0 and n & (n - 1) == 0 and d & (d - 1) == 0, "bad dyadic power")
    return sign, n.bit_length() - d.bit_length()


def normalize(word):
    """Commute all diagonal scales to the END and retain normalized shears."""
    signs, powers, uses = [1] * 8, [0] * 8, [0] * 8
    shears, scales = [], []
    for op in word:
        if op[0] == "scale":
            r = op[1]
            sign, power = signed_power(op[2], op[3])
            signs[r] *= sign
            powers[r] += power
            scales.append((r, sign, power))
        elif op[0] == "add":
            t, s = op[1:3]
            sign, power = signed_power(op[3], op[4])
            shears.append((t, s, sign * signs[t] * signs[s], power + powers[s] - powers[t]))
            uses[t] += 1
            uses[s] += 1
        else:
            raise ValueError("unknown macro")
    return shears, uses, signs, powers


def expand(shears, uses, signs, powers, positions):
    """Materialize a new stream directly from scale-free normalized shears."""
    clocks, applied = [0] * 8, set()
    primitives = []
    macros = 0

    def scale(r):
        nonlocal macros
        if r in positions and r not in applied and positions[r] == clocks[r]:
            primitives.extend([("D" if powers[r] > 0 else "H", r)] * abs(powers[r]))
            if signs[r] < 0:
                primitives.append(("N", r))
            applied.add(r)
            macros += 1

    for t, s, sign, power in shears:
        scale(t)
        scale(s)
        p = power + (powers[t] if t in applied else 0) - (powers[s] if s in applied else 0)
        sg = sign * (signs[t] if t in applied else 1) * (signs[s] if s in applied else 1)
        if p:
            primitives.append(("C", 8, s))
            primitives.extend([("D" if p > 0 else "H", 8)] * abs(p))
            source = 8
        else:
            source = s
        primitives.append(("A" if sg > 0 else "S", t, source))
        primitives.append(("Z", 8))
        clocks[t] += 1
        clocks[s] += 1
        macros += 1
    for r in range(8):
        scale(r)
    check(applied == set(positions) and clocks == uses, "placement did not finish")
    return primitives, macros


def execute(primitives):
    rows = [[GRID if i == j else 0 for j in range(9)] for i in range(9)]
    for op in primitives:
        tag, r = op[:2]
        if tag == "Z":
            rows[r] = [0] * 9
        elif tag == "C":
            rows[r] = rows[op[2]].copy()
        elif tag == "D":
            rows[r] = [x * 2 for x in rows[r]]
        elif tag == "H":
            check(all(x % 2 == 0 for x in rows[r]), "fixed grid insufficient; would round")
            rows[r] = [x // 2 for x in rows[r]]
        elif tag == "N":
            rows[r] = [-x for x in rows[r]]
        elif tag == "A":
            rows[r] = [x + y for x, y in zip(rows[r], rows[op[2]])]
        elif tag == "S":
            rows[r] = [x - y for x, y in zip(rows[r], rows[op[2]])]
        else:
            raise ValueError("unknown primitive")
    check(rows[8] == [0] * 9, "private work remains dirty")
    return rows


def original_primitives(word):
    """Literal source stream, without commuting any scales."""
    out = []
    for op in word:
        if op[0] == "scale":
            sign, p = signed_power(op[2], op[3])
            out.extend([("D" if p > 0 else "H", op[1])] * abs(p))
            if sign < 0:
                out.append(("N", op[1]))
        else:
            sign, p = signed_power(op[3], op[4])
            t, s = op[1:3]
            if p:
                out.append(("C", 8, s))
                out.extend([("D" if p > 0 else "H", 8)] * abs(p))
                s = 8
            out.extend([("A" if sign > 0 else "S", t, s), ("Z", 8)])
    return out


def run(word):
    shears, uses, signs, powers = normalize(word)
    moving = [r for r in range(8) if powers[r]]
    sign_only = [r for r in range(8) if not powers[r] and signs[r] == -1]
    check(sign_only == [5], "unexpected sign-only quotient")
    reference = execute(original_primitives(word))
    hist, winners, count, best = Counter(), [], 0, 10 ** 9
    # Different ordering and sign-only representative than the primary census.
    for values in itertools.product(*(range(uses[r], -1, -1) for r in moving)):
        positions = dict(zip(moving, values))
        positions[5] = 27 % (uses[5] + 1)
        stream, macros = expand(shears, uses, signs, powers, positions)
        check(macros == 32, "wrong macro bill")
        check(execute(stream) == reference, "arbitrary-input endpoint differs")
        cost = len(stream)
        hist[cost] += 1
        count += 1
        if cost < best:
            best, winners = cost, []
        if cost == best:
            winners.append({str(r): positions[r] for r in moving})
    return {"histogram_magnitude": {str(k): v for k, v in sorted(hist.items())},
            "magnitude_placements": count, "minimum_primitives": best,
            "optimal_magnitude_positions": winners, "exact_columns_each": 9,
            "sign_only_representative": 27 % (uses[5] + 1),
            "exact_endpoint_replays": count, "grid_bits": 128}


def main():
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    for rel, sha in pins.items():
        check(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, "source pin: " + rel)
    word = json.loads((HERE / "sources/PR924-COMPOSITION.json").read_text())["replacement"]
    result = run(word)
    expected = json.loads((HERE / "EXPECTED.json").read_text())
    for key in ("histogram_magnitude", "magnitude_placements", "minimum_primitives", "optimal_magnitude_positions"):
        check(result[key] == expected[key], "independent mismatch: " + key)
    print(json.dumps(result, sort_keys=True))
    print("PASS_FACTORY_SCALE_ORACLE matrices=39424 columns=9 minimum=73 no_rounding")


if __name__ == "__main__":
    main()
