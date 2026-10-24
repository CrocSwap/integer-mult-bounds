#!/usr/bin/env python3
"""Exact finite corroboration of the written resource law. Apache-2.0."""
import argparse
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parameters(m, f, s):
    require(all(type(v) is int for v in (m, f, s)), "integer parameters required")
    require(1 <= m <= 4 and 1 <= f <= 3, "outside finite replay domain")
    require(m * f <= 8 and 0 <= s <= m, "invalid replay shape")


def gaussian_product(x, y):
    a, b = x
    c, d = y
    return a*c-b*d, a*d+b*c


def gaussian_power(x, exponent):
    require(0 <= exponent <= 8, "power outside replay bound")
    result = (1, 0)
    for _ in range(exponent):
        result = gaussian_product(result, x)
    return result


def combine(x, y):
    """Compute a*x+b*y, with a=(1+i)/2 and b=(1-i)/2."""
    values, exponent = x
    other, other_exponent = y
    require(len(values) == len(other), "different vector lengths")
    require(exponent == other_exponent, "different common denominators")
    result = tuple((r-t+u+v, r+t+v-u)
                   for (r, t), (u, v) in zip(values, other))
    return result, exponent + 1


def shift(state, mask):
    values, exponent = state
    require(0 < mask < len(values), "invalid XOR mask")
    return tuple(values[j ^ mask] for j in range(len(values))), exponent


def paid(state, direction, m, f):
    require(0 < direction < (1 << m), "invalid paid direction")
    for column in range(f):
        state = combine(state, shift(state, direction << (m * column)))
    return state


def program(m, f, s):
    parameters(m, f, s)
    steps = [("paid", 1 << axis) for axis in range(s)]
    for axis in range(s, m):
        for column in range(f):
            steps.extend((("copy", 0), ("shift", 1 << (m*column+axis)),
                          ("mix", 0), ("clear", 0)))
    return tuple(steps)


def support(state):
    return sum(value != (0, 0) for value in state[0])


def execute(steps, m, f, input_column):
    n = 1 << (m*f)
    require(0 <= input_column < n, "invalid input column")
    zero = ((0, 0),) * n
    x = (tuple((int(j == input_column), 0) for j in range(n)), 0)
    helper = (zero, 0)
    calls = additions = 0
    for kind, operand in steps:
        if kind == "paid":
            x = paid(x, operand, m, f)
            calls += 1
        elif kind == "copy":
            require(support(helper) == 0, "copy requires zero helper")
            helper = x
        elif kind == "shift":
            helper = shift(helper, operand)
        elif kind == "mix":
            x = combine(x, helper)
            additions += 1
        elif kind == "clear":
            helper = (zero, 0)
        else:
            raise ValueError("unknown instruction")
        require(max(support(x), support(helper)) <= 1 << (f*calls+additions),
                "support budget exceeded")
    return x, helper, calls, additions


def reference(m, f, column):
    bits = m*f
    values = tuple(gaussian_product(gaussian_power((1, 1), bits-d),
                                    gaussian_power((1, -1), d))
                   for d in range(bits + 1))
    return tuple(values[(j ^ column).bit_count()] for j in range(1 << bits)), bits


def equal_states(x, y):
    values, exponent = x
    other, other_exponent = y
    common = max(exponent, other_exponent)
    return tuple((r << (common-exponent), t << (common-exponent))
                 for r, t in values) == tuple(
                     (r << (common-other_exponent), t << (common-other_exponent))
                     for r, t in other)


def construction_checks():
    digest = hashlib.sha256()
    fixtures = columns = 0
    for m in range(1, 5):
        for f in range(1, 4):
            if m*f > 8:
                continue
            for s in range(m + 1):
                steps = program(m, f, s)
                fixtures += 1
                for column in range(1 << (m*f)):
                    x, helper, calls, additions = execute(steps, m, f, column)
                    require(equal_states(x, reference(m, f, column)), "wrong endpoint")
                    require(support(helper) == 0, "helper not returned to zero")
                    require(calls == s and additions == f*(m-s), "wrong invoice")
                    require(support(x) == 1 << (m*f), "target is not dense")
                    digest.update(repr((m, f, s, column, x)).encode())
                    columns += 1
    return fixtures, columns, digest.hexdigest()


def tensor_reference(m, f, direction, column):
    n = 1 << (m*f)
    values = [(0, 0)] * n
    for subset in range(1 << f):
        index = column
        for digit in range(f):
            if (subset >> digit) & 1:
                index ^= direction << (m*digit)
        d = subset.bit_count()
        require(values[index] == (0, 0), "tensor paths collided")
        values[index] = gaussian_product(gaussian_power((1, 1), f-d),
                                         gaussian_power((1, -1), d))
    return tuple(values), f


def tensor_checks():
    cases = columns = 0
    for m in range(1, 4):
        for f in range(1, 4):
            if m*f > 6:
                continue
            n = 1 << (m*f)
            for direction in range(1, 1 << m):
                cases += 1
                for column in range(n):
                    state = (tuple((int(j == column), 0) for j in range(n)), 0)
                    actual = paid(state, direction, m, f)
                    require(equal_states(actual, tensor_reference(m, f, direction, column)),
                            "paid tensor differs from subset expansion")
                    require(support(actual) == 1 << f, "wrong paid support")
                    columns += 1
    return cases, columns


def rejection_checks():
    cases = ((0, 2, 0), (3, 0, 0), (3, 2, -1), (3, 2, 4),
             (True, 2, 0), (2, 1.5, 0), (4, 3, 0), (5, 1, 1))
    count = 0
    for args in cases:
        try:
            program(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid shape accepted")
    return count


def mutation_checks():
    m, f, s = 3, 2, 2
    steps = program(m, f, s)
    rejected = 0
    for index, (kind, _) in enumerate(steps):
        if kind not in ("paid", "mix", "clear"):
            continue
        mutant = steps[:index] + steps[index+1:]
        wrong = False
        for column in range(1 << (m*f)):
            try:
                x, helper, _, _ = execute(mutant, m, f, column)
                wrong |= not equal_states(x, reference(m, f, column)) or support(helper) != 0
            except ValueError:
                wrong = True
        require(wrong, "single-operation mutant survived")
        rejected += 1
    wrong_masks = tuple((kind, (1 << 2) | (1 << 5)) if kind == "shift" else (kind, v)
                        for kind, v in steps)
    x, _, _, _ = execute(wrong_masks, m, f, 0)
    require(not equal_states(x, reference(m, f, 0)), "tied-mask mutant survived")
    return rejected + 1


def receipt():
    fixtures, columns, digest = construction_checks()
    tensor_cases, tensor_columns = tensor_checks()
    result = {"claim_type": "scoped proof with finite corroboration",
              "construction_fixtures": fixtures, "full_input_columns": columns,
              "endpoint_sha256": digest, "paid_tensor_cases": tensor_cases,
              "paid_tensor_input_columns": tensor_columns,
              "input_rejections": rejection_checks(),
              "mutation_rejections": mutation_checks(), "no_new_kappa": True}
    root = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    result["source_sha256"] = {}
    for name in names:
        data = (root / name).read_bytes()
        require(len(data) <= 262144, "package file exceeds receipt bound")
        result["source_sha256"][name] = hashlib.sha256(data).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit-receipt", action="store_true")
    args = parser.parse_args()
    result = receipt()
    if not args.emit_receipt:
        print("PASS_FINITE_WIDTH_CALL_MIXING_TRADEOFF no_new_kappa")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
