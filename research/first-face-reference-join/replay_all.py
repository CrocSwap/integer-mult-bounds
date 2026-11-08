#!/usr/bin/env python3
"""Run the three registered component/composition packages sequentially."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGES = (
    "research/sparse-halo-tape-transaction",
    "research/shrinking-reference-halo",
    "research/first-face-reference-join",
)

for package in PACKAGES:
    subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts/research_package.py"),
         "--package", package], cwd=ROOT, check=True, timeout=1200,
    )
print("PASS_COMPLETE_FIRST_FACE_HALO_PACKAGE")
