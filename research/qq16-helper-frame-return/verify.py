#!/usr/bin/env python3
"""Exact, source-bound helper endpoint certificate. Nick Petalas. Apache-2.0."""

import argparse
import hashlib
import json
import types
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DIM = 512
HELPER = 224
INPUTS = {
    "research/qq16-native-rounded-components/verify.py",
    "research/qq16-native-rounded-components/SOURCES.json",
    "research/qq16-native-rounded-components/vendor/native.py",
    "research/joint-query/certificate.json.gz",
    "research/community-frontier1042-audit/selected-replay.tar.gz",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticated_source():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    pins = sources["files"]
    need(
        len(pins) == 7 and len({pin["path"] for pin in pins}) == 7,
        "Unique source inventory",
    )
    need(
        {pin["path"] for pin in pins if pin["usage"] == "input"} == INPUTS,
        "Complete live source inventory",
    )
    for pin in pins:
        if pin["usage"] == "input":
            path = ROOT / pin["path"]
            need(path.stat().st_size <= 32_000_000, "Source size bound")
            need(
                hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"],
                "Source hash: " + pin["path"],
            )
    path = ROOT / "research/qq16-native-rounded-components/verify.py"
    module = types.ModuleType("credited_reference")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def coefficient_bound(v, data):
    """Bound every column coefficient and its dyadic denominator, before packing."""
    children = {(r["old"], r["new"]): r for r in data[3]["children"]}
    h, grid = [Fraction(0)] * 712, [0] * 712
    h[HELPER] = Fraction(1)
    peak, guard = Fraction(1), 0
    need(len(data[0]) == 26099, "Literal event bound")
    for event in data[0]:
        kind = event[0]
        if kind == "phase":
            continue
        if kind == "scalar":
            gate = event[1]
            dst = v.reg(gate[1])
            if gate[0] == "clear":
                h[dst], grid[dst] = Fraction(0), 0
            else:
                c = Fraction(*gate[-2:])
                shift = c.denominator.bit_length() - 1
                need(c.denominator == 1 << shift, "Dyadic scalar")
                if gate[0] == "scale":
                    h[dst] *= abs(c)
                    grid[dst] += shift
                else:
                    need(gate[0] == "add", "Scalar kind")
                    src = v.reg(gate[2])
                    h[dst] += abs(c) * h[src]
                    grid[dst] = max(grid[dst], grid[src] + shift)
        elif kind == "climb":
            dst = event[2]
            grid[dst] += children[event[3], event[4]]["rank"]
        elif kind in ("adapter", "residual_adapter"):
            dst = event[2]
        else:
            need(kind == "native_line", "Native event kind")
            dst = v.reg(event[1])
            grid[dst] += data[1]["native_line_recipes"][event[2]]["recipe"]["rank"]
        peak, guard = max(peak, h[dst]), max(guard, grid[dst])
    need(guard <= 128 and peak < 2**64, "Packed arithmetic capacity")
    # peak < 2**bit_length(numerator), denominator scaling <= 2**guard.
    bits = peak.numerator.bit_length() + guard + 4
    need(bits <= 196, "Radix capacity")
    return peak, guard, bits


class ExactEntry:
    """The authenticated dispatcher supplies Y0, then L224; only L224 is nonzero."""

    def __init__(self, native, entry):
        self.native = native
        self.entry = entry
        self.zero = native.ZERO
        self.calls = 0
        self.event = None

    def constant(self, _value):
        self.calls += 1
        need(self.calls <= 2, "Exactly two initialized fields")
        return self.zero if self.calls == 1 else self.entry

    def canonical(self, value):
        return value

    def scalar(self, value, numerator, denominator, _stage):
        return self.native.scaled(value, Fraction(numerator, denominator))

    def add(self, left, right):
        return self.native.plus(left, right)

    def mono(self, value, key, adjoint=False):
        return self.native.mono(value, key, adjoint)

    def recipe(self, value, record, axes=9):
        return self.native.recipe(value, record, axes)

    def report(self):
        return []


def execute(v, data, entry):
    engine = ExactEntry(v.N, entry)
    state, faults, _cuts = v.run(data, engine=engine)
    need(engine.calls == 2 and not faults, "Exact entry execution")
    need(
        all(x == v.N.ZERO for i, x in enumerate(state) if i != HELPER),
        "No data, other-helper or private leakage",
    )
    return state[HELPER]


def product(native, value, sign=1):
    for axis in range(9):
        value = native.line(value, 1 << axis, sign)
    return value


def vector_hash(value):
    # Avoid Python's decimal conversion limit for the deliberately packed integers.
    re, im, exponent = value
    text = str(exponent) + ";" + ";".join(hex(x) for x in re + im)
    return hashlib.sha256(text.encode()).hexdigest()


def audit():
    v = authenticated_source()
    data = v.load()
    need(
        data[2]["start"][HELPER] == 0 and data[2]["final"][HELPER] == 1,
        "Literal helper endpoint frames",
    )
    peak, guard, bits = coefficient_bound(v, data)
    entry = v.N.vector([1 << (bits * j) for j in range(DIM)])
    endpoint = execute(v, data, entry)
    target = product(v.N, entry)
    need(endpoint == target, "All 512 complex basis columns equal C tensor power 9")
    need(product(v.N, endpoint, -1) == entry, "Explicit inverse restores packed input")
    delta = v.N.vector([1] + [0] * (DIM - 1))
    witness = execute(v, data, delta)
    need(witness == product(v.N, delta) and witness != delta, "Nonconstant witness")
    norm_numerator = sum(x * x for row in witness[:2] for x in row)
    need(norm_numerator == 1 << (2 * witness[2]), "Witness norm preserved")
    constant = execute(v, data, v.N.ONE)
    need(constant == v.N.ONE, "Constant fixture hides the frame return")
    worst = v.N.vector([(-1) ** ((3 & j).bit_count()) for j in range(DIM)])
    need(
        execute(v, data, worst) == v.N.scaled(worst, Fraction(-1)),
        "Relative helper-return error two is attained",
    )
    dimensions = [sum(j.bit_count() % 4 == k for j in range(DIM)) for k in range(4)]
    need(dimensions == [136, 136, 120, 120], "Walsh eigenspace multiplicities")
    return {
        "status": "PASS_QQ16_HELPER_FRAME_RETURN",
        "helper": HELPER,
        "events": len(data[0]),
        "basis_columns": DIM,
        "coefficient_norm_bound": str(peak),
        "denominator_guard": guard,
        "radix_bits": bits,
        "packed_endpoint_sha256": vector_hash(endpoint),
        "witness_sha256": vector_hash(witness),
        "witness_denominator_power": witness[2],
        "witness_complex_support": sum(
            bool(a or b) for a, b in zip(*witness[:2], strict=True)
        ),
        "eigenvalue_multiplicities_1_i_minus1_minusi": dimensions,
        "fixed_complex_dimension": dimensions[0],
        "mismatch_complex_rank": DIM - dimensions[0],
        "other_711_outputs_zero": True,
        "constant_entry_returns_literally": True,
        "inverse_coordinate_lines": 9,
        "sharp_relative_helper_return_error": 2,
        "new_supplier_or_kappa": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.write:
        with args.write.open("x") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        need(
            result == json.loads((HERE / "RESULT.json").read_text()), "Receipt mismatch"
        )
    print(result["status"])


if __name__ == "__main__":
    main()
