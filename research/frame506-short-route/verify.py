#!/usr/bin/env python3
"""Check the new fixed matcher word, its lift, carries and complete ledger.

Produced by Nick Petalas. Apache-2.0.
PR4989 / JoyboyBrian supplies the unchanged matcher and schedule contract.
No predecessor executable is imported or replayed.
"""

import argparse
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
FRAME_PATH = "research/kappa-rebuild/bit/sources/pr589-regenerated/records/frames.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    return [[sum(x * y for x, y in zip(row, col))
             for col in zip(*b)] for row in a]


def load_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    hashes = {}
    for source in manifest["files"]:
        if source["usage"] == "input":
            path = source["path"]
            raw = (ROOT / path).read_bytes()
            need(sha256(raw).hexdigest() == source["sha256"], "source drift: " + path)
            hashes[path] = source["sha256"]
    frame = json.loads((ROOT / FRAME_PATH).read_text())["frames"]["506"]
    need(frame["dim"] == 4, "wrong frame dimension")
    matrix = [[F(x) for x in row] for row in zip(*(frame["B"] + frame["A"]))]
    need(len(matrix) == 8 and all(len(row) == 8 for row in matrix), "matcher shape")
    return matrix, hashes


def parse_word(raw):
    need(isinstance(raw, list) and 1 <= len(raw) <= 32, "word size")
    word = []
    for entry in raw:
        need(isinstance(entry, list) and len(entry) == 4, "factor shape")
        kind, i, j, coefficient = entry
        need(kind in ("add", "scale", "swap"), "factor kind")
        need(type(i) is int and type(j) is int and 0 <= i < 8 and 0 <= j < 8,
             "factor address")
        need(type(coefficient) is int and coefficient != 0, "factor coefficient")
        need((i == j) == (kind == "scale"), "factor ports")
        need(kind != "swap" or coefficient == 1, "swap coefficient")
        word.append((kind, i, j, F(coefficient)))
    return tuple(word)


def inverse_word(word):
    return tuple((kind, i, j, 1 / c if kind == "scale" else -c if kind == "add" else c)
                 for kind, i, j, c in reversed(word))


def apply_rational(row, word):
    result = list(row)
    for kind, i, j, c in word:
        if kind == "swap":
            result[i], result[j] = result[j], result[i]
        elif kind == "scale":
            result[i] *= c
        else:
            result[j] += c * result[i]
    return result


def word_matrix(word):
    return [apply_rational(row, word) for row in identity(8)]


def residue(c, modulus):
    return (c.numerator * pow(c.denominator, -1, modulus)) % modulus


def apply_modular(row, word, f, modulus):
    result = list(row)
    for kind, i, j, c in word:
        for lane in range(f):
            a, b = i * f + lane, j * f + lane
            if kind == "swap":
                result[a], result[b] = result[b], result[a]
            elif kind == "scale":
                result[a] = result[a] * residue(c, modulus) % modulus
            else:
                result[b] = (result[b] + residue(c, modulus) * result[a]) % modulus
    return result


def dense_modular(row, matrix, f, modulus):
    result = [0] * (8 * f)
    for i in range(8):
        for j in range(8):
            c = residue(matrix[i][j], modulus)
            for lane in range(f):
                result[j * f + lane] += c * row[i * f + lane]
    return [value % modulus for value in result]


def carry_route(row, word, matrix, f, q, w):
    """The retained whole-route low cache / carry / commit interface."""
    modulus, high_modulus = q ** w, q ** (w - 1)
    low, high = [x % q for x in row], [x // q for x in row]
    linear = apply_modular(high, word, f, high_modulus)
    low_image = dense_modular(low, matrix, f, modulus)
    new_low = [value % q for value in low_image]
    carry = [(value - digit) // q for value, digit in zip(low_image, new_low)]
    need(all(0 <= value < high_modulus for value in carry), "carry range")
    return [digit + q * ((value + shift) % high_modulus)
            for digit, value, shift in zip(new_low, linear, carry)]


def emit(f, borrowed):
    """Emit the inherited addressed shell with the new factor sequence."""
    need(type(f) is int and 1 <= f <= 8, "checker tensor width")
    need(type(borrowed) is bool, "branch type")
    n = 8 * f
    word = parse_word(json.loads((HERE / "WORD.json").read_text()))
    steps = [("outer_enter", ())]
    for direction in (1, -1):
        steps.extend((name, ()) for name in ("route_enter", "cache_allocate"))
        steps.extend(("cache_copy", (cell,)) for cell in range(n * n))
        factors = word if direction == 1 else inverse_word(word)
        for kind, i, j, _ in factors:
            for row in range(n):
                for lane in range(f):
                    addresses = (row * n + i * f + lane, row * n + j * f + lane)
                    if kind == "swap" and borrowed:
                        names = ("inner_borrow", "row_pad", "body_sub", "raw_reverse_swap",
                                 "body_add", "raw_reverse_swap", "body_rsub", "inner_return",
                                 "row_unpad", "older_high_swap")
                    else:
                        names = ({"swap": "older_full_swap", "scale": "unit_scale",
                                  "add": "ordered_shift"}[kind],)
                    steps.extend((name, addresses) for name in names)
        steps.extend(("carry_shift", (cell,)) for cell in range(n * n))
        steps.append(("low_type_commit", ()))
        steps.extend(("cache_clear", (cell,)) for cell in range(n * n))
        steps.extend((name, ()) for name in ("cache_release", "route_return"))
        if direction == 1:
            steps.append(("native_canonical", (4 * f,)))
    steps.append(("outer_return", ()))
    return steps


def check_ledgers():
    records = []
    for f in (1, 2, 3, 8):
        n = 8 * f
        for borrowed in (False, True):
            steps = emit(f, borrowed)
            counts = Counter(name for name, _ in steps)
            need(counts["unit_scale"] == 8 * n * f, "scale ledger")
            need(counts["ordered_shift"] == 14 * n * f, "shift ledger")
            earlier = sum(name == "ordered_shift" and ports[1] < ports[0]
                          for name, ports in steps)
            need(earlier == 8 * n * f, "earlier-target ledger")
            need(counts["ordered_shift"] - earlier == 6 * n * f, "later-target ledger")
            swap = "older_high_swap" if borrowed else "older_full_swap"
            need(counts[swap] == 10 * n * f, "ordinary swap ledger")
            for name in ("cache_copy", "cache_clear", "carry_shift"):
                need(counts[name] == 2 * n * n, name + " ledger")
            need(counts["low_type_commit"] == 2 and counts["native_canonical"] == 1,
                 "commit/native ledger")
            coefficient = 122 if borrowed else 32
            need(len(steps) == 13 + 6 * n * n + coefficient * n * f, "full ledger")
            for name, addresses in steps:
                if name != "native_canonical":
                    need(all(0 <= address < n * n for address in addresses), "address range")
            records.append({"f": f, "borrowed": borrowed, "steps": len(steps),
                            "removed_steps": 16 * n * f, "earlier_target_shifts": earlier,
                            "later_target_shifts": 6 * n * f,
                            "counts": dict(sorted(counts.items()))})
    return records


def check_rows(word, matrix, inverse):
    cases = 0
    inverse_matrix = word_matrix(inverse)
    for f in (1, 2, 3):
        n = 8 * f
        for q in (3, 5, 7, 11):
            for w in (2, 3, 5):
                modulus = q ** w
                rows = [[int(i == j) for j in range(n)] for i in range(n)]
                rows.extend([[(i * i + 13 * i + 7 * seed + 3) % modulus
                              for i in range(n)] for seed in range(8)])
                rows.extend([[modulus - 1] * n, [q - 1] * n])
                for row in rows:
                    expected = dense_modular(row, matrix, f, modulus)
                    actual = apply_modular(row, word, f, modulus)
                    need(actual == expected, "literal modular endpoint")
                    need(carry_route(row, word, matrix, f, q, w) == expected, "forward carry")
                    need(carry_route(expected, inverse, inverse_matrix, f, q, w) == row,
                         "inverse carry restoration")
                    cases += 1
    return cases


def rejects_word(raw, matrix):
    try:
        candidate = parse_word(raw)
        return word_matrix(candidate) != matrix
    except (ValueError, TypeError, IndexError):
        return True


def check_controls(raw, word, matrix):
    rejected = []
    for position in range(len(raw)):
        need(rejects_word(raw[:position] + raw[position + 1:], matrix), "omitted factor accepted")
        rejected.append("omit_factor_" + str(position))
    for position in (0, 2, 3, 5, 6, 7, 8):
        mutant = [list(entry) for entry in raw]
        mutant[position][3] *= -1
        need(rejects_word(mutant, matrix), "wrong sign accepted")
        rejected.append("wrong_sign_" + str(position))
    need(rejects_word(list(reversed(raw)), matrix), "wrong order accepted")
    rejected.append("reversed_word")
    row = [4, 4, 4, 4, 4, 4, 4, 4]
    expected = dense_modular(row, matrix, 1, 25)
    no_carry = [value % 5 for value in expected]
    need(no_carry != expected, "nonzero carry control")
    rejected.append("omitted_global_carry")
    malformed = [list(entry) for entry in raw]
    malformed[0][1] = True
    need(rejects_word(malformed, matrix), "Boolean address accepted")
    rejected.append("Boolean_address")
    need(word_matrix(inverse_word(word)) != matrix, "inverse orientation control")
    rejected.append("inverse_as_forward")
    return rejected


def run():
    matrix, sources = load_sources()
    raw = json.loads((HERE / "WORD.json").read_text())
    word = parse_word(raw)
    need(word_matrix(word) == matrix, "new rational factorization")
    inverse = inverse_word(word)
    need(multiply(word_matrix(word), word_matrix(inverse)) == identity(8), "right inverse")
    need(multiply(word_matrix(inverse), matrix) == identity(8), "left inverse")
    counts = dict(sorted(Counter(entry[0] for entry in word).items()))
    need(counts == {"add": 7, "scale": 4, "swap": 5}, "new factor counts")
    rows = check_rows(word, matrix, inverse)
    ledgers = check_ledgers()
    controls = check_controls(raw, word, matrix)
    hashes = {path.name: sha256(path.read_bytes()).hexdigest()
              for path in sorted(HERE.iterdir()) if path.is_file() and path.name != "RESULT.json"}
    return {"claim_type": "finite factorization certificate with scoped tensor-lift proof",
            "factors": len(word), "factor_counts": counts, "modular_rows": rows,
            "ledgers": ledgers, "rejected_controls": controls,
            "source_sha256": sources, "package_sha256": hashes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path, help="exclusive-create generated receipt")
    args = parser.parse_args()
    result = run()
    if args.emit is not None:
        with args.emit.open("x", encoding="utf-8") as output:
            output.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text())
        need(json.dumps(expected, sort_keys=True) == json.dumps(result, sort_keys=True),
             "receipt drift")
    print(json.dumps({"factors": result["factors"], "factor_counts": result["factor_counts"],
                      "modular_rows": result["modular_rows"],
                      "controls": len(result["rejected_controls"])}, sort_keys=True))
    print("PASS_FRAME506_SHORT_ROUTE")


if __name__ == "__main__":
    main()
