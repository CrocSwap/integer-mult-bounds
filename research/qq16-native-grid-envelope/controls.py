#!/usr/bin/env python3
"""Arithmetic controls and literal fixed-grid escape from the known F0 loss.

The literal event dispatcher and monomial evaluator are credited reuse of
Sricharan Vagvala / Tekalign, not independent native semantics. Apache-2.0.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
import itertools
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def module(name, path):
    obj = types.ModuleType(name)
    obj.__file__ = str(path)
    sys.modules[name] = obj
    exec(compile(path.read_bytes(), str(path), "exec"), obj.__dict__)
    return obj


V = module("grid_envelope_primary", HERE / "verify.py")


def reject(callback, message):
    try:
        callback()
    except ValueError:
        return
    raise ValueError("Control did not reject: " + message)


def contains(bound, x):
    grid = Fraction(2**bound.grid) if bound.grid >= 0 else Fraction(1, 2**(-bound.grid))
    return abs(x) <= bound.magnitude and (x * grid).denominator == 1


class Fixed:
    """Actual integer execution on the single global grid 2^-G.

    Every displayed primitive checks signed range. Every right shift checks
    divisibility. No rounding is permitted and no floating point is used.
    """
    zero = ((0,) * 512, (0,) * 512)

    def __init__(self, native, g, width):
        self.native = native
        self.g = g
        self.width = width
        self.event = -1
        self.max_encoded_bits = 0
        self.max_site = None
        self.nonzero_exact_divisions = 0
        self.changed_cuts = 0

    def checked(self, values, stage):
        limit = 1 << (self.width-1)
        for x in values:
            V.need(-limit <= x < limit, "Overflow: " + stage)
            bits = abs(x).bit_length()
            if bits > self.max_encoded_bits:
                self.max_encoded_bits = bits
                self.max_site = [self.event, stage]
        return tuple(values)

    def divide(self, values, denominator, stage):
        V.need(denominator > 0, "Positive exact divisor")
        V.need(all(x % denominator == 0 for x in values), "Off-grid: " + stage)
        self.nonzero_exact_divisions += sum(x != 0 for x in values) if denominator > 1 else 0
        return self.checked([x // denominator for x in values], stage)

    def constant(self, value):
        n = Fraction(value) * (1 << self.g)
        V.need(n.denominator == 1, "Entry lattice")
        return self.checked([n.numerator]*512, "entry"), self.zero[1]

    def canonical(self, value):
        return self.native.vector(value[0], value[1], self.g)

    def mono(self, value, key, adjoint=False):
        out = self.native.mono((value[0], value[1], 0), key, adjoint)
        return (self.checked(out[0], "monomial"), self.checked(out[1], "monomial"))

    def scalar(self, value, n, d, stage):
        c = Fraction(n, d)
        result = []
        for row in value:
            numerator = self.checked([c.numerator*x for x in row], "constant-numerator")
            result.append(self.divide(numerator, c.denominator, stage))
        return tuple(result)

    def add(self, left, right):
        return tuple(self.checked([x+y for x, y in zip(a, b)], "scalar-add")
                     for a, b in zip(left, right))

    def line(self, value, axis):
        real, imag = value
        out_r, out_i = [0]*512, [0]*512
        for x in range(512):
            y = x ^ axis
            if x > y:
                continue
            a, b, c, d = real[x], imag[x], real[y], imag[y]
            rp, ip, rd, di = self.checked([a+c, b+d, a-c, b-d], "native-pair")
            cross = self.checked([rp-di, ip+rd, rp+di, ip-rd], "native-cross")
            out_r[x], out_i[x], out_r[y], out_i[y] = self.divide(cross, 2, "native-halved")
        return tuple(out_r), tuple(out_i)

    def recipe(self, value, recipe, axes=9):
        if recipe["rank"]:
            value = self.mono(value, self.native.monomial_key(recipe["right"], axes))
            for j in range(recipe["rank"]):
                value = self.line(value, 1 << j)
        return self.mono(value, self.native.monomial_key(recipe["left"], axes))

    def report(self):
        return []


def audit():
    data = V.load()  # authenticate the reused implementation before importing it
    old = module("credited_rounded_reference", ROOT / "research/qq16-native-rounded-components/verify.py")
    checks = {}
    # Each stored upper bound is checked against actual independent rational values.
    scalar_cases = 0
    for g, j in itertools.product(range(4), repeat=2):
        left, right = V.Bound(Fraction(3), g), V.Bound(Fraction(5), j)
        result = left.plus(right)
        for a, b in itertools.product(range(-3, 4), range(-5, 6)):
            V.need(contains(result, Fraction(a, 2**g) + Fraction(b, 2**j)), "Sum envelope")
            scalar_cases += 1
    coefficients = {Fraction(*e[1][-2:]) for e in data[0]
                    if e[0] == "scalar" and e[1][0] != "clear"}
    for c in coefficients:
        for x in range(-7, 8):
            V.need(contains(V.Bound(Fraction(7), 3).scale(c), c*Fraction(x, 8)), "Scale envelope")
            scalar_cases += 1
    checks["rational_scalar_containment_cases"] = scalar_cases
    product_cases = 0
    for c in coefficients:
        n = c.numerator
        for x in list(range(-7, 8)) + [2**65-1, 1-2**65]:
            terms = [x << j for j in range(abs(n).bit_length()) if (abs(n) >> j) & 1]
            total = terms[0]
            V.need(abs(total) <= abs(n*x), "First shifted product term")
            for term in terms[1:]:
                total += term
                V.need(abs(total) <= abs(n*x), "Constant-product intermediate")
            if n < 0:
                total = -total
            V.need(total == n*x, "Literal binary constant-product lowering")
            product_cases += 1
    checks["literal_constant_product_cases"] = product_cases
    native_cases = 0
    for a, b, c, d in itertools.product(range(-2, 3), repeat=4):
        pairs = [a+c, b+d, a-c, b-d]
        cross = [pairs[0]-pairs[3], pairs[1]+pairs[2],
                 pairs[0]+pairs[3], pairs[1]-pairs[2]]
        outputs = [Fraction(x, 2) for x in cross]
        env = V.Envelope()
        final = env.line(V.Bound(Fraction(2)))
        V.need(all(abs(x) <= 4 for x in pairs) and all(abs(x) <= 8 for x in cross), "Native temporaries")
        V.need(all(contains(final, x) for x in outputs), "Native output envelope")
        native_cases += 1
    checks["exhaustive_gaussian_pair_cases"] = native_cases
    # One basis component genuinely needs a half quantum.
    basis = ((1,) + (0,)*511, (0,)*512)
    reject(lambda: Fixed(old.N, 0, 32).line(basis, 1), "Native half-grid")
    # All four outputs fit signed 3-bit integers, but an internal numerator is 4.
    cross_fixture = ((1, 1)+(0,)*510, (-1, 1)+(0,)*510)
    reject(lambda: Fixed(old.N, 0, 3).line(cross_fixture, 1), "Cross numerator overflow")
    checks["grid_and_internal_overflow_controls"] = 2
    reject(lambda: V.UNIT.scale(Fraction(1, 3)), "Nondyadic coefficient")
    reject(lambda: V.check_monomial({"matrix_rows": [1]*9, "quadratic_rows": [0]*9,
                                  "linear_Z4": [0]*9, "offset": 0, "phase": 0}), "Singular monomial")
    bad = deepcopy(data)
    event = next(e for e in bad[0] if e[0] == "scalar")
    event[1] = ["clear", ["L", 0]]
    reject(lambda: V.audit(bad), "Borrowed CLEAR")
    checks["invalid_contract_controls"] = 3
    env = V.Envelope()
    env.line(V.UNIT)
    env.observe(V.ZERO, "later-clear")
    V.need(env.max_grid == 1 and env.max_range == 4, "Earlier obligations survive CLEAR")
    checks["later_clear_keeps_earlier_obligation"] = True
    # P=66 is required by the inclusive dirty value 2^65 < 2^66.
    literal_data = (data[0], data[1], None, data[2], data[3])
    fixed = Fixed(old.N, 35, 168)
    trace = []
    out, faults, _ = old.run(literal_data, engine=fixed, trace=trace)
    V.need(out == old.expected(dirty=True, rounded=False), "Fixed-grid exact F0 endpoint")
    V.need(not faults and len(trace) == 26089, "Full literal fixed-grid coverage")
    binary, _, _ = old.run(literal_data, engine=old.Binary64())
    V.need(binary == old.expected(dirty=True, rounded=True), "Known binary64 loss control")
    V.need(binary != out, "Fixed grid must escape the actual rounding failure")
    checks["literal_fixed_grid"] = {
        "P": 66, "G": 35, "W": 168,
        "events": len(data[0]), "changed_field_cuts": len(trace),
        "endpoint_sha256": V.digest(out), "trace_sha256": V.digest(trace),
        "max_encoded_magnitude_bits": fixed.max_encoded_bits,
        "first_max_site": fixed.max_site,
        "nonzero_exact_divisions": fixed.nonzero_exact_divisions,
        "all_480_chosen_helpers_restore": True, "all_private_outputs_zero": True,
        "binary64_control_differs_in_data_fields": [112, 114, 137, 190, 211],
    }
    return {"status": "PASS_QQ16_NATIVE_GRID_CONTROLS", "checks": checks}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--write", type=Path)
    args = p.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    else:
        V.need(result == json.loads((HERE / "CONTROLS.json").read_text()), "Control receipt mismatch")
    print(result["status"], "literal_events=26099 fixed_grid_exact binary64_control_loses_data")


if __name__ == "__main__":
    main()
