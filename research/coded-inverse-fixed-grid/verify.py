#!/usr/bin/env python3
"""Independent rational, signed-remainder, cleanup and failure controls.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random

import kernel

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nearest52(value):
    quotient, remainder = divmod(abs(value), 52)
    return (-1 if value < 0 else 1) * (quotient + int(2 * remainder >= 52))


def reject(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("failed rejection control: " + message)


def invoke(namespace, values, columns, bound):
    width = namespace["word_width"](bound)
    words = [namespace["encode"](value, width) for value in values]
    scratch = [[1] * width for _ in range(9)]
    bill = namespace["recode"](words, columns, bound, scratch)
    return [namespace["decode"](word) for word in words], scratch, bill


def mutated(old, new):
    source = (PACKAGE / "kernel.py").read_text()
    require(source.count(old) == 1, "mutation must select one real implementation site")
    namespace = {}
    exec(compile(source.replace(old, new), "<semantic-control>", "exec"), namespace)
    return namespace


def verify():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = [row for row in sources["files"] if row["usage"] == "input"]
    for row in live:
        require(hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                "source byte mismatch: " + row["path"])
    normalizers = json.loads((ROOT / "research/coded-native-caller/NORMALIZERS.json").read_text())
    code_bytes = (ROOT / "research/coded-native-caller/CODE.json").read_bytes()
    require(hashlib.sha256(code_bytes).hexdigest() == normalizers["code_sha256"], "source code binding")
    columns = normalizers["mode_columns"]
    code = json.loads(code_bytes)
    a = [[Fraction(value) for value in row] for row in code["A"]]
    require(len(a) == 112 and all(len(row) == 112 for row in a), "actual owner matrix")
    inverse = [[(a[i][j] + (12 if i == j else 0)) / 13 for j in range(112)] for i in range(112)]
    for i in range(112):
        for j in range(112):
            product = sum(column[i] * column[j] for column in columns)
            require(a[i][j] == (int(i == j) - Fraction(product, 4)), "actual M factorization")
            require(inverse[i][j] == (int(i == j) - Fraction(product, 52)), "inverse source binding")
    for left in range(8):
        for right in range(8):
            require(sum(x * y for x, y in zip(columns[left], columns[right])) == 56 * int(left == right),
                    "source mode Gram matrix")

    division_cases = 0
    for quotient in range(32):
        for remainder13 in range(13):
            for low in range(4):
                for sign in (-1, 1):
                    value = sign * (4 * (13 * quotient + remainder13) + low)
                    word, work = kernel.encode(value, 16), [1] * 16
                    kernel.round52_into(word, work)
                    require(kernel.decode(word) == nearest52(value), "signed /13 remainder-class oracle")
                    require(not any(work), "divider buffer must return zero")
                    division_cases += 1

    fixture = json.loads((PACKAGE / "FIRST-FIXTURE.json").read_text())
    first = [4] + [0] * 111
    require([sum(c * x for c, x in zip(column, first)) for column in columns] == fixture["mode_numerators"],
            "first fixture must bind actual source modes")
    cases = [("zero", [0] * 112, 0), ("first-odd-denominator", first, 4),
             ("positive-halfway", [26] + [0] * 111, 26),
             ("negative-halfway", [-26] + [0] * 111, 26)]
    for mode in (0, 7):
        for sign in (-1, 1):
            cases.append((f"mode-{mode}-extreme-{sign}", [sign * 52 * c for c in columns[mode]], 52))
    rng = random.Random(4933)
    for index in range(4):
        cases.append((f"signed-{index}", [rng.randint(-52, 52) for _ in range(112)], 52))
    max_error = Fraction(0)
    first_exact = None
    first_output = None
    namespace = vars(kernel)
    for name, values, bound in cases:
        output, scratch, bill = invoke(namespace, values, columns, bound)
        exact = [sum(c * x for c, x in zip(row, values)) for row in inverse]
        modes = [nearest52(sum(c * x for c, x in zip(column, values))) for column in columns]
        specification = [x - sum(column[i] * q for column, q in zip(columns, modes))
                         for i, x in enumerate(values)]
        require(output == specification, "literal rounded eight-mode program: " + name)
        error = max(abs(y - z) for y, z in zip(output, exact))
        require(error <= 2, "uniform two-grid-unit error: " + name)
        max_error = max(max_error, error)
        require(all(not any(word) for word in scratch), "every owned word must return zero")
        require(max(map(abs, output), default=0) <= 56 * bound + 2, "signed magnitude guard")
        require(bill["signed_adds"] == 896 and bill["round52_calls"] == 8, "literal operation invoice")
        if name == "positive-halfway":
            require(output[0] == 22 and exact[0] == 24 and error == 2, "source-attained positive bound")
        if name == "negative-halfway":
            require(output[0] == -22 and exact[0] == -24 and error == 2, "source-attained negative bound")
        if name == "first-odd-denominator":
            first_exact, first_output = str(exact[0]), output[0]

    zero, _, _ = invoke(namespace, [0] * 112, columns, 1)
    collision, _, _ = invoke(namespace, columns[0], columns, 1)
    require(collision == zero == [0] * 112, "noninjective rounded kernel collision")

    guards = []
    for guard in range(7):
        output, _, _ = invoke(namespace, [value << guard for value in first], columns, 4 << guard)
        exact = [sum(c * x for c, x in zip(row, first)) for row in inverse]
        scaled_error = max(abs(Fraction(value, 1 << guard) - target) for value, target in zip(output, exact))
        require(scaled_error <= Fraction(2, 1 << guard), "fractional guard contract")
        guards.append({"guard_bits": guard, "error_in_coarse_units": str(scaled_error)})

    width = kernel.word_width(52)
    for count in (0, 1, 3):
        bill = kernel.tape_invoice(width, count)
        decomposed = (9 * (2 * width + 4)
                      + count * (112 * (8 * width + 16) + 896 * (2 * width + 4)
                                 + 8 * (24 * width + 64) + 8 * (2 * width + 4) + width + 1)
                      + count * (width + 1) + 64)
        require(bill["transition_upper"] == decomposed, "complete sequential tape tariff")

    omitted = mutated("if sign:\n", "if sign and column is not mode_columns[0]:\n")
    values = [52 * c for c in columns[0]]
    output, _, _ = invoke(omitted, values, columns, 52)
    exact = [sum(c * x for c, x in zip(row, values)) for row in inverse]
    require(max(abs(y - z) for y, z in zip(output, exact)) > 2, "omitted mode must violate error contract")
    narrow = mutated("return (56 * bound + 2).bit_length() + 1", "return (56 * bound + 2).bit_length()")
    output, _, _ = invoke(narrow, values, columns, 52)
    require(max(abs(y - z) for y, z in zip(output, exact)) > 2, "missing sign guard must cause overflow failure")
    for label, old, new, value in (
            ("wrong rounding sign", "    negate_if(word, negative)\n", "    negate_if(word, 0)\n", -27),
            ("wrong halfway convention", "4 * remainder + low >= 26", "4 * remainder + low > 26", 26)):
        mutant = mutated(old, new)
        word, work = kernel.encode(value, 16), [1] * 16
        mutant["round52_into"](word, work)
        require(kernel.decode(word) != nearest52(value), label + " must fail the rounding ABI")
    dirty = mutated("for word in modes:\n        clear(word)", "for word in modes[:7]:\n        clear(word)")
    _, scratch, _ = invoke(dirty, [52 * c for c in columns[7]], columns, 52)
    require(any(any(word) for word in scratch), "missing final cleanup must be rejected")

    words = [kernel.encode(0, width) for _ in range(112)]
    scratch = [[1] * width for _ in range(9)]
    aliased = words.copy()
    aliased[1] = aliased[0]
    reject(lambda: kernel.recode(aliased, columns, 52, scratch), "owner alias")
    reject(lambda: kernel.recode(words, columns, 52, [words[0]] + scratch[1:]), "borrowed-as-owned alias")
    invalid = words.copy()
    invalid[0] = kernel.encode(53, width)
    reject(lambda: kernel.recode(invalid, columns, 52, scratch), "out-of-range input")
    invalid = words.copy()
    invalid[0] = words[0].copy()
    invalid[0][0] = 2
    reject(lambda: kernel.recode(invalid, columns, 52, scratch), "nonbinary input")
    reject(lambda: kernel.recode(words, [[1] * 112 for _ in range(8)], 52, scratch), "wrong mode incidence")
    return {"status": "PASS_CONDITIONAL_CLASSICAL_FIXED_GRID_KERNEL", "source_inputs": len(live),
            "matrix_entries_bound": 12544, "mode_gram_entries": 64,
            "division_remainder_cases": division_cases, "signed_owner_fixtures": len(cases),
            "first_fixture_exact_coordinate_0": first_exact, "first_fixture_output_coordinate_0": first_output,
            "maximum_error_grid_units": str(max_error), "attained_error_grid_units": "2",
            "noninjective_collision": "recode(M[:,0]) = recode(0) = 0",
            "semantic_mutations_rejected": 5, "input_rejections": 5,
            "fractional_guard_fixtures": guards, "invoice_H52_N1": kernel.tape_invoice(width),
            "scope": "Classical in-place bit/tape arithmetic with paid irreversible owned writes; physical caller binding and reversible cleanup are not established."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = verify()
    receipt = PACKAGE / "RESULT.json"
    if args.write:
        receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads(receipt.read_text()), "committed receipt differs")
    print(result["status"] + ": 3328 signed division cases, sharp 2-unit error, collision and five semantic controls")


if __name__ == "__main__":
    main()
