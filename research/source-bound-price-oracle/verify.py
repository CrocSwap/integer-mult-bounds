#!/usr/bin/env python3
"""Bounded offline compatibility replay; no scientific engine execution.

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import json
import sys
import unittest

import oracle as o
import calibrate
import check_join

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise o.ContractError(message)


def check_frozen():
    frozen = HERE / "frozen"
    manifest_bytes = (frozen / "MANIFEST.json").read_bytes()
    require(o.digest(manifest_bytes) ==
            "3dd8af4470220929ee516f2d3a97eba6db45ff55908c2cb5ca441f75459fdbed",
            "FROZEN_MANIFEST_CHANGED")
    rows = o.decode(manifest_bytes)["files"]
    expected = {row["path"] for row in rows}
    require(len(rows) == len(expected) == 93, "FROZEN_INVENTORY_CHANGED")
    actual = {p.relative_to(frozen).as_posix() for p in frozen.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts}
    require(actual == expected | {"MANIFEST.json"}, "FROZEN_FILE_SET_CHANGED")
    for row in rows:
        path = frozen / row["path"]
        require(not path.is_symlink(), "FROZEN_SYMLINK")
        raw = path.read_bytes()
        require(len(raw) == row["bytes"] and o.digest(raw) == row["sha256"],
                "FROZEN_BYTES_CHANGED:" + row["path"])
    # The reusable library is the exact original reviewed oracle. Calibration
    # alone is adapted to avoid writes and keep predicates active under -O.
    require((HERE / "oracle.py").read_bytes() == (frozen / "oracle.py").read_bytes(),
            "LIBRARY_DIFFERS_FROM_FROZEN_ORACLE")
    return len(rows)


def check_policy(view, policy_bytes):
    pins = o.decode((HERE / "TRUSTED-POLICIES.json").read_bytes())["views"][view]
    require(o.digest(policy_bytes) == pins["policy_sha256"], "TRUSTED_POLICY_CHANGED")
    return pins


def run():
    count = check_frozen()
    results = {}
    for view in ("joined-v5", "joined-5387-v4"):
        path = HERE / "frozen" / view
        pins = check_policy(view, (path / "policy.json").read_bytes())
        require(o.digest((path / "candidate.json").read_bytes()) == pins["candidate_sha256"],
                "FROZEN_CANDIDATE_CHANGED")
        result = check_join.check(path)
        require(result["label"] == pins["label"] and result["funded_kappa"] == pins["funded_kappa"],
                "SOURCE_BOUND_DECISION_CHANGED")
        require(result["scientific_payload_sha256"] == pins["scientific_payload_sha256"],
                "SOURCE_BOUND_PAYLOAD_CHANGED")
        results[view] = result
    calibration = calibrate.run()
    suite = unittest.TestSuite()
    loader = unittest.TestLoader()
    for module in ("test_oracle", "test_joins"):
        suite.addTests(loader.loadTestsFromName(module))
    tested = unittest.TextTestRunner(verbosity=2, stream=sys.stderr).run(suite)
    require(tested.wasSuccessful(), "CONTRACT_CONTROLS_FAILED")
    return {"status": "PASS_SOURCE_BOUND_PRICE_ORACLE", "frozen_files": count,
            "test_groups": tested.testsRun, "views": results,
            "calibration_profiles": len(calibration["records"]),
            "scientific_engines_replayed": False, "selected_mutated": False}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
