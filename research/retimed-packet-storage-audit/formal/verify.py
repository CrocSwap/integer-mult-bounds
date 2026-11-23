#!/usr/bin/env python3
"""Bind #8042's capped predicate and check the Lean 4.36 proof and axiom report."""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
PINS = {
    "positive.py": "a1b5d1725c6230667646d3e50551d566e2faac39bc39a02c703c3da065f4db5c",
    "retimed_supplier.py": "4bd969e3f1cfdcdf26c36e5fa7ab64c8e72904f516a51af6b2a29524e1cf8eb2",
    "installations.py": "2244e7e27f7348575944eb652a741861a0a04d77b18c297db221ef74b3116a16",
    "band_product.py": "98595de1aa89a158cfddeb462f9a87bad4a8d59c0d1eb01f24790cb46050044d",
    "OuterStop.lean": "1cbaf689d8bb02722e0361376780b326872f5e4775b30c6c5ae10a98c5994930",
}
EXPECTED_THEOREMS = {
    "cap_threshold", "loop_correct", "low_bit_branch", "sourceLoop_eq_loop",
    "sourceLoop_correct", "power_le_correct", "retimed_stop_correct",
    "callerStop_correct", "callerContinue_correct", "exponent_zero", "base_one",
    "cap_mutation_rejected", "equality_boundary_retained", "early_reject_retained",
    "accumulator_premise_needed",
}
PREDICATE = """def power_le(base, power, ceiling):
    value = 1
    while power:
        if power & 1:
            value *= base
            if value > ceiling:
                return False
        power //= 2
        if power:
            base = min(ceiling + 1, base * base)
    return True
"""


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def shape(node):
    return ast.dump(node, include_attributes=False)


def extract_function(text):
    node = next(n for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == "power_le")
    env = {}
    exec(compile(ast.Module(body=[node], type_ignores=[]), "pinned-power-le", "exec"), env)
    return node, env["power_le"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", required=True, type=Path)
    parser.add_argument("--runtime", required=True, type=Path)
    parser.add_argument("--positive", required=True, type=Path)
    parser.add_argument("--outer-stop", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "evidence")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    paths = {name: args.runtime / name for name in PINS}
    paths.update({"positive.py": args.positive, "OuterStop.lean": args.outer_stop})
    for name, expected in PINS.items():
        require(digest(paths[name]) == expected, f"changed source: {name}")

    node, source_le = extract_function(paths["positive.py"].read_text())
    require(shape(node) == shape(ast.parse(PREDICATE).body[0]), "changed predicate AST")
    caller = ast.parse(paths["retimed_supplier.py"].read_text())
    cls = next(n for n in caller.body if isinstance(n, ast.ClassDef) and n.name == "Positive")
    run = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_run")
    guard = next(n.test for n in run.body if isinstance(n, ast.If))
    expected_guard = ast.parse("selected <= n or power_le(selected, self.denominator, root_width)",
                               mode="eval").body
    require(shape(guard) == shape(expected_guard), "changed caller guard")
    profile = next(n.value for n in ast.parse(paths["installations.py"].read_text()).body
                   if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "RESOLUTION" for t in n.targets))
    require(shape(profile.args[-1]) == shape(ast.parse("10**21", mode="eval").body),
            "changed source exponent")
    supplier = next(n for n in ast.parse(paths["band_product.py"].read_text()).body
                    if isinstance(n, ast.FunctionDef) and n.name == "production_supplier")
    require(shape(supplier.body[0]) == shape(ast.parse("return Positive(rank_log, stop_denominator)").body[0]),
            "changed supplier parameter forwarding")

    cases = [(2, 2, 3, False), (2, 3, 8, True), (2, 3, 7, False),
             (1, 10**21, 1, True), (2, 10**21, 64, False),
             (2, 0, 1, True), (17, 0, 1, True), (17, 1, 1, False)]
    for base, power, ceiling, answer in cases:
        require(source_le(base, power, ceiling) == answer, "source boundary case failed")
    _, bad_cap = extract_function(PREDICATE.replace("ceiling + 1", "ceiling"))
    _, strict = extract_function(PREDICATE.replace("value > ceiling", "value >= ceiling"))
    require(bad_cap(2, 2, 3) and not source_le(2, 2, 3), "cap mutation escaped")
    require(source_le(2, 3, 8) and not strict(2, 3, 8), "equality mutation escaped")
    require(source_le(2, 0, 0) and not 2**0 <= 0, "zero-ceiling domain control escaped")

    proof = HERE / "CappedPower.lean"
    text = proof.read_text()
    require(re.findall(r"^import .+$", text, re.MULTILINE) == ["import Lean"], "changed imports")
    require(not re.search(r"\b(sorry|admit|native_decide)\b|^\s*(axiom|unsafe|partial)\b",
                          text, re.MULTILINE), "untrusted proof construct")
    env = os.environ.copy()
    env.pop("LEAN_PATH", None)
    version = subprocess.run([str(args.lean), "--version"], env=env, check=True,
                             capture_output=True, text=True).stdout.strip()
    require("version 4.36.0" in version, "unexpected Lean version")
    command = [str(args.lean), str(proof)]
    compiled = subprocess.run(command, env=env, capture_output=True, text=True, timeout=60)
    log = compiled.stdout + compiled.stderr
    (args.output / "lean-check.txt").write_text(log)
    require(compiled.returncode == 0, "Lean compilation failed; see lean-check.txt")
    require("sorryAx" not in log and "warning:" not in log and "error:" not in log,
            "Lean diagnostic or incomplete proof")
    reports = re.findall(r"'RetimedCappedPower\.([^']+)' depends on axioms: \[([^\]]*)\]", log)
    axioms = {name: [a.strip() for a in ax.split(",") if a.strip()] for name, ax in reports}
    require(set(axioms) == EXPECTED_THEOREMS, "missing or unexpected axiom report")
    allowed = {"propext", "Quot.sound", "Classical.choice"}
    require(all(set(xs) <= allowed for xs in axioms.values()), "unexpected axiom dependency")
    receipt = {
        "status": "PASS_CAPPED_POWER_KERNEL_AND_SOURCE_BINDING",
        "source_repository": "aliromman/integer-mult-bounds",
        "source_pr": 8042, "source_commit": "dfd25d553a843a946ca0b94130a5ff8943e98fdd",
        "lean_version": version, "compile_command": command, "LEAN_PATH": "unset",
        "proof_sha256": digest(proof), "checker_sha256": digest(Path(__file__)),
        "source_sha256": PINS, "axioms": axioms, "source_boundary_cases": len(cases),
        "negative_controls": ["cap_h", "strict_equality", "missing_initial_accumulator_bound"],
        "scope": "Nat predicate denotation; inspected Python correspondence; no machine-time theorem",
    }
    (args.output / "RESULT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
