"""Meaningful source, isolation, work-directory and acceptance-budget controls."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    require(__debug__, "Control assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    root, work = args.root.resolve(), args.work.resolve()
    require(not work.exists() and not work.is_relative_to(root), "Fresh external control directory required")
    work.mkdir(parents=True)
    here = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("_reuse_controls_driver", here / "verify.py")
    verifier = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(verifier)
    source_before = verifier.sources(root)
    word = here / "data/CANONICAL-WORD.json.gz"
    word_before = word.read_bytes()
    controls = []

    def reject(name, message, *, script=None, alternate_root=None, alternate_word=None,
               target=None, optimize=False, hard=60):
        command = [sys.executable, "-I", "-B"]
        if optimize:
            command.append("-O")
        target = target or work / (name + "-run")
        command += [str(script or here / "verify.py"), "--root", str(alternate_root or root),
                    "--word", str(alternate_word or word), "--work", str(target),
                    "--rounds", "1", "--hard-seconds", str(hard)]
        tick = time.monotonic()
        result = subprocess.run(command, capture_output=True, timeout=10)
        log = result.stdout + result.stderr
        (work / (name + ".log")).write_bytes(log)
        require(result.returncode != 0 and message.encode() in log, "Control did not reject: " + name)
        row = {"name": name, "argv": command, "exit_code": result.returncode,
               "required_error": message, "seconds": time.monotonic() - tick,
               "log_sha256": hashlib.sha256(log).hexdigest(), "rejected": True}
        controls.append(row)
        return target

    reject("assertions-off", "Assertions must remain enabled", optimize=True)
    wrong_word = work / "wrong-word.json.gz"
    wrong_word.write_bytes(word_before + b"\n")
    reject("word-pin", "Canonical gzip pin mismatch", alternate_word=wrong_word)
    for name, source in [("compiler-pin", verifier.COMPILER), ("driver-pin", verifier.DRIVER)]:
        copy_root = work / name
        for path, raw in source_before.items():
            copied = copy_root / path
            copied.parent.mkdir(parents=True, exist_ok=True)
            copied.write_bytes(raw + (b"\n# mutation\n" if path == source else b""))
        reject(name, "Source pin mismatch", alternate_root=copy_root)
    existing = work / "existing"
    existing.mkdir()
    sentinel = existing / "KEEP"
    sentinel.write_bytes(b"preserve existing work\n")
    reject("existing-work", "Work directory must be fresh", target=existing)
    require(sentinel.read_bytes() == b"preserve existing work\n" and len(list(existing.iterdir())) == 1,
            "Existing work changed")
    inside = root / "research/clifford-state-reuse/CONTROL-MUST-NOT-CREATE"
    require(not inside.exists(), "Inside-checkout sentinel already exists")
    reject("inside-checkout", "Work directory must be outside this checkout", target=inside)
    require(not inside.exists(), "Rejected inside-checkout work was created")
    generated = work / "generated"
    verifier.prepare(root, word, generated)
    bad = generated / "compilers/candidate/clifford_exact.py"
    bad.write_bytes(bad.read_bytes() + b"\n# mutation\n")
    try:
        verifier.check_generated(generated)
    except ValueError as error:
        require("Generated source pin mismatch" in str(error), "Wrong generated-source rejection")
        controls.append({"name": "generated-pin", "rejected": True, "required_error": str(error)})
    else:
        raise ValueError("Generated compiler mutation accepted")
    bad_tool = work / "mutated-controls"
    bad_tool.mkdir()
    shutil.copyfile(here / "verify.py", bad_tool / "verify.py")
    (bad_tool / "semantic_controls.py").write_bytes((here / "semantic_controls.py").read_bytes() + b"\n# mutation\n")
    reject("independent-pin", "Independent control source pin mismatch", script=bad_tool / "verify.py")
    timed = reject("budget", "Allocated phase replay timed out", hard=1)
    failed = json.loads((timed / "RESULT.json").read_bytes())
    require(failed["status"] == "FAILED_OR_INCOMPLETE" and len(failed["jobs"]) == 1
            and failed["jobs"][0]["status"] == "ALLOCATED_HARD_TIMEOUT",
            "Budget control did not reach actual phase-child timeout")
    controls[-1]["phase_child_reached"] = True
    controls[-1]["terminal_receipt_sha256"] = hashlib.sha256((timed / "RESULT.json").read_bytes()).hexdigest()
    positive = work / "positive-preflight"
    tick = time.monotonic()
    verifier.prepare(root, word, positive)
    semantic = verifier.semantic_preflight(positive, tick, 60)
    hostile_out = work / "HOSTILE-ENV-SEMANTIC.json"
    hostile_command = [sys.executable, "-I", "-B", str(here / "semantic_controls.py"),
                       "--baseline", str(positive / "compilers/baseline/clifford_exact.py"),
                       "--candidate", str(positive / "compilers/candidate/clifford_exact.py"),
                       "--out", str(hostile_out)]
    hostile = subprocess.run(hostile_command, capture_output=True, timeout=10,
                             env=dict(os.environ, PYTHONOPTIMIZE="2", PYTHONPATH="/untrusted/unused"))
    (work / "hostile-environment.log").write_bytes(hostile.stdout + hostile.stderr)
    require(hostile.returncode == 0 and json.loads(hostile_out.read_bytes())["status"]
            == "PASS_INDEPENDENT_CLIFFORD_STATE_REUSE_CONTROLS", "Isolated hostile-environment positive failed")
    require(verifier.sources(root) == source_before and word.read_bytes() == word_before,
            "Original retained inputs changed")
    require(len(controls) == 9 and all(row["rejected"] for row in controls), "Control coverage drift")
    receipt = {"status": "PASS_REUSE_DRIVER_CONTROLS", "negative_controls": controls,
               "positive_semantic_preflight": semantic, "hostile_environment_argv": hostile_command,
               "hostile_environment_receipt_sha256": hashlib.sha256(hostile_out.read_bytes()).hexdigest(),
               "original_retained_inputs_unchanged": True, "full_phase_replay_certified": False}
    verifier.write_json(work / "CONTROLS.json", receipt)
    print("PASS_REUSE_DRIVER_CONTROLS negative=9 positive_preflight=1 hostile_environment=1", flush=True)


if __name__ == "__main__":
    main()
