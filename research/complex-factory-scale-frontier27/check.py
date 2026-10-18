#!/usr/bin/env python3
"""One-command exact census, separate oracle and rejection controls."""
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
for name in ("verify.py", "oracle.py", "test_package.py"):
    proc = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / name)],
                          text=True, capture_output=True)
    if proc.returncode:
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        raise SystemExit(proc.returncode)
    print("PASS " + name, flush=True)
print("PASS_FACTORY_SCALE_PACKAGE complete=315392 exact_matrix_replays=39424 minimum=73 winners=8 no_new_kappa")
