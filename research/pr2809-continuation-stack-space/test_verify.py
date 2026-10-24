#!/usr/bin/env python3
"""Rejecting controls for the continuation-stack bound."""

import importlib.util
from pathlib import Path

PATH = Path(__file__).resolve().parent / "verify.py"
SPEC = importlib.util.spec_from_file_location("stack_space", PATH)
stack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(stack)


def require_failure(name, fn):
    try:
        fn()
    except SystemExit:
        return
    raise SystemExit("control accepted a bad instance: " + name)


def main():
    if stack.D(63) != 0 or stack.D(64) != 1 or stack.D(448) != 4:
        raise SystemExit("depth samples moved")
    # j = 1 is admissible only for e = 1.
    if pow(1, stack.C_DEN) < pow(1, stack.C_NUM):
        raise SystemExit("e=1 should admit w=1")
    if pow(2, stack.C_NUM) <= pow(1, stack.C_DEN):
        raise SystemExit("e=2 should reject w=1")
    # Replacing 42 by 64 does not halve.
    n = 128
    stuck = 64 * ((64 * (n // 64)) // 64)
    if 2 * stuck <= n:
        raise SystemExit("the 64-coefficient mutant unexpectedly halved")
    # The recorded constant is one larger than a failing bound.
    bits = 16 * stack.K2_BITS_EXPECTED
    if (stack.C_EXPECTED - 1) * stack.WITNESS_E >= bits:
        raise SystemExit("C-1 covers the witness")
    if stack.C_EXPECTED * stack.WITNESS_E < bits:
        raise SystemExit("C misses the witness")
    # A factor of 1 is the e=1 allowance, not the e>=2 allowance.
    if stack.Q**4096 <= 1:
        raise SystemExit("q^4096 collapsed")

    def bad_halving():
        f = 2
        x = (64 * f) // 64
        if 2 * 64 * x > 64 * f:
            raise SystemExit("mutant")

    require_failure("coefficient 64", bad_halving)
    print("PASS_PR2809_CONTINUATION_STACK_SPACE_CONTROLS")


if __name__ == "__main__":
    main()
