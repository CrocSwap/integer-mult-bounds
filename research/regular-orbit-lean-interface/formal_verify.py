"""Fresh Lean compilation and actual axiom reports; never reuse package oleans."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOTS = ["coefficient_extract", "action_faithful", "matrix_coefficient_extract",
         "complete_endpoint_faithful", "mv3_basis", "basis_tuple_separates_matrices",
         "mv3_identity", "gl3_identity_basis", "gl3_basis_separates", "gl3_complete_endpoint_faithful"]
CONTROL_ROOTS = ["collision_operators_equal", "duplicate_operators_equal",
                 "omitted_label_operators_equal", "clean_role_hides_leak",
                 "dirty_role_exposes_leak", "concrete_complete_endpoint"]
NEGATIVES = {
    "colliding_orbit": "example : coeffA false = coeffB false := by decide\n",
    "duplicate_enumeration": "example : coeffB false = false := by decide\n",
    "missing_label": "example : coeffA true = false := by decide\n",
    "omitted_dirty_role": "example : matrixAction [false,true] [()] identityAddress diagonal dirty false false = matrixAction [false,true] [()] identityAddress withLeak dirty false false := by decide\n",
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def audit_roots(output, roots):
    result = {}
    for root in roots:
        prefix = "RegularOrbit." + root
        pattern = re.compile(r"^'" + re.escape(prefix) + r"' (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)$", re.M)
        rows = list(pattern.finditer(output))
        require(len(rows) == 1, "missing/duplicate axiom report: " + prefix)
        axioms = [] if not rows[0][1] else [x.strip() for x in rows[0][1].split(",")]
        require(set(axioms) <= {"propext", "Quot.sound", "Classical.choice"}, "unexpected axiom: " + prefix)
        result[prefix] = axioms
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--lean", type=Path, required=True, help="existing Lean4.34.1 executable; no download")
    ap.add_argument("--out", type=Path, help="write a NEW receipt only")
    args = ap.parse_args()
    if args.out:
        require(not args.out.exists(), "output already exists")
    lean = args.lean.resolve()
    version = subprocess.check_output([str(lean), "--version"], text=True, encoding="utf-8").strip()
    require("version 4.34.1," in version and "5045d0056413266e57c625dcd7c365b10e377c52" in version, "wrong Lean version")
    source_hashes = {}
    axioms = {}
    controls = {}
    with tempfile.TemporaryDirectory(prefix="regular-orbit-lean-") as tmp:
        target = Path(tmp)
        env = dict(os.environ)
        env["LEAN_PATH"] = str(target)
        for name in ("RegularOrbit.lean", "Controls.lean"):
            raw = (HERE/name).read_bytes()
            source_hashes[name] = hashlib.sha256(raw).hexdigest()
            (target/name).write_bytes(raw)
        def compile_file(name, artifact=None):
            command = [str(lean)]
            if artifact:
                command += ["-o", artifact]
            command += [name]
            return subprocess.run(command, cwd=target, env=env, capture_output=True,
                                  text=True, encoding="utf-8", timeout=90)
        for name, roots in (("RegularOrbit", ROOTS), ("Controls", ["Controls."+x for x in CONTROL_ROOTS])):
            result = compile_file(name+".lean", name+".olean")
            require(result.returncode == 0, name+" failed:\n"+result.stdout+result.stderr)
            require("warning:" not in result.stdout and "error:" not in result.stdout, "unexpected Lean diagnostic")
            axioms.update(audit_roots(result.stdout, roots))
        for name, false_statement in NEGATIVES.items():
            (target/(name+".lean")).write_text("import Controls\nopen RegularOrbit RegularOrbit.Controls\n"+false_statement,
                                              encoding="utf-8", newline="\n")
            result = compile_file(name+".lean")
            require(result.returncode != 0, "false statement compiled: "+name)
            require("error:" in result.stdout and ("false" in result.stdout or "decide" in result.stdout), "unrelated negative failure: "+name)
            controls[name] = {"rejected": True, "diagnostic": result.stdout.strip()}
    receipt = {"status":"PASS_FRESH_LEAN_REGULAR_ORBIT_INTERFACE", "version":version,
               "sources_sha256":source_hashes, "axioms":axioms, "negative_statements":controls,
               "reused_candidate_olean":False, "limits":"Explicit finite enumerations/action-source correspondence and prior search census remain external; this is not a supplier or full theorem formalization."}
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as f:
            json.dump(receipt, f, indent=2)
            f.write("\n")
    print(json.dumps({"status":receipt["status"], "roots":len(axioms), "negative_statements":len(controls), "version":version}))


if __name__ == "__main__":
    main()
