#!/usr/bin/env python3
"""Rebuild both certificates and run the independent checker and controls."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from budget import solve_budget
from construct import canonical_payload, construct, load_source
from verify import read_word

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_source_pins(root=ROOT):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for relative, expected in pins["repository_inputs_sha256"].items():
        # The original selected record is now retained as an exact checkpoint.
        resolved = ("certificates/checkpoints/k492626.json"
                    if relative == "certificates/selected-result.json" else relative)
        path = root / resolved
        require(path.is_file(), "missing pinned input: " + resolved)
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                "pinned input changed: " + resolved)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lean", type=Path, help="optional Lean 4.21.0 executable")
    args = parser.parse_args()
    check_source_pins()
    source = load_source()
    result = solve_budget(source, seed=6)
    expected = json.loads((HERE / "data/budget.json").read_text())
    require(canonical_payload(result) == canonical_payload(expected), "budget reconstruction differs")
    for name, cuts, recipe_name in (("word", result["cuts"], "recipe"),
                                     ("optimum", (), "optimum-recipe")):
        word, recipe = construct(source, seed=6, cuts=cuts)
        frozen_word = read_word(HERE / "data" / (name + ".json.gz"))
        frozen_recipe = json.loads((HERE / "data" / (recipe_name + ".json")).read_text())
        require(canonical_payload(word) == canonical_payload(frozen_word), name + " payload differs")
        require(canonical_payload(recipe) == canonical_payload(frozen_recipe), name + " recipe differs")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    commands = [
        [sys.executable, "-B", HERE / "verify.py"],
        [sys.executable, "-B", HERE / "verify.py", "--candidate", HERE / "data/optimum.json.gz",
         "--recipe", HERE / "data/optimum-recipe.json", "--expect-prefix-rejection"],
        [sys.executable, "-B", HERE / "test_verify.py"],
        [sys.executable, "-B", HERE / "test_reproduce.py"],
        [sys.executable, "-B", HERE / "test_budget.py"],
        [sys.executable, "-B", HERE / "test_semantic_bridge.py"],
    ]
    for command in commands:
        completed = subprocess.run(list(map(str, command)), env=env, capture_output=True,
                                   text=True, timeout=120, check=False)
        require(completed.returncode == 0, completed.stdout + completed.stderr)
        if command[2].name.startswith("test_"):
            print(completed.stdout + completed.stderr, end="", flush=True)
    if args.lean:
        version = subprocess.run([str(args.lean), "--version"], capture_output=True,
                                 text=True, timeout=30, check=True).stdout
        require("version 4.21.0" in version, "expected pinned Lean 4.21.0")
        completed = subprocess.run([str(args.lean.resolve()), str(HERE / "Forest.lean")],
                                   capture_output=True, text=True, timeout=120, check=False)
        require(completed.returncode == 0, completed.stdout + completed.stderr)
        lines = completed.stdout.splitlines()
        require(len(lines) == 7 and all("[propext, Quot.sound]" in line for line in lines),
                "unexpected Lean theorem axiom report: " + completed.stdout)
        print("PASS_LEAN_FOREST generic compensation; seven axiom reports checked")
    print("PASS_R420_TARGET_FOREST D=19922->15025 ADDs=26916->22019 saved=4897 "
          "columns=660 payload_bits=104 cut_states=724; uncut_optimum=14921 rejected_at_106_bits")


if __name__ == "__main__":
    main()
