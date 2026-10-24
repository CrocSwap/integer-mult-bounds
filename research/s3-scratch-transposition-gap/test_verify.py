#!/usr/bin/env python3
"""Failure controls for the length-2 transposition obstruction."""

import importlib.util
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    verify = load("verify")
    ball, gap = verify.support_ball()
    if gap in ball:
        raise SystemExit("gap must stay outside the length-2 ball")
    # Dropping the generator restriction does write the gap in one coordinate move.
    group, index, identity, _s, _t, gap_element, table = verify.algebra()
    coordinate = ((1, 0, 0), (0, 0, 0), (0, 0, 0))
    move = verify.paid(index[gap_element], coordinate, index[identity])
    if verify.gap_bit_count(move, index[gap_element]) != 1:
        raise SystemExit("a paid gap label must be visible to the bit test")
    if not verify.length3_coordinate_writes_gap(
        table, index, identity, (1, 0, 2), (0, 2, 1), gap_element
    ):
        raise SystemExit("length-3 control failed inside the test")
    if len(group) != 6:
        raise SystemExit("group order")
    print("PASS_S3_SCRATCH_TRANSPOSITION_GAP_TESTS")


if __name__ == "__main__":
    main()
