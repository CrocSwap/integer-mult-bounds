#!/usr/bin/env python3
"""Build the analytic dependency and exact floor transfer in an isolated directory.

Uses installed Lean/Lake, Python standard library, and an existing pinned
Lean4.21.0/Mathlib project. Installs nothing; edits no sources or project files.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
DECL = re.compile(r"^theorem\s+(\w+)\s*(?=[:({])", re.M)
AUDIT = re.compile(r"^'([^']+)' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", re.M)


def require(condition, message):
    if not condition:
        raise SystemExit(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake-project", required=True, type=Path)
    parser.add_argument("--analytic-dir", type=Path, default=HERE.parents[1] / "next-proof" / "analytic")
    parser.add_argument("--certificate", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "verification")
    parser.add_argument("--check-sources-only", action="store_true")
    args = parser.parse_args()
    project, analytic, output = args.lake_project.resolve(), args.analytic_dir.resolve(), args.output.resolve()
    manifest = json.loads((HERE / "theorem-manifest.json").read_text())
    require(digest(analytic / "theorem-manifest.json") == manifest["analytic_dependency_manifest_sha256"],
            "Analytic dependency manifest changed")
    dependency = json.loads((analytic / "theorem-manifest.json").read_text())
    require((project / "lean-toolchain").read_text().strip() == manifest["lean_toolchain"], "Wrong Lean pin")
    packages = json.loads((project / "lake-manifest.json").read_text())["packages"]
    mathlib = [p for p in packages if p["name"] == "mathlib"]
    require(len(mathlib) == 1 and all(mathlib[0].get(k) == v for k, v in manifest["mathlib"].items()),
            "Wrong Mathlib pin")
    builds = []
    for folder, inventory in [(analytic, dependency), (HERE, manifest)]:
        require({p.name for p in folder.glob("*.lean")} == set(inventory["files"]), "Source inventory mismatch")
        for name, item in inventory["files"].items():
            source = (folder / name).read_text()
            require(digest(folder / name) == item["sha256"], "Source hash changed: " + name)
            declared = [Path(name).stem + "." + n for n in DECL.findall(source)]
            require(declared == item["theorems"], "Theorem inventory mismatch: " + name)
            prints = re.findall(r"^#print axioms (\S+)\s*$", source, re.M)
            names = [n if "." in n else Path(name).stem + "." + n for n in prints]
            require(len(names) == len(set(names)) and set(names) == set(declared), "Audit coverage mismatch: " + name)
            require(not re.search(r"\b(sorry|admit|native_decide)\b", source), "Proof escape: " + name)
            require(not re.search(r"^\s*(axiom|constant)\s+\w+\s*[:({]", source, re.M), "Custom axiom: " + name)
            builds.append((folder, name, item))
    spec = importlib.util.spec_from_file_location("analytic_binding", analytic / "check.py")
    binding_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(binding_module)
    binding = binding_module.check_binding(args.certificate)
    output.mkdir(parents=True, exist_ok=True)
    (output / "source-binding.json").write_text(json.dumps(binding, indent=2) + "\n")
    dependency_count = sum(len(item["theorems"]) for item in dependency["files"].values())
    new_count = sum(len(item["theorems"]) for item in manifest["files"].values())
    print(f"PASS pins, selected-profile binding, {dependency_count} dependency + {new_count} new theorem source hashes", flush=True)
    if args.check_sources_only:
        return
    env = os.environ.copy()
    env.pop("LEAN_PATH", None)
    result = subprocess.run(["lake", "env", sys.executable, "-c", "import json,os; print(json.dumps(dict(os.environ)))"],
                            cwd=project, env=env, capture_output=True, text=True, check=True)
    lean_env = json.loads(result.stdout)
    objects = output / "olean"
    objects.mkdir(exist_ok=True)
    lean_env["LEAN_PATH"] = str(objects) + os.pathsep + lean_env.get("LEAN_PATH", "")
    version = subprocess.run(["lean", "--version"], cwd=project, env=lean_env,
                             capture_output=True, text=True, check=True).stdout.strip()
    require(re.search(r"Lean \(version 4\.21\.0(?:[, )])", version), "Wrong compiler: " + version)
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    require(set(manifest["allowed_axioms"]) == allowed == set(dependency["allowed_axioms"]), "Changed axiom policy")
    report = {"compiler": version, "mathlib": manifest["mathlib"], "source_binding": binding,
              "dependency_theorem_count": dependency_count, "new_theorem_count": new_count, "files": {}}
    for folder, name, item in builds:
        print("Checking " + name, flush=True)
        result = subprocess.run(["lean", "--root=" + str(folder), "-o", str(objects / (Path(name).stem + ".olean")),
                                 str(folder / name)], cwd=project, env=lean_env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        (output / (Path(name).stem + ".log")).write_text(result.stdout)
        rows = AUDIT.findall(result.stdout)
        names = [n for n, a in rows]
        bad = [(n, a) for n, a in rows if {x.strip() for x in a.split(",") if x.strip()} - allowed]
        require(result.returncode == 0 and not bad and len(names) == len(set(names))
                and set(names) == set(item["theorems"]), "Compile/axiom audit failed: " + name + "\n" + result.stdout)
        report["files"][name] = {"sha256": item["sha256"],
                                 "theorems": {n: sorted(x.strip() for x in a.split(",") if x.strip()) for n, a in rows}}
        print(f"PASS {len(names)} theorem audits", flush=True)
    (output / "axiom-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS all {dependency_count + new_count} theorem audits; exact floor transfer has {new_count} new theorems")


if __name__ == "__main__":
    main()
