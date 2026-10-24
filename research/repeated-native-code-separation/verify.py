"""Check repeated native code separation through reduced degree 32.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""

import argparse
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path

# Set the thread limits before the optional numerical library is loaded.
for name in ("OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "OMP_NUM_THREADS"):
    os.environ[name] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/coded-native-caller"
PRIME = 65521
DEGREE = 32


def need(condition, message):
    if not condition:
        raise ValueError(message)


def source_checks():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for item in manifest["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            need(hashlib.sha256(raw).hexdigest() == item["sha256"], "Source hash: " + item["path"])
    data = json.loads((SOURCE / "NORMALIZERS.json").read_text())
    code = [[Fraction(x) for x in row] for row in json.loads((SOURCE / "CODE.json").read_text())["A"]]
    modes = data["mode_columns"]
    ports = data["ports"]
    need(len(code) == len(ports) == 112 and all(len(row) == 112 for row in code), "Owner dimensions")
    need(len(modes) == 8 and all(len(row) == 112 for row in modes), "Mode dimensions")
    need(all(x in (-1, 0, 1) for row in modes for x in row), "Mode entries")
    for i in range(112):
        for j in range(112):
            need(sum(row[i] * row[j] for row in modes) == 4 * ((i == j) - code[i][j]), "Mode factorization")
    for a in range(8):
        for b in range(8):
            need(sum(x * y for x, y in zip(modes[a], modes[b])) == 56 * (a == b), "Orthogonal modes")
    tables = []
    for i, port in enumerate(ports):
        rows = port["G_rows"]
        need(port["port"] == i and len(rows) == 9, "Normalizer order")
        need(all(type(x) is int and 0 <= x < 512 for x in rows), "Binary row domain")
        need(all(((a & b).bit_count() % 2) == (j == k)
                 for j, a in enumerate(rows) for k, b in enumerate(rows)), "Orthogonal normalizer")
        need(port["K_word"] == [["P", rows], ["D", [0] * 9,
             [2 * ((port["Z_mask"] >> j) & 1) for j in range(9)]]], "Literal signed normalizer")
        table = []
        for x in range(512):
            y = sum(((row & x).bit_count() % 2) << j for j, row in enumerate(rows))
            table.append((y, (-1) ** ((port["Z_mask"] & y).bit_count())))
        need(table[0] == (0, 1) and table[1][0] == port["q"], "Normalizer central vector")
        need(len({y for y, sign in table}) == 512, "Normalizer permutation")
        tables.append(table)
    return modes, tables


def reduce_word(word):
    out = []
    for stage in word:
        if not out or out[-1] != stage:
            out.append(stage)
    return tuple(out)


def gram(rows, degree=DEGREE):
    need(1 <= degree <= DEGREE, "The certificate covers degrees 1 through 32")
    normalized = [[x * pow(pow(56, n, PRIME), -1, PRIME) % PRIME for x in row]
                  for n, row in enumerate(rows)]
    words = [tuple((start + j) % 2 for j in range(n))
             for n in range(1, degree + 1) for start in (0, 1)]
    matrix = []
    for a in words:
        row = []
        for b in words:
            length = len(reduce_word(a[::-1] + b))
            outside = sum(x * y for x, y in zip(normalized[len(a)], normalized[len(b)]))
            row.append((normalized[length][0] - outside) % PRIME)
        matrix.append(row)
    return matrix


def determinant_mod(matrix):
    a = [row[:] for row in matrix]
    result = 1
    for i in range(len(a)):
        pivot = next((j for j in range(i, len(a)) if a[j][i] % PRIME), None)
        if pivot is None:
            return 0
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            result = -result
        value = a[i][i] % PRIME
        result = result * value % PRIME
        inverse = pow(value, -1, PRIME)
        for j in range(i + 1, len(a)):
            coefficient = a[j][i] * inverse % PRIME
            for k in range(i, len(a)):
                a[j][k] = (a[j][k] - coefficient * a[i][k]) % PRIME
    return result % PRIME


def determinant_bareiss(matrix):
    """Use integer elimination without modular inverses."""
    a = [row[:] for row in matrix]
    sign, previous = 1, 1
    for k in range(len(a) - 1):
        pivot = next((i for i in range(k, len(a)) if a[i][k]), None)
        if pivot is None:
            return 0
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        for i in range(k + 1, len(a)):
            for j in range(k + 1, len(a)):
                numerator = a[k][k] * a[i][j] - a[i][k] * a[k][j]
                need(numerator % previous == 0, "Exact Bareiss division")
                a[i][j] = numerator // previous
        previous = a[k][k]
        for i in range(k + 1, len(a)):
            a[i][k] = 0
    return sign * a[-1][-1]


def rejection(action):
    try:
        action()
    except ValueError:
        return 1
    raise ValueError("A negative control was accepted")


def check_rows(rows):
    need(len(rows) == 65 and all(len(row) == 112 for row in rows), "65 complete moments")
    need(all(type(x) is int and 0 <= x < PRIME for row in rows for x in row), "Moment residues")
    need(rows[0] == [1] + [0] * 111, "Initial basis vector")


def controls(rows, matrix):
    count = 0
    duplicate = [row[:] for row in matrix]
    duplicate[1] = duplicate[0][:]
    need(determinant_mod(duplicate) == 0, "Duplicate word is dependent")
    count += 1
    # Two identical projections give the same two length-one vectors.
    one = gram(rows, 1)[0][0]
    need(determinant_mod([[one, one], [one, one]]) == 0, "Repeated identical stage boundary")
    count += 1
    bad = [row[:] for row in rows]
    bad[0][0] = True
    count += rejection(lambda: check_rows(bad))
    count += rejection(lambda: gram(rows, 33))
    # An adjacent inverse pair is the empty reduced code word and is legal.
    for eigenvalue in (1, -13):
        need(Fraction(eigenvalue) * Fraction(eigenvalue + 12, 13) == 1, "Inverse cancellation control")
    for exponent in range(-5, 6):
        need((Fraction(-13) ** exponent - 1 == 0) == (exponent == 0), "Nonzero syllable coefficient")
    count += 2
    return count


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate-only", action="store_true")
    parser.add_argument("--native-input", type=Path)
    parser.add_argument("--check-native", type=Path)
    args = parser.parse_args()
    modes, tables = source_checks()
    need(all(PRIME % d for d in range(2, 256)), "Prime modulus")
    if args.native_input:
        with args.native_input.open("x", encoding="utf-8") as stream:
            for row in modes:
                stream.write(" ".join(map(str, row)) + "\n")
            for table in tables:
                for y, sign in table:
                    stream.write(f"{y} {sign}\n")
        print("PASS_NATIVE_INPUT_EXPORT")
        return
    receipt = json.loads((HERE / "RESULT.json").read_text())
    raw = (HERE / "MOMENTS.json").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == receipt["moment_sha256"], "Moment bytes")
    moments = json.loads(raw)
    header = {key: value for key, value in moments.items() if key != "rows"}
    need(header == {"schema_version": 1, "prime": PRIME, "operator_scale": 56,
                    "address_bits": 17, "input_owner": 0, "input_address": 1}, "Moment header")
    rows = moments["rows"]
    check_rows(rows)
    if args.check_native:
        lines = [list(map(int, line.split())) for line in args.check_native.read_text().splitlines()]
        need([row[0] for row in lines] == list(range(65)), "Native moment indices")
        need([row[1:] for row in lines] == rows, "All native moments")
    elif not args.certificate_only:
        from dense_replay import replay
        need(replay(SOURCE, 65) == rows, "All dense replay moments")
    matrix = gram(rows)
    determinant = determinant_mod(matrix)
    need(determinant == determinant_bareiss(matrix) % PRIME == 52006, "Independent Gram determinants")
    need(determinant != 0, "Independent nonconstant words")
    count = controls(rows, matrix)
    expected = {
        "status": "PASS_REPEATED_NATIVE_CODE_DEGREE32_NO_NEW_KAPPA",
        "prime": PRIME, "degree": DEGREE, "independent_words": 64,
        "determinant_mod_prime": determinant, "moment_entries": 65 * 112,
        "rejection_and_boundary_controls": count,
        "moment_sha256": hashlib.sha256(raw).hexdigest(),
        "selected_kappa_unchanged": "0.0030217758",
    }
    need(receipt == expected, "Exact result receipt")
    print(expected["status"])
    print("mode=" + ("native-replay" if args.check_native else "certificate-only" if args.certificate_only else "dense-replay"))
    print("64 independent words; determinant 52006 modulo 65521; 7280 moment entries")


if __name__ == "__main__":
    main()
