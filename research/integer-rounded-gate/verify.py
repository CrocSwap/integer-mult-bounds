"""Exact finite evidence for the new bounded arithmetic kernel.

Produced by Nick Petalas. Apache-2.0.
"""

import ast
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent
sys.path.insert(0, str(PACKAGE))
from kernel import Words, apply_gate, require, rounded_row


def authenticate():
    source_manifest = PACKAGE / "SOURCES.json"
    require(source_manifest.stat().st_size <= 1048576, "source manifest capacity")
    manifest = json.loads(source_manifest.read_text())
    require(len(manifest["files"]) == 7, "source inventory capacity")
    inputs = [item for item in manifest["files"] if item["usage"] == "input"]
    require(len(inputs) == 5, "declared source closure")
    for item in inputs:
        path = ROOT / item["path"]
        require(path.stat().st_size <= 1048576, "source file capacity")
        require(sha256(path.read_bytes()).hexdigest() == item["sha256"],
                "source digest: " + item["path"])
    return len(inputs)


def literal_round(value):
    shifted = value + Fraction(1, 2)
    return shifted.numerator // shifted.denominator


def oracle(row, state):
    return literal_round(sum((Fraction(*pair) * x for pair, x in zip(row, state)),
                             Fraction(0)))


def row_cases():
    alphabet = [(-1, 1), (-1, 2), (0, 1), (1, 2), (1, 1)]
    cases = 0
    max_peak = 0
    for row in product(alphabet, repeat=4):
        for state in product((-2, 0, 1), repeat=4):
            words = Words(12)
            actual = rounded_row(row, state, words)
            require(actual == oracle(row, state), "four-term exact rounding")
            require(words.peak <= 12, "four-term width")
            max_peak = max(max_peak, words.peak)
            cases += 1
    return cases, max_peak


def two_term_cases():
    alphabet = sorted({Fraction(a, d) for a in range(-3, 4) for d in range(1, 4)})
    cases = 0
    for first, second in product(alphabet, repeat=2):
        row = ((first.numerator, first.denominator),
               (second.numerator, second.denominator), (0, 1), (0, 1))
        for x, y in product(range(-2, 2), repeat=2):
            state = (x, y, 0, 0)
            require(rounded_row(row, state, Words(12)) == oracle(row, state),
                    "complete signed two-term domain")
            cases += 1
    return cases


def division_cases():
    cases = 0
    for numerator in range(1024):
        for denominator in range(1, 32):
            actual = Words(13).divide(numerator, denominator)
            require(actual == divmod(numerator, denominator), "binary division")
            cases += 1
    return cases


def extreme_cases():
    cases = 0
    max_peak = 0
    for data_bits, coefficient_bits in product((2, 18, 128, 512, 2048),
                                                (1, 2, 15, 64, 256)):
        high = (1 << coefficient_bits) - 1
        row = tuple((sign * high, high) for sign in (1, -1, 1, -1))
        state = tuple(sign * ((1 << (data_bits - 1)) - 1) for sign in (1, -1, 1, -1))
        width = data_bits + 4 * coefficient_bits + 2
        for current in (state, tuple(-x - 1 for x in state)):
            words = Words(width)
            require(rounded_row(row, current, words) == oracle(row, current),
                    "extreme products and cancellation")
            require(words.peak <= width, "extreme temporary width")
            max_peak = max(max_peak, words.peak)
            cases += 1
    return cases, max_peak


def real_rows(gate):
    rows = []
    for row in gate:
        real = [part for value in row for part in (value.re, -value.im)]
        imag = [part for value in row for part in (value.im, value.re)]
        rows.extend(tuple((x.numerator, x.denominator) for x in parts)
                    for parts in (real, imag))
    return tuple(rows)


def actual_gate_cases():
    sys.path.insert(0, str(ROOT / "research/rational-unitary-fft"))
    import engine
    import exact
    source = (ROOT / "research/cubic-cyclic-inverse/vendor/interval_kernel.py").read_text()
    phases = engine.Phases(4, source)
    builder = object.__new__(engine.Builder)
    builder.phases = phases
    gate = builder.butterfly(phases.phase(4, 1))
    rows = real_rows(gate)
    height = max(max(abs(a).bit_length(), d.bit_length()) for row in rows for a, d in row)
    require(height == 15, "concrete source-produced gate height")
    cases = 0
    for bits, state in product((1, 12, 128), product((-131072, -1, 0, 131071), repeat=4)):
        scale = 1 << bits
        vector = exact.Vec([exact.C(Fraction(state[0], scale), Fraction(state[1], scale)),
                            exact.C(Fraction(state[2], scale), Fraction(state[3], scale))])
        expected, _ = exact.apply([[(tuple(range(2)), gate)]], vector, bits)
        expected = tuple(int(part * scale) for value in expected for part in (value.re, value.im))
        current = list(state)
        words = apply_gate(rows, current, 18, height)
        require(tuple(current) == expected, "source once-rounded butterfly contract")
        require(words.width == 80 and words.peak <= 80, "concrete arithmetic width")
        cases += 1
    require(2 * 18 + 8 * height + 32 == 188, "same-parameter cited allowance")
    return cases, [[value.record() for value in row] for row in gate]


def controls():
    checks = 0
    row = ((1, 2), (1, 2), (0, 1), (0, 1))
    require(rounded_row(row, (1, 1, 0, 0), Words(12)) == 1,
            "sum before rounding")
    checks += 1
    require(sum(literal_round(Fraction(*pair) * x) for pair, x in zip(row, (1, 1, 0, 0))) == 2,
            "per-product rounding differs")
    checks += 1
    for value, expected in ((1, 1), (-1, 0), (3, 2), (-3, -1)):
        require(rounded_row(((1, 2), (0, 1), (0, 1), (0, 1)),
                            (value, 0, 0, 0), Words(12)) == expected, "signed halfway ties")
        checks += 1
    swap = tuple(tuple((int(j == (i ^ 2)), 1) for j in range(4)) for i in range(4))
    state = [1, 2, 3, 4]
    apply_gate(swap, state, 4, 1)
    require(state == [3, 4, 1, 2], "saved source coordinates")
    checks += 1
    broken = [1, 2, 3, 4]
    for i in range(4):
        broken[i] = oracle(swap[i], broken)
    require(broken != state, "overwrite-before-read differs")
    checks += 1
    return checks


def rejection_controls():
    identity = tuple(tuple((int(i == j), 1) for j in range(4)) for i in range(4))
    cases = [(identity, [0] * 4, 1, 2), (identity, [0] * 4, 2049, 2),
             (identity, [0] * 4, 4, 0), (identity, [0] * 4, 4, 257),
             (identity, [0] * 3, 4, 2), (identity[:3], [0] * 4, 4, 2),
             (identity, [True, 0, 0, 0], 4, 2), (identity, [8, 0, 0, 0], 4, 2),
             (identity, [-9, 0, 0, 0], 4, 2), (identity, (0, 0, 0, 0), 4, 2)]
    for pair in ((1, 0), (1, -1), (4, 1), (1, 4), (True, 1)):
        cases.append((((pair,) + identity[0][1:],) + identity[1:], [0] * 4, 4, 2))
    for rows, state, data_bits, coefficient_bits in cases:
        before = tuple(state)
        try:
            apply_gate(rows, state, data_bits, coefficient_bits)
        except ValueError:
            require(tuple(state) == before, "invalid request leaves state unchanged")
        else:
            raise ValueError("invalid request accepted")
    for value in (128, -129):
        try:
            Words(8).check(value)
        except OverflowError:
            continue
        raise ValueError("overflow accepted")
    return len(cases) + 2


def main():
    source_count = authenticate()
    rows, row_peak = row_cases()
    two_terms = two_term_cases()
    divisions = division_cases()
    extremes, extreme_peak = extreme_cases()
    actual, gate = actual_gate_cases()
    semantic = controls()
    rejected = rejection_controls()
    hashes = {}
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
             "kernel.py", "verify.py")
    for name in names:
        path = PACKAGE / name
        require(path.stat().st_size <= 1048576, "package file capacity")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
        if path.suffix == ".py":
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    require(node.end_lineno - node.lineno + 1 <= 60, "function size")
    receipt = dict(marker="PASS_INTEGER_ROUNDED_GATE", sources=source_count,
                   four_term_rows=rows, two_term_rows=two_terms, divisions=divisions,
                   extreme_rows=extremes, actual_gate_cases=actual,
                   row_peak_bits=row_peak, extreme_peak_bits=extreme_peak,
                   semantic_controls=semantic, rejection_controls=rejected,
                   source_gate=gate, package_sha256=hashes)
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
