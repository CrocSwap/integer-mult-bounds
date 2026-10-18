#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for exclusion leave-two-out supports.

Read-only by default. Regenerates no certificate. Timing is not a pass gate;
see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
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
import exclusion_circuit as production  # noqa: E402

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "aaa99986c4b81c5d4fbe016fd216a4818940bb95"
ORIGINAL_SHA256 = "b253f9d7318becda1c1f3b24e2287ed44a9c27fcea00cf9d531afb950d0457a0"
OPTIMIZED_SHA256 = "f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3"

PINNED_CERTIFICATES = (
    "certificates/positive-side-core.json",
    "certificates/dyadic-central-factor.json",
    "certificates/ternary-side.json",
    "certificates/disjoint-tensor-compression.json",
)


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
    original = git_show("scripts/exclusion_circuit.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base exclusion_circuit.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/exclusion_circuit.py"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base exclusion_circuit.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "exclusion_circuit.py") == OPTIMIZED_SHA256,
        "production exclusion_circuit.py does not match the claimed optimized digest",
    )


def historical_expected(inputs, a, b) -> int:
    return sum(1 << i for i, p in enumerate(inputs) if a not in p and b not in p)


def closed_form_expected(full: int, vertex: list[int], a: int, b: int) -> int:
    return full ^ (vertex[a] | vertex[b])


def check_mask_equivalence() -> dict:
    """Closed-form leave-two-out masks must match the historical genexpr."""
    cases = 0
    for n in (4, 6, 8, 12, 16, 24, 32, 45):
        circuit = production.ExclusionCircuit(n)
        full = (1 << len(circuit.inputs)) - 1
        vertex = [0] * circuit.n
        for i, (p, q) in enumerate(circuit.inputs):
            bit = 1 << i
            vertex[p] |= bit
            vertex[q] |= bit
        for (a, b), node in circuit.outputs.items():
            old = historical_expected(circuit.inputs, a, b)
            new = closed_form_expected(full, vertex, a, b)
            require(old == new, f"mask mismatch n={n} exclude=({a},{b})")
            require(circuit.support[node] == new, f"live support mismatch n={n} exclude=({a},{b})")
            cases += 1
        # Mutant foil: XOR without the double-count fix keeps the (a,b) bit.
        a, b = next(iter(circuit.outputs))
        mutant = full ^ vertex[a] ^ vertex[b]
        correct = closed_form_expected(full, vertex, a, b)
        require(mutant != correct, f"xor-mutant must differ on n={n}")
    return {"mask_cases": cases, "xor_mutant": "rejected"}


def check_verify_equivalence(baseline, optimized) -> dict:
    records = []
    for n in (4, 6, 8, 12, 16, 24, 32, 45):
        circuit = optimized.ExclusionCircuit(n)
        old = baseline.ExclusionCircuit.verify(circuit)
        new = circuit.verify()
        require(old == new, f"verify mismatch on n={n}")
        records.append(
            dict(
                n=n,
                inputs=new["inputs"],
                outputs=new["outputs"],
                additions=new["additions"],
                scratch_roles=new["scratch_roles"],
                nonzero_coefficients=new["nonzero_coefficients"],
                circuit_sha256=new["circuit_sha256"],
            )
        )
    require(records[-1]["additions"] == 11566, "unexpected n=45 additions")
    require(records[-1]["outputs"] == 990, "unexpected n=45 outputs")
    exact = "3b1a4d7731db2950040552672fbc56ebd172e36e3412129030ff2aec472d5f6c"
    require(records[-1]["circuit_sha256"] == exact, "unexpected n=45 circuit_sha256")
    return {"verify_cases": len(records), "records": records, "n45_circuit_sha256": exact}


def check_support_rejection(baseline, optimized) -> dict:
    circuit = optimized.ExclusionCircuit(8)
    target, node = next(iter(circuit.outputs.items()))
    # Flip one expected support bit; both engines must reject.
    circuit.support[node] ^= 1
    with _expect_assertion():
        optimized.ExclusionCircuit.verify(circuit)
    with _expect_assertion():
        baseline.ExclusionCircuit.verify(circuit)
    return {"support_rejection": "preserved", "corrupted_output": list(target)}


class _expect_assertion:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is AssertionError, "expected AssertionError from corrupted support")
        return True


def check_certificate_pin_discipline() -> dict:
    """Certificates may update exclusion_circuit.py and companion disjoint_tensor.py pins."""
    companion_key = "scripts/experiments/disjoint_tensor.py"
    companion_orig = "102dd59bf96033f96ba0dab4c2aba77b3a7a73b67b0f96929ff8b20a98b91cd8"
    companion_opt = "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac"
    reports = {}
    for rel in PINNED_CERTIFICATES:
        base = json.loads(git_show(rel).decode())
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        base_pin = base["source_sha256"]["scripts/exclusion_circuit.py"]
        live_pin = live["source_sha256"]["scripts/exclusion_circuit.py"]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = deepcopy(live)
        restored["source_sha256"]["scripts/exclusion_circuit.py"] = ORIGINAL_SHA256
        if companion_key in live["source_sha256"]:
            require(
                live["source_sha256"][companion_key] in {companion_orig, companion_opt},
                f"{rel}: unexpected companion disjoint_tensor pin",
            )
            restored["source_sha256"][companion_key] = companion_orig
        require(restored == base, f"{rel}: changed fields beyond allowed source pins")
        reports[rel] = {
            "base_pin": base_pin,
            "live_pin": live_pin,
            "only_pin_changed": True,
        }
    return reports


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true", help="unused; kept for API parity")
    args = parser.parse_args()
    require(not args.write_certificate, "this package does not rewrite certificate payloads")

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "exclusion_support_masks_baseline")
    masks = check_mask_equivalence()
    verifies = check_verify_equivalence(baseline, production)
    if __debug__:
        rejection = check_support_rejection(baseline, production)
    else:
        # Historical ExclusionCircuit.verify uses assert, stripped under -O.
        rejection = {"support_rejection": "skipped_under_-O"}
    pins = check_certificate_pin_discipline()
    print(
        "PASS_EXCLUSION_SUPPORT_MASKS",
        f"verify_cases={verifies['verify_cases']}",
        f"mask_cases={masks['mask_cases']}",
        f"certs={len(pins)}",
        "no_new_kappa",
    )
    print(
        "controls",
        rejection["support_rejection"],
        f"n45_sha={verifies['n45_circuit_sha256'][:16]}",
        flush=True,
    )


if __name__ == "__main__":
    main()
