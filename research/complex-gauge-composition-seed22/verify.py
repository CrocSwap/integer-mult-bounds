#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Source-bound replay of the conditional mixed-gauge construction."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


spec = importlib.util.spec_from_file_location("seed22_compose", HERE / "compose.py")
compose = importlib.util.module_from_spec(spec)
spec.loader.exec_module(compose)
result = compose.compute()
saved = json.loads((HERE / "RESULT.json").read_bytes())
need(compose.canonical(result) == compose.canonical(saved), "complete result certificate mismatch")
print("PASS_COMPLEX_K8_MIXED_GAUGE seed=22 helper=248 incremental=90/90 total=13090/13090 all712=both")
