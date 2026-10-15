#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for DisjointTensor output supports.

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
from experiments import disjoint_tensor as production  # noqa: E402

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "dd196e67162c349d9b6f7aa27edbed2b1b0b601f"
ORIGINAL_SHA256 = "102dd59bf96033f96ba0dab4c2aba77b3a7a73b67b0f96929ff8b20a98b91cd8"
OPTIMIZED_SHA256 = "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac"
H26_DAG_SHA256 = "5da8011dadf51d6121d343416fa38b6b4bf524fd689e5b1b2def91324660f19b"

PINNED_CERTIFICATES = (
    "certificates/disjoint-tensor-compression.json",
    "certificates/ternary-side.json",
    "certificates/dyadic-central-factor.json",
    "certificates/parity-side.json",
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
    original = git_show("scripts/experiments/disjoint_tensor.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base disjoint_tensor.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/disjoint_tensor.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base disjoint_tensor.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "experiments" / "disjoint_tensor.py") == OPTIMIZED_SHA256,
        "production disjoint_tensor.py does not match the claimed optimized digest",
    )


def historical_expected(inputs, T: int) -> int:
    return sum(1 << i for i, S in enumerate(inputs) if not S & T)


def closed_form_expected(full: int, vertex: list[int], T: int) -> int:
    hit = 0
    bits = T
    while bits:
        bit = bits & -bits
        bits ^= bit
        hit |= vertex[bit.bit_length() - 1]
    return full ^ hit


def build_vertex(inputs, h: int) -> tuple[int, list[int]]:
    full = (1 << len(inputs)) - 1
    vertex = [0] * h
    for i, S in enumerate(inputs):
        bits = S
        while bits:
            bit = bits & -bits
            bits ^= bit
            vertex[bit.bit_length() - 1] |= 1 << i
    return full, vertex


def check_mask_equivalence() -> dict:
    """Closed-form disjoint-output masks must match the historical genexpr."""
    cases = 0
    for h in (8, 10, 12, 14, 16, 18, 20, 22, 26):
        circuit = production.DisjointTensor(h)
        full, vertex = build_vertex(circuit.inputs, circuit.h)
        for T, node in circuit.outputs.items():
            old = historical_expected(circuit.inputs, T)
            new = closed_form_expected(full, vertex, T)
            require(old == new, f"mask mismatch h={h} T={T}")
            require(circuit.support[node] == new, f"live support mismatch h={h} T={T}")
            cases += 1
        # Mutant foil: XOR of per-point masks cancels inputs that meet T twice.
        T = next(iter(circuit.outputs))
        xor_hit = 0
        bits = T
        while bits:
            bit = bits & -bits
            bits ^= bit
            xor_hit ^= vertex[bit.bit_length() - 1]
        mutant = full ^ xor_hit
        correct = closed_form_expected(full, vertex, T)
        require(mutant != correct, f"xor-mutant must differ on h={h}")
    return {"mask_cases": cases, "xor_mutant": "rejected"}


def check_verify_equivalence(baseline, optimized) -> dict:
    records = []
    for h in (8, 10, 12, 16, 20, 26):
        circuit = optimized.DisjointTensor(h)
        old = baseline.DisjointTensor.verify(circuit)
        new = circuit.verify()
        require(old == new, f"verify mismatch on h={h}")
        records.append(
            dict(
                h=h,
                inputs=new["inputs"],
                outputs=new["outputs"],
                additions=new["additions"],
                roles=new["roles"],
                coefficients=new["coefficients"],
                dag_sha256=new["dag_sha256"],
            )
        )
    require(records[-1]["additions"] == 57772, "unexpected h=26 additions")
    require(records[-1]["roles"] == 60372, "unexpected h=26 roles")
    require(records[-1]["dag_sha256"] == H26_DAG_SHA256, "unexpected h=26 dag_sha256")
    return {"verify_cases": len(records), "records": records, "h26_dag_sha256": H26_DAG_SHA256}


def check_support_rejection(baseline, optimized) -> dict:
    circuit = optimized.DisjointTensor(10)
    _target, node = next(iter(circuit.outputs.items()))
    # Flip one expected support bit; both engines must reject.
    circuit.support[node] ^= 1
    with _expect_value_error():
        optimized.DisjointTensor.verify(circuit)
    with _expect_value_error():
        baseline.DisjointTensor.verify(circuit)
    return {"support_rejection": "preserved", "corrupted_h": 10}


class _expect_value_error:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is ValueError, "expected ValueError from corrupted support")
        return True


def check_certificate_pin_discipline() -> dict:
    """Certificates may update disjoint_tensor.py and companion exclusion_circuit.py pins."""
    companion_key = "scripts/exclusion_circuit.py"
    companion_orig = "b253f9d7318becda1c1f3b24e2287ed44a9c27fcea00cf9d531afb950d0457a0"
    companion_opt = "f9fbcd6e85e442cbd0926ac0887414e20735b2dc923d2d5822c803ceb46726d3"
    reports = {}
    for rel in PINNED_CERTIFICATES:
        base = json.loads(git_show(rel).decode())
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        key = "scripts/experiments/disjoint_tensor.py"
        base_pin = base["source_sha256"][key]
        live_pin = live["source_sha256"][key]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = deepcopy(live)
        restored["source_sha256"][key] = ORIGINAL_SHA256
        if companion_key in live["source_sha256"]:
            require(
                live["source_sha256"][companion_key] in {companion_orig, companion_opt},
                f"{rel}: unexpected companion exclusion_circuit pin",
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
    baseline = load_module(PACKAGE / "baseline.py", "disjoint_tensor_support_masks_baseline")
    masks = check_mask_equivalence()
    verifies = check_verify_equivalence(baseline, production)
    rejection = check_support_rejection(baseline, production)
    pins = check_certificate_pin_discipline()
    print(
        "PASS_DISJOINT_TENSOR_SUPPORT_MASKS",
        f"verify_cases={verifies['verify_cases']}",
        f"mask_cases={masks['mask_cases']}",
        f"certs={len(pins)}",
        "no_new_kappa",
    )
    print(
        "controls",
        rejection["support_rejection"],
        f"h26_sha={verifies['h26_dag_sha256'][:16]}",
        flush=True,
    )


if __name__ == "__main__":
    main()
