#!/usr/bin/env python3
"""Controls target source authentication and the mathematical caller boundary."""

import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import verify as v

ROOT = Path(__file__).resolve().parent


def fails(call):
    try:
        call()
    except (ValueError, KeyError, TypeError):
        return
    raise ValueError("invalid input accepted")


def source_controls():
    # Each copy is private, below the caller's session TMPDIR.
    with tempfile.TemporaryDirectory(prefix="original-cover-controls-") as temp:
        for mode in range(8):
            target = Path(temp) / str(mode)
            shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns("__pycache__"))
            # The source export may be read-only; only private mutant copies change.
            target.chmod(0o700)
            for file in target.rglob("*"):
                file.chmod(0o700 if file.is_dir() else 0o600)
            manifest = v.read_json(target / "SOURCES.json")
            if mode == 0:
                manifest["retained_files"][0]["usage"] = "provenance"
            elif mode == 1:
                manifest["retained_files"].pop()
            elif mode == 2:
                manifest["retained_files"][0]["unexpected"] = True
            elif mode == 3:
                manifest["retained_files"].append(
                    copy.deepcopy(manifest["retained_files"][0])
                )
            elif mode == 4:
                (target / "vendor/PR3282-RESULT.json").write_text("{}")
            elif mode == 5:
                (target / "vendor/unexpected.txt").write_text("not declared")
            elif mode == 6:
                manifest["schema_version"] = True
            else:
                receipt = v.read_json(target / "RESULT.json")
                receipt["rows"][0]["attempts"]["alpha74"]["count"] += 1
                (target / "RESULT.json").write_text(json.dumps(receipt))
            (target / "SOURCES.json").write_text(json.dumps(manifest))
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
            run = subprocess.run(
                [sys.executable, "-O", "-B", str(target / "verify.py")],
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
            )
            v.require(run.returncode != 0, "source/receipt mutant accepted")


def caller_controls():
    result = v.read_json(ROOT / "RESULT.json")
    row = next(r for r in result["rows"] if r["previous"] is None and r["covered"])
    w = row["weights"]
    witness = row["attempts"]["beta7p2"]["witness"]
    v.validate_witness(w, v.RULES[1], witness)
    invalid = copy.deepcopy(witness)
    invalid["groups"][0].append(invalid["groups"][1][0])
    fails(lambda: v.validate_witness(w, v.RULES[1], invalid))
    invalid = copy.deepcopy(witness)
    invalid["direction_bound"] = 3
    fails(lambda: v.validate_witness(w, v.RULES[1], invalid))
    # Rank-seven nonbasis pieces cannot silently use the rank-six theorem.
    fails(lambda: v.validate_witness(w, v.RULES[2], witness))
    # The fourth candidate needs four root sites; a budget of2 does not suffice.
    boundary = [2, 3, 4, 4] + [7] * 6
    v.require(v.attempts(boundary, v.RULES[1])["count"] == 0, "two-cut boundary")
    relaxed = ("unproved-beta7p4", 6, 6, 4, 4, 7)
    v.require(v.attempts(boundary, relaxed)["count"] > 0, "four-cut losing control")


def main():
    v.sources(ROOT)
    source_controls()
    caller_controls()
    print("PASS_CONTROLS eight source/receipt cases;five caller checks")


if __name__ == "__main__":
    main()
