#!/usr/bin/env python3
"""The selected checker body is not the bit reversal of its 23-bit source."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("unit_root_tape_boundary", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    initial = verify.published_initial()
    injected = verify.checker_body(initial)
    if injected == bytes(reversed(initial)):
        raise SystemExit("checker body collapsed to a pure bit reversal")
    if verify.checker_body(injected) != initial:
        raise SystemExit("checker body is not an involution")
    if verify.ACCEPTED == (0, 1):
        raise SystemExit("accepted coefficients are the unit pair")
    print("PASS_SELECTED_UNIT_ROOT_TAPE_BOUNDARY_TESTS groups=3")


if __name__ == "__main__":
    main()
