#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production P112 signed modular determinants.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import io
import itertools
import json
import subprocess
import sys
import tempfile
import types
from contextlib import redirect_stdout
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SINK = ROOT / "research/p112-free-sink-audit97"
PRODUCTION = SINK / "independent.py"
BASELINE = PACKAGE / "baseline.py"
CERTIFICATE = SINK / "CERTIFICATE.json"
OPT_IN_ENGINE = ROOT / "research/p112-signed-modular86/engine.py"

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "c65f3fbfe130a4f8cf07b9d2fa4d180cde2957c5"
ORIGINAL_SHA256 = "46806efe1ee7744c810a69981d471b42dfceaa336fee226991c55ba1edfd129f"
OPTIMIZED_SHA256 = "c77cf3dd1234c26cfb7df2d356752721e8b1b37169f20543678fe2f4d07a53f8"
CERT_SHA256 = "45abf8c46b54ab752a16573cc6e03a225a6d76a853b093f186d52bd2b51ec9c6"
ENGINE_SHA256 = "b74c6dd99e9cad0eb4cb252c810acea74c1cba979c7766d194933e4bc35a35fa"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_checker(name: str, source: Path):
    """Load independent.py with assertions kept even when this wrapper runs under -O.

    `__file__` is always the live sink path so HERE/verify.py/CERTIFICATE resolve.
    """
    module = types.ModuleType(name)
    module.__file__ = str(PRODUCTION)
    exec(compile(source.read_bytes(), str(PRODUCTION), "exec", optimize=0), module.__dict__)
    return module


def load_engine():
    module = types.ModuleType("signed_modular_engine")
    module.__file__ = str(OPT_IN_ENGINE)
    exec(compile(OPT_IN_ENGINE.read_bytes(), str(OPT_IN_ENGINE), "exec", optimize=0), module.__dict__)
    return module


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/p112-free-sink-audit97/independent.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base independent.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/p112-free-sink-audit97/independent.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base independent.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit independent.py")
    require(digest_file(PRODUCTION) == OPTIMIZED_SHA256, "production independent.py digest drift")
    require(PRODUCTION.read_bytes() != original, "production must differ from Fraction baseline")
    require(digest_file(CERTIFICATE) == CERT_SHA256, "certificate digest drift")
    require(digest_file(OPT_IN_ENGINE) == ENGINE_SHA256, "opt-in engine digest drift")
    prod_text = PRODUCTION.read_text(encoding="utf-8")
    base_text = BASELINE.read_text(encoding="utf-8")
    require("def _modular_determinant(" in prod_text, "production must define _modular_determinant")
    require("def rational_determinant(" in prod_text, "production must retain rational_determinant")
    require("PRIME = 521" in prod_text, "production must pin modulus 521")
    require("def _modular_determinant(" not in base_text, "baseline must stay Fraction-only")
    require("def fraction_determinant(rows):" in base_text, "baseline must keep fraction_determinant")
    require(OPT_IN_ENGINE.exists(), "opt-in engine missing")


def audit_outcome(module, certificate):
    printed = io.StringIO()
    with redirect_stdout(printed):
        result = module.audit(certificate)
    return result, printed.getvalue()


def run_equivalence() -> dict:
    check_baseline_bytes()
    certificate = json.loads(CERTIFICATE.read_bytes(), object_pairs_hook=unique_object)
    baseline = load_checker("p112_baseline", BASELINE)
    production = load_checker("p112_production", PRODUCTION)
    engine = load_engine()

    baseline.source.checked_sources()
    production.source.checked_sources()

    base_result, _ = audit_outcome(baseline, certificate)
    prod_result, _ = audit_outcome(production, certificate)
    require(base_result == prod_result, "baseline/production audit results differ")
    require(
        base_result
        == {"cases": 28560, "rank_histogram": {7: 448, 8: 28112}, "exact_minors": 4030},
        "unexpected audit inventory",
    )

    lines, _ = baseline.source.geometry()
    signed = []
    for minor in certificate["minors"]:
        rows = [[lines[i][j] for j in minor["columns"]] for i in minor["rows"]]
        require(engine.eligible(rows), "every frozen minor enters checked bound")
        require(production._eligible(rows), "production eligibility matches engine")
        a = baseline.fraction_determinant(rows)
        b = production.fraction_determinant(rows)
        c = engine.determinant(rows, baseline.fraction_determinant)
        require(a == b == c == minor["determinant"], "full signed determinant agreement")
        signed.append([minor["rows"], minor["columns"], b])

    controls = []

    def reject(name, fn):
        try:
            fn()
        except (ValueError, AssertionError):
            controls.append(name)
        else:
            raise AssertionError("accepted control: " + name)

    for name, change in (
        (
            "wrong signed determinant",
            lambda x: x["minors"][0].__setitem__("determinant", -x["minors"][0]["determinant"]),
        ),
        ("missing minor", lambda x: x["minors"].pop()),
        ("duplicate minor", lambda x: x["minors"].append(copy.deepcopy(x["minors"][0]))),
        ("Boolean determinant", lambda x: x["minors"][0].__setitem__("determinant", True)),
        ("missing pattern", lambda x: x["patterns"].pop()),
        ("false free count", lambda x: x.__setitem__("free_alternatives", 1)),
    ):
        bad = copy.deepcopy(certificate)
        change(bad)
        reject(name, lambda bad=bad: production.audit(bad))

    reject("insufficient modulus", lambda: production._recover(256, 257, 256))
    reject("invalid residue", lambda: production._recover(521, 521, 256))
    reject("violated determinant bound", lambda: production._recover(257, 521, 256))

    boundary = [[2 * int(i == j) for j in range(8)] for i in range(8)]
    require(production.fraction_determinant(boundary) == 256, "positive Hadamard boundary")
    boundary[0], boundary[1] = boundary[1], boundary[0]
    require(production.fraction_determinant(boundary) == -256, "negative Hadamard boundary")
    require(production.fraction_determinant([[1, 1], [1, 1]]) == 0, "singular exact zero")

    fallback_cases = [
        [[521]],
        [[3]],
        [[int(i == j) for j in range(9)] for i in range(9)],
        [[Fraction(1, 2), 0], [0, 2]],
    ]
    for rows in fallback_cases:
        require(not production._eligible(rows), "fallback fixture outside fast envelope")
        require(
            production.fraction_determinant(rows) == baseline.fraction_determinant(rows),
            "exact fallback",
        )

    tested = 0
    for n in (1, 2, 3):
        for flat in itertools.product((-1, 0, 1), repeat=n * n):
            rows = [list(flat[i * n : (i + 1) * n]) for i in range(n)]
            require(
                production.fraction_determinant(rows) == baseline.fraction_determinant(rows),
                "exhaustive signed matrix",
            )
            tested += 1

    # On-disk corruption foil: flip one certificate determinant in a temp copy.
    with tempfile.TemporaryDirectory(prefix="p112-mod-prod-") as tmp:
        foil = Path(tmp) / "CERTIFICATE.json"
        bad = copy.deepcopy(certificate)
        bad["minors"][0]["determinant"] = -bad["minors"][0]["determinant"]
        foil.write_text(json.dumps(bad), encoding="utf-8")
        try:
            production.audit(json.loads(foil.read_text(encoding="utf-8"), object_pairs_hook=unique_object))
        except (ValueError, AssertionError):
            controls.append("temp certificate determinant flip")
        else:
            raise AssertionError("accepted temp certificate determinant flip")

    stream = hashlib.sha256(
        json.dumps(signed, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return {
        "complete_audit": prod_result,
        "exact_minors": len(signed),
        "signed_minor_stream_sha256": stream,
        "small_signed_matrices": tested,
        "fallback_cases": len(fallback_cases),
        "controls_rejected": controls,
        "hadamard_bound": 256,
        "prime": 521,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    before = digest_file(PRODUCTION)
    result = run_equivalence()
    require(digest_file(PRODUCTION) == before, "verify must be read-only on production independent.py")
    require(digest_file(BASELINE) == ORIGINAL_SHA256, "verify must be read-only on baseline.py")
    require(len(result["controls_rejected"]) >= 9, "expected rejection controls")
    print(
        "PASS_P112_SIGNED_MODULAR_PRODUCTION "
        f"cases={result['complete_audit']['cases']} "
        f"minors={result['exact_minors']} "
        f"signed_matrices={result['small_signed_matrices']} "
        f"controls={len(result['controls_rejected'])} "
        "no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
