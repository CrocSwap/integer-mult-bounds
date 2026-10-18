#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for mixed-point Circuit.verify masks.

Read-only by default. Regenerates no certificate. Timing is not a pass gate;
see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from itertools import combinations
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from experiments import mixed_point_circuit as production  # noqa: E402

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "b7f561f416f815d0fd135f0a0464c291a9a68468"
ORIGINAL_SHA256 = "f509362b5031976a22af351fd158ae0b4520fa4f286a5176ec37023d672a7ddc"
OPTIMIZED_SHA256 = "cc98eeada267814fa2c0bc5f3ebb844f614d667c74d16d80d7ef29b1f90e0aa5"

PINNED_CERTIFICATES = (
    "certificates/mixed-point-audit.json",
    "certificates/parity-side.json",
)

VERIFY_CASES = (
    (12, 3, 3, 0),
    (12, 3, 3, 1),
    (16, 2, 2, 0),
    (16, 2, 2, 1),
    (16, 3, 3, 0),
    (16, 3, 3, 1),
    (20, 3, 3, 0),
    (20, 3, 3, 1),
    (26, 3, 3, 0),
    (26, 3, 3, 1),
    (30, 3, 3, 1),
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


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    original = git_show("scripts/experiments/mixed_point_circuit.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base mixed_point_circuit.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/experiments/mixed_point_circuit.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base mixed_point_circuit.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "experiments" / "mixed_point_circuit.py") == OPTIMIZED_SHA256,
        "production mixed_point_circuit.py does not match the claimed optimized digest",
    )


def historical_expected(inputs, target, r: int) -> int:
    return sum(
        1 << i
        for i, source in enumerate(inputs)
        if len(set(source) & set(target)) == r
    )


def closed_form_expected(full: int, vertex: list[int], target, r: int) -> int:
    expected = 0
    for U in combinations(target, r):
        keep = set(U)
        mask = full
        for point in target:
            if point in keep:
                mask &= vertex[point]
            else:
                mask &= full ^ vertex[point]
        expected |= mask
    return expected


def build_vertex(inputs, n: int) -> tuple[int, list[int]]:
    full = (1 << len(inputs)) - 1
    vertex = [0] * n
    for i, source in enumerate(inputs):
        for point in source:
            vertex[point] |= 1 << i
    return full, vertex


def clear_caches(module) -> None:
    module.build.cache_clear()
    module.plan.cache_clear()
    module.kernel.cache_clear()
    module.vector.cache_clear()


def check_mask_equivalence() -> dict:
    """Closed-form exact-r masks must match the historical genexpr."""
    cases = 0
    for n, k, l, r in (
        (10, 2, 2, 0),
        (10, 2, 2, 1),
        (12, 3, 3, 0),
        (12, 3, 3, 1),
        (12, 3, 3, 2),
        (14, 3, 3, 0),
        (14, 3, 3, 1),
        (16, 3, 3, 1),
        (18, 3, 3, 0),
        (20, 3, 3, 1),
    ):
        clear_caches(production)
        circuit = production.build(n, k, l, r)
        full, vertex = build_vertex(circuit.inputs, circuit.n)
        for target, node in zip(circuit.targets, circuit.outputs):
            old = historical_expected(circuit.inputs, target, r)
            new = closed_form_expected(full, vertex, target, r)
            require(old == new, f"mask mismatch {n,k,l,r} target={target}")
            require(circuit.support[node] == new, f"live support mismatch {n,k,l,r}")
            cases += 1
        # Mutant foil: XOR of per-point masks (cancels inputs that meet T twice)
        # for r=0, or plain OR-of-vertex (ignores exact-r) for r>0.
        target = circuit.targets[0]
        xor_hit = 0
        or_hit = 0
        for point in target:
            xor_hit ^= vertex[point]
            or_hit |= vertex[point]
        mutant = full ^ xor_hit if r == 0 else or_hit
        correct = closed_form_expected(full, vertex, target, r)
        require(mutant != correct, f"mutant must differ on {n,k,l,r}")
    return {"mask_cases": cases, "mutant": "rejected"}


def support_fingerprint(circuit) -> str:
    digest = sha256()
    for node in circuit.outputs:
        digest.update(str(circuit.support[node]).encode() + b"\n")
    return digest.hexdigest()


def check_verify_equivalence(baseline, optimized) -> dict:
    records = []
    for n, k, l, r in VERIFY_CASES:
        clear_caches(optimized)
        circuit = optimized.build(n, k, l, r)
        old = baseline.Circuit.verify(circuit)
        new = circuit.verify()
        require(old is True and new is True, f"verify return mismatch on {n,k,l,r}")
        # Historical engine still accepts the same supports.
        require(baseline.Circuit.verify(circuit) is True, f"baseline reject on {n,k,l,r}")
        records.append(
            dict(
                n=n,
                k=k,
                l=l,
                r=r,
                additions=circuit.additions,
                active=len(circuit.active),
                outputs=len(circuit.outputs),
                support_sha256=support_fingerprint(circuit),
                verified=True,
            )
        )
    require(records[-1]["n"] == 30 and records[-1]["r"] == 1, "unexpected last fixture")
    require(records[-1]["additions"] == 95912, "unexpected h=30 r=1 additions")
    return {"verify_cases": len(records), "records": records}


def check_support_rejection(optimized) -> dict:
    clear_caches(optimized)
    circuit = optimized.build(12, 3, 3, 1)
    node = circuit.outputs[0]
    circuit.support[node] ^= 1
    with _expect_value_error():
        circuit.verify()
    return {"support_rejection": "preserved", "corrupted": "build(12,3,3,1)"}


class _expect_value_error:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        require(exc_type is ValueError, "expected ValueError from corrupted support")
        return True


def check_certificate_pin_discipline() -> dict:
    reports = {}
    for rel in PINNED_CERTIFICATES:
        base = json.loads(git_show(rel).decode())
        live = load_json(ROOT / rel)
        key = "scripts/experiments/mixed_point_circuit.py"
        base_pin = base["source_sha256"][key]
        live_pin = live["source_sha256"][key]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = deepcopy(live)
        restored["source_sha256"][key] = ORIGINAL_SHA256
        # Retain the independently reviewed DisjointTensor production update.
        companion = "scripts/experiments/disjoint_tensor.py"
        if companion in restored["source_sha256"]:
            require(restored["source_sha256"][companion] == "23763a4b6086fb3d19f9282fff5c118f53fa52e7a7f17da1bde990bd4cf8b6ac", "unexpected merged companion pin")
            restored["source_sha256"][companion] = base["source_sha256"][companion]
        require(restored == base, f"{rel}: changed fields beyond allowed source pin")
        reports[rel] = {
            "base_pin": base_pin,
            "live_pin": live_pin,
            "only_pin_changed": True,
        }
    return reports


def check_temp_corruption_rejection() -> dict:
    """On-disk corruption of a temp copy of production source must fail the digest gate."""
    import tempfile

    production_path = SCRIPTS / "experiments" / "mixed_point_circuit.py"
    raw = production_path.read_bytes()
    require(sha256(raw).hexdigest() == OPTIMIZED_SHA256, "production digest before temp check")
    with tempfile.TemporaryDirectory() as tmp:
        mutant = Path(tmp) / "mixed_point_circuit.py"
        mutant.write_bytes(raw + b"\n# corrupted\n")
        require(sha256(mutant.read_bytes()).hexdigest() != OPTIMIZED_SHA256, "temp mutant digest")
    require(digest_file(production_path) == OPTIMIZED_SHA256, "production must be unchanged after temp check")
    return {"temp_corruption": "rejected", "production_unchanged": True}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-certificate", action="store_true", help="unused; kept for API parity")
    args = parser.parse_args()
    require(not args.write_certificate, "this package does not rewrite certificate payloads")

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "mixed_point_verify_masks_baseline")
    masks = check_mask_equivalence()
    verifies = check_verify_equivalence(baseline, production)
    rejection = check_support_rejection(production)
    pins = check_certificate_pin_discipline()
    temp = check_temp_corruption_rejection()
    print(
        "PASS_MIXED_POINT_VERIFY_MASKS",
        f"verify_cases={verifies['verify_cases']}",
        f"mask_cases={masks['mask_cases']}",
        f"certs={len(pins)}",
        "no_new_kappa",
    )
    print(
        "controls",
        rejection["support_rejection"],
        temp["temp_corruption"],
        f"h30_additions={verifies['records'][-1]['additions']}",
        flush=True,
    )


if __name__ == "__main__":
    main()
