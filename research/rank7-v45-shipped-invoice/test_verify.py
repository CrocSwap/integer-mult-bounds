#!/usr/bin/env python3
"""The buffer count and the recorded cap order, without the word files."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rank7_v45_shipped_invoice", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if len(verify.basis_of(verify.PARENT_FRAME)) != 8 or len(verify.basis_of(verify.SUBSPACE)) != 7:
        raise SystemExit("frame ranks changed")
    if not verify.contained(verify.SUBSPACE, verify.PARENT_FRAME):
        raise SystemExit("the subspace left the parent frame")
    if 86 + len(verify.EXTRACTIONS) != 91:
        raise SystemExit("buffer arithmetic changed")
    brackets = [
        Fraction("17228172707428495209099/10000000000000000000000000"),
        Fraction("172281727074284952091/100000000000000000000000"),
        Fraction("17262265796413098725813/10000000000000000000000000"),
    ]
    if not brackets[0] < brackets[1] < brackets[2]:
        raise SystemExit("the parent bracket does not sit below stage 1")
    print("PASS_RANK7_V45_SHIPPED_INVOICE_TESTS groups=3")


if __name__ == "__main__":
    main()
