#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production packed verify_factor.

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
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
from audit_complex_centers import certificate as production_certificate  # noqa: E402
from experiments import complex_centers as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "13be871d501b7ebaaaec7e755ff4834c6cc49dc7"
ORIGINAL_SHA256 = "3744396587d729253d80980f6310b56e7bf0ea21b165bd178d0d6d4c49faf2e2"
BASE_CERTIFICATE_SHA256 = "3f46000e645c338a583e0f2ab669a7c681980743d03335548eeb838072f1d458"
HEIGHTS = (8, 10, 12, 18, 26)


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
    import subprocess

    return subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:certificates/dyadic-central-factor.json"],
        cwd=ROOT,
    )


def check_baseline_bytes() -> None:
    import subprocess

    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:scripts/experiments/complex_centers.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base complex_centers.py sha256 drift")
    require(
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/complex_centers.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
        == ORIGINAL_BLOB,
        "base complex_centers.py blob drift",
    )
    require(
        (PACKAGE / "baseline.py").read_bytes() == original,
        "baseline.py must be an exact copy of the base-commit source",
    )


def check_factor_equivalence(baseline, optimized) -> list[dict]:
    rows = []
    for h in HEIGHTS:
        factor = optimized.factor(h)
        require(factor == baseline.factor(h), f"factor({h}) drifted")
        old = baseline.verify_factor(factor)
        new = optimized.verify_factor(factor)
        require(old == new, f"verify_factor({h}) receipts differ")
        triples = h * (h - 1) * (h - 2) // 6
        require(old["triples"] == triples, f"verify_factor({h}) triple count")
        require(
            old["coefficients_checked"] == triples * triples,
            f"verify_factor({h}) coefficient count",
        )
        rows.append(old)
    return rows


def check_rejections(baseline, optimized) -> None:
    for eng, name in ((baseline, "baseline"), (optimized, "optimized")):
        f = eng.factor(8)
        bad = deepcopy(f)
        # Structural gather gate: weight must be -1 or +1, but coordinate may repeat.
        bad["gather"][0] = ((0, 1), (0, 1))
        try:
            eng.verify_factor(bad)
            raise AssertionError(f"{name} accepted duplicated gather coordinate")
        except ValueError as exc:
            require("gather" in str(exc).lower() or "invalid" in str(exc).lower(), str(exc))
        bad = deepcopy(f)
        from fractions import Fraction as Q

        bad["scatter"][0] = (Q(1, 2),) * 8
        try:
            eng.verify_factor(bad)
            raise AssertionError(f"{name} accepted non-integral scatter")
        except ValueError as exc:
            require("integral" in str(exc).lower(), str(exc))
        bad = deepcopy(f)
        scatter = list(bad["scatter"][0])
        scatter[0] = 3
        bad["scatter"][0] = tuple(scatter)
        try:
            eng.verify_factor(bad)
            raise AssertionError(f"{name} accepted inadmissible scalar charge")
        except ValueError as exc:
            require(
                "mismatch" in str(exc).lower()
                or "dyadic" in str(exc).lower()
                or "charge" in str(exc).lower(),
                str(exc),
            )


def check_temp_corruption(optimized) -> None:
    with tempfile.TemporaryDirectory(prefix="central-factor-prod-") as tmp:
        dest = Path(tmp) / "complex_centers.py"
        shutil.copy2(SCRIPTS / "experiments" / "complex_centers.py", dest)
        text = dest.read_text(encoding="utf-8")
        mutated = text.replace(
            "require(actual==expected,'Central factor coefficient mismatch')",
            "require(True,'Central factor coefficient mismatch')",
            1,
        )
        require(mutated != text, "mutation did not edit production source text")
        dest.write_text(mutated, encoding="utf-8")
        mutant = load_module(dest, "complex_centers_mutant")
        f = mutant.factor(8)
        bad = deepcopy(f)
        scatter = list(bad["scatter"][0])
        # Keep weights in the dyadic charge set so only the product gate should fire.
        scatter[0] = 0 if scatter[0] != 0 else 1
        bad["scatter"][0] = tuple(scatter)
        try:
            production.verify_factor(bad)
            raise AssertionError("production accepted a corrupted scatter row")
        except ValueError as exc:
            require("mismatch" in str(exc).lower(), str(exc))
        # Mutant disables the product equality gate and must accept this row.
        mutant.verify_factor(bad)


def check_certificate(write: bool) -> dict:
    result = production_certificate()
    path = ROOT / "certificates" / "dyadic-central-factor.json"
    text = json.dumps(serializable(result), indent=2, sort_keys=True) + "\n"
    if write:
        path.write_text(text, encoding="utf-8")
    committed = path.read_text(encoding="utf-8")
    require(
        committed == text,
        "working certificates/dyadic-central-factor.json does not match regenerated certificate()",
    )
    load_json_unique(path)
    base = load_base_certificate_bytes()
    require(sha256(base).hexdigest() == BASE_CERTIFICATE_SHA256, "base certificate sha256 drift")
    old = json.loads(base.decode("utf-8"))
    new = json.loads(committed)
    old_pin = old["source_sha256"].pop("scripts/experiments/complex_centers.py")
    new_pin = new["source_sha256"].pop("scripts/experiments/complex_centers.py")
    require(old_pin == ORIGINAL_SHA256, "unexpected base pin")
    require(
        new_pin == digest_file(SCRIPTS / "experiments" / "complex_centers.py"),
        "certificate pin != working source",
    )
    companion = "scripts/experiments/disjoint_tensor.py"
    require(new["source_sha256"][companion] == "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac", "reviewed PR2117 companion pin drift")
    new["source_sha256"][companion] = old["source_sha256"][companion]
    require(old == new, "certificate changed outside reviewed source pins")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="regenerate certificates/dyadic-central-factor.json (default: read-only compare)",
    )
    args = parser.parse_args(argv)

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "complex_centers_baseline")
    optimized = production
    require(
        digest_file(SCRIPTS / "experiments" / "complex_centers.py") != ORIGINAL_SHA256,
        "production source still equals the unoptimized base pin",
    )
    require(
        digest_file(PACKAGE / "baseline.py") == ORIGINAL_SHA256,
        "baseline.py must equal the original source sha256",
    )

    rows = check_factor_equivalence(baseline, optimized)
    check_rejections(baseline, optimized)
    check_temp_corruption(optimized)
    cert = check_certificate(write=args.write_certificate)

    print(
        "PASS_CENTRAL_FACTOR_PRODUCTION "
        f"heights={list(HEIGHTS)} "
        f"coeffs={[r['coefficients_checked'] for r in rows]} "
        f"optimize={sys.flags.optimize} "
        f"certificate_source_pin={cert['source_sha256']['scripts/experiments/complex_centers.py'][:12]} "
        "no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
