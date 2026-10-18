#!/usr/bin/env python3
"""Replay the seed-5 r659 joint-boundary census and its controls."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
run = subprocess.run(
    [sys.executable, "-B", str(PKG / "atlas.py")], cwd=ROOT,
    text=True, capture_output=True, check=True,
)
actual = json.loads(run.stdout)
expected = json.loads((PKG / "EXPECTED.json").read_text())
assert actual == expected, "exact census differs from EXPECTED.json"
assert actual["candidate_assignments"] == 20
assert actual["valid_assignments"] == 12
assert actual["static_fixed_boundary_assignments"] == 12
assert actual["joint_only_assignments"] == 0
assert actual["tie"] == 8 and actual["worse"] == 4
assert actual.get("better", 0) == 0 and actual.get("unresolved", 0) == 0
assert actual["illegal_A_upper_boundary"] == 8
assert actual["relaxed_boundary_negative_control"][-1] == "A_upper_boundary"
assert actual["literal_replay_count"] == 12
assert len(actual["literal_replay"]) == 3
print("PASS_BIT589_BOUNDARY_ADAPTIVE_R659 seed=5 candidates=20 valid=12 joint_only=0")
