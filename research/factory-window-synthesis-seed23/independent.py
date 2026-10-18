#!/usr/bin/env python3
"""Finite-field lower-bound check, separate from the rational constructor.

Imports no synthesis, matrix, cost or predecessor implementation. Every dyadic
word maps into F_65537; a modular exclusion therefore excludes that rational
word too. Collisions can weaken this lower bound, never strengthen it.
Hanson Sun with substantial OpenAI Codex assistance. Apache-2.0.
"""

from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P = 65537


def ensure(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def unit(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def mul(left, right, modulus=P):
    columns = list(zip(*right))
    return tuple(tuple(sum(a * b for a, b in zip(row, col)) % modulus
                       for col in columns) for row in left)


def invert(matrix):
    n = len(matrix)
    aug = [list(row) + list(unit(n)[i]) for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if aug[r][col]), None)
        ensure(pivot is not None, "singular matrix")
        aug[pivot], aug[col] = aug[col], aug[pivot]
        q = pow(aug[col][col], P - 2, P)
        aug[col] = [(x * q) % P for x in aug[col]]
        for r in range(n):
            if r != col:
                q = aug[r][col]
                aug[r] = [(x - q * y) % P for x, y in zip(aug[r], aug[col])]
    return tuple(tuple(row[n:]) for row in aug)


def transpose(matrix):
    return tuple(zip(*matrix))


def gate_matrix(n, kind, t, s, q):
    rows = [list(row) for row in unit(n)]
    value = (q.numerator * pow(q.denominator, P - 2, P)) % P
    rows[t][t if kind == "scale" else s] = value
    return tuple(tuple(row) for row in rows)


def instructions(kind, t, s, q):
    # Independent literal PR696 primitive expansion, not the cost formula.
    out = []
    if kind == "scale":
        numerator, denominator = abs(q.numerator), q.denominator
        while numerator > 1:
            out.append(("twice", t))
            numerator //= 2
        while denominator > 1:
            out.append(("half", t))
            denominator //= 2
        if q < 0:
            out.append(("minus", t))
        return out
    if abs(q) == 1:
        return [("accumulate", t, s, 1 if q > 0 else -1), ("zero", "work")]
    out.append(("assign", "work", s))
    numerator, denominator = abs(q.numerator), q.denominator
    while numerator > 1:
        out.append(("twice", "work"))
        numerator //= 2
    while denominator > 1:
        out.append(("half", "work"))
        denominator //= 2
    out.extend([("accumulate", t, "work", 1 if q > 0 else -1), ("zero", "work")])
    return out


def generators(n):
    # Intentionally different ordering and representation from verify.py.
    qs = tuple(map(Fraction, ("1", "-1", "2", "-2", "1/2", "-1/2")))
    out = []
    for q in qs:
        for t in reversed(range(n)):
            if q != 1:
                out.append((gate_matrix(n, "scale", t, None, q), len(instructions("scale", t, None, q))))
            for s in reversed(range(n)):
                if s != t:
                    out.append((gate_matrix(n, "add", t, s, q), len(instructions("add", t, s, q))))
    ensure(len(out) == 6 * n * n - n, "generator inventory")
    return out


def frontier(n):
    edges = generators(n)
    states = {unit(n): (0, 0)}
    for matrix, charge in edges:
        price = (1, charge)
        states[matrix] = min(states.get(matrix, price), price)
    # Enumerate every ordered pair, not just the states retained above.
    for a, a_charge in edges:
        for b, b_charge in edges:
            matrix = mul(a, b)
            price = (2, a_charge + b_charge)
            states[matrix] = min(states.get(matrix, price), price)
    inverses = [(invert(matrix), price) for matrix, price in states.items()]
    ensure(all(mul(matrix, invert(matrix)) == unit(n) for matrix in states), "inverse check")
    return states, inverses


def lower_bound(target, data):
    states, inverses = data
    best = None
    # Right factorization T = S F, with S = T F^{-1}; the primary search
    # instead removes literal suffix gates by sparse left row operations.
    for inverse_prefix, prefix_price in inverses:
        suffix = mul(target, inverse_prefix)
        if suffix in states:
            suffix_price = states[suffix]
            price = tuple(x + y for x, y in zip(prefix_price, suffix_price))
            if best is None or price < best:
                best = price
    return best


def source_matrix(block, wires):
    matrix = unit(len(wires))
    charge = 0
    for op in block:
        if op[0] == "add":
            _, target, source, numerator, denominator, _ = op
            source = wires.index(source)
        else:
            _, target, numerator, denominator, _ = op
            source = None
        target = wires.index(target)
        q = Fraction(numerator, denominator)
        matrix = mul(gate_matrix(len(wires), op[0], target, source, q), matrix)
        charge += len(instructions(op[0], target, source, q))
    return matrix, charge


def run():
    ensure(P > 2 and all(P % d for d in range(2, 257)), "field modulus not prime")
    pins = read(HERE / "SOURCES.json")
    for name, expected in pins["files"].items():
        ensure(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
               "independent source pin: " + name)
    source = read(ROOT / pins["object_path"])["replacement"]
    receipt = read(HERE / "EXPECTED.json")
    ensure(type(receipt["orientation_cases"]) is int and receipt["orientation_cases"] == 128,
           "orientation count")
    frontiers = {n: frontier(n) for n in (2, 3, 4)}
    for n, data in frontiers.items():
        ensure(len(data[0]) == receipt["frontiers"][str(n)]["distinct_prefix_matrices"],
               "finite-field/rational frontier cardinality")
    expected_windows = []
    checked = 0
    for width in (4, 5, 6):
        for first in range(33 - width):
            block = source[first:first + width]
            wire_set = set()
            for gate in block:
                wire_set.add(gate[1])
                if gate[0] == "add":
                    wire_set.add(gate[2])
            if len(wire_set) > 4:
                continue
            wires = sorted(wire_set)
            expected_windows.append((first, first + width, wires))
            records = [r for r in receipt["windows"] if (r["start"], r["stop"]) == (first, first + width)]
            ensure(len(records) == 1 and records[0]["wires"] == wires, "window inventory")
            matrix, charge = source_matrix(block, wires)
            ensure(charge == records[0]["original_primitives"], "literal primitive charge")
            ensure(records[0]["macro_lower_bound"] == min(width, 5)
                   and records[0]["macro_upper_bound"] == width, "macro bound interval")
            ensure(records[0]["primitive_minimum_at_minimum_length"] == (charge if width == 4 else None),
                   "primitive bound scope")
            orientations = {"forward": matrix, "inverse": invert(matrix),
                            "transpose": transpose(matrix), "inverse_transpose": transpose(invert(matrix))}
            ensure(set(records[0]["orientations"]) == set(orientations), "orientation inventory")
            for name, target in orientations.items():
                bound = lower_bound(target, frontiers[len(wires)])
                stored = records[0]["orientations"][name]["best"]
                ensure(bound == (None if stored is None else (stored["macros"], stored["primitives"])),
                       "independent minimum disagrees")
                ensure(bound == ((4, charge) if width == 4 else None), "claimed exclusion false")
                checked += 1
    actual_windows = [(r["start"], r["stop"], r["wires"]) for r in receipt["windows"]]
    ensure(expected_windows == actual_windows and len(expected_windows) == 32, "complete window census")
    # The independently generated alphabet must find a planted contraction and
    # distinguish a noncommuting reverse order; it cannot simply return None.
    a = gate_matrix(3, "add", 1, 2, Fraction(1))
    b = gate_matrix(3, "add", 0, 1, Fraction(1))
    c = gate_matrix(3, "add", 0, 2, Fraction(-1))
    ensure(lower_bound(mul(c, mul(b, a)), frontiers[3]) == (2, 4), "planted contraction")
    ensure(mul(a, b) != mul(b, a), "noncommuting control")
    ensure(lower_bound(unit(3), frontiers[3]) == (0, 0), "empty-word control")
    ensure(checked == 128, "incomplete independent coverage")
    print("PASS_FACTORY_WINDOW_MODULAR prime=65537 windows=32 orientations=128 "
          "same_lower_bounds planted_controls=3 no_new_kappa")


if __name__ == "__main__":
    run()
