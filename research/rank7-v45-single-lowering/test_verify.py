#!/usr/bin/env python3
"""The V45 margin signs and one hyperplane, without the stage file."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rank7_v45_single_lowering", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    break_even = 2091300
    if verify.margin(-2038159, 1, break_even) != -53141:
        raise SystemExit("single margin changed")
    if verify.margin(-8388172, 4, break_even) != 22972:
        raise SystemExit("joint margin changed")
    if verify.margin(-2038159, 1, break_even) >= 0 or verify.margin(-8388172, 4, break_even) <= 0:
        raise SystemExit("the sign pattern reversed")
    old = [256, 128, 64, 35, 16, 11, 5, 1]
    new = [256, 128, 64, 35, 16, 11, 5]
    if not verify.hyperplane(old, new) or verify.rank(new) != 7:
        raise SystemExit("the sample subspace is not a rank-7 hyperplane")
    print("PASS_RANK7_V45_SINGLE_LOWERING_TESTS groups=3")


if __name__ == "__main__":
    main()
