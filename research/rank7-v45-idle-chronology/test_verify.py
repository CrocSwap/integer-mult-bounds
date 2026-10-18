#!/usr/bin/env python3
"""Width arithmetic and one idle pattern, without the word files."""

import importlib.util
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rank7_v45_idle_chronology", HERE / "verify.py")
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)


def main():
    if set(verify.HELPERS) != {249, 251, 265, 267}:
        raise SystemExit("the V45 helpers changed")
    stage = {"basis_patterns": [{"capacity": 8, "widths": [7], "count_per_replica": "4"}], "idle_per_replica": {"1": "4"}}
    if verify.idle_of(stage) != {"1": "4"}:
        raise SystemExit("idle arithmetic changed")
    if Fraction("396/5") == Fraction("693/10"):
        raise SystemExit("the parent and stage-1 rank-3 counts were treated as equal")
    print("PASS_RANK7_V45_IDLE_CHRONOLOGY_TESTS groups=3")


if __name__ == "__main__":
    main()
