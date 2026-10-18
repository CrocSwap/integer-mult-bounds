# SPDX-License-Identifier: Apache-2.0
"""Derive the exact BIT boundary certificate. Use Python's standard library."""
import argparse
import gzip
import hashlib
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent


def add_vector(rows, vector):
    row = list(map(Fraction, vector))
    for pivot in sorted(rows):
        q = row[pivot]
        row = [a - q * b for a, b in zip(row, rows[pivot])]
    pivot = next((i for i, x in enumerate(row) if x), None)
    if pivot is None:
        return False
    q = row[pivot]
    rows[pivot] = [x / q for x in row]
    return True


def determinant(vectors):
    rows = [list(map(Fraction, row)) for row in vectors]
    out = Fraction(1)
    for col in range(len(rows)):
        pivot = next(i for i in range(col, len(rows)) if rows[i][col])
        if pivot != col:
            rows[pivot], rows[col] = rows[col], rows[pivot]
            out = -out
        q = rows[col][col]
        out *= q
        for i in range(col + 1, len(rows)):
            factor = rows[i][col] / q
            rows[i] = [a - factor * b for a, b in zip(rows[i], rows[col])]
    assert out.denominator == 1
    return out.numerator


def support(value):
    out = []
    while value:
        bit = value & -value
        out.append(bit.bit_length() - 1)
        value -= bit
    return out


def span_evidence(word, current, donors, frame_bases):
    vectors, witness, rows = [], [], {}
    for register in sorted(donors):
        if len(vectors) == word["h"]:
            break
        for line in frame_bases[current[register]]:
            vector = word["lines"][line]
            if add_vector(rows, vector):
                vectors.append(vector)
                witness.append([register, line])
            if len(vectors) == word["h"]:
                break
    rank = len(vectors)
    result = {"rank": rank, "basis": witness}
    if rank == word["h"]:
        result["determinant"] = determinant(vectors)
    else:
        free = next(i for i in range(word["h"]) if i not in rows)
        normal = [Fraction(i == free) for i in range(word["h"])]
        for pivot in sorted(rows, reverse=True):
            normal[pivot] = -sum(rows[pivot][i] * normal[i] for i in range(pivot + 1, word["h"]))
        denominator = math.lcm(*(x.denominator for x in normal))
        normal = [int(x * denominator) for x in normal]
        divisor = math.gcd(*normal)
        normal = [x // divisor for x in normal]
        if next(x for x in normal if x) < 0:
            normal = [-x for x in normal]
        result["normal"] = normal
    return result


def derive(word):
    v = word["v"]
    n = 2 * v + word["R"]
    helpers = range(2 * v, n)
    z = [r for r in range(n) if not v <= r < 2 * v]
    frame_bases = []
    for frame in word["frames"]:
        chosen, rows = [], {}
        for line in frame:
            if add_vector(rows, word["lines"][line]):
                chosen.append(line)
        frame_bases.append(chosen)
    current = word["start"][:]
    values = [1 << r for r in range(n)]
    z_gates = []

    def run(section):
        for frame, target, sources in word[section]:
            for register in [target, *sources]:
                current[register] = frame
            for source in sources:
                values[target] ^= values[source]
            if section in ("A", "B") and target in z:
                z_gates.append((target, sources))

    def cut(name):
        inverse = [1 << r for r in range(n)]
        for target, sources in reversed(z_gates):
            for source in sources:
                inverse[target] ^= inverse[source]
        entries = []
        for helper in helpers:
            restore = support(inverse[helper])
            dirt = [r for r, value in enumerate(values) if value >> helper & 1]
            donors = set(restore) | set(dirt) | {helper}
            evidence = span_evidence(word, current, donors, frame_bases)
            if name == "after_B":
                # The restoration condition alone suffices at this cut.
                evidence = span_evidence(word, current, set(restore) | {helper}, frame_bases)
            entries.append({"helper": helper, "restore": restore, "dirt": dirt, **evidence})
        return {"name": name, "frames": current[:], "helpers": entries,
                "rank_counts": {str(rank): count for rank, count in sorted(Counter(row["rank"] for row in entries).items())},
                "survivors": [row["helper"] for row in entries if row["rank"] < word["h"]]}

    run("D")
    run("A")
    for target, totals in enumerate(word["scatter"]):
        for total in totals:
            values[v + target] ^= values[word["ret"][total]]
    cuts = [cut("after_scatter")]
    run("B")
    cuts.append(cut("after_B"))
    run("C")
    for r, value in enumerate(values):
        assert value == ((1 << r) ^ (1 << (r - v)) if v <= r < 2 * v else 1 << r)
    compensation = []
    for helper in helpers:
        targets = [target for _, target, sources in word["D"] if helper in sources]
        assert targets
        compensation.append({"helper": helper, "targets": targets})
    return {"status": "SCOPED_BIT_BOUNDARY_OBSTRUCTION", "v": v, "R": word["R"],
            "dimension": word["h"], "cuts": cuts, "compensation": compensation,
            "scope": "Fixed D/A/scatter prefix; common-frame invertible suffix and monotone climbs. No new kappa."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=HERE.parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for path, digest in sources["inputs"].items():
        assert hashlib.sha256((args.root / path).read_bytes()).hexdigest() == digest, path
    word = json.loads(gzip.decompress((args.root / sources["word"]).read_bytes()))
    result = derive(word)
    encoded = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(encoded)
    else:
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        assert json.dumps(result, sort_keys=True, separators=(",", ":")) == json.dumps(expected, sort_keys=True, separators=(",", ":"))
    print("PASS_BIT_BOUNDARY_DERIVATION after_scatter=433/439 after_B=439/439")


if __name__ == "__main__":
    main()
