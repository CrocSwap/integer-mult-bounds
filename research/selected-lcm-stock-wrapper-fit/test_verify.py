#!/usr/bin/env python3
"""Focused integrity checks for the lcm-stock wrapper binding."""

from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import subprocess
import sys

_LOADER = SourceFileLoader(
    "selected_lcm_stock_wrapper_fit",
    str(Path(__file__).with_name("verify.py")),
)
_SPEC = spec_from_loader(_LOADER.name, _LOADER)
MODULE = module_from_spec(_SPEC)
_LOADER.exec_module(MODULE)


def main():
    if MODULE.lcm(MODULE.LIVE, MODULE.PHYSICAL) != MODULE.M_CLAIM:
        raise SystemExit("lcm identity")
    if MODULE.coefficient_room(1) is not True:
        raise SystemExit("w=1 room")
    if MODULE.padding_fits(3, 28) is not True or MODULE.padding_fits(3, 0) is not False:
        raise SystemExit("padding fixture")
    if MODULE.packet_comparison_proved(MODULE.M_CLAIM) is not False:
        raise SystemExit("boundary prime")
    if MODULE.depth(63) != 0 or MODULE.depth(64) != 1 or MODULE.depth(42 * 64) < 2:
        raise SystemExit("depth samples")
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(Path(__file__).with_name("verify.py"))],
        cwd=MODULE.ROOT, check=False, text=True, capture_output=True,
    )
    if completed.returncode != 0 or "PASS_SELECTED_LCM_STOCK_WRAPPER_FIT" not in completed.stdout:
        raise SystemExit(completed.stderr or completed.stdout or "verifier failed")
    print("PASS_SELECTED_LCM_STOCK_WRAPPER_FIT_TESTS groups=5")


if __name__ == "__main__":
    main()
