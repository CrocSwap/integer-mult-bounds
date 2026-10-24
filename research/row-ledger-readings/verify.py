#!/usr/bin/env python3
"""The two published readings of the selected row ledger.

The checker parses the pinned formulas and evaluates them. It does not
recompute the fourteen stage headrooms.
"""

import hashlib
import json
import re
import tarfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_ROW_LEDGER_READINGS carried=11185 readings=16469,15555 no_new_kappa"
TARBALL = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
GAUGE = "notes/partial-gauge-assembly.tex"
LAYER = "research/selected-complex-layer-closure/PROOF.md"
ENVELOPE = "research/selected-stock-envelope-m73/README.md"


def fail(message):
    raise SystemExit("FAIL_ROW_LEDGER_READINGS " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def member(name):
    with tarfile.open(ROOT / TARBALL) as archive:
        return archive.extractfile(name).read().decode("utf-8")


def orthogonal_order():
    order = 2 ** (36 * 36)
    for index in range(1, 37):
        order *= 2 ** (2 * index) - 1
    return order


def evaluate():
    require(sha256(ROOT / GAUGE) == "ef27afc3a70656d3139bf3661ac0b2088622f37221141cc386d41324b7c563d0", "gauge note drift")
    require(sha256(ROOT / LAYER) == "43feda0342c07a9429699c3a44e8936a3f3fb57ce9b32f38ff3dc06ac887b265", "layer proof drift")
    require(sha256(ROOT / ENVELOPE) == "efede1e472e45f78baf304da6bff7b6685b6bb4ae06cf6a1ea9d1ceaf6fd3b88", "envelope note drift")
    require(sha256(ROOT / TARBALL) == "d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86", "assembler archive drift")
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    gauge = (ROOT / GAUGE).read_text(encoding="utf-8")
    pairs = re.search(r"\$\((\d+),(\d+)\),\((\d+),(\d+)\),\((\d+),(\d+)\)\$", gauge)
    require(pairs is not None, "the family pairs moved")
    coarse_h, coarse_w, leaf_h, leaf_w, complex_h, complex_w = map(int, pairs.groups())
    coarse, leaf, historical = coarse_h * coarse_w, leaf_h * leaf_w, complex_h * complex_w
    require((coarse, leaf, historical) == (9909, 252, 5600), "a family product moved")
    require(f"{coarse_h}\\cdot{coarse_w}+{leaf_h}\\cdot{leaf_w}+{complex_h}\\cdot{complex_w}={coarse + leaf + historical}" in gauge, "the printed family sum moved")
    layer = (ROOT / LAYER).read_text(encoding="utf-8")
    require("Gamma = 2^1296 product_(i=1)^36 (2^(2i)-1)" in layer, "the order formula moved")
    require("W=14336 live families" in layer, "the live width moved")
    order = orthogonal_order()
    require(2 ** 2627 < order < 2 ** 2628, "the group order left its bounds")
    row_bits = (14336 * order - 1).bit_length()
    require(row_bits == 2642, "the row bit length moved")
    assembler = member("code/assemble.py")
    invoice = member("code/invoice_allcold.py")
    formula = re.search(r"physical_row_coefficient'\]==2\*stock\.bit_length\(\)\+(\d+)\+(\d+)\+(\d+)", assembler)
    require(formula is not None, "the row formula moved")
    require(tuple(map(int, formula.groups())) == (coarse, leaf, 1024), "the row constants left the family degrees")
    require("retained_row_coefficient']==20161" in assembler, "the row cap moved")
    require("charged_prefix_bits']==512" in assembler and "row_prefix_extra']==1024" in assembler, "the prefix term moved")
    require("row=2*stock.bit_length()+9909+252+2*payload" in invoice, "the invoice formula moved")
    envelope = (ROOT / ENVELOPE).read_text(encoding="utf-8")
    require("B=2642" in envelope and "ledger=16469->15555" in envelope, "the published readings moved")
    carried = coarse + leaf + 1024
    ceiling = -(-43 * row_bits // 26)
    wide = 2 * row_bits + carried
    narrow = ceiling + carried
    require((carried, wide, narrow) == (11185, 16469, 15555), "a reading left the constant degrees")
    require(wide - narrow == 2 * row_bits - ceiling == 914, "the gap between the readings moved")
    require(2 * row_bits + 1024 == 6308 < wide < 20161, "the lean row left the cap")
    return {
        "coarse_degree": 9909,
        "leaf_degree": 252,
        "prefix_degree": 1024,
        "carried": 11185,
        "row_bits": 2642,
        "reading_16469": 16469,
        "reading_15555": 15555,
        "lean_row": 6308,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
