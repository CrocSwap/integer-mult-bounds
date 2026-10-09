#!/usr/bin/env python3
"""Rebuild all analytic certificates with pinned Lean and audit their axioms.

Requires an existing Lean 4.21.0/Mathlib project; installs nothing. The selected
certificate is external input: all literal widths, multiplicities, m, W and a
must match before compiling. This binding check is separate from the Lean
theorem, which proves the real inequality for its literal finite data.
"""
import argparse
from fractions import Fraction
import hashlib
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


def check_binding(certificate):
    selected = json.loads(certificate.read_text())
    data = json.loads((HERE / "selected-witnesses.json").read_text())
    source = (HERE / "SelectedProfileCertificate.lean").read_text()
    # Parse the literal constructors, not a separate copied list of integers.
    row_region = source.split("def rows : List Row := [", 1)[1].split("]", 1)[0]
    rows = re.findall(r"⟨(\d+), (\d+), (\d+), \((\d+) / (\d+) : ℚ\), \((\d+) / (\d+) : ℚ\)⟩", row_region)
    require(len(rows) == row_region.count("⟨") == 27, "Unexpected literal row constructors")
    literal = [{"width": int(t), "multiplicity": int(n), "scale": int(k),
                "logSmall": str(Fraction(int(ln), int(ld))),
                "expUpper": str(Fraction(int(un), int(ud)))}
               for t, n, k, ln, ld, un, ud in rows]
    require(literal == data["rows"], "Lean literals differ from selected-witnesses.json")
    projection = {str(row["width"]): row["multiplicity"] for row in literal}
    require(len(projection) == len(literal), "Duplicate literal width")
    require(projection == selected["bit"]["child_multiplicities"],
            "Literal multiplicities differ from the selected certificate")
    for name in ("m", "W"):
        match = re.search(rf"^def {name} : ℕ := (\d+)$", source, re.M)
        require(match and int(match[1]) == data[name] == selected["bit"][name]
                == selected["finite_bridge"]["bit"][name], f"Mismatched {name}")
    match = re.search(r"^def saving : ℚ := \((\d+) / (\d+) : ℚ\)$", source, re.M)
    require(match is not None, "Missing literal saving")
    saving = Fraction(int(match[1]), int(match[2]))
    require(saving == Fraction(data["saving"]) == Fraction(selected["bit_saving"])
            == Fraction(selected["assembly"]["parameters"]["a_bit"]), "Mismatched saving a")
    mass = sum(row["width"] * row["multiplicity"] for row in literal)
    require(mass == selected["bit"]["total_rank"], "Mismatched rank mass")
    require(max(row["width"] for row in literal) == selected["bit"]["maxchild"],
            "Mismatched maximum child")
    historical_hash = selected.get("characteristic_certificate", {}).get("source_sha256")
    if historical_hash is not None:
        require(data["source_sha256"] == historical_hash,
                "Profile provenance hash differs from selected certificate")
    return {"certificate_sha256": digest(certificate),
            "profile_source_sha256": data["source_sha256"],
            "literal_source_sha256": digest(HERE / "SelectedProfileCertificate.lean"),
            "saving": str(saving), "m": data["m"], "W": data["W"],
            "historical_profile_hash_present": historical_hash is not None,
            "row_count": len(literal), "rank_mass": mass,
            "width_multiplicity_projection": projection,
            "scope": "Exact source-data binding; physical construction is not certified by this script"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake-project", required=True, type=Path)
    parser.add_argument("--certificate", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "verification")
    parser.add_argument("--check-sources-only", action="store_true")
    args = parser.parse_args()
    project, output = args.lake_project.resolve(), args.output.resolve()
    manifest = json.loads((HERE / "theorem-manifest.json").read_text())
    require((project / "lean-toolchain").read_text().strip() == manifest["lean_toolchain"],
            "Wrong project Lean pin")
    packages = json.loads((project / "lake-manifest.json").read_text())["packages"]
    mathlib = [p for p in packages if p["name"] == "mathlib"]
    require(len(mathlib) == 1 and all(mathlib[0].get(k) == v for k, v in manifest["mathlib"].items()),
            "Wrong project Mathlib pin")
    require({p.name for p in HERE.glob("*.lean")} == set(manifest["files"]), "Source inventory mismatch")
    for name, item in manifest["files"].items():
        path = HERE / name
        source = path.read_text()
        require(digest(path) == item["sha256"], f"Source hash changed: {name}")
        names = [path.stem + "." + n for n in DECL.findall(source)]
        require(names == item["theorems"], f"Declaration coverage mismatch: {name}")
        prints = re.findall(r"^#print axioms (\S+)\s*$", source, re.M)
        qualified = [n if "." in n else path.stem + "." + n for n in prints]
        require(len(qualified) == len(set(qualified)) and set(qualified) == set(names),
                f"Axiom coverage mismatch: {name}")
        require(not re.search(r"\b(sorry|admit|native_decide)\b", source), f"Proof escape: {name}")
        require(not re.search(r"^\s*(axiom|constant)\s", source, re.M), f"Custom axiom: {name}")
    binding = check_binding(args.certificate)
    output.mkdir(parents=True, exist_ok=True)
    (output / "source-binding.json").write_text(json.dumps(binding, indent=2) + "\n")
    print("PASS literal selected-certificate binding, source hashes, 17 declarations, dependency pins", flush=True)
    if args.check_sources_only:
        return
    env = os.environ.copy()
    env.pop("LEAN_PATH", None)
    result = subprocess.run(["lake", "env", sys.executable, "-c",
                             "import json, os; print(json.dumps(dict(os.environ)))"],
                            cwd=project, env=env, capture_output=True, text=True, check=True)
    lean_env = json.loads(result.stdout)
    objects = output / "olean"
    objects.mkdir(exist_ok=True)
    lean_env["LEAN_PATH"] = str(objects) + os.pathsep + lean_env.get("LEAN_PATH", "")
    version = subprocess.run(["lean", "--version"], cwd=project, env=lean_env,
                             capture_output=True, text=True, check=True).stdout.strip()
    require(re.search(r"Lean \(version 4\.21\.0(?:[, )])", version), "Wrong actual compiler: " + version)
    allowed = {"propext", "Classical.choice", "Quot.sound"}
    require(set(manifest["allowed_axioms"]) == allowed, "Axiom policy changed")
    report = {"compiler": version, "lean_toolchain": manifest["lean_toolchain"],
              "mathlib": manifest["mathlib"], "source_binding": binding, "files": {}}
    for name, item in manifest["files"].items():
        print("Checking " + name, flush=True)
        result = subprocess.run(["lean", "--root=" + str(HERE), "-o",
                                 str(objects / (Path(name).stem + ".olean")), str(HERE / name)],
                                cwd=project, env=lean_env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True)
        (output / (Path(name).stem + ".log")).write_text(result.stdout)
        audits = AUDIT.findall(result.stdout)
        names = [name for name, _ in audits]
        bad = [(n, a) for n, a in audits if {x.strip() for x in a.split(",") if x.strip()} - allowed]
        require(result.returncode == 0 and not bad and len(names) == len(set(names))
                and set(names) == set(item["theorems"]),
                f"Compilation/axiom audit failed for {name}:\n{result.stdout}")
        report["files"][name] = {"sha256": item["sha256"],
                                 "theorems": {n: sorted(x.strip() for x in a.split(",") if x.strip())
                                              for n, a in audits}}
        print(f"PASS {len(names)} theorem audits", flush=True)
    (output / "axiom-audit.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS all 17 analytic theorems; actual real characteristic is strictly below 1")


if __name__ == "__main__":
    main()
