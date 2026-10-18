#!/usr/bin/env python3
"""Independent checks for the one-gap reversal. No machine execution."""

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("unit_weight_reversal", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    columns = [verify.column_reversal(address) for address in range(81)]
    if columns[0] != 0 or columns[1] != 27 or columns[2] != 54:
        raise SystemExit("reversal samples changed")
    if any(verify.column_reversal(image) != address for address, image in enumerate(columns)):
        raise SystemExit("reversal is not an involution")
    if sum(image != address for address, image in enumerate(columns)) != 72:
        raise SystemExit("identity disagreement count changed")
    print("PASS_SELECTED_UNIT_WEIGHT_REVERSAL_TESTS groups=3")


if __name__ == "__main__":
    main()
