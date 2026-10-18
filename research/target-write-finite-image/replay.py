#!/usr/bin/env python3
"""Replay the dependency and finite-image successor with complete axiom censuses.

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
    gate = sources["kernel_replay"]
    require(gate["status"] == "ready" and gate["approved_successor_sha256"],
            "draft: exact Pro-repaired successor hash has not been approved for replay")
    require(gate["approved_successor_sha256"]
            == sources["delivered_files"]["TargetWriteFiniteImage.lean"],
            "approved successor hash mismatch")
    manifests = json.loads((package / "THEOREMS.json").read_text())
    proof_sources, inventories = {}, {}
    for kind, module, count, private in (
            ("dependency", "TargetWriteCertificate", 78, 13),
            ("successor", "TargetWriteFiniteImage", 43, 0)):
        name = module + ".lean"
        raw = (package / name).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == sources["delivered_files"][name], "source hash mismatch: " + name)
        manifest = manifests[kind]
        require(manifest["source_sha256"] == digest, "theorem inventory source mismatch: " + name)
        source = raw.decode()
        theorems = inventory(source)
        require(theorems == manifest["theorems"] and len(theorems) == count
                and sum(t["private"] for t in theorems) == private,
                "theorem inventory mismatch: " + name)
        proof_sources[module], inventories[kind] = source, theorems
    selected = os.environ.get("LEAN") or shutil.which("lean")
    require(selected, "set LEAN to an installed Lean 4.30.0 binary, or place it on PATH")
    lean = str(Path(selected).resolve(strict=True))
    receipt = {"status": "PASS", "scope": "actual finite-image injection; no conventional rank bridge",
               "source_hashes": {name: sources["delivered_files"][name]
                                 for name in ("TargetWriteCertificate.lean", "TargetWriteFiniteImage.lean")},
               "commands": []}
    with tempfile.TemporaryDirectory(prefix="target-write-finite-image-") as tmp:
        scratch = Path(tmp)
        # No inherited Lean paths, sysroot, plugins, or project toolchain settings.
        env = {"PATH": str(Path(lean).parent) + os.pathsep + "/usr/bin:/bin",
               "LANG": "C.UTF-8", "LEAN_PATH": str(scratch)}
        for module in proof_sources:
            shutil.copyfile(package / (module + ".lean"), scratch / (module + ".lean"))
        version = run([lean, "--short-version"], scratch, env)
        commit = run([lean, "--githash"], scratch, env)
        require(version["stdout"].strip() == VERSION, "Lean release mismatch")
        require(commit["stdout"].strip() == COMMIT, "Lean commit mismatch")
        receipt.update(lean_version=VERSION, lean_commit=COMMIT)
        for module in ("TargetWriteCertificate", "AllAxioms", "TargetWriteFiniteImage"):
            if module == "AllAxioms":
                (scratch / "AllAxioms.lean").write_text(reporting_copy(
                    proof_sources["TargetWriteCertificate"], inventories["dependency"]))
            record = run([lean, "-o", module + ".olean", module + ".lean"], scratch, env)
            check_diagnostics(record["stdout"] + record["stderr"])
            require((scratch / (module + ".olean")).is_file(), "missing compiled artifact")
            receipt["commands"].append(record)
            if module == "AllAxioms":
                receipt["dependency_axioms"] = axiom_census(record["stdout"], inventories["dependency"])
            elif module == "TargetWriteFiniteImage":
                receipt["successor_axioms"] = axiom_census(record["stdout"], inventories["successor"])
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        sys.exit("FAIL_TARGET_WRITE_FINITE_IMAGE_REPLAY: " + str(exc))
