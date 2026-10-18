#!/usr/bin/env python3
"""Portable mechanical replay of the pinned bridge and its original axiom parser.

Andrey Mas, with Codex packaging assistance. Apache-2.0.
Requires an installed Lean; performs no installation or network operation.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

VERSION = "4.30.0"
COMMIT = "d024af099ca4bf2c86f649261ebf59565dc8c622"
SOURCES = ("PR1497Bridge.lean", "fixtures/Positive.lean",
           "fixtures/RejectWrongW.lean", "fixtures/RejectMissingMP.lean",
           "fixtures/RejectMissingQP.lean", "check_axioms.py", "test_tooling.py")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(argv, cwd, env, succeeds=True):
    start = time.monotonic()
    result = subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True, timeout=120)
    record = {"argv": [Path(argv[0]).name, *argv[1:]], "exit_code": result.returncode,
              "seconds": round(time.monotonic() - start, 6),
              "stdout": result.stdout, "stderr": result.stderr}
    if succeeds and result.returncode:
        print(json.dumps(record, indent=2), file=sys.stderr)
        raise ValueError("replay command failed")
    return record


def main():
    require(sys.version_info[:2] == (3, 12), "use Python 3.12")
    package = Path(__file__).resolve().parent
    pins = json.loads((package / "SOURCES.json").read_text())["delivered_files"]
    require(set(pins) == set(SOURCES), "source inventory mismatch")
    for name in SOURCES:
        require(hashlib.sha256((package / name).read_bytes()).hexdigest() == pins[name],
                "source hash mismatch: " + name)
    selected = os.environ.get("LEAN") or shutil.which("lean")
    require(selected, "set LEAN to an installed Lean 4.30.0 binary, or place it on PATH")
    lean = str(Path(selected).resolve(strict=True))
    # Only the fresh scratch directory is added for the package-local Lean imports.
    env = {"PATH": str(Path(lean).parent) + os.pathsep + "/usr/bin:/bin", "LANG": "C.UTF-8"}
    receipt = {"status": "PASS", "lean_version": VERSION, "lean_commit": COMMIT,
               "source_sha256": pins, "commands": []}
    with tempfile.TemporaryDirectory(prefix="integral-retraction-replay-") as tmp:
        scratch = Path(tmp)
        (scratch / "fixtures").mkdir()
        for name in SOURCES:
            shutil.copyfile(package / name, scratch / name)
        version = run([lean, "--short-version"], scratch, env)
        commit = run([lean, "--githash"], scratch, env)
        require(version["stdout"].strip() == VERSION, "Lean release mismatch")
        require(commit["stdout"].strip() == COMMIT, "Lean commit mismatch")
        env["LEAN_PATH"] = str(scratch)
        pairs = []
        for module, label, count in (("PR1497Bridge", "universal", 159),
                                     ("fixtures/Positive", "positive", 197)):
            record = run([lean, "-o", module + ".olean", module + ".lean"], scratch, env)
            output = record["stdout"] + record["stderr"]
            require(not re.search(r"\berror(?:\([^)]*\))?:|sorryAx|declaration uses ['\"]sorry", output),
                    "Lean error or proof-placeholder diagnostic")
            require((scratch / (module + ".olean")).is_file(), "missing compiled artifact")
            receipt["commands"].append(record)
            (scratch / (label + ".log")).write_text(output)
            pairs += [module + ".lean", label + ".log"]
            audit = run([sys.executable, "-I", "-B", "check_axioms.py", *pairs], scratch, env)
            census = json.loads(audit["stdout"])
            require(census["declaration_count"] == count, "axiom query count mismatch")
            receipt[label + "_axioms"] = census
        for label in ("RejectWrongW", "RejectMissingMP", "RejectMissingQP"):
            record = run([lean, "fixtures/" + label + ".lean"], scratch, env, succeeds=False)
            output = record["stdout"] + record["stderr"]
            errors = re.findall(r"\berror(?:\([^)]*\))?:", output)
            require(record["exit_code"] != 0 and len(errors) == 1
                    and 'Tactic `decide` proved that the proposition' in output and 'is false' in output,
                    "negative fixture did not fail only at its intended false proposition: " + label)
            receipt["commands"].append(record)
        # The unchanged script imports its sibling parser. The minimal environment
        # excludes inherited PYTHONPATH; ordinary script-directory import is needed.
        receipt["commands"].append(run([sys.executable, "-B", "test_tooling.py"], scratch, env))
    receipt["observed_axiom_union"] = sorted({a for values in receipt["positive_axioms"]
                                              ["observed_dependencies"].values() for a in values})
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        sys.exit("FAIL_INTEGRAL_RETRACTION_REPLAY: " + str(exc))
