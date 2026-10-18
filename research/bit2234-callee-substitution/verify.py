#!/usr/bin/env python3
"""Exact endpoint and source-API checks; written proof is in README.md."""
import argparse
import ast
from fractions import Fraction as F
from hashlib import sha256, sha1
from itertools import product
from math import gcd, prod
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import adapter as a


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        a.need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_object)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def authenticate():
    sources = read_json(HERE / "SOURCES.json")
    for item in sources["vendored_files"]:
        data = (HERE / item["path"]).read_bytes()
        a.need(sha256(data).hexdigest() == item["sha256"], "vendored source SHA256: " + item["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        a.need(sha1(blob).hexdigest() == item["git_blob"], "vendored Git blob: " + item["path"])
    return len(sources["vendored_files"])


def decode(index, radices):
    result = []
    for radix in reversed(radices):
        index, value = divmod(index, radix)
        result.append(value)
    a.need(index == 0, "address extent")
    return result[::-1]


def encode(values, radices):
    out = 0
    for value, radix in zip(values, radices, strict=True):
        a.need(0 <= value < radix, "coordinate extent")
        out = out * radix + value
    return out


def direct(raw, radices, change):
    """Independent address-scatter oracle, used only by verification."""
    out = [None] * len(raw)
    for index, label in enumerate(raw):
        values = decode(index, radices)
        change(values)
        target = encode(values, radices)
        a.need(out[target] is None, "oracle injectivity")
        out[target] = label
    a.need(all(x is not None for x in out), "oracle surjectivity")
    return out


def swap_oracle(raw, q, width, before, middle, suffix):
    def change(v):
        v[1], v[3] = v[3], v[1]
    return direct(raw, [before, q**width, middle, q**width, suffix], change)


def check_adapters():
    count = volume = calls = 0
    digest = sha256()
    for q, width, shape in product((3, 5), range(4),
                                  ((1, 1, 1), (2, 1, 1), (1, 3, 1), (1, 1, 2), (2, 3, 2))):
        before, middle, suffix = shape
        size = before * q**(2 * width) * middle * suffix
        raw = list(range(size))
        source, meter = a.Stream(raw[:]), a.Meter()
        out = a.qadic_exchange(source, q, width, before, middle, suffix, meter)
        a.need(out.data == swap_oracle(raw, q, width, before, middle, suffix) and out.head == 0,
               "padded swap endpoint")
        a.need(len(meter.calls) == int(width > 0), "exactly one completed call, except width zero")
        if width:
            call = meter.calls[0]
            a.need(not source.data and source.head == 0, "consumed original input")
            a.need((call["before"], call["middle"], call["suffix"]) == shape, "spectators not padded")
            a.need(meter.pad_reads == meter.crop_writes == size, "genuine copy counts")
            a.need(meter.pad_writes == meter.crop_reads == call["padded_volume"], "dummy scan counts")
            a.need(call["binary_width"] <= (q - 1).bit_length() * width, "integer binary-width bound")
        else:
            a.need(out is source and meter.zero_width == 1, "zero-width identity")
        digest.update(canonical([q, width, shape, out.data]).encode())
        count += 1
        volume += size
        calls += len(meter.calls)
    # Exhaust every genuine Boolean payload at Q=3; the callback checks that
    # padding introduced only actual bits, not a sentinel alphabet extension.
    for bits in product((0, 1), repeat=9):
        def binary_only(source, *args):
            a.need(all(type(v) is int and v in (0, 1) for v in source.data), "binary-only callee input")
            return a.binary_reference(source, *args)
        result = a.qadic_exchange(a.Stream(list(bits)), 3, 1, 1, 1, 1, a.Meter(), binary_only)
        a.need(result.data == swap_oracle(list(bits), 3, 1, 1, 1, 1), "Boolean payload padding")
    return {"cases": count, "coordinates": volume, "binary_calls": calls,
            "exhaustive_boolean_inputs": 512, "sha256": digest.hexdigest()}


def check_leaves():
    count = coordinates = calls = 0
    digest = sha256()
    for q, width, n in [(3, 1, 0), (3, 1, 1), (3, 2, 1), (5, 1, 1),
                         (5, 2, 1), (3, 1, 2), (3, 2, 2)]:
        radix = q**width
        units = [v for v in range(1, radix) if gcd(v, radix) == 1]
        weights = [[units[(2 * p + i + 1) % len(units)] for i in range(n)] for p in range(2)]
        radices = [2] + [radix] * n + [2] + [radix] * n + [2]
        raw = list(range(prod(radices)))
        out, meter = a.weighted_leaf(raw, q, width, weights, gap=2, suffix=2)
        def change(v):
            old = v[:]
            for i, weight in enumerate(weights[v[0]]):
                first, second = 1 + i, 2 * n + 1 - i
                v[first] = weight * old[second] % radix
                v[second] = pow(weight, -1, radix) * old[first] % radix
        a.need(out == direct(raw, radices, change), "weighted leaf full endpoint")
        a.need(len(meter.calls) == 4 * n, "leaf completed call inventory")
        digest.update(canonical([q, width, weights, out]).encode())
        count += 1
        coordinates += len(raw)
        calls += len(meter.calls)
    return {"cases": count, "coordinates": coordinates, "binary_calls": calls, "sha256": digest.hexdigest()}


class Tape:
    """Symbolic interpreter for source headers; real heads and consumed scratch.

    Distinct integer tokens prove the whole position permutation in one run.
    Source functions never inspect tokens, so this also checks arbitrary bits.
    """
    def __init__(self, meter, bits=()):
        self.meter, self.bits, self.head = meter, list(bits), 0
    def read(self):
        a.need(self.head < len(self.bits), "source header read extent")
        value = self.bits[self.head]
        self.head += 1
        return value
    def write(self, value):
        a.need(self.head == len(self.bits), "source header append")
        self.bits.append(value)
        self.head += 1
    def rewind(self):
        self.head = 0
    def finished(self):
        a.need(self.head == len(self.bits), "source header consumed")
    def erase(self):
        self.bits.clear()
        self.head = 0


class HeaderMeter:
    def __init__(self):
        self.movement = None
        self.ordered_shifts = self.fixed_signs = self.max_bucket_tapes = 0
        self.adapters = a.Meter()


def source_functions(path, names, namespace):
    tree = ast.parse(path.read_text())
    chosen = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    a.need({node.name for node in chosen} == set(names), "all selected source functions present")
    exec(compile(ast.Module(body=chosen, type_ignores=[]), str(path), "exec"), namespace)


def load_header(omit_return=False):
    def copy_bits(source, target, count):
        for _ in range(count):
            target.write(source.read())
    def pop_bit(tape):
        a.need(bool(tape.bits) and tape.head == len(tape.bits), "stack pop at end")
        tape.head -= 1
        return tape.bits.pop()
    def ordinary_fields(source, q, width, before, middle, suffix, meter):
        if omit_return and meter.adapters.calls:
            return source
        a.need(source.head == 0, "source header adapter entry")
        result = a.qadic_exchange(a.Stream(source.bits[:]), q, width, before, middle, suffix, meter.adapters)
        source.erase()
        return Tape(meter.movement, result.data)
    ns = {"F": F, "gcd": gcd, "Tape": Tape, "copy_bits": copy_bits,
          "need": a.need, "pop_bit": pop_bit, "ordinary_fields": ordinary_fields}
    source_functions(HERE / "sources/pr-2234/qadic_streams.py", ["low_update"], ns)
    source_functions(HERE / "sources/pr-2234/header_streams.py",
                     ["rotate", "multiply_fixed", "negate", "scale", "add", "scale_affine"], ns)
    return ns


def header_case(ns, q, width, low_x, low_y, coefficient, reverse, omit_carry=False):
    radix = q**(width - 1)
    radices = [2, radix, 2, radix, 2]
    raw = list(range(prod(radices)))
    meter = HeaderMeter()
    result, new_low = ns["add"](Tape(None, raw), q, width, low_x, low_y,
                                coefficient, 2, 2, 2, meter, reversed_fields=reverse,
                                omit_carry=omit_carry)
    cmod = coefficient.numerator * pow(coefficient.denominator, -1, q**width) % (q**width)
    def change(v):
        xi, yi = (3, 1) if reverse else (1, 3)
        x = low_x + q * v[xi]
        y = low_y + q * v[yi]
        target = (y + cmod * x) % (q**width)
        a.need(target % q == new_low, "header low/high agreement")
        v[yi] = target // q
    a.need(result.head == 0 and result.bits == direct(raw, radices, change),
           "source header endpoint with substituted callee")
    a.need(len(meter.adapters.calls) == (2 if reverse and width > 1 else 0),
           "two high-field calls in reversed header ADD")
    return len(raw), len(meter.adapters.calls), result.bits


def check_headers():
    ns = load_header()
    count = coordinates = calls = 0
    digest = sha256()
    alphabet = [F(sign * numerator, denominator) for sign in (-1, 1)
                for numerator, denominator in ((1, 4), (1, 2), (1, 1), (2, 1), (4, 1))]
    for q, width, coefficient, reverse in product((3, 5), (1, 2, 3), alphabet, (False, True)):
        lows = product(range(q), repeat=2) if width < 3 else [(0, 0), (1, q - 1), (q - 1, 1)]
        for low_x, low_y in lows:
            size, used, result = header_case(ns, q, width, low_x, low_y, coefficient, reverse)
            digest.update(canonical([q, width, low_x, low_y, str(coefficient), reverse, result]).encode())
            count += 1
            coordinates += size
            calls += used
    return {"cases": count, "coordinates": coordinates, "binary_calls": calls,
            "coefficient_alphabet": list(map(str, alphabet)), "sha256": digest.hexdigest()}


def source_inventory():
    tree = ast.parse((HERE / "sources/pr-2234/leaf.py").read_text())
    function = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "execute_leaf")
    loop = next(x for x in function.body if isinstance(x, ast.For) and isinstance(x.target, ast.Name) and x.target.id == "i")
    calls = []
    for statement in loop.body:
        if isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call):
            name = getattr(statement.value.func, "id", None)
            if name in ("ordinary_swap", "shift", "sign_pass"):
                calls.append(name)
    a.need(calls == ["ordinary_swap", "shift", "ordinary_swap", "shift", "ordinary_swap",
                     "shift", "ordinary_swap", "sign_pass"], "exact source weighted-leaf schedule")
    header = ast.parse((HERE / "sources/pr-2234/header_streams.py").read_text())
    add = next(x for x in header.body if isinstance(x, ast.FunctionDef) and x.name == "add")
    swaps = [x for x in ast.walk(add) if isinstance(x, ast.Call) and getattr(x.func, "id", None) == "ordinary_fields"]
    a.need(len(swaps) == 2, "source reversed header has two ordinary sites")
    for call in swaps:
        a.need(ast.dump(call.args[2]) == ast.dump(ast.parse("width-1", mode="eval").body), "high-field width is w-1")
    recursion = ast.parse((HERE / "sources/pr-2234/check_recursion.py").read_text())
    moments = next(x for x in recursion.body if isinstance(x, ast.FunctionDef) and x.name == "moments")
    point = next(x.value for x in moments.body if isinstance(x, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id == "c" for t in x.targets))
    a.need(isinstance(point, ast.Call) and isinstance(point.func, ast.Name) and point.func.id == "F",
           "source coarse point constructor")
    a.need([ast.literal_eval(x) for x in point.args] == [17, 10000], "actual source coarse point")
    return {"leaf_schedule": calls, "header_ordinary_sites": len(swaps), "header_width": "w-1",
            "source_coarse_point": "17/10000"}


def exponent_corollary():
    c = F(17, 10000)
    first = c * (1 - c)
    second = c * (1 - c) + c * first
    a.need(second == c * (1 - c**2) and first < second < c, "one fixed bootstrap arithmetic")
    a.need(1 - second > c and c - first > 0, "positive borrowing and atom exponent gaps")
    return {"c": str(c), "old_saving": str(first), "conditional_second_saving": str(second),
            "linear_coefficient": 200, "power_coefficient": 10000,
            "moment_hypotheses": ["mu_1<199/200", "mu_(1-c)<9999/10000"],
            "scope": "Conditional primitive-substitution corollary; moment and physical caller premises retained."}


def controls():
    names = []
    def rejects(name, run):
        try:
            run()
        except (a.ContractError, ValueError):
            names.append(name)
            return
        raise a.ContractError("control unexpectedly accepted: " + name)
    def wrong_endpoint(kind):
        def bad(source, bits, before, middle, suffix, meter):
            result = a.binary_reference(source, bits, before, middle, suffix, meter)
            if kind == "return_head":
                result.stream.head = 1
            elif kind == "scratch":
                result.scratch_empty = False
            elif kind == "parking":
                result.parking_restored = False
            elif kind == "spectator":
                d = result.stream.data
                for j in range(0, len(d), 2):
                    d[j], d[j + 1] = d[j + 1], d[j]
            elif kind == "dummy_leak":
                # (x,gap,y,suffix)=(0,0,3,0) is outside Q=3 in the L=4 cube.
                j = 3 * suffix
                result.stream.data[j], result.stream.data[1] = result.stream.data[1], result.stream.data[j]
            return result
        raw = list(range(54))
        result = a.qadic_exchange(a.Stream(raw[:]), 3, 1, 1, 3, 2, a.Meter(), bad)
        a.need(result.data == swap_oracle(raw, 3, 1, 1, 3, 2), "semantic callee mismatch")
    for name in ("return_head", "scratch", "parking", "spectator", "dummy_leak"):
        rejects(name, lambda name=name: wrong_endpoint(name))
    def clean_identity():
        raw = list(range(9))
        result = a.qadic_exchange(a.Stream(raw[:]), 3, 1, 1, 1, 1, a.Meter(),
                                  lambda source, *_args: a.BinaryReturn(source))
        a.need(result.data == swap_oracle(raw, 3, 1, 1, 1, 1), "clean return is not the swap endpoint")
    rejects("clean_identity_is_not_swap", clean_identity)
    rejects("incomplete_genuine_rectangle", lambda: a.qadic_exchange(a.Stream([1]), 3, 1, 1, 1, 1, a.Meter()))
    rejects("invalid_width", lambda: a.qadic_exchange(a.Stream([]), 3, -1, 1, 1, 1, a.Meter()))
    rejects("nonunit_weight", lambda: a.weighted_leaf(list(range(81)), 3, 2, [[3]]))
    raw = list(range(81))
    expected, _ = a.weighted_leaf(raw, 3, 2, [[2]])
    for flag in ("wrong_inverse", "omit_sign"):
        def changed(flag=flag):
            result, _ = a.weighted_leaf(raw, 3, 2, [[2]], **{flag: True})
            a.need(result == expected, "changed weighted endpoint")
        rejects(flag, changed)
    rejects("omit_header_return_swap", lambda: header_case(load_header(True), 3, 2, 1, 2, F(1, 2), True))
    rejects("omit_header_carry", lambda: header_case(load_header(), 3, 2, 1, 2, F(1, 2), False, True))
    rejects("duplicate_receipt_key", lambda: json.loads('{"x":1,"x":2}', object_pairs_hook=unique_object))
    rejects("boolean_integer_receipt", lambda: a.need(canonical({"n": True}) == canonical({"n": 1}), "typed receipt"))
    # Padding must close before an operation in the original ring: otherwise
    # the genuine pair (1,2) goes to target3 mod4, instead of target0 mod3.
    a.need((2 + 1) % 4 == 3 and (2 + 1) % 3 == 0, "wrong-modulus intermediate witness")
    names.append("padding_must_close_before_original_ring_add")
    return names


def run():
    pins = authenticate()
    return {"status": "PASS_BIT2234_CALLEE_SUBSTITUTION", "source_files": pins,
            "source_inventory": source_inventory(), "adapter": check_adapters(),
            "leaf": check_leaves(), "headers": check_headers(),
            "conditional_corollary": exponent_corollary(), "controls": controls()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path, help="write a new receipt; never overwrite")
    args = parser.parse_args()
    result = run()
    if args.emit:
        with args.emit.open("x") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        a.need(canonical(result) == canonical(read_json(HERE / "RESULT.json")), "exact typed receipt comparison")
    print(result["status"], "adapter_cases=" + str(result["adapter"]["cases"]),
          "leaf_cases=" + str(result["leaf"]["cases"]), "header_cases=" + str(result["headers"]["cases"]),
          "controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    main()
