#!/usr/bin/env python3
"""Focused assertions for the seed57 persistent-boundary package."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("seed57_verify", HERE / "verify.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
legacy, predecessor = module.load_legacy()
work, output = module.phase_vectors(legacy, predecessor)
states5, v5 = module.optimize(5, work, output)
brute5, paths5 = module.exhaustive(5, work, output)
assert (states5, v5, paths5, brute5[0]) == ([0, 1, 2, 3, 0, 0], (126, 14), 1024, 140)
result = json.loads((HERE / "RESULT.json").read_text())
assert result["ten_child_joint"]["exhaustive_paths"] == 1048576
assert result["ten_child_joint"]["complete_primitives"] == 1904
assert result["two_separate_calls"]["combined_primitives"] == 2016
assert result["saving_joint_vs_separate"]["total_primitives"] == 112
assert result["controls"]["missing_terminal_restoration"] == "REJECTED"
print("PASS_SEED57_PACKAGE_TESTS focused_recurrence=1 receipt=1")
