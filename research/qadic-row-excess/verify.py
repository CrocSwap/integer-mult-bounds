#!/usr/bin/env python3
"""One q-adic level against the external row cap.

The checker bounds the order of GL_64 and multiplies by the published depth.
It does not recompute the fourteen stage headrooms.
"""

import hashlib
import json
import tarfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_QADIC_ROW_EXCESS row=655360 cap=20161 no_new_kappa"
PROOF = "research/selected-bit-recursive-closure/PROOF.md"
PARENT = "research/selected-bit-parent-reserve/README.md"
TARBALL = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"


def fail(message):
    raise SystemExit("FAIL_QADIC_ROW_EXCESS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def level_bits():
    """Bit length of |GL_64(q)| for an integer q > 2^80 is at least 64^2 * 80."""
    dimension = 64
    product = Fraction(1)
    for index in range(1, dimension + 1):
        product *= 1 - Fraction(1, 3 ** index)
    # q=3 is the smallest integer above 2, and every factor grows with q.
    require(product > Fraction(1, 2), "the group-order product left one half")
    return dimension * dimension * 80


def evaluate():
    require(sha256(ROOT / PROOF) == "74cc8de20f21acb5123fe2d20996fe0925ea6e51b3dec633bd5221fb719b3344", "closure proof drift")
    require(sha256(ROOT / PARENT) == "16b84730b7a604e805034008e11bae4f90fe6c91db6098d5bd5d011dded5f4ee", "parent note drift")
    require(sha256(ROOT / TARBALL) == "d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86", "assembler archive drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    proof = (ROOT / PROOF).read_text(encoding="utf-8")
    require("odd prime q>2^80" in proof, "the prime bound moved")
    require("log_q K < 4096w+1 <=4097w" in proof, "the level exponent moved")
    require(64 * 64 == 4096 and 64 * 64 + 1 == 4097, "the matrix exponent moved")
    parent = (ROOT / PARENT).read_text(encoding="utf-8")
    require("2*(64^2+1)=8194" in parent, "the depth factor moved")
    require(2 * (64 * 64 + 1) == 8194, "the published allowance moved")
    with tarfile.open(ROOT / TARBALL) as archive:
        assembler = archive.extractfile("code/assemble.py").read().decode("utf-8")
    require("retained_row_coefficient']==20161" in assembler, "the row cap moved")
    bits = level_bits()
    row = 2 * bits
    require(bits == 327680 and row == 655360 and row > 20161, "the q-adic row left the cap")
    return {"level_bits": 327680, "depth": 2, "row_term": 655360, "cap": 20161, "no_new_kappa": True}


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
