"""Exact new packing checks. Produced by Nick Petalas. Apache-2.0."""
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from packing import child_bits, decode, residue_lane


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def convolution(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


def exhaustive():
    cases = coefficients = 0
    for k, maximum_length in ((1, 4), (2, 3), (3, 2)):
        modulus = 1 << k
        arrays = [a for length in range(1, maximum_length + 1)
                  for a in product(range(modulus), repeat=length)]
        for a in arrays:
            for b in arrays:
                residues, bill = residue_lane(a, b, k)
                expected = convolution(a, b)
                check(residues == [x % modulus for x in expected], "literal residue convolution")
                signed_a = tuple(x if x < modulus // 2 else x - modulus for x in a)
                signed_b = tuple(x if x < modulus // 2 else x - modulus for x in b)
                signed = convolution(signed_a, signed_b)
                slot = bill["slot_bits"]
                packed = sum(x << (j * slot) for j, x in enumerate(signed))
                check(decode(packed, len(a), len(b), k, slot) == signed, "every signed coefficient")
                check(bill["exact_child_calls"] == 1, "one paid magnitude product")
                cases += 1
                coefficients += len(expected)
    return {"array_pairs": cases, "coefficients": coefficients}


def literal_size(n, digit_bits, k, original):
    length = (n + digit_bits - 1) // digit_bits
    base = 1 << digit_bits
    digits = [(original >> (j * digit_bits)) % base for j in range(length)]
    residues, bill = residue_lane(digits, [0] * length, k)
    check(residues == [0] * (2 * length - 1), "zero partner")
    return bill["left_child_bits"]


def size_checks():
    cases = inputs = 0
    for digit_bits in range(1, 5):
        for n in range(1, 11):
            for k in range(1, digit_bits + 1):
                largest = max(literal_size(n, digit_bits, k, x) for x in range(1 << n))
                check(largest == child_bits(n, digit_bits, k), "attained small maximum")
                inputs += 1 << n
                cases += 1
    admitted = old_admitted = width_pairs = tail_widths = 0
    for n in range(1, 14593):
        length = (n + 63) // 64
        top = n - 64 * (length - 1)
        h = (length - 1).bit_length()
        for k in range(1, 65):
            exact = child_bits(n, 64, k)
            old = min(k, top) + (length - 1) * (2 * k + h)
            check(old - exact == length - 1, "slot saving")
            admitted += exact < n
            old_admitted += old < n
            width_pairs += 1
        if n >= 29:
            check(child_bits(n, 64, 28) < n, "uniform k28 tail")
            tail_widths += 1
    for n, k in ((14592, 28), (8193, 28), (8193, 29), (65, 28), (29, 28)):
        length = (n + 63) // 64
        top = n - 64 * (length - 1)
        attainer = 1 << (64 * (length - 1) + min(k, top) - 1)
        check(literal_size(n, 64, k, attainer) == child_bits(n, 64, k), "large attainer")
    check(child_bits(8193, 64, 29) == 8321, "k29 boundary obstruction")
    return {"small_size_cases": cases, "small_inputs": inputs,
            "width_pairs": width_pairs, "admitted": admitted,
            "unsigned_admitted": old_admitted, "k28_tail_widths": tail_widths,
            "full_k28_bits": child_bits(14592, 64, 28)}


def controls():
    rejected = 0
    for a, b, k in (([], [1], 2), ([1], [], 2), ([True], [1], 2),
                    ([-1], [1], 2), ([1 << 64], [1], 2), ([1], [1], 0),
                    ([1], [1], 65), ([0] * 229, [1], 2)):
        try:
            residue_lane(a, b, k)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid lane accepted")
    for args in ((0, 64, 28), (14593, 64, 28), (100, 0, 1), (100, 64, 65)):
        try:
            child_bits(*args)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid size accepted")
    # All -half gives the positive half-base endpoint, which symmetric
    # half-open centered extraction would turn into a negative coefficient.
    signed = convolution((-2, -2), (-2, -2))
    check(signed == [4, 8, 4], "positive endpoint fixture")
    check(decode(4 + 8 * 16 + 4 * 256, 2, 2, 2, 4) == signed, "asymmetric endpoint")
    check(((8 + 8) % 16) - 8 != 8, "symmetric decoder must fail")
    # One fewer bit puts the attainable middle coefficients -4 and +4
    # in the same residue class modulo eight.
    check(convolution((-1, -1), (-2, -2))[1] == 4, "positive collision attainer")
    check(convolution((-2, -2), (1, 1))[1] == -4, "negative collision attainer")
    check(4 % 8 == (-4) % 8, "undersized-slot collision")
    actual, _ = residue_lane((3, 0), (1, 0), 2)
    check(actual == [3, 0, 0], "negative packed product")
    naive = [((-1 >> (4 * j)) & 15) % 4 for j in range(3)]
    check(naive != actual, "unsigned extraction must fail on negative pack")
    for args in ((0, 2, 2, 2, 3), (16 ** 3, 2, 2, 2, 4)):
        try:
            decode(*args)
        except ValueError:
            rejected += 1
        else:
            raise AssertionError("invalid decoder accepted")
    return {"rejections": rejected, "semantic_controls": 4}


def receipt():
    result = {"status": "PASS_CENTERED_GAUSSIAN_RESIDUE", "claim_type": "scoped proof",
              "exhaustive": exhaustive(), "sizes": size_checks(), "controls": controls()}
    files = sorted(p for p in ROOT.iterdir() if p.is_file())
    check(len(files) == 8, "package file count")
    result["sha256"] = {}
    for path in files:
        with path.open("rb") as stream:
            raw = stream.read(1024 * 1024 + 1)
        check(len(raw) <= 1024 * 1024, "receipt file capacity")
        result["sha256"][path.name] = sha256(raw).hexdigest()
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    receipt()
