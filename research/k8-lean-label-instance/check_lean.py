#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Freshly compile the concrete k8 label certificates using Mathlib v4.21.0."""
import argparse
import json
import os
import re
import shutil
import signal
import subprocess
import tempfile
import time
from pathlib import Path

import generate
from translate import translate
from verify import HERE, ROOT, digest, encoded, read, rebuild, require, source_check

ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def package_snapshot(directory=HERE):
    return {name: digest((directory / name).read_bytes()) for name in
            ("TreeCheckpoint.lean", "generate.py", "translate.py")}


def verify_snapshot(expected, directory=HERE):
    require(package_snapshot(directory) == expected, "formal sources changed during replay")


def command_result(command, project, environment, timeout):
    require(os.name == "posix", "formal driver requires POSIX process groups")
    with subprocess.Popen(command, cwd=project, env=environment, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          start_new_session=True) as process:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        finally:
            # Lean is launched through Lake. Retire the complete owned process
            # group on success, failure, timeout or cancellation.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait(timeout=10)


def compile_file(path, temporary, project, environment):
    command = ["lake", "env", "lean", "--root=" + str(temporary), "-j1",
               "-DwarningAsError=true", "-o", str(path.with_suffix(".olean")), str(path)]
    result = command_result(command, project, environment, 180)
    require(result.returncode == 0, path.name + " failed:\n" + result.stdout + result.stderr)
    print("CHECKED " + path.name, flush=True)
    return result.stdout


def false_control(temporary, project, environment):
    path = temporary / "FalseControl.lean"
    path.write_text("""import TreeCheckpoint
open LemmaG LemmaG.TreeCheckpoint
-- Reg0 is labelled9; a relabel claiming source10 is inadmissible.
def before : State 0 := .leaf 9
def bad : List (Event (Fin 1) Nat Rat) := [.relabel 0 10 11]
theorem falseLabel : check bad before = some (.leaf 11) := by decide +kernel
""")
    command = ["lake", "env", "lean", "--root=" + str(temporary), "-j1", str(path)]
    result = command_result(command, project, environment, 60)
    require(result.returncode != 0 and "decide" in result.stdout,
            "false label theorem was not rejected by the decision tactic")
    return "inadmissible_relabel_rejected"


def run(project):
    inputs = source_check()
    package_sources = package_snapshot()
    project = project.resolve()
    require((project / "lakefile.toml").is_file(), "missing Lake project")
    require((project / "lean-toolchain").read_text().strip() == "leanprover/lean4:v4.21.0",
            "Lean toolchain must be4.21.0")
    mathlib = [p for p in read(project / "lake-manifest.json")["packages"] if p["name"] == "mathlib"]
    require(len(mathlib) == 1 and mathlib[0]["rev"] ==
            "308445d7985027f538e281e18df29ca16ede2ba3", "Mathlib must match v4.21.0")
    environment = dict(os.environ)
    for key in ("LEAN_PATH", "PYTHONPATH", "PYTHONHOME", "PYTHONOPTIMIZE"):
        environment.pop(key, None)
    version = subprocess.run(["lake", "env", "lean", "--version"], cwd=project,
                             env=environment, capture_output=True, text=True, timeout=30, check=True)
    require("version 4.21.0" in version.stdout, "wrong Lean version")
    outputs, generated = {}, {}
    with tempfile.TemporaryDirectory(prefix="k8-lean-kernel-") as directory:
        temporary = Path(directory)
        environment["LEAN_PATH"] = str(temporary)
        (temporary / "LemmaG").mkdir()
        stream = temporary / "LemmaG/Stream.lean"
        shutil.copyfile(ROOT / "research/e8-lemma-g-lean/LemmaG/Stream.lean", stream)
        checkpoint = temporary / "TreeCheckpoint.lean"
        shutil.copyfile(HERE / "TreeCheckpoint.lean", checkpoint)
        require(digest(checkpoint.read_bytes()) == package_sources["TreeCheckpoint.lean"],
                "checker changed before snapshot")
        compile_file(stream, temporary, project, environment)
        compile_file(checkpoint, temporary, project, environment)
        c, programs, _, _ = rebuild(temporary / "local")
        for name in ("Forward", "Backward"):
            start, events, _ = translate(c, programs[name.lower()])
            files = generate.emit(temporary, name, start, events)
            for path in files:
                generated[path.name] = digest(path.read_bytes())
                output = compile_file(path, temporary, project, environment)
            reports = re.findall(r"'([^']+)' depends on axioms: \[([^]]*)\]", output)
            require(len(reports) == 2, "missing live axiom report")
            for root, axioms in reports:
                names = set(axioms.replace(" ", "").split(",")) - {""}
                require(names <= ALLOWED_AXIOMS, "unexpected axiom: " + root)
                outputs[root] = sorted(names)
        rejected = false_control(temporary, project, environment)
        require(source_check() == inputs, "sources changed during kernel replay")
        verify_snapshot(package_sources)
    return {"status": "PASS_K8_LEAN_LABEL_KERNEL", "lean": version.stdout.strip(),
            "roots": outputs, "generated_sha256": generated, "inputs": inputs,
            "checkpoint_sha256": package_sources["TreeCheckpoint.lean"],
            "generator_sha256": package_sources["generate.py"],
            "translation_sha256": package_sources["translate.py"],
            "formal_control": rejected,
            "scope": "WellLabelled and final labels for two source-bound translated event words; "
                     "not a proof of the Python adapter, RecipesExact, scalar endpoints or supplier admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lake-project", type=Path, default=ROOT / "formal/lean")
    parser.add_argument("--write-receipt", type=Path)
    args = parser.parse_args()
    began = time.monotonic()
    result = run(args.lake_project)
    if args.write_receipt:
        with args.write_receipt.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = read(HERE / "KERNEL.json")
        # Compiler platform strings are environment metadata, not mathematical equality.
        observed_core = {k: v for k, v in result.items() if k != "lean"}
        expected_core = {k: v for k, v in expected.items() if k != "lean"}
        require(encoded(observed_core) == encoded(expected_core), "kernel receipt mismatch")
    print(result["status"] + f" roots=4 elapsed_seconds={time.monotonic() - began:.1f}")


if __name__ == "__main__":
    main()
