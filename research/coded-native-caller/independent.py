#!/usr/bin/env python3
"""Finite modular controls, independently implemented without Clifford imports.

Apache-2.0. Prepared by a separate OpenAI Codex review agent, not an independent
human reviewer. These deterministic finite controls corroborate PHYSICAL.md;
they do not prove the universal identities or replay the native producer.
"""
from fractions import Fraction
from pathlib import Path
import argparse
import json

HERE = Path(__file__).resolve().parent
PRIME = 65537
IMAGINARY = 256
HALF = pow(2, -1, PRIME)
WIDTH = 512
OWNERS = 112


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    require(IMAGINARY * IMAGINARY % PRIME == PRIME - 1,
            "The chosen field element must represent i")
    receipt = json.loads((HERE / "NORMALIZERS.json").read_text())
    raw_code = json.loads((HERE / "CODE.json").read_text())["A"]
    require(len(raw_code) == OWNERS and
            all(len(row) == OWNERS for row in raw_code), "Code dimensions")
    code = []
    for row in raw_code:
        sparse = []
        for j, value in enumerate(row):
            c = Fraction(value)
            if c:
                sparse.append((j, c.numerator * pow(c.denominator, -1, PRIME)
                               % PRIME))
        code.append(sparse)

    require(len(receipt["ports"]) == OWNERS, "All physical port records")
    permutations = []
    compiled_words = 0
    for record in receipt["ports"]:
        rows, mask = record["G_rows"], record["Z_mask"]
        require(len(rows) == 9, "Nine binary address axes")
        mapping = []
        for x in range(WIDTH):
            y = sum(((g & x).bit_count() % 2) << j
                    for j, g in enumerate(rows))
            mapping.append((y, -1 if (mask & y).bit_count() % 2 else 1))
        require(sorted(y for y, _ in mapping) == list(range(WIDTH)),
                "Each retained K is a signed permutation")
        permutations.append(mapping)
        wrappers = record["compiled_wrappers"]
        require(len(wrappers) == 8, "Four forward and four backward wrappers")
        for wrapper in wrappers.values():
            require(all(event[0] in ("P", "D", "X", "phase")
                        for event in wrapper["word"]),
                    "Compiled physical wrappers contain no Gaussian gate")
            compiled_words += 1

    def signed_map(bank, inverse=False):
        out = [[0] * WIDTH for _ in range(OWNERS)]
        for i, row in enumerate(bank):
            if inverse:
                for j, (k, sign) in enumerate(permutations[i]):
                    out[i][j] = sign * row[k] % PRIME
            else:
                for j, (k, sign) in enumerate(permutations[i]):
                    out[i][k] = sign * row[j] % PRIME
        return out

    def recode(bank, inverse=False):
        common = signed_map(bank)
        out = []
        for i in range(OWNERS):
            row = [0] * WIDTH
            for j, coefficient in code[i]:
                for k in range(WIDTH):
                    row[k] += coefficient * common[j][k]
            out.append([value % PRIME for value in row])
        out = signed_map(out, True)
        if inverse:
            denominator = pow(13, -1, PRIME)
            out = [[(a + 12 * b) * denominator % PRIME
                    for a, b in zip(row, original)]
                   for row, original in zip(out, bank)]
        return out

    def gaussian(bank, axes, sign=1):
        out = [row[:] for row in bank]
        diagonal = (1 + sign * IMAGINARY) * HALF % PRIME
        off_diagonal = (1 - sign * IMAGINARY) * HALF % PRIME
        for bit in axes:
            step = 1 << bit
            for row in out:
                for start in range(0, WIDTH, 2 * step):
                    for k in range(start, start + step):
                        u, v = row[k], row[k + step]
                        row[k] = (diagonal * u + off_diagonal * v) % PRIME
                        row[k + step] = (off_diagonal * u + diagonal * v) % PRIME
        return out

    def q(bank, exponent=1):
        out = bank
        for _ in range(abs(exponent)):
            out = gaussian(out, [0], 1 if exponent > 0 else -1)
        return out

    def d(bank, exponent=1):
        out = bank
        for _ in range(abs(exponent)):
            out = gaussian(out, range(1, 9), 1 if exponent > 0 else -1)
        return out

    def add(left, right, sign=1):
        return [[(a + sign * b) % PRIME for a, b in zip(u, v)]
                for u, v in zip(left, right)]

    x = [[(17 * i * i + 13 * j * j + 3 * i * j + 2 * i + 5 * j + 7)
          % PRIME for j in range(WIDTH)] for i in range(OWNERS)]
    y = [[(19 * i * i + 11 * j * j + 7 * i * j + 3 * i + 2 * j + 11)
          % PRIME for j in range(WIDTH)] for i in range(OWNERS)]
    require(signed_map(signed_map(x), True) == x, "K inverse finite control")
    cx = recode(x)
    require(recode(cx, True) == x, "C inverse finite control")
    require(recode(q(d(x))) == q(d(cx)), "Actual code commutes with DQ")
    require(recode(q(x)) != q(cx), "Actual code must expose [C,Q] nonzero")

    # Evaluate the raw inverse transpose, then the proposed physical correction.
    x0 = q(x, -2)
    u = d(add(x0, q(recode(y), -1), -1), -1)
    v = d(y, -1)
    u, v = q(d(u, 2), 2), d(v, 2)
    require(u == d(add(x, q(recode(y)), -1)) and v == d(y),
            "X-only Q squared correction of the actual raw dual")

    # The old Y-only convention is a genuine failing control for this actual C.
    y0 = q(y, -2)
    old_u = d(add(x, q(recode(y0), -1), -1), -1)
    old_u = d(old_u, 2)
    require(old_u != u, "Old Y-only Q squared convention must fail")
    return {
        "schema": "coded-native-independent-modular-controls/1",
        "status": "PASS_INDEPENDENT_FINITE_MODULAR_CONTROLS",
        "prime": PRIME,
        "imaginary_unit": IMAGINARY,
        "fiber_columns": 1,
        "owners_per_bank": OWNERS,
        "addresses_per_owner": WIDTH,
        "deterministic_test_vectors": 2,
        "compiled_gaussian_free_words": compiled_words,
        "positive_controls": ["signed-map inverse", "code inverse",
                              "C commutes with DQ", "X-only raw-dual correction"],
        "negative_controls": ["C does not commute with Q",
                              "old Y-only correction fails"],
        "scope": "Finite deterministic modular corroboration; not a universal "
                 "proof, native-word replay, or independent human acceptance.",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result = run()
    target = HERE / "INDEPENDENT.json"
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(json.loads(target.read_text()) == result,
                "Regenerated independent-control receipt")
    print(result["status"])


if __name__ == "__main__":
    main()
