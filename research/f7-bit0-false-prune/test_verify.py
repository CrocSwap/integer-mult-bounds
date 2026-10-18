#!/usr/bin/env python3
"""The eight prefix states and both budgets, without the domain enumeration."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("f7_bit0_false_prune", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    states = verify.prefixes(verify.WORD)
    if states != [0, 1, 3, 2, 6, 4, 12, 8, 0]:
        raise SystemExit("prefix states changed")
    if verify.budget(4, 4, 4) != 5 or verify.budget(6, 2, 4) != 9:
        raise SystemExit("budgets changed")
    bit_collisions, bit_even, bit_odd, trace = verify.collision_walk(verify.WORD, verify.bit0)
    weight_collisions, weight_even, weight_odd, _ = verify.collision_walk(verify.WORD, verify.weight)
    if (bit_collisions, bit_even, bit_odd) != (8, 6, 2):
        raise SystemExit("bit-0 walk changed")
    if (weight_collisions, weight_even, weight_odd) != (0, 4, 4):
        raise SystemExit("weight walk changed")
    crossed = next(index for index, value in enumerate(trace) if value > 5)
    if crossed != 6 or trace[6] != 8:
        raise SystemExit("the balanced budget is not crossed at the recorded step")
    print("PASS_F7_BIT0_FALSE_PRUNE_TESTS groups=3")


if __name__ == "__main__":
    main()
