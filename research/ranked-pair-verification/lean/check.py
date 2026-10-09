#!/usr/bin/env python3
"""Compile the pinned ranked-pair Lean sources and audit every theorem.

Run from any directory. The default project is the enclosing repository's
formal/lean; pass --project when checking a source bundle before integration.
The script uses only the standard library and an installed `lake` command.
It neither installs tools nor modifies Lean sources or dependency pins.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


HERE = Path(__file__).resolve().parent
DECLARATION = re.compile(r"^(?:theorem|lemma)\s+(\w+)\s*(?=[:({])", re.M)
AUDIT_ROW = re.compile(
    r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", re.M
)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def default_project():
    for parent in HERE.parents:
        candidate = parent / "formal" / "lean"
        if (candidate / "lean-toolchain").is_file():
            return candidate
    raise SystemExit("No enclosing formal/lean project found; pass --project PATH")


def run_lean(project, arguments):
    env = os.environ.copy()
    # Lake supplies the pinned project's search paths; unrelated caller paths
    # must not override the dependency environment being checked.
    env.pop("LEAN_PATH", None)
    return subprocess.run(
        ["lake", "env", "lean", *arguments], cwd=project, env=env,
        text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake-project", "--project", dest="project", type=Path)
    parser.add_argument("--output", type=Path,
                        help="audit log directory; default: repository build/ranked-pair-formal")
    parser.add_argument("--check-sources-only", action="store_true",
                        help="verify source hashes, theorem coverage and dependency pins without compiling")
    args = parser.parse_args()
    project = (args.project or default_project()).resolve()
    manifest = json.loads((HERE / "theorem-manifest.json").read_text())
    require(manifest["schema_version"] == 1, "Unsupported theorem manifest schema")
    require((project / "lean-toolchain").read_text().strip() == manifest["lean_toolchain"],
            "Lean toolchain pin differs from theorem-manifest.json")
    dependencies = json.loads((project / "lake-manifest.json").read_text())["packages"]
    mathlib = [row for row in dependencies if row["name"] == "mathlib"]
    require(len(mathlib) == 1, "Expected exactly one pinned Mathlib dependency")
    require(all(mathlib[0].get(key) == value for key, value in manifest["mathlib"].items()),
            "Mathlib dependency pin differs from theorem-manifest.json")
    require({p.name for p in HERE.glob("*.lean")} == set(manifest["files"]),
            "Lean source inventory differs from theorem-manifest.json")

    for name, entry in manifest["files"].items():
        path = HERE / name
        source = path.read_text()
        require(hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"],
                f"Source changed since the audited theorem manifest: {name}")
        declared = {path.stem + "." + item for item in DECLARATION.findall(source)}
        expected = entry["theorems"]
        require(len(expected) == len(set(expected)) and declared == set(expected),
                f"Theorem coverage mismatch: {name}")
        printed = re.findall(r"^#print axioms (\S+)\s*$", source, re.M)
        qualified = {item if "." in item else path.stem + "." + item for item in printed}
        require(len(printed) == len(set(printed)) and qualified == declared,
                f"Missing or duplicate #print axioms statement: {name}")
        require(not re.search(r"\b(sorry|admit|native_decide)\b", source),
                f"Disallowed proof escape in {name}")
        require(not re.search(r"^\s*(axiom|constant)\s", source, re.M),
                f"Custom axiom or constant declaration in {name}")

    count = sum(len(entry["theorems"]) for entry in manifest["files"].values())
    print(f"PASS source hashes, {count} theorem declarations and pinned Lean/Mathlib", flush=True)
    if args.check_sources_only:
        return

    version = run_lean(project, ["--version"])
    matched = re.search(r"Lean \(version ([0-9]+\.[0-9]+\.[0-9]+)(?:[, )])", version.stdout)
    require(version.returncode == 0 and matched and matched[1] == manifest["lean_version"],
            "Wrong compiler or unavailable pinned Lean environment:\n" + version.stdout)
    output = (args.output or project.parent.parent / "build" / "ranked-pair-formal").resolve()
    output.mkdir(parents=True, exist_ok=True)
    allowed = set(manifest["allowed_axioms"])
    require(allowed == {"propext", "Classical.choice", "Quot.sound"},
            "Unexpected allowed-axiom policy in manifest")
    report = {"toolchain": manifest["lean_toolchain"], "mathlib": manifest["mathlib"],
              "compiler": version.stdout.strip(), "files": {}}
    for name, entry in manifest["files"].items():
        print(f"Checking {name} ...", flush=True)
        result = run_lean(project, [str(HERE / name)])
        (output / (Path(name).stem + ".log")).write_text(result.stdout)
        rows = AUDIT_ROW.findall(result.stdout)
        names = [name for name, _ in rows]
        bad = [(name, axioms) for name, axioms in rows
               if {a.strip() for a in axioms.split(",") if a.strip()} - allowed]
        success = (result.returncode == 0 and len(names) == len(set(names))
                   and set(names) == set(entry["theorems"]) and not bad)
        if not success:
            print(result.stdout, file=sys.stderr)
            raise SystemExit(f"Compilation/axiom audit failed for {name}; unexpected axioms: {bad}")
        report["files"][name] = {
            "sha256": entry["sha256"],
            "theorems": {theorem: sorted(a.strip() for a in axioms.split(",") if a.strip())
                         for theorem, axioms in rows},
        }
        print(f"PASS {len(names)} theorem audits", flush=True)
    (output / "axiom-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS all {count} theorems; logs: {output}")


if __name__ == "__main__":
    main()
