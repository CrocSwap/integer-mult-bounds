#!/usr/bin/env python3
"""The four-width idle mass, without the certificate file."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rank7_v45_width_idle", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    parent = {"1": "234", "3": "396/5", "5": "84", "48": "1844/5"}
    moved = {"1": "234", "3": "387/5", "5": "75", "48": "1853/5"}
    if verify.idle_mass(moved) - verify.idle_mass(parent) != verify.WIDTH_DROP * verify.CALLS:
        raise SystemExit("four widths did not add 36 idle-rank units")
    if verify.idle_mass(parent) - verify.idle_mass(moved) == verify.WIDTH_DROP * verify.CALLS:
        raise SystemExit("the idle mass moved in the wrong direction")
    if Fraction(parent["48"]) == Fraction(moved["48"]):
        raise SystemExit("the rank-48 idle was left unchanged")
    print("PASS_RANK7_V45_WIDTH_IDLE_TESTS groups=3")


if __name__ == "__main__":
    main()
