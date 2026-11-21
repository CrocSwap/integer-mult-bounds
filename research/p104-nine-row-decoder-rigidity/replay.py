#!/usr/bin/env python3
"""Replay the exact decoder control and compare its receipt."""
from pathlib import Path
import json
import subprocess
import sys

root = Path(__file__).resolve().parent
run = subprocess.run(
    [sys.executable, "-I", "-B", str(root / "control.py")],
    check=True,
    capture_output=True,
    text=True,
)
if json.loads(run.stdout) != json.loads((root / "result.json").read_text()):
    raise SystemExit("decoder control did not reproduce the frozen receipt")
print("PASS_P104_NINE_ROW_DECODER 10816 cells, masses 72/73, 40 mutation failures")
