#!/usr/bin/env python3
"""Independent integer/rational oracles for PR2287's frozen grid primitives.

AAAmirinu, with substantial OpenAI Codex assistance. Apache-2.0.
The retained implementation is the subject, never the expected-value oracle.
"""
import argparse
import ast
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate_bytes(raw, row):
    require(hashlib.sha256(raw).hexdigest() == row["sha256"], "source hash: " + row["path"])
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source blob: " + row["path"])


def authenticate(directory=HERE):
    manifest = json.loads((directory / "SOURCES.json").read_text(encoding="utf-8"))
    predecessor = manifest["predecessor"]
    require(predecessor["head"] == "8c60765b5dea9d862b3b190d55da102a576031bf", "predecessor head")
    for row in predecessor["files"]:
        raw = (directory / row["path"]).read_bytes()
        authenticate_bytes(raw, row)
    return predecessor


def load_module(name, path, source=None):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    raw = path.read_text(encoding="utf-8") if source is None else source
    exec(compile(raw, str(path), "exec", optimize=0), module.__dict__)
    return module


def load_subject():
    source = HERE / "sources/pr2287"
    streams = load_module("streams", source / "vendor/streams.py")
    arithmetic = load_module("audited_grid", source / "arithmetic.py")
    tree = ast.parse((source / "bounds.py").read_text(encoding="utf-8"))
    function, = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "scalar_charge"]
    namespace = {"F": F, "need": require}
    exec(compile(ast.Module(body=[function], type_ignores=[]), "retained_scalar_charge", "exec"), namespace)
    return streams, arithmetic, namespace["scalar_charge"]


def encode_integer(value, bits):
    require(-(1 << (bits - 1)) <= value < (1 << (bits - 1)), "oracle signed range")
    value %= 1 << bits
    return bytearray((value // (1 << i)) % 2 for i in range(bits))


def decode_integer(word):
    # Independent of streams.key_value/bit_key and the predecessor checker.
    value = sum(int(bit) * (1 << i) for i, bit in enumerate(word))
    return value - (1 << len(word)) if word[-1] else value


def rejected(action, expected):
    try:
        action()
    except ValueError as error:
        require(str(error) == expected, "wrong rejection: " + str(error))
        return
    raise ValueError("accepted invalid operation: " + expected)


def exhaustive_words(arithmetic):
    counts = {"additions": 0, "negations": 0, "divisions": 0,
              "overflow_rejections": 0, "nonintegral_rejections": 0}
    for bits in range(4, 9):
        grid = arithmetic.Grid(bits, 0)
        low, high = -(1 << (bits - 1)), (1 << (bits - 1)) - 1
        for a in range(low, high + 1):
            aw = encode_integer(a, bits)
            if a == low:
                rejected(lambda: grid.neg(aw), "signed negation headroom")
                counts["overflow_rejections"] += 1
            else:
                require(decode_integer(grid.neg(aw)) == -a, "negation oracle")
            counts["negations"] += 1
            grid.close()
            for k in range(bits):
                if a % (1 << k):
                    rejected(lambda: grid.divide(aw, k), "division discards only reserved zero bits")
                    counts["nonintegral_rejections"] += 1
                else:
                    require(decode_integer(grid.divide(aw, k)) == a // (1 << k), "exact signed division oracle")
                counts["divisions"] += 1
                grid.close()
            for b in range(low, high + 1):
                bw = encode_integer(b, bits)
                if low <= a + b <= high:
                    require(decode_integer(grid.add(aw, bw)) == a + b, "addition oracle")
                else:
                    rejected(lambda: grid.add(aw, bw), "signed addition headroom")
                    counts["overflow_rejections"] += 1
                counts["additions"] += 1
                grid.close()
    return {"word_bits": [4, 5, 6, 7, 8], **counts}


def auditing_grid(arithmetic):
    class AuditGrid(arithmetic.Grid):
        """Observe every retained arithmetic intermediate with independent integers."""
        largest_numerator = 0
        largest_denominator_exponent = 0
        checked_operations = 0

        def track(self, word):
            value = decode_integer(word)
            self.largest_numerator = max(self.largest_numerator, abs(value))
            den = F(value, 1 << self.fraction_bits).denominator
            self.largest_denominator_exponent = max(self.largest_denominator_exponent, den.bit_length() - 1)
            return super().track(word)

        def add(self, a, b):
            expected = decode_integer(a) + decode_integer(b)
            result = super().add(a, b)
            require(decode_integer(result) == expected, "intermediate addition oracle")
            self.checked_operations += 1
            return result

        def neg(self, a):
            expected = -decode_integer(a)
            result = super().neg(a)
            require(decode_integer(result) == expected, "intermediate negation oracle")
            self.checked_operations += 1
            return result

        def divide(self, a, k):
            expected = F(decode_integer(a), 1 << k)
            result = super().divide(a, k)
            require(F(decode_integer(result)) == expected, "intermediate division oracle")
            self.checked_operations += 1
            return result
    return AuditGrid


def scalar_bounds(arithmetic, charge):
    # Every reduced coefficient in this finite alphabet; the proof covers all n,k.
    coefficients = sorted({F(n, 1 << k) for n in range(-9, 10) for k in range(5)})
    cases = 0
    for c in coefficients:
        b = abs(c.numerator).bit_length()
        k = c.denominator.bit_length() - 1
        h = max(b, k)
        for numerator in range(-16, 17):
            Grid = auditing_grid(arithmetic)
            grid = Grid(48, 16)
            value = F(numerator, 16)
            word = encode_integer(int(value * (1 << grid.fraction_bits)), grid.bits)
            scaled = grid.scale(word, c)
            require(F(decode_integer(scaled), 1 << grid.fraction_bits) == value * c, "scale rational oracle")
            target = encode_integer((1 if numerator >= 0 else -1) << grid.fraction_bits, grid.bits)
            added = grid.add(target, scaled)
            expected = (1 if numerator >= 0 else -1) + value * c
            require(F(decode_integer(added), 1 << grid.fraction_bits) == expected, "scalar ADD rational oracle")
            require(grid.largest_numerator <= (1 << (grid.fraction_bits + h)), "Horner prefix magnitude bound")
            require(grid.largest_denominator_exponent <= 4 + h, "Horner prefix denominator bound")
            grid.close()
            require(not grid.workspace, "scalar workspace closure")
            cases += 1
        events = [["scalar", ["scale", 0, c.numerator, c.denominator]],
                  ["scalar", ["add", 0, 1, c.numerator, c.denominator]]]
        total, largest = charge(events)
        require(largest == 2*b + k + 4 and total == 2*largest and largest >= h, "retained scalar charge dominates prefix")
    return {"coefficient_count": len(coefficients), "scalar_cases": cases,
            "numerators": [-9, 9], "denominator_powers": [0, 4],
            "input_numerators_over_16": [-16, 16], "proved_prefix_increment": "max(bit_length(abs(n)),k)"}


def encode_values(values, grid):
    raw = bytearray()
    for z in values:
        for x in z:
            value = x * (1 << grid.fraction_bits)
            require(value.denominator == 1, "oracle input grid")
            raw.extend(encode_integer(int(value), grid.bits))
    return raw


def decode_values(raw, grid):
    require(len(raw) % (2*grid.bits) == 0, "oracle Gaussian record extent")
    result = []
    for start in range(0, len(raw), 2*grid.bits):
        result.append(tuple(F(decode_integer(raw[start+j*grid.bits:start+(j+1)*grid.bits]),
                              1 << grid.fraction_bits) for j in range(2)))
    return result


def mul(z, w):
    return (z[0]*w[0]-z[1]*w[1], z[0]*w[1]+z[1]*w[0])


def plus(z, w):
    return z[0]+w[0], z[1]+w[1]


def axis_oracle(values, address_bits, axis, inverse=False):
    # Direct Gaussian matrix multiplication, separate from the source pair formula.
    diagonal = (F(1, 2), F(-1 if inverse else 1, 2))
    off = (F(1, 2), -diagonal[1])
    result = list(values)
    stride = 1 << (address_bits-axis-1)
    for i in range(len(values)):
        if i & stride:
            continue
        j = i + stride
        result[i] = plus(mul(diagonal, values[i]), mul(off, values[j]))
        result[j] = plus(mul(off, values[i]), mul(diagonal, values[j]))
    return result


def has_height(values, p, t):
    return all(x.denominator <= 1 << (p+t) and (1 << (p+t)) % x.denominator == 0
               for z in values for x in z) and all(r*r+i*i <= 1 << (2*t) for r, i in values)


def least_height(values, p):
    t = 0
    while not has_height(values, p, t):
        t += 1
    return t


def kernel_and_normalization(streams, arithmetic):
    # Entire p=2 Gaussian unit disk, both input slots and both C orientations.
    disk = [(F(r, 4), F(i, 4)) for r in range(-4, 5) for i in range(-4, 5)
            if r*r+i*i <= 16]
    pair_cases = 0
    for inverse in (False, True):
        for a in disk:
            for b in disk:
                Grid = auditing_grid(arithmetic)
                grid = Grid(28, 12)
                words = [tuple(encode_integer(int(x*(1 << grid.fraction_bits)), grid.bits) for x in z)
                         for z in (a, b)]
                out = grid.pair(*words, inverse=inverse)
                actual = [tuple(F(decode_integer(x), 1 << grid.fraction_bits) for x in z) for z in out]
                require(actual == axis_oracle([a, b], 1, 0, inverse), "C-pair independent matrix oracle")
                require(has_height(actual, 2, 1), "C-pair completed height")
                require(grid.largest_numerator <= (1 << (grid.fraction_bits+2)), "C-pair prefix magnitude")
                require(grid.largest_denominator_exponent <= 3, "C-pair prefix denominator")
                grid.close()
                pair_cases += 1
    Grid = auditing_grid(arithmetic)
    grid = Grid(28, 12)
    pair = [(F(5, 8), F(-5, 8)), (F(5, 8), F(5, 8))]
    words = [tuple(encode_integer(int(x*(1 << grid.fraction_bits)), grid.bits) for x in z) for z in pair]
    out = grid.pair(*words)
    require(F(grid.largest_numerator, 1 << grid.fraction_bits) == F(5, 2), "sharp prefix-height witness")
    require(F(decode_integer(out[0][0]), 1 << grid.fraction_bits) == F(5, 4), "prefix witness endpoint")

    normalization_cases = 0
    dimensions = list(range(19)) + [32, 63, 64]
    for axes in dimensions:
        grid = auditing_grid(arithmetic)(128, 96)
        output = arithmetic.normalize_b(streams.Tape(streams.Meter(), encode_values(disk, grid)), axes, grid)
        power = (F(1), F(0))
        for _ in range(axes):
            power = mul(power, (F(1, 2), F(-1, 2)))
        expected = [mul(z, power) for z in disk]
        require(decode_values(output.data, grid) == expected, "normalization repeated-product oracle")
        increment = (axes+1)//2
        require(grid.largest_numerator <= 1 << (grid.fraction_bits+increment), "normalization prefix magnitude")
        require(grid.largest_denominator_exponent <= 2+increment, "normalization prefix denominator")
        require(not grid.workspace and output.head == 0, "normalization work/head closure")
        normalization_cases += len(disk)
    return {"unit_disk_points": len(disk), "pair_cases": pair_cases,
            "normalization_dimensions": dimensions, "normalization_cases": normalization_cases,
            "prefix_witness": {"inputs": ["(5-5i)/8", "(5+5i)/8"],
                               "largest_real_temporary": "5/2", "first_output": "5/4"}}


def nested_calls(streams, arithmetic):
    Grid = auditing_grid(arithmetic)
    grid = Grid(72, 28)  # p=4 and one fixed 24-bit guard throughout all children.
    meter = streams.Meter()
    p = 4
    traces = []
    completed = 0
    for bits in range(1, 5):
        outer_rows = 3
        count = outer_rows*(1 << bits)
        initial = [(F((i % 9)-4, 16), F((i % 7)-3, 16)) for i in range(count)]
        helper = [(F((i % 5)-2, 16), F((3*i % 7)-3, 16)) for i in range(count)]
        left = streams.Tape(meter, encode_values(initial, grid))
        right = streams.Tape(meter, encode_values(helper, grid))

        def call(left, right, axes, inverse=False):
            nonlocal completed
            before = [decode_values(t.data, grid) for t in (left, right)]
            incoming = max(least_height(v, p) for v in before)
            expected = before
            # A cancelled dyadic shear surrounds a nested common unary call.
            left = arithmetic.scalar_add(left, right, F(3, 4), grid)
            axis, *remaining = axes
            left = arithmetic.c_axis(left, bits, axis, 1, grid, inverse, outer_rows)
            right = arithmetic.c_axis(right, bits, axis, 1, grid, inverse, outer_rows)
            if remaining:
                left, right = call(left, right, remaining, inverse)
            left = arithmetic.scalar_add(left, right, F(-3, 4), grid)
            for a in axes:
                expected = [axis_oracle(v, bits, a, inverse) for v in expected]
            actual = [decode_values(t.data, grid) for t in (left, right)]
            require(actual == expected, "nested completed-child tensor oracle")
            require(all(has_height(v, p, incoming+len(axes)) for v in actual), "completed-child height and divisibility")
            require(not grid.workspace and left.head == right.head == 0, "nested return workspace/head closure")
            traces.append({"axes": list(axes), "inverse": inverse, "incoming_height": incoming,
                           "returned_height": max(least_height(v, p) for v in actual)})
            completed += 1
            return left, right

        left, right = call(left, right, list(range(bits)))
        left, right = call(left, right, list(reversed(range(bits))), True)
        require(decode_values(left.data, grid) == initial and decode_values(right.data, grid) == helper,
                "nested exact inverse and correlated helper restoration")
    return {"max_depth": 4, "outer_rows": 3, "completed_child_returns": completed,
            "checked_primitive_operations": grid.checked_operations,
            "largest_denominator_exponent": grid.largest_denominator_exponent,
            "word_bits": grid.bits, "fraction_bits": grid.fraction_bits,
            "return_traces": traces,
            "scope": "composed actual primitives with a cancelled shear; not the selected R480 payload"}


def failure_controls(streams, arithmetic):
    # Final 90 fits in eight signed bits, but the numerator 3*60 does not.
    grid = arithmetic.Grid(8, 0)
    require(-128 <= F(3, 2)*60 <= 127, "endpoint-fit counterexample premise")
    rejected(lambda: grid.scale(encode_integer(60, 8), F(3, 2)), "signed addition headroom")
    guarded = arithmetic.Grid(10, 1)
    require(decode_integer(guarded.scale(encode_integer(120, 10), F(3, 2))) == 180,
            "Horner headroom positive control")
    small = arithmetic.Grid(24, 2)
    initial = [(F(1, 4), F(0)), (F(0), F(0))]
    rejected(lambda: arithmetic.c_axis(streams.Tape(streams.Meter(), encode_values(initial, small)),
                                      1, 0, 1, small), "division discards only reserved zero bits")
    full = arithmetic.Grid(32, 12)
    forward = arithmetic.c_axis(streams.Tape(streams.Meter(), encode_values(initial, full)), 1, 0, 1, full)
    values = decode_values(forward.data, full)
    rounded = [tuple(F(int(x*4), 4) for x in z) for z in values]
    wrong = arithmetic.c_axis(streams.Tape(streams.Meter(), encode_values(rounded, full)), 1, 0, 1, full, True)
    require(decode_values(wrong.data, full) != initial, "rounded completed-child loss")
    right = arithmetic.c_axis(forward, 1, 0, 1, full, True)
    require(decode_values(right.data, full) == initial, "same-grid inverse positive control")
    rejected(lambda: full.scale(encode_integer(12, 32), F(1, 3)), "Gaussian-dyadic scalar")
    # All ideal values are zero, but the source still requires a legal shift size.
    extent = arithmetic.Grid(3, 0)
    rejected(lambda: extent.scale(encode_integer(0, 3), F(1, 8)), "binary division extent")
    path = HERE / "sources/pr2287/arithmetic.py"
    original = path.read_text(encoding="utf-8")
    mutations = [
        ('need(not any(a[:k]),"division discards only reserved zero bits")', 'pass',
         lambda g: g.divide(encode_integer(1, g.bits), 1), "intermediate division oracle"),
        ('need(a[-1]!=b[-1] or out[-1]==a[-1],"signed addition headroom")', 'pass',
         lambda g: g.add(encode_integer(100, g.bits), encode_integer(100, g.bits)), "intermediate addition oracle"),
    ]
    for index, (old, new, action, error) in enumerate(mutations):
        require(original.count(old) == 1, "exact source mutation location")
        mutant = load_module("grid_mutant_"+str(index), path, original.replace(old, new))
        rejected(lambda: action(auditing_grid(mutant)(8, 0)), error)
    # A changed retained implementation must fail authentication before imports.
    rows = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))["predecessor"]["files"]
    row, = [r for r in rows if r["path"] == "sources/pr2287/arithmetic.py"]
    corrupted = path.read_bytes() + b"\nraise RuntimeError('must not execute')\n"
    rejected(lambda: authenticate_bytes(corrupted, row), "source hash: sources/pr2287/arithmetic.py")
    return {"endpoint_fit_but_Horner_overflow": "REJECT",
            "final_identity_but_insufficient_intermediate_grid": "REJECT",
            "rounded_child_return": "WRONG_ENDPOINT",
            "nondyadic_scalar": "REJECT", "independent_oracle_semantic_mutants": 2,
            "zero_value_but_invalid_shift_extent": "REJECT",
            "source_corruption_before_import": "REJECT"}


def run():
    predecessor = authenticate()
    streams, arithmetic, charge = load_subject()
    return {"status": "PASS_COMPLEX_GRID_PREFIX_AUDIT", "predecessor_head": predecessor["head"],
            "sources_authenticated": len(predecessor["files"]),
            "exhaustive_words": exhaustive_words(arithmetic),
            "scalar_prefixes": scalar_bounds(arithmetic, charge),
            "kernel_and_normalization": kernel_and_normalization(streams, arithmetic),
            "nested_calls": nested_calls(streams, arithmetic),
            "failure_controls": failure_controls(streams, arithmetic),
            "limits": "Independent primitive and composition audit plus written quantified lemma; no full selected payload, stock/time admission, Lean proof, or new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="write a NEW receipt; never overwrite evidence")
    args = parser.parse_args()
    result = run()
    if args.emit:
        with args.emit.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2)
            stream.write("\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        require(result == expected, "committed audit receipt mismatch")
    print(result["status"] + " " + json.dumps({"words": result["exhaustive_words"],
          "scalar_cases": result["scalar_prefixes"]["scalar_cases"],
          "nested_returns": result["nested_calls"]["completed_child_returns"]}, sort_keys=True))


if __name__ == "__main__":
    main()
