#!/usr/bin/env python3
"""Uniqueness is sufficient for the two scatter actions, and stronger than odd multiplicity."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("scatter_duplicate_boundary", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    selected = [[4, 5, 6, 7, 8]]
    even = [[4, 5, 6, 7, 8, 0, 0]]
    triple = [[4, 5, 6, 7, 8, 0, 0, 0]]
    if not verify.unique_rows(selected) or not verify.odd_positive_multiplicities(selected):
        raise SystemExit("the selected row failed a guard it should pass")
    if verify.unique_rows(even) or verify.odd_positive_multiplicities(even):
        raise SystemExit("the even duplicate was accepted")
    if verify.unique_rows(triple) or not verify.odd_positive_multiplicities(triple):
        raise SystemExit("the odd triple was classified incorrectly")
    print("PASS_SCATTER_DUPLICATE_BOUNDARY_TESTS groups=3")


if __name__ == "__main__":
    main()
