#!/usr/bin/env python3
"""Equivalence, rejection and receipt controls for production integer RREF.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/e8-bit-r420/code/xcheck.py"
BASELINE = PACKAGE / "baseline.py"
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
MUTANTS = ROOT / "research/e8-bit-r420/code/mutants.py"
MANIFEST = ROOT / "research/e8-bit-r420/MANIFEST.sha256"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "fbff8607e4c61e18481f696b99dd38a32444e90d"
ORIGINAL_SHA256 = "5737d18a7826fd51e131035f2d7bebba2e2868af91dd7672a5f11208b036d424"
OPTIMIZED_SHA256 = "cd1d91b32831b4bd75290edf8b19f3a4378c5733bf4755ba59ed5161e2c468b9"
CHECK_STDOUT_SHA256 = "e4637c1fe38b10fb82e0e4f710a28821e980f629ad3e22b51c1e75b3cdf40acd"
MUTANTS_STDOUT_SHA256 = "8c2738b3258e207370597b60c2ebd318e740fc0feaca04cb8b0e3a26089258d8"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_unique(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_xcheck(script: Path) -> bytes:
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(script), str(WORD)],
        cwd=ROOT,
        env=clean_env(),
        capture_output=True,
    )
    require(proc.returncode == 0, f"{script.name} failed\n{proc.stderr.decode()}\n{proc.stdout.decode()}")
    return proc.stdout


def run_mutants(script: Path) -> bytes:
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(MUTANTS), str(script), str(WORD)],
        cwd=ROOT,
        env=clean_env(),
        capture_output=True,
    )
    require(
        proc.returncode == 0,
        f"mutants against {script.name} failed\n{proc.stderr.decode()}\n{proc.stdout.decode()}",
    )
    return proc.stdout


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/e8-bit-r420/code/xcheck.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base xcheck.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/e8-bit-r420/code/xcheck.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base xcheck.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit xcheck.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production xcheck.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the Fraction baseline")


def check_manifest_binds_production() -> None:
    listed = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, path = line.split("  ", 1)
        require(path not in listed, f"duplicate MANIFEST path: {path}")
        listed[path] = digest
    require(listed.get("code/xcheck.py") == OPTIMIZED_SHA256, "MANIFEST.sha256 must bind production xcheck.py")
    actual = digest_file(ROOT / "research/e8-bit-r420" / "code/xcheck.py")
    require(actual == OPTIMIZED_SHA256, "live xcheck.py drifted from OPTIMIZED_SHA256")


def check_frame_rref_equivalence(baseline, production) -> dict:
    with gzip.open(WORD, "rt", encoding="utf-8") as handle:
        # gzip JSON is a single object without duplicate keys in this fixture.
        word = json.load(handle)
    frames = word["frames"]
    lines = word["lines"]
    compared = 0
    for frame in frames:
        rows = [lines[i] for i in frame]
        before = copy.deepcopy(rows)
        left = baseline.rref(rows)
        right = production.rref(rows)
        require(left == right, "frame RREF/pivot mismatch")
        require(rows == before, "rref mutated its input rows")
        require(all(isinstance(x, Fraction) for row in right[0] for x in row), "RREF type changed")
        ns_l = baseline.nullspace_int(rows)
        ns_r = production.nullspace_int(rows)
        require(ns_l == ns_r, "integer annihilator basis changed")
        require(len(ns_r) == 8 - len(right[1]), "rank/nullity mismatch")
        require(
            all(sum(x * y for x, y in zip(row, n)) == 0 for row in rows for n in ns_r),
            "annihilator dot product is not zero",
        )
        compared += 1
    # Supplemental rational / empty / dependent cases (same spirit as the opt-in adapter).
    extras = [
        [],
        [[0, -2, 3], [0, 4, -6]],
        [[0, 0, 1], [0, -3, 2]],
        [[2, 1, 1], [0, 3, 1]],
        [[Fraction(1, 3), Fraction(2, 7)], [Fraction(2, 3), Fraction(4, 7)]],
    ]
    for rows in extras:
        before = copy.deepcopy(rows)
        left = baseline.rref(rows)
        right = production.rref(rows)
        require(left == right and rows == before, "supplemental RREF mismatch or mutation")
        compared += 1
    return {"frames": len(frames), "matrices_compared": compared}


def check_stdout_equivalence() -> dict:
    base_check = run_xcheck(BASELINE)
    prod_check = run_xcheck(PRODUCTION)
    require(base_check == prod_check, "complete check stdout differs")
    require(sha256(prod_check).hexdigest() == CHECK_STDOUT_SHA256, "check stdout digest drift")
    base_mut = run_mutants(BASELINE)
    prod_mut = run_mutants(PRODUCTION)
    require(base_mut == prod_mut, "mutation-harness stdout differs")
    require(sha256(prod_mut).hexdigest() == MUTANTS_STDOUT_SHA256, "mutants stdout digest drift")
    require(b"PASS interleaved interface lemma" in prod_check, "missing interface lemma marker")
    require(b"PASS mutation controls: 9/9" in prod_mut, "missing mutation control marker")
    return {
        "check_stdout_sha256": CHECK_STDOUT_SHA256,
        "mutants_stdout_sha256": MUTANTS_STDOUT_SHA256,
        "check_bytes": len(prod_check),
        "mutants_bytes": len(prod_mut),
    }


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that flips the elimination sign must diverge from the honest RREF."""
    production = load_module(PRODUCTION, "xcheck_production_live")
    with gzip.open(WORD, "rt", encoding="utf-8") as handle:
        word = json.load(handle)
    # Frame 127 needs reduced cleanup; sign-flip also breaks simpler frames.
    sample = [word["lines"][i] for i in word["frames"][127]]
    honest = production.rref(sample)
    with tempfile.TemporaryDirectory(prefix="r420-rref-prod-") as tmp:
        mutant_path = Path(tmp) / "xcheck.py"
        text = PRODUCTION.read_text(encoding="utf-8")
        needle = "rows[i] = _primitive([a * x - b * y for x, y in zip(row, base)])"
        require(needle in text, "elimination update line missing for corruption control")
        foil = "rows[i] = _primitive([a * x + b * y for x, y in zip(row, base)])  # foil: wrong sign"
        mutant_path.write_text(text.replace(needle, foil, 1), encoding="utf-8")
        require(mutant_path.read_bytes() != PRODUCTION.read_bytes(), "mutant must differ on disk")
        mutant = load_module(mutant_path, "xcheck_production_mutant")
        bad = mutant.rref(sample)
        require(bad != honest, "sign-flip foil must change the sample RREF")
        # Complete checker against the foil must either reject or print a different receipt.
        try:
            foil_out = run_xcheck(mutant_path)
            honest_out = run_xcheck(PRODUCTION)
            require(foil_out != honest_out, "foil accepted with identical complete stdout")
            return {"rejected": True, "mode": "stdout_divergence"}
        except AssertionError as exc:
            return {"rejected": True, "mode": "subprocess_failure", "detail": str(exc)[:240]}


def check_o_policy_children() -> None:
    """Package require() gates still launch assertion-enabled children under -O."""
    # The production/baseline checkers themselves may use assertions in mutants.py;
    # children are always launched with -I -B and without PYTHONOPTIMIZE.
    out = run_xcheck(PRODUCTION)
    require(sha256(out).hexdigest() == CHECK_STDOUT_SHA256, "-O parent still gets assertion-enabled child")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="unused placeholder; default verify is read-only and never writes certificates",
    )
    args = parser.parse_args(argv)
    require(not args.write_result, "default verify is read-only; do not pass --write-result")

    check_baseline_bytes()
    check_manifest_binds_production()
    baseline = load_module(BASELINE, "xcheck_baseline")
    production = load_module(PRODUCTION, "xcheck_production")
    algebra = check_frame_rref_equivalence(baseline, production)
    receipts = check_stdout_equivalence()
    corruption = check_temp_corruption_rejection()
    check_o_policy_children()

    # Duplicate-key guard on RESULT.json when present (read-only).
    result_path = PACKAGE / "RESULT.json"
    if result_path.exists():
        load_json_unique(result_path)

    print(
        "PASS_R420_RREF_PRODUCTION "
        f"frames={algebra['frames']} "
        f"matrices={algebra['matrices_compared']} "
        f"corruption={corruption['mode']} "
        f"check_sha={receipts['check_stdout_sha256'][:12]} "
        "certs=0 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
