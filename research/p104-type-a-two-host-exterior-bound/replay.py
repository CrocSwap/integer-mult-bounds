# SPDX-License-Identifier: Apache-2.0
"""Reproduce the two frozen receipts without Git or third-party libraries."""
from pathlib import Path
from subprocess import check_output
import sys

HERE = Path(__file__).resolve().parent

if __name__ == "__main__":
    assert __debug__
    for script, receipt in (
        ("screen.py", "TIMED-RECEIPT.json"),
        ("screen_phase.py", "PHASE-RECEIPT.json"),
    ):
        actual = check_output([sys.executable, "-I", "-B", str(HERE / script), str(HERE)])
        assert actual == (HERE / receipt).read_bytes(), receipt
    print("PASS exact J8/J9 timed-input and imaginary-phase exterior obstructions")
