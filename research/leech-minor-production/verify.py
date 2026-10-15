#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production Leech byte lanes.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
from audit_affine_vectors import certificate as production_certificate  # noqa: E402
from experiments import affine_vector_screens as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "0686b47d4844bedc9dddfacb0bff52ec552120a2"
ORIGINAL_SHA256 = "756778eeca27f490adc7354a122dc50c40375156259991469c47a90949118ea1"
BASE_CERTIFICATE_SHA256 = "e7920c3305bd5e3058d2614fadc064ec1f658029183325f600c7ee4b56a7906e"
WITNESSES = SCRIPTS / "experiments" / "affine_vector_witnesses.json"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json_unique(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def load_base_certificate_bytes() -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:certificates/affine-vector-screens.json"],
        cwd=ROOT,
    )


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:scripts/experiments/affine_vector_screens.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base affine_vector_screens.py sha256 drift")
    require(
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/affine_vector_screens.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base affine_vector_screens.py blob drift",
    )
    require(
        (PACKAGE / "baseline.py").read_bytes() == original,
        "baseline.py must be an exact copy of the base-commit source",
    )


def check_leech_equivalence(baseline, optimized) -> list[dict]:
    data = load_json_unique(WITNESSES)
    rows = []
    for fixture in data["leech"]:
        old = baseline.leech_minor(**fixture)
        new = optimized.leech_minor(**fixture)
        require(old == new, f"leech_minor receipt differs for shift={fixture.get('shift')}")
        require(old["positive_deficit_excluded"], "admission flag lost")
        require(old["binary_rank_lower"] == len(fixture["independent_rows"]), "rank mismatch")
        rows.append(old)
    require(len(rows) == 5, "expected five frozen Leech minors")
    return rows


def check_rejections(baseline, optimized) -> None:
    for eng, name in ((baseline, "baseline"), (optimized, "optimized")):
        try:
            eng.leech_minor([0, 0], [0])
            raise AssertionError(f"{name} accepted duplicate global indices")
        except ValueError as exc:
            require("index" in str(exc).lower() or "invalid" in str(exc).lower(), str(exc))
        try:
            eng.leech_minor([0], [0], shift=3)
            raise AssertionError(f"{name} accepted unsupported shift")
        except ValueError as exc:
            require("offset" in str(exc).lower() or "shift" in str(exc).lower(), str(exc))
        try:
            eng.leech_minor([0, 1], [0, 1], shift=-8, signed=False)
            raise AssertionError(f"{name} accepted shifted unsigned family")
        except ValueError as exc:
            require("signed" in str(exc).lower() or "shift" in str(exc).lower(), str(exc))


def check_temp_corruption(optimized) -> None:
    with tempfile.TemporaryDirectory(prefix="leech-minor-prod-") as tmp:
        dest = Path(tmp) / "affine_vector_screens.py"
        shutil.copy2(SCRIPTS / "experiments" / "affine_vector_screens.py", dest)
        text = dest.read_text(encoding="utf-8")
        # Drop every selected bit (including the forced diagonal) so the binary
        # rank gate must reject the frozen independent-row witness.
        mutated = text.replace(
            "if i == j or value == shift + offset",
            "if False",
            1,
        )
        require(mutated != text, "mutation did not edit production source text")
        dest.write_text(mutated, encoding="utf-8")
        mutant = load_module(dest, "affine_vector_screens_mutant")
        data = load_json_unique(WITNESSES)
        fixture = data["leech"][0]
        try:
            mutant.leech_minor(**fixture)
            raise AssertionError("mutant accepted a zero-row lane decode")
        except ValueError as exc:
            require(
                "dependent" in str(exc).lower() or "independent" in str(exc).lower(),
                str(exc),
            )
        # Production path still accepts the frozen fixture.
        optimized.leech_minor(**fixture)


def check_certificate(write: bool) -> dict:
    result = production_certificate()
    path = ROOT / "certificates" / "affine-vector-screens.json"
    text = json.dumps(serializable(result), indent=2, sort_keys=True) + "\n"
    if write:
        path.write_text(text, encoding="utf-8")
    committed = path.read_text(encoding="utf-8")
    require(
        committed == text,
        "working certificates/affine-vector-screens.json does not match regenerated certificate()",
    )
    load_json_unique(path)
    base = load_base_certificate_bytes()
    require(sha256(base).hexdigest() == BASE_CERTIFICATE_SHA256, "base certificate sha256 drift")
    old = json.loads(base.decode("utf-8"))
    new = json.loads(committed)
    old_pin = old["source_sha256"].pop("scripts/experiments/affine_vector_screens.py")
    new_pin = new["source_sha256"].pop("scripts/experiments/affine_vector_screens.py")
    require(old_pin == ORIGINAL_SHA256, "unexpected base pin")
    require(
        new_pin == digest_file(SCRIPTS / "experiments" / "affine_vector_screens.py"),
        "certificate pin != working source",
    )
    require(old == new, "certificate changed outside the single affine_vector_screens.py source pin")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="rewrite certificates/affine-vector-screens.json (default: read-only check)",
    )
    args = parser.parse_args(argv)

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "affine_vector_screens_baseline")
    rows = check_leech_equivalence(baseline, production)
    check_rejections(baseline, production)
    check_temp_corruption(production)
    result = check_certificate(write=args.write_certificate)
    print(
        "PASS_LEECH_MINOR_PRODUCTION "
        f"leech_cases={len(rows)} "
        f"code_cases={len(result['polynomial_code_screens'])} "
        "certs=1 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
