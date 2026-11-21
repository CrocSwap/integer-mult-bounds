#!/usr/bin/env python3
"""Independently check the excluded exchanges from forward and adjoint literal tapes."""
import hashlib
import itertools
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENGINE = "36b3da4f72f8a6c946136fbd58b20838c00b0243c2effaf909c20b76967a5349"


def quotient(rows, owners):
    pivots = {}

    def reduce(row):
        residue = 0
        while row:
            k = row.bit_length() - 1
            if k in pivots:
                row ^= pivots[k]
            else:
                residue |= 1 << k
                row ^= 1 << k
        return residue

    for row in rows:
        remainder = reduce(row)
        if remainder:
            pivots[remainder.bit_length() - 1] = remainder
    return len(pivots), {i: reduce(1 << i) for i in owners}


def main():
    engine = ROOT / "sources/binary_operator.py"
    assert __debug__ and hashlib.sha256(engine.read_bytes()).hexdigest() == ENGINE
    op = runpy.run_path(str(engine))
    word = op["load_json"](ROOT / "sources/WORD.json.gz", op["WORD_GZIP"], True)
    assert op["canonical_hash"](word) == op["WORD"]
    atlas = op["Atlas"](word["frames"])
    forward = op["run_tape"](word, atlas, False)
    adjoint = op["run_tape"](word, atlas, True)
    assert forward.output == op["expected_operator"](False)
    assert adjoint.output == op["expected_operator"](True)
    assert forward.dirty == adjoint.dirty == 3554

    owners = range(222, word["public"])
    starts, ends = word["start"], word["final"]
    ranks = {i: atlas.grade(starts[i], ends[i]) for i in owners}
    pairs = []
    for i, j in itertools.combinations(owners, 2):
        old = (ranks[i], ranks[j])
        new = (atlas.grade(starts[i], ends[j]), atlas.grade(starts[j], ends[i]))
        if min(new) > min(old) and sum(new) == sum(old):
            pairs.append((i, j))
    expected = json.loads((ROOT / "EXPECTED.json").read_bytes())
    assert len(pairs) == expected["pairs"] == 3112
    assert hashlib.sha256(json.dumps(pairs, separators=(",", ":")).encode()).hexdigest() == expected["pair_sha256"]
    counts = []
    for chart in sorted(atlas.body):
        a, read = quotient((obs.row for obs in forward.stock[chart]), owners)
        b, write = quotient((obs.row for obs in adjoint.stock[chart]), owners)
        matches = sum(read[i] == read[j] and write[i] == write[j] for i, j in pairs)
        assert matches == 0
        counts.append([chart, a, b, matches])
    assert len(counts) == 636 and counts == expected["charts"]
    print("PASS_LITERAL_TAPE_EXCHANGE_EXCLUSION 680 public rows each way, 3554 dirty retirements each way, 1979232 decisions")


if __name__ == "__main__":
    main()
