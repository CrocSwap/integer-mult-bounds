"""Seal or check the focused positive publication, excluding build outputs.

Apache-2.0. Substantial OpenAI Codex assistance. Signed Cao Yifan.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "f626db5c3a3d781d8f7695038776c621651f75e1"
GROUPS = {
    "warp-interface-20261022": ".gitattributes .gitignore ACTUAL-WORD-FREEZE.json ACTUAL-WORD.json.gz CANDIDATE-WORD.json.gz CANDIDATE.json free_warp_contacts.py free_warp_milp.py warp_merge.py PATCH.json SOURCES.json regenerate.py verify_candidate.py uniform_gain.py NATIVE-VALIDATION.json PHASE-VALIDATION.json.gz UNIFORM-GAIN.json PROOF.md README.md freeze_candidate.py make_patch.py make_source_pins.py DISCOVERY-FREEZE.json MILP-OPall.json",
    "kappa-interface-round2-20261022": ".gitattributes price_profile.py verify_result.py ARITHMETIC.json PROFILE.json PROOF.md RESULT.md SESSION-VERIFICATION.json regeneration.log native.log absolute-phases.log uniform-gain.log retained-dependencies.log whole-arithmetic.log independent-audit.log",
    "query-projector-interface-20261022": ".gitattributes positive-candidate-audit/audit.py positive-candidate-audit/audit-result.json positive-candidate-audit/README.md",
    "kappa-search-20261022": ".gitattributes BASELINE-REPLAY.json baseline-native.log baseline-arithmetic.log baseline-dependencies.log",
    "scalar-reorder-20261022": ".gitattributes intervals.py",
}
LEAN_FILES = ".gitattributes .gitignore README.md ANALYTIC-SCOPE.md CAPACITY-SCOPE.md Native-note.md REVIEW.md lakefile.toml lake-manifest.json lean-toolchain MATH-LEAN-VERIFICATION.json NATIVE-LEAN-VERIFICATION.json ARITHMETIC-TRANSCRIPTION.json LEAN-VERIFICATION.json native_generate.py numerical_generate.py generate_arithmetic.py verify_lean.py publication_inventory.py verify_lean_controls.py LEAN-WRAPPER-CONTROLS.json"


def inventory():
    receipt = json.loads((HERE / "LEAN-VERIFICATION.json").read_text(encoding="utf-8"))
    if receipt["status"] != "PASS_SCOPED_LEAN_REPLAY":
        raise ValueError("A complete successful scoped Lean receipt is required")
    files = {ROOT / "research" / group / name
             for group, names in GROUPS.items() for name in names.split()}
    files.update(HERE / name for name in LEAN_FILES.split())
    for row in receipt["modules"]:
        files.add(HERE / row["source"])
        files.add(HERE / row["log"])
    rows = []
    for path in sorted(files):
        relative = path.resolve().relative_to(ROOT).as_posix()
        data = path.read_bytes()
        rows.append({"path": relative, "bytes": len(data), "sha256": sha256(data).hexdigest()})
    return {"schema_version": 1, "base_commit": BASE, "kappa": "37769/12500000",
            "scope": "Focused positive construction and scoped Lean evidence; build outputs and unrelated exploratory archives excluded.",
            "file_count": len(rows), "total_bytes": sum(row["bytes"] for row in rows), "files": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the manifest after all verification and documentation settle")
    args = parser.parse_args()
    path = HERE / "FOCUSED-INVENTORY.json"
    result = inventory()
    if args.write:
        path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    elif json.loads(path.read_text(encoding="utf-8")) != result:
        raise ValueError("Focused publication inventory differs")
    print("PASS_FOCUSED_PUBLICATION_INVENTORY", result["file_count"], result["total_bytes"])


if __name__ == "__main__":
    main()
