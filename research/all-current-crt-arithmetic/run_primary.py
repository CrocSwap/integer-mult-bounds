"""Bounded entry point for the three unchanged primary checks.

Each check runs in a fresh isolated interpreter. The parent mode is forwarded.
This groups publication commands; it changes no mathematical test or receipt.
"""
from pathlib import Path
import subprocess
import sys

here = Path(__file__).resolve().parent
for name, seconds in (("source_check.py", 60), ("test_core.py", 60),
                      ("verify_source.py", 180)):
    command = [sys.executable, "-I", "-W", "error", "-B"]
    if sys.flags.optimize:
        command.append("-O")
    command.append(str(here / name))
    print("PRIMARY_CHECK", name, "optimized=" + str(bool(sys.flags.optimize)), flush=True)
    subprocess.run(command, check=True, timeout=seconds)
print("PASS_ALL_CURRENT_ARITHMETIC_PRIMARY_SUITE", flush=True)
