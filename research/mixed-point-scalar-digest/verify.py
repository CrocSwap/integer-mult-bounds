#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for mixed-point scalar digests.

Read-only by default. Regenerates no certificate. Timing is not a pass gate;
see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
import audit_mixed_point as production  # noqa: E402
from experiments.mixed_point_circuit import build, factored_transpose  # noqa: E402

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "0c9e11b9f5d7fae9b5e5a312eca3f246b7aa7d3c"
ORIGINAL_SHA256 = "2eead5d410d1c96f1a7ef47c9c35d16ca6bb6d9c2a6a8d24273290add842214d"
OPTIMIZED_SHA256 = "fc7ca3e07d8a3ad54e894c387a89b310ae0b7048763cd48bb27f5daeb0d73dba"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT)


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    original = git_show("scripts/audit_mixed_point.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base audit_mixed_point.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/audit_mixed_point.py"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base audit_mixed_point.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "audit_mixed_point.py") == OPTIMIZED_SHA256,
        "production audit_mixed_point.py does not match the claimed optimized digest",
    )


def check_encoding_foil() -> dict:
    """Hand-rolled lines must match json.dumps text, and a mutant must differ."""
    samples = [
        (0, None),
        (1, (2, 3)),
        (999999, (0, 1)),
        (42, None),
        (7, (100, 200)),
    ]
    for node, edge in samples:
        old = json.dumps((node, edge), separators=(",", ":")) + "\n"
        if edge is None:
            new = f"[{node},null]\n"
        else:
            new = f"[{node},[{edge[0]},{edge[1]}]]\n"
        require(old == new, f"encoding mismatch for {(node, edge)}")
    # Mutant foil: Python's historical None spelling is lowercase null.
    bad = "[0,None]\n"
    good = json.dumps((0, None), separators=(",", ":")) + "\n"
    require(bad != good, "mutant None spelling must differ from json null")
    return {"encoding_cases": len(samples), "none_mutant": "rejected"}


def check_scalar_equivalence(baseline, optimized) -> dict:
    build.cache_clear()
    records = []
    # Mixed-point certificate shapes: block-only / hybrid full size, then four
    # factored rounds starting from the default hybrid build.
    for common, label in ((False, "block_only"), (True, "hybrid")):
        c = build(50, 3, 3, 1, common=common)
        old = baseline.scalar_check(c)
        new = optimized.scalar_check(c)
        require(old == new, f"scalar_check mismatch on {label}")
        records.append(
            dict(label=label, roles=new["roles"], circuit_sha256=new["circuit_sha256"])
        )
        build.cache_clear()
        del c
    c = build(50, 3, 3, 1)
    build.cache_clear()
    for step in range(1, 5):
        c, stats = factored_transpose(c)
        old = baseline.scalar_check(c)
        new = optimized.scalar_check(c)
        require(old == new, f"scalar_check mismatch on factored step {step}")
        records.append(
            dict(
                label=f"factored_{step}",
                roles=new["roles"],
                circuit_sha256=new["circuit_sha256"],
                factoring=stats,
            )
        )
    require(records[-1]["roles"] == 447488, "unexpected factored role count")
    # Early-sharing full-size baseline circuit uses the same scalar_check.
    from experiments.mixed_point_circuit import build as mpc_build

    early = mpc_build(50, 3, 3, 1)
    old = baseline.scalar_check(early)
    new = optimized.scalar_check(early)
    require(old == new, "early-sharing full-size scalar_check mismatch")
    require(new["roles"] == 509194, "unexpected early-sharing hybrid roles")
    records.append(dict(label="early_hybrid", roles=new["roles"], circuit_sha256=new["circuit_sha256"]))
    return {"scalar_cases": len(records), "records": records}


def check_certificate_payloads(optimized) -> dict:
    mixed = serializable(optimized.certificate())
    committed = json.loads((ROOT / "certificates/mixed-point-audit.json").read_text())
    for key in (
        "decision",
        "full_size_decompositions",
        "factored_transposition_rounds",
        "small_frame_controls",
        "enclosure_obstruction",
        "optimistic_score",
        "role_reduction",
        "target",
        "status",
    ):
        require(mixed[key] == committed[key], f"mixed-point payload drift on {key}")
    # audit_mixed_point.py is not among the certificate's source_sha256 pins.
    require(
        "scripts/audit_mixed_point.py" not in committed["source_sha256"],
        "unexpected pin of audit_mixed_point.py",
    )

    import audit_early_sharing as early_mod

    early = serializable(early_mod.certificate())
    early_committed = json.loads((ROOT / "certificates/early-sharing-audit.json").read_text())
    for key in ("decision", "full_size", "small_trials", "status"):
        require(early[key] == early_committed[key], f"early-sharing payload drift on {key}")
    return {
        "mixed_point_payload": "identical",
        "early_sharing_payload": "identical",
        "audit_mixed_point_pinned": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true", help="unused; kept for API parity")
    args = parser.parse_args()
    require(not args.write_certificate, "this package does not rewrite certificates")

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "mixed_point_scalar_baseline")
    encoding = check_encoding_foil()
    scalars = check_scalar_equivalence(baseline, production)
    payloads = check_certificate_payloads(production)
    print(
        "PASS_MIXED_POINT_SCALAR_DIGEST",
        f"scalar_cases={scalars['scalar_cases']}",
        f"encoding_cases={encoding['encoding_cases']}",
        "certs=0",
        "no_new_kappa",
    )
    print(
        "payloads",
        payloads["mixed_point_payload"],
        payloads["early_sharing_payload"],
        flush=True,
    )


if __name__ == "__main__":
    main()
