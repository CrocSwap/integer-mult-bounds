#!/usr/bin/env python3
"""Forward-reader and flat-polynomial checker, separate from core's replay.

The compiler emits the object being checked in a subprocess. No predecessor
or primary mathematical/replay module is imported here. All arithmetic is Q.
"""
from fractions import Fraction
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PIVOTS = (224, 225, 226, 227, 240, 241, 256, 257)
ORDER = (3, 0, 1, 2, 7, 4, 5, 6)
PREFIX = "candidate/strict/global/base/providers/gauge44/"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read_source():
    archive = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
    payload = archive.read_bytes()
    require(sha256(payload).hexdigest() == "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6",
            "independent archive binding")
    with tarfile.open(fileobj=io.BytesIO(payload)) as tape:
        def member(name):
            matches = [m for m in tape.getmembers() if m.name == PREFIX + name]
            require(len(matches) == 1 and matches[0].isfile(), "unique source member")
            return json.loads(gzip.decompress(tape.extractfile(matches[0]).read()))
        program = member("LOCAL-PROGRAMS.json.gz")["forward"]
        word = member("CANONICAL-WORD.json.gz")
    begin = program.index(["phase", "entry_adapters"])
    end = program.index(["phase", "centers"])
    require((begin, end) == (7401, 12550), "named source cut")
    # Unlike the predecessor's backward covectors, propagate every live row.
    rows = [{i: Fraction(1)} for i in range(704)]
    gates = 0
    for event in program[begin:end]:
        if event[0] != "scalar":
            continue
        gate = event[1]
        target = gate[1][1]
        require(gate[1][0] == "L", "local scalar destination")
        if gate[0] == "add":
            require(gate[2][0] == "L", "local scalar source")
            coefficient = Fraction(gate[3], gate[4])
            for j, x in rows[gate[2][1]].items():
                value = rows[target].get(j, Fraction(0)) + coefficient * x
                if value:
                    rows[target][j] = value
                else:
                    rows[target].pop(j, None)
        else:
            require(gate[0] == "scale", "closed reader alphabet")
            rows[target] = {j: Fraction(gate[2], gate[3]) * x for j, x in rows[target].items()}
        gates += 1
    require(gates == 3451, "complete reader source interval")
    return [rows[j] for j in word["centers"]]


def invert(matrix):
    size = len(matrix)
    aug = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(size)]
           for i, row in enumerate(matrix)]
    for column in range(size):
        pivot = next(i for i in range(column, size) if aug[i][column])
        aug[column], aug[pivot] = aug[pivot], aug[column]
        q = aug[column][column]
        aug[column] = [x / q for x in aug[column]]
        for i in range(size):
            if i == column:
                continue
            q = aug[i][column]
            aug[i] = [x - q * y for x, y in zip(aug[i], aug[column])]
    return [row[size:] for row in aug]


def put(row, index, value):
    result = row.get(index, Fraction(0)) + value
    if result:
        row[index] = result
    else:
        row.pop(index, None)


def expected(reader, phase, sign):
    # Coefficients use flat keys 4*input_field + power, not tuple polynomials.
    rows = [{4 * i: Fraction(1)} for i in range(1408)]
    order = list(range(8))
    for _ in range(phase):
        order = [order[i] for i in ORDER]
    columns = [tuple(row.get(j, Fraction(0)) for row in reader) for j in range(704)]
    lookup = {column: j for j, column in enumerate(columns[:112])}
    require(len(lookup) == 112, "distinct data columns")
    for j, column in enumerate(columns[:112]):
        image = tuple(column[i] for i in order)
        if image in lookup:
            i, coefficient = lookup[image], 1
        else:
            i, coefficient = lookup[tuple(-x for x in image)], -1
        put(rows[704 + i], 4 * j + phase, Fraction(sign * coefficient))
    for j in range(112, 704):
        if j not in PIVOTS:
            put(rows[704 + j], 4 * j, Fraction(sign))
    inverse = invert([[reader[i].get(j, Fraction(0)) for j in PIVOTS] for i in range(8)])
    for i, target in enumerate(PIVOTS):
        for j in range(224, 704):
            transported = sum(inverse[i][k] * reader[order[k]].get(j, Fraction(0)) for k in range(8))
            put(rows[704 + target], 4 * j + phase, sign * transported)
            if j not in PIVOTS:
                original = sum(inverse[i][k] * reader[k].get(j, Fraction(0)) for k in range(8))
                put(rows[704 + target], 4 * j, -sign * original)
    return rows


def execute(word):
    rows = [{4 * i: Fraction(1)} for i in range(1408)]
    for event in word:
        opcode, target = event[:2]
        require(type(target) is int and 704 <= target < 1408, "source immutable at every prefix")
        if opcode == "add":
            source, coefficient = event[2:]
            require(type(source) is int and 0 <= source < 1408 and source != target,
                    "valid independent source")
            require(type(coefficient) is int and coefficient in (-1, 1), "signed unit injection")
            for j, value in rows[source].items():
                put(rows[target], j, coefficient * value)
        elif opcode == "scale":
            coefficient = Fraction(event[2])
            require(coefficient in (-1, 2, Fraction(1, 2)), "independent scalar alphabet")
            rows[target] = {j: coefficient * x for j, x in rows[target].items()}
        else:
            require(opcode == "z" and type(event[2]) is int and event[2] in (1, 2, 3),
                    "independent monomial alphabet")
            rows[target] = {4 * (j // 4) + (j + event[2]) % 4: x for j, x in rows[target].items()}
    return rows


def main():
    reader = read_source()
    run = subprocess.run([sys.executable, "-I", "-B", str(HERE / "verify.py"), "--emit-words"],
                         check=True, capture_output=True, text=True)
    cases = json.loads(run.stdout)
    require([(c["phase"], c["sign"]) for c in cases] == [(t, s) for t in range(4) for s in (-1, 1)],
            "complete emitted phase/sign domain")
    count = 0
    for case in cases:
        actual = execute(case["word"])
        oracle = expected(reader, case["phase"], case["sign"])
        require(actual == oracle, "independent complete block identity")
        count += sum(len(row) for row in actual)
    # Wrong phase and dirty-source omissions must be distinguished by this oracle.
    require(expected(reader, 1, 1) != expected(reader, 3, 1), "phase sensitivity")
    changed = [dict(row) for row in reader]
    j = next(j for j in range(224, 704) if j not in PIVOTS and any(j in row for row in reader))
    for row in changed:
        row.pop(j, None)
    require(expected(changed, 1, 1) != expected(reader, 1, 1), "dirty helper sensitivity")
    print(f"PASS_INDEPENDENT_TRANSPORTED_SHEAR maps=8 inputs_per_map=1408 nonzero_terms={count}")


if __name__ == "__main__":
    main()
