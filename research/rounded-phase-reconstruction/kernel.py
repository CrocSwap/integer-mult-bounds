"""Fresh pinned Lean compilation and rejection probes; separate from Python replay."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
VERSION = 'Lean (version 4.34.1, x86_64-w64-windows-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)'
AXIOMS = {"RoundedPhase." + name: ["propext"] for name in (
    "unrotate_rotate", "rotate_unrotate", "back_step", "step_back",
    "reconstruct", "reconstruct_reverse", "same_readout")}
HELPERS = '''
open RoundedPhase
def zeroC : Coeff := ⟨.zero, fun _ => 0, fun _ => 0⟩
def oneC : Coeff := ⟨.one, fun _ => 0, fun _ => 0⟩
def halfC : Coeff := ⟨.zero, fun x => (x + 1) / 2, fun _ => 0⟩
def wrongInverse (v : Grid) := xm (fun x => (1-x)/2) (xm (fun x => (1-x)/2) v)
def changingChart (v : Grid) : Coeff := if v.1 = 0 then oneC else zeroC
def initial : State := ((0, 1), (1, 0))
def staleBack (v : State) : State := (unrotate (changingChart v.2) v.1, unrotate oneC v.2)
'''
FOILS = {
    "negated_rounder_at_half_tie": "wrongInverse (rotate halfC (0, 1)) = (0, 1)",
    "omitted_inverse_quarter": "unrotate zeroC (rotate oneC (2, 3)) = (2, 3)",
    "chart_before_ratio_restoration": "staleBack (step changingChart oneC initial) = initial",
    "incomplete_reverse_walk": "walk (back changingChart oneC) 0 (walk (step changingChart oneC) 1 initial) = initial",
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def audit_output(output):
    matches = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", output)
    found = {name: [x.strip() for x in values.split(',') if x.strip()] for name, values in matches}
    need(len(matches) == len(AXIOMS) and found == AXIOMS, "axiom/root mismatch")
    need(all(x not in output for x in ("sorryAx", "warning:", "error:")), "untrusted kernel output")
    return found


def receipt_check():
    value = json.loads((HERE / "KERNEL.json").read_text(encoding="utf-8"))
    need(value["formal_sha256"] == hashlib.sha256((HERE / "Reconstruction.lean").read_bytes()).hexdigest(), "formal source receipt mismatch")
    need(value["version"] == VERSION and value["axioms"] == AXIOMS, "formal receipt toolchain/axioms")
    need(value["fresh_kernel_compile"] is True and value["axiom_guard_negative_control"] is True, "formal receipt status")
    need(value["rejected_false_probes"] == list(FOILS), "formal receipt controls")
    return value


def run(lean):
    lean = Path(lean).resolve(strict=True)
    version = subprocess.run([str(lean), "--version"], text=True, capture_output=True, check=True).stdout.strip()
    need(version == VERSION, "pinned platform-specific Lean version required")
    source = (HERE / "Reconstruction.lean").read_bytes()
    need(not re.search(rb"\b(sorry|axiom|admit|native_decide)\b", source), "forbidden proof escape")
    with tempfile.TemporaryDirectory(prefix="rounded-phase-kernel-") as tmp:
        folder = Path(tmp)
        def compile_file(name, raw):
            (folder / name).write_bytes(raw)
            return subprocess.run([str(lean), name], cwd=folder, text=True, capture_output=True, timeout=120)
        result = compile_file("Reconstruction.lean", source)
        need(result.returncode == 0, result.stdout + result.stderr)
        axioms = audit_output(result.stdout)
        rejected = []
        for label, proposition in FOILS.items():
            foil = source + (HELPERS + "\nexample : " + proposition + " := by decide\n").encode()
            answer = compile_file(label + ".lean", foil)
            need(answer.returncode != 0 and "Tactic `decide` proved that the proposition" in answer.stdout and "is false" in answer.stdout,
                 "false probe not rejected: " + label + "\n" + answer.stdout + answer.stderr)
            rejected.append(label)
        try:
            audit_output(result.stdout.replace("[propext]", "[propext, sorryAx]", 1))
        except ValueError:
            pass
        else:
            raise ValueError("axiom control accepted")
    return {"formal_sha256": hashlib.sha256(source).hexdigest(), "version": version,
            "axioms": axioms, "fresh_kernel_compile": True, "rejected_false_probes": rejected,
            "axiom_guard_negative_control": True,
            "limits": "Std and Lean trusted. Source interpretation is reviewed and finitely tested, not a verified Python translation. No analytic error, physical resource or full supplier theorem."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(), "refuse receipt overwrite")
    result = run(args.lean)
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as dest:
            json.dump(result, dest, indent=2, sort_keys=True)
            dest.write("\n")
    else:
        need(result == receipt_check(), "fresh kernel receipt mismatch")
    print("PASS_ROUNDED_PHASE_KERNEL roots=7 false_probes=4 axiom_control=1")


if __name__ == "__main__":
    main()
