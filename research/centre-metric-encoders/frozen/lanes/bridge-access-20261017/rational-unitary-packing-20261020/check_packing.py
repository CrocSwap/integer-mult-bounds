#!/usr/bin/env python3
"""Check the exact packing word and its odd-grid requirements."""

import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[1]
SOURCE = LANES / "independent-review-20261017/odd-unitary-packing-20261020/run-normal/PACKING.json.gz"
SOURCE_PIN = "b460c1b4603f4b75da5ca4bf1da4a642f2cc4d970599f9c1068832e7b230ac32"
PRICE = LANES / "new-core-transfer-20261017/low-displacement-20261020/check_response.py"
PRICE_PIN = "c6d92104e4345816e86163f6c1dea24fbd9b6e9b133ffd2e0c646dca17ca00a8"


def need(value, message):
    if not value:
        raise ValueError(message)


def eye(n):
    return [{i: F(1)} for i in range(n)]


def add(row, other, c):
    for j, value in other.items():
        row[j] = row.get(j, F(0)) + c * value
        if not row[j]:
            del row[j]


def product(a, b):
    result = []
    for row in a:
        out = {}
        for k, value in row.items():
            add(out, b[k], value)
        result.append(out)
    return result


def transpose(a):
    out = [{} for _ in a]
    for i, row in enumerate(a):
        for j, value in row.items():
            out[j][i] = value
    return out


def scaled(a, c):
    return [{j: c * value for j, value in row.items() if c * value}
            for row in a]


def realify(a):
    out = [{} for _ in range(2 * len(a))]
    for i, row in enumerate(a):
        for j, (x, y) in enumerate(row):
            for target, source, c in (
                    (2 * i, 2 * j, x), (2 * i, 2 * j + 1, -y),
                    (2 * i + 1, 2 * j, y), (2 * i + 1, 2 * j + 1, x)):
                if c:
                    out[target][source] = F(c)
    return out


def direct_sum(a, count):
    n = len(a)
    return [{j + k * n: c for j, c in row.items()}
            for k in range(count) for row in a]


def realify_sparse(a, n=1280):
    out = eye(n)
    for i, row in enumerate(a):
        out[2 * i], out[2 * i + 1] = {}, {}
        for j, (x, y) in row.items():
            j, x, y = int(j), F(x), F(y)
            for target, source, c in (
                    (2 * i, 2 * j, x), (2 * i, 2 * j + 1, -y),
                    (2 * i + 1, 2 * j, y), (2 * i + 1, 2 * j + 1, x)):
                if c:
                    out[target][source] = c
    return out


def heights(a):
    binary = odd = 0
    for row in a:
        for c in row.values():
            d, h2, h3 = c.denominator, 0, 0
            while d % 2 == 0:
                d //= 2
                h2 += 1
            while d % 3 == 0:
                d //= 3
                h3 += 1
            need(d == 1, "Only two and three occur in denominators")
            binary, odd = max(binary, h2), max(odd, h3)
    return binary, odd


def add_complex(word, target, source, re, im):
    for a, b, c in ((0, 0, re), (0, 1, -im), (1, 0, im), (1, 1, re)):
        if c:
            word.append(["add", 2 * target + a, 2 * source + b, str(c)])


def scale_alpha(word, port):
    x, y = 2 * port, 2 * port + 1
    word += [["add", x, y, "-1"], ["scale", y, None, "2"],
             ["add", y, x, "1"], ["scale", x, None, "1/2"],
             ["scale", y, None, "1/2"]]


def scale_one_minus_i(word, port):
    x, y = 2 * port, 2 * port + 1
    word += [["add", x, y, "1"], ["scale", y, None, "2"],
             ["add", y, x, "-1"]]


def odd_scale(word, port, c):
    for bit in (0, 1):
        word.append(["odd", 2 * port + bit, None, str(c)])


def factor_a(word, x, y):
    add_complex(word, x, y, F(1), F(1))
    odd_scale(word, y, F(3))
    add_complex(word, y, x, F(-1), F(1))


def factor_b(word, x, y):
    add_complex(word, x, y, F(1, 2), F(-1, 2))
    scale_one_minus_i(word, x)
    scale_alpha(word, y)
    odd_scale(word, y, F(3))
    add_complex(word, y, x, F(1, 2), F(-1, 2))


def inverse_word(word):
    return [[op, target, source,
             str(-F(c) if op == "add" else 1 / F(c))]
            for op, target, source, c in reversed(word)]


def swap_complex(word, x, y):
    for bit in (0, 1):
        a, b = 2 * x + bit, 2 * y + bit
        word += [["add", a, b, "1"], ["add", b, a, "-1"],
                 ["add", a, b, "1"], ["scale", b, None, "-1"]]


def packing_word(offset):
    word, a_word = [], []
    for x, y in ((offset, offset + 1), (offset + 2, offset + 3)):
        factor_b(word, x, y)
        factor_a(a_word, x, y)
    swap_complex(word, offset + 1, offset + 2)
    return word + inverse_word(a_word)


def scalar_price(op, c):
    a, b = abs(c.numerator), c.denominator
    need(a and b & (b - 1) == 0, "A dyadic old scalar coefficient")
    if op == "scale":
        need(a & (a - 1) == 0, "A signed binary scale")
        return abs(a.bit_length() - b.bit_length()) + int(c < 0)
    return 1 + a.bit_length() + a.bit_count() + b.bit_length()


def replay(word, n=1280, active_components=32):
    state = eye(n)
    price = 0
    scan = Counter()
    peak = F(1)
    binary = odd = 0
    for op, target, source, value in word:
        c = F(value)
        need(0 <= target < active_components, "Only declared data components change")
        if op == "add":
            need(source != target and 0 <= source < active_components,
                 "Distinct data components")
            add(state[target], state[source], c)
        else:
            need(op in ("scale", "odd"), "A scalar operation")
            state[target] = {j: c * v for j, v in state[target].items()}
        if op == "odd":
            need(c in (3, F(1, 3)), "A fixed three scan")
            scan[str(c)] += 1
        else:
            price += scalar_price(op, c)
        peak = max(peak, sum(abs(v) for v in state[target].values()))
        h2, h3 = heights([state[target]])
        binary, odd = max(binary, h2), max(odd, h3)
    return state, {"old_real_scalar": price, "real_odd_scans": dict(scan),
                   "instructions": len(word), "prefix_real_row_norm": str(peak),
                   "binary_height": binary, "odd_height": odd}


def mod_three(c):
    need(c.denominator % 3, "A dyadic residue exists")
    return c.numerator * pow(c.denominator, -1, 3) % 3


def rank_three(matrix):
    a = [[mod_three(row.get(j, F(0))) for j in range(len(matrix))]
         for row in matrix]
    rank = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][j]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        a[rank] = [x * pow(a[rank][j], -1, 3) % 3 for x in a[rank]]
        for i in range(len(a)):
            if i != rank and a[i][j]:
                c = a[i][j]
                a[i] = [(x - c * y) % 3 for x, y in zip(a[i], a[rank])]
        rank += 1
    return rank, a


def signed_scan(n, width, divide):
    bits = [(n % (1 << width) >> j) & 1 for j in range(width)]
    carry, output = 0, 0
    for j, b in enumerate(bits):
        if divide:
            a = (b - carry) % 2
            carry = (carry + 3 * a - b) // 2
        else:
            a, carry = (3 * b + carry) % 2, (3 * b + carry) // 2
        need(0 <= carry < 3, "The fixed carry range")
        output |= a << j
    sn, sq = bits[-1], (output >> (width - 1)) & 1
    signed = output - sq * (1 << width)
    valid = carry == (3 * sq - sn if divide else 3 * sn - sq)
    return valid, signed


def scan_checks():
    count = 0
    for width in range(1, 12):
        for n in range(-(1 << (width - 1)), 1 << (width - 1)):
            valid, value = signed_scan(n, width, True)
            need(valid == (n % 3 == 0), "The exact division domain")
            if valid:
                need(value == n // 3, "The signed quotient")
            valid, value = signed_scan(n, width, False)
            fits = -(1 << (width - 1)) <= 3 * n < 1 << (width - 1)
            need(valid == fits, "The multiplication overflow test")
            if valid:
                need(value == 3 * n, "The signed product")
            count += 2
    return count


def integer_word(word, root_scale):
    binary = replay(word)[1]["binary_height"]
    state = [[int(i == j) * root_scale * 2 ** binary for j in range(32)]
             for i in range(32)]
    for op, target, source, value in word:
        c = F(value)
        candidate = ([F(x) + c * y for x, y in zip(state[target], state[source])]
                     if op == "add" else [c * x for x in state[target]])
        if any(x.denominator != 1 for x in candidate):
            return False
        state[target] = [int(x) for x in candidate]
    return True


def serialized(matrix):
    return [{str(j): str(v) for j, v in sorted(row.items())} for row in matrix]


def actual_code(word, inverse, r):
    raw = gzip.decompress(SOURCE.read_bytes())
    need(sha256(raw).hexdigest() == SOURCE_PIN, "The frozen actual packing source")
    need(sha256(PRICE.read_bytes()).hexdigest() == PRICE_PIN, "The scalar tariff source")
    source = json.loads(raw)
    need(realify_sparse(source["packing"], 8) == r, "The same four-field packing")
    ports = sum(source["packing_ports"], [])
    need(len(ports) == len(set(ports)) == 16, "Four disjoint actual quartets")

    def placed(instructions):
        return [[op, 2 * ports[target // 2] + target % 2,
                 None if old is None else 2 * ports[old // 2] + old % 2, c]
                for op, target, old, c in instructions]

    code = source["precode_words"]["precode"] + placed(word)
    adjoint = placed(inverse) + source["precode_words"]["precode_adjoint"]
    expected = realify_sparse(source["code"])
    fw, report = replay(code, active_components=224)
    bw, inverse_report = replay(adjoint, active_components=224)
    need(fw == expected, "The actual full code on all1280 real input columns")
    need(bw == transpose(expected), "The actual full adjoint on all1280 columns")
    need(product(fw, bw) == product(bw, fw) == eye(1280),
         "The actual complete code restores arbitrary data and borrowed state")
    trace = [sum((F(row.get(str(i), ["0", "0"])[k])
                  for i, row in enumerate(source["code"])), F(0)) for k in (0, 1)]
    need(trace == [F(11, 6), F(7, 6)], "The exact nonintegral three-adic trace")
    small = expected[:224]
    matrix, powers = eye(224), []
    for exponent in range(1, 5):
        matrix = product(small, matrix)
        need(heights(matrix)[1] == exponent, "The first four actual power heights")
        powers.append({"power": exponent, "odd_height": exponent})
    precode_inverse = realify_sparse(source["precode_adjoint"], 224)
    witness = [row.get(2 * ports[0], F(0)) for row in precode_inverse]
    need(heights([{i: c for i, c in enumerate(witness) if c}])[1] == 0,
         "A dyadic input gives the failing first packing basis vector")
    need(heights([r[0]])[1] == 1, "That unscaled input has a genuine third")
    return {"source": str(SOURCE.relative_to(LANES)), "source_sha256": SOURCE_PIN,
            "packing_ports": source["packing_ports"],
            "words": {"code": code, "adjoint": adjoint}}, {
                "code": report, "adjoint": inverse_report,
                "trace": list(map(str, trace)), "power_checks": powers,
                "all_positive_power_odd_height": "m, by the trace and spectral-radius proof",
                "untouched_complex_fields": 528, "full_real_columns": 1280}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    a = realify([[(1, 0), (1, 1)], [(-1, 1), (1, 0)]])
    b = realify([[(1, -1), (0, -1)], [(0, -1), (1, 1)]])
    need(product(transpose(a), a) == scaled(eye(4), 3), "A* A = 3I")
    need(product(transpose(b), b) == scaled(eye(4), 3), "B* B = 3I")
    p = eye(8)
    p[2], p[4], p[3], p[5] = p[4], p[2], p[5], p[3]
    numerator = product(product(direct_sum(transpose(a), 2), p), direct_sum(b, 2))
    r = scaled(numerator, F(1, 3))
    need(product(transpose(r), r) == product(r, transpose(r)) == eye(8),
         "Both exact unitary orders")
    word = sum((packing_word(4 * block) for block in range(4)), [])
    inverse = inverse_word(word)
    expected = direct_sum(r, 4) + eye(1280)[32:]
    forward, fw = replay(word)
    backward, bw = replay(inverse)
    need(forward == expected, "All 1280 real columns of the forward word")
    need(backward == transpose(expected), "All 1280 real columns of the inverse")
    need(product(forward, backward) == product(backward, forward) == eye(1280),
         "Both full inverse orders with arbitrary borrowed columns")
    rank, reduced = rank_three(numerator)
    need(rank == 2, "Two real, or one Gaussian, residue constraints per block")
    need(integer_word(word, 3) and integer_word(inverse, 3),
         "One paid root factor gives integer prefixes in each direction")
    need(not integer_word(word, 1) and not integer_word(inverse, 1),
         "The unscaled arbitrary input contract fails")
    need(replay(word + inverse)[0] == eye(1280), "Exact complete restoration")
    need(integer_word(word + inverse, 3), "One root factor for the restored pair")
    powers, matrix = [], eye(8)
    for exponent in range(1, 13):
        matrix = product(r, matrix)
        powers.append({"power": exponent, "odd_height": heights(matrix)[1]})
    need(product(product(r, r), product(r, r)) == eye(8), "The packing has order four")
    sign = eye(8)
    sign[0], sign[1] = {0: F(-1)}, {1: F(-1)}
    signed_numerator = product(numerator, sign)
    need(rank_three(signed_numerator)[0] == 2, "The signed residue has Gaussian rank one")
    signed_trace = [sum((signed_numerator[2 * i + k].get(2 * i, F(0))
                        for i in range(4)), F(0)) for k in (0, 1)]
    need(signed_trace == [F(-2), F(2)], "The nonzero signed residue trace")
    damaged = [event for i, event in enumerate(word) if i != 0]
    need(replay(damaged)[0] != expected, "An omitted scalar gate is rejected")
    program = {"A_real": serialized(a), "B_real": serialized(b),
               "R_real": serialized(r), "numerator_real": serialized(numerator),
               "residue_reduced_rows": reduced[:rank],
               "words": {"packing": word, "inverse": inverse}}
    actual, actual_report = actual_code(word, inverse, r)
    program["actual_code"] = actual
    receipt = {"status": "PASS_RATIONAL_PACKING_GRID",
               "packing": fw, "inverse": bw, "residue_rank_real": rank,
               "full_real_columns": 1280, "untouched_complex_fields": 624,
               "signed_scan_cases": scan_checks(), "repeated_packing": powers,
               "signed_interleaving_trace": list(map(str, signed_trace)),
               "actual_code": actual_report}
    for name, data in (("PACKING.json", program), ("CHECKS.json", receipt)):
        raw = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode()
        (args.out / name).write_bytes(raw)
        print(name, sha256(raw).hexdigest())
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
