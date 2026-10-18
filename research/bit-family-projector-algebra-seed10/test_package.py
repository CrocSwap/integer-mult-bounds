#!/usr/bin/env python3
"""Focused positive and negative-control checks for this audit package."""
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("family_algebra_verify", HERE / "verify.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def need(condition, message):
    if not condition:
        raise RuntimeError(message)


result = module.verify()
need(result["status"] == "PASS_BIT_FAMILY_PROJECTOR_ALGEBRA", "positive identity")
need(len(result["intervals"]) == 2, "both frozen intervals")
need(result["negative_controls"] == {
    "omitted_helper": "rejected",
    "same_rank_wrong_axis": "rejected",
    "duplicate_helper": "rejected",
}, "all three algebraic controls")
print("PASS_BIT_FAMILY_PROJECTOR_ALGEBRA_CONTROLS positive=2 intervals negative=3")
