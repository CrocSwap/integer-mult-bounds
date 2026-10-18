#!/usr/bin/env python3
"""Replay the unchanged proof and complete axiom census with an installed Lean.

Andrey Mas, with Codex assistance for this mechanical wrapper. Apache-2.0.
No installation, network access, repository mutation or proof repair is performed.
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
ALLOWED = {"propext", "Classical.choice", "Quot.sound"}
CHECKS = ("restored_row_certificate", "restored_at_most_certificate",
          "row_generation", "prefix_row_generation", "donors_target_snoc",
          "zero_target_projected_eq_raw")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def inventory(source):
    """Read declaration names from this hash-pinned source's simple layout."""
    namespaces, result = [], []
    for line in source.splitlines():
        if match := re.fullmatch(r"namespace (\w+)", line):
            namespaces.append(match[1])
        elif match := re.fullmatch(r"end (\w+)", line):
            require(namespaces and namespaces.pop() == match[1], "namespace mismatch")
        elif match := re.match(r"^(?:@\[[^]]+\]\s*)?(private )?theorem (\w+)\b", line):
            result.append({"name": ".".join([*namespaces, match[2]]),
                           "private": bool(match[1])})
    require(not namespaces, "unclosed source namespace")
    return result


def reporting_copy(source, theorems):
    # Only reporting commands change; every definition and proof remains intact.
    source = re.sub(r"^#print axioms .+$", "", source, flags=re.M)
    ending = "end TargetWriteCertificate\n"
    require(source.endswith(ending), "unexpected final namespace")
    commands = ["#print axioms " + t["name"] for t in theorems]
    commands += ["#check TargetWriteCertificate." + name for name in CHECKS]
    return source[:-len(ending)] + "\n".join(commands) + "\n\n" + ending


def check_diagnostics(output):
    require(not re.search(r"\berror(?:\([^)]*\))?:|sorryAx|declaration uses ['\"]sorry", output),
            "Lean error or proof-placeholder diagnostic")


def axiom_census(output, theorems):
    check_diagnostics(output)
    expected = {t["name"]: t["private"] for t in theorems}
    require(len(expected) == len(theorems), "duplicate expected theorem")
    records = {}
    pattern = r"^'([^']+)' (?:does not depend on any axioms|depends on axioms:\s*\[([^]]*)\])"
    for match in re.finditer(pattern, output, flags=re.M):
        raw_name = match[1]
        name = re.sub(r"^_private\.AllAxioms\.\d+\.", "", raw_name)
        require(name in expected and name not in records, "unknown or duplicate axiom record: " + name)
        require((name != raw_name) == expected[name], "private/public name mismatch: " + name)
        axioms = [] if match[2] is None else [s.strip() for s in match[2].split(",") if s.strip()]
        require(set(axioms) <= ALLOWED, "disallowed axiom dependency: " + name)
        records[name] = sorted(axioms)
    require(set(records) == set(expected), "incomplete axiom census")
    return {"theorem_count": len(records), "per_theorem": records,
            "axiom_union": sorted({a for values in records.values() for a in values})}


def run(argv, cwd, env):
    start = time.monotonic()
    result = subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True, timeout=120)
    record = {"argv": [Path(argv[0]).name, *argv[1:]], "exit_code": result.returncode,
              "seconds": round(time.monotonic() - start, 6),
              "stdout": result.stdout, "stderr": result.stderr}
    if result.returncode:
        print(json.dumps(record, indent=2), file=sys.stderr)
        raise ValueError("replay command failed")
    return record


def main():
    require(sys.version_info[:2] == (3, 12), "use Python 3.12")
    package = Path(__file__).resolve().parent
    sources = json.loads((package / "SOURCES.json").read_text())
    for name in ("TargetWriteCertificate.lean", "verify_fixtures.py"):
        require(hashlib.sha256((package / name).read_bytes()).hexdigest()
                == sources["delivered_files"][name], "source hash mismatch: " + name)
    manifest = json.loads((package / "THEOREMS.json").read_text())
    require(manifest["source_sha256"] == sources["delivered_files"]["TargetWriteCertificate.lean"],
            "theorem inventory source mismatch")
    source = (package / "TargetWriteCertificate.lean").read_text()
    theorems = inventory(source)
    require(theorems == manifest["theorems"] and len(theorems) == 78
            and sum(t["private"] for t in theorems) == 13, "theorem inventory mismatch")
    selected = os.environ.get("LEAN") or shutil.which("lean")
    require(selected, "set LEAN to an installed Lean 4.30.0 binary, or place it on PATH")
    lean = str(Path(selected).resolve(strict=True))
    # Do not inherit LEAN_PATH, LEAN_SYSROOT, plugins, or project toolchain settings.
    env = {"PATH": str(Path(lean).parent) + os.pathsep + "/usr/bin:/bin", "LANG": "C.UTF-8"}
    receipt = {"status": "PASS", "scope": "concrete row certificate; no numeric rank bridge",
               "source_sha256": manifest["source_sha256"], "commands": []}
    with tempfile.TemporaryDirectory(prefix="target-write-replay-") as tmp:
        scratch = Path(tmp)
        for name in ("TargetWriteCertificate.lean", "verify_fixtures.py"):
            shutil.copyfile(package / name, scratch / name)
        version = run([lean, "--short-version"], scratch, env)
        commit = run([lean, "--githash"], scratch, env)
        require(version["stdout"].strip() == VERSION, "Lean release mismatch")
        require(commit["stdout"].strip() == COMMIT, "Lean commit mismatch")
        receipt.update(lean_version=VERSION, lean_commit=COMMIT)
        for module in ("TargetWriteCertificate", "AllAxioms"):
            if module == "AllAxioms":
                (scratch / "AllAxioms.lean").write_text(reporting_copy(source, theorems))
            record = run([lean, "-o", module + ".olean", module + ".lean"], scratch, env)
            check_diagnostics(record["stdout"] + record["stderr"])
            require((scratch / (module + ".olean")).is_file(), "missing compiled artifact")
            receipt["commands"].append(record)
        receipt["axioms"] = axiom_census(receipt["commands"][-1]["stdout"], theorems)
        receipt["commands"].append(run([sys.executable, "-I", "-O", "-B", "verify_fixtures.py"], scratch, env))
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        sys.exit("FAIL_TARGET_WRITE_REPLAY: " + str(exc))
