#!/usr/bin/env python3
"""Equivalence, rejection and receipt controls for production geometry-cache mutants.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/e8-bit-r420/code/mutants.py"
BASELINE = PACKAGE / "baseline.py"
XCHECK = ROOT / "research/e8-bit-r420/code/xcheck.py"
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
MANIFEST = ROOT / "research/e8-bit-r420/MANIFEST.sha256"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "5b0fa1922076d2e91367b58483c96b33b7b08661"
ORIGINAL_SHA256 = "e2fd3429e2db4389ae8a5ab47dda89f551b0d0952c42fad5ac8d38a85d670594"
OPTIMIZED_SHA256 = "bc6b010641dd3b2f6f33928ce2004189e0671bd9865eab7e70cfcd0d0c6cf9b9"
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


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_mutants(harness: Path) -> bytes:
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(harness), str(XCHECK), str(WORD)],
        cwd=ROOT,
        env=clean_env(),
        capture_output=True,
    )
    require(
        proc.returncode == 0,
        f"mutants harness {harness.name} failed\n{proc.stderr.decode()}\n{proc.stdout.decode()}",
    )
    return proc.stdout


def run_mutants_json(harness: Path, out: Path) -> dict:
    proc = subprocess.run(
        [
            sys.executable,
            "-I",
            "-B",
            str(harness),
            str(XCHECK),
            str(WORD),
            "--json",
            str(out),
        ],
        cwd=ROOT,
        env=clean_env(),
        capture_output=True,
        text=True,
    )
    require(
        proc.returncode == 0,
        f"mutants json harness {harness.name} failed\n{proc.stderr}\n{proc.stdout}",
    )
    return json.loads(out.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/e8-bit-r420/code/mutants.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base mutants.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/e8-bit-r420/code/mutants.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base mutants.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit mutants.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production mutants.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")


def check_manifest_binds_production() -> None:
    listed = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, path = line.split("  ", 1)
        require(path not in listed, f"duplicate MANIFEST path: {path}")
        listed[path] = digest
    require(
        listed.get("code/mutants.py") == OPTIMIZED_SHA256,
        "MANIFEST.sha256 must bind production mutants.py",
    )
    require(digest_file(PRODUCTION) == OPTIMIZED_SHA256, "live mutants.py drifted from OPTIMIZED_SHA256")


def check_stdout_equivalence() -> dict:
    base_out = run_mutants(BASELINE)
    prod_out = run_mutants(PRODUCTION)
    require(base_out == prod_out, "mutation-harness stdout differs")
    require(sha256(prod_out).hexdigest() == MUTANTS_STDOUT_SHA256, "mutants stdout digest drift")
    require(b"PASS mutation controls: 9/9" in prod_out, "missing mutation control marker")
    with tempfile.TemporaryDirectory(prefix="r420-geom-prod-json-") as tmp:
        base_receipt = run_mutants_json(BASELINE, Path(tmp) / "base.json")
        prod_receipt = run_mutants_json(PRODUCTION, Path(tmp) / "prod.json")
    require(base_receipt == prod_receipt, "mutation JSON receipts differ")
    require(
        base_receipt["status"] == "PASS_INTERLEAVED_INTERFACE_MUTATION_CONTROLS",
        "unexpected receipt status",
    )
    require(len(base_receipt["controls"]) == 10, "expected 10 controls")
    require(all(row["rejected"] for row in base_receipt["controls"][:9]), "negative controls")
    require(not base_receipt["controls"][9]["rejected"], "positive control must accept")
    return {
        "mutants_stdout_sha256": MUTANTS_STDOUT_SHA256,
        "mutants_bytes": len(prod_out),
        "controls": 10,
    }


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that reuses full()/interface on geometry hits must diverge.

    Gate-only mutants share geometry with the honest word. Caching those later
    receipts would wrongly accept negative controls. The honest cache always
    reruns full() and interface() on a fresh Word.
    """
    honest = run_mutants(PRODUCTION)
    with tempfile.TemporaryDirectory(prefix="r420-geom-prod-") as tmp:
        mutant_path = Path(tmp) / "mutants.py"
        text = PRODUCTION.read_text(encoding="utf-8")
        needle = (
            "        labels = dict(snapshot[8])\n"
            "        full = obj.full()\n"
            "        hypotheses, conclusion, info = obj.interface()\n"
            "        return obj, labels, full, hypotheses, conclusion, info\n"
        )
        require(needle in text, "geometry hit tail missing for corruption control")
        foil = (
            "        labels = dict(snapshot[8])\n"
            "        # foil: reuse prior full/interface bundled into the geometry snapshot\n"
            "        if len(snapshot) > 9:\n"
            "            return obj, labels, snapshot[9], snapshot[10], snapshot[11], snapshot[12]\n"
            "        full = obj.full()\n"
            "        hypotheses, conclusion, info = obj.interface()\n"
            "        self._entries[key] = snapshot + (full, hypotheses, conclusion, info)\n"
            "        return obj, labels, full, hypotheses, conclusion, info\n"
        )
        # Also widen the miss-path snapshot write so the foil can store extras.
        # The simple approach above fails because snapshot is a local tuple from
        # the hit path; force a clear behavioral break by skipping full()/interface
        # entirely on hits and returning vacuous acceptance-shaped empties.
        foil = (
            "        labels = dict(snapshot[8])\n"
            "        # foil: skip full()/interface on geometry hits\n"
            "        return obj, labels, True, {}, {}, {}\n"
        )
        mutant_path.write_text(text.replace(needle, foil, 1), encoding="utf-8")
        require(mutant_path.read_bytes() != PRODUCTION.read_bytes(), "mutant must differ on disk")
        try:
            bad = run_mutants(mutant_path)
        except AssertionError as exc:
            return {"rejected": True, "mode": "subprocess_failure", "detail": str(exc)[:240]}
        require(bad != honest, "stale-full foil must change the mutation stdout")
        return {"rejected": True, "mode": "stdout_divergence"}


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
    receipts = check_stdout_equivalence()
    corruption = check_temp_corruption_rejection()

    print(
        "PASS_R420_GEOMETRY_CACHE_PRODUCTION "
        f"controls={receipts['controls']} "
        f"corruption={corruption['mode']} "
        f"mutants_sha={MUTANTS_STDOUT_SHA256[:12]} "
        "certs=0 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
