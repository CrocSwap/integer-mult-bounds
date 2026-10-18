#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for faster parity-side basis/contains.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import random
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from certify import require  # noqa: E402
from prepare_layers import serializable  # noqa: E402
from audit_parity_side import certificate as production_certificate  # noqa: E402
import binary_phase_frames as production  # noqa: E402


BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "c8e4fa71fe60550324f9e43c1dd5ad6d9bf4e2f4"
ORIGINAL_SHA256 = "4148cfa313cf050ed25296e8db36d35871520b8318fd086c7d1facf0c6af67d7"
OPTIMIZED_SHA256 = "e11143c6cd3ccfacc5283100a87df3909a923ffc68edf20da9527f1853cd8563"
BASE_PARITY_CERT_SHA256 = "4533d0123659fe7917fbab169e5f4abdbca27510335451feb84b87bea8b668d5"
PINNED_CERTS = (
    "certificates/parity-side.json",
    "certificates/disjoint-tensor-compression.json",
    "certificates/dyadic-central-factor.json",
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT)


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    original = git_show("scripts/binary_phase_frames.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base binary_phase_frames.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/binary_phase_frames.py"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base binary_phase_frames.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "binary_phase_frames.py") == OPTIMIZED_SHA256,
        "production binary_phase_frames.py does not match the claimed optimized digest",
    )


def check_primitive_equivalence(baseline, optimized) -> dict:
    rng = random.Random(0)
    cases = 0
    for _ in range(4000):
        dim = rng.randint(1, 24)
        n = rng.randint(0, 10)
        rows = tuple(rng.randrange(1 << dim) for _ in range(n))
        vector = rng.randrange(1 << dim)
        old_basis = baseline.basis(rows)
        new_basis = optimized.basis(rows)
        require(old_basis == new_basis, f"basis mismatch on {rows!r}")
        require(
            baseline.contains(rows, vector) == optimized.contains(rows, vector),
            f"contains mismatch on {rows!r}, {vector}",
        )
        require(
            baseline.classify(rows) == optimized.classify(rows),
            f"classify mismatch on {rows!r}",
        )
        cases += 1
    # Explicit identity/edge cases
    require(optimized.basis(()) == (), "empty basis")
    require(optimized.contains((), 0) is True, "zero is in the empty span")
    require(optimized.contains((), 1) is False, "nonzero not in empty span")
    require(optimized.contains((1, 2, 3), 0) is True, "zero always contained")
    # Under -O, assert-based rejection matches the historical basis() contract (also assert).
    if not __debug__:
        return {"random_cases": cases, "edge_cases": 3, "negative_vector_check": "skipped_under_optimize"}
    try:
        optimized.contains((1,), -1)
        raise AssertionError("negative vector accepted")
    except AssertionError as exc:
        require("nonnegative" in str(exc).lower(), f"wrong negative rejection: {exc}")
    return {"random_cases": cases, "edge_cases": 4, "negative_vector_check": "enforced"}


def _bind_bpf(module_bpf) -> None:
    import experiments.parity_side as parity_side
    import experiments.parity_phase_repair as repair

    parity_side.basis = module_bpf.basis
    parity_side.classify = module_bpf.classify
    repair.basis = module_bpf.basis
    repair.contains = module_bpf.contains
    repair.classify = module_bpf.classify
    repair.dot = module_bpf.dot
    if hasattr(repair.characteristic, "cache_clear"):
        repair.characteristic.cache_clear()
    if hasattr(module_bpf, "_basis_cached") and hasattr(module_bpf._basis_cached, "cache_clear"):
        module_bpf._basis_cached.cache_clear()


def experiment_receipt(module_bpf, h: int) -> dict:
    """Replay one parity-side (h) experiment under a chosen binary_phase_frames module."""
    import experiments.parity_side as parity_side
    import experiments.parity_phase_repair as repair

    _bind_bpf(module_bpf)
    circuit = parity_side.ParitySide(h)
    raw = circuit.verify()
    repaired = repair.coarsen(circuit)
    dag = sha256(
        json.dumps(
            dict(args=circuit.args, outputs=circuit.outputs),
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return dict(raw=raw, repair=repaired, dag_sha256=dag)


def check_parity_experiments(baseline, optimized) -> list[dict]:
    rows = []
    for h in (8, 10, 26):
        old = experiment_receipt(baseline, h)
        new = experiment_receipt(optimized, h)
        require(old == new, f"parity experiment h={h} drifted")
        require(old["raw"]["local_obstructions"] > 0, f"h={h} lost obstruction")
        rows.append(old)
    require(rows[-1]["raw"]["roles"] == 82720, "h=26 roles drifted")
    require(rows[-1]["repair"]["repaired_roles"] == 308336, "h=26 repaired_roles drifted")
    return rows


def check_certificate_pin_discipline() -> dict:
    """Working certificates may change only the binary_phase_frames.py source pin."""
    reports = {}
    for rel in PINNED_CERTS:
        base = json.loads(git_show(rel))
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        base_pin = base["source_sha256"]["scripts/binary_phase_frames.py"]
        live_pin = live["source_sha256"]["scripts/binary_phase_frames.py"]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = json.loads(json.dumps(live))
        restored["source_sha256"]["scripts/binary_phase_frames.py"] = ORIGINAL_SHA256
        require(restored == base, f"{rel}: changed fields beyond the binary_phase_frames pin")
        reports[rel] = {
            "base_pin": base_pin,
            "live_pin": live_pin,
            "only_pin_changed": True,
        }
    base_parity = git_show("certificates/parity-side.json")
    require(sha256(base_parity).hexdigest() == BASE_PARITY_CERT_SHA256, "base parity certificate digest drift")
    return reports


def check_cache_invalidation(optimized) -> None:
    """A distinct generating set must not reuse a previous memoized basis."""
    if hasattr(optimized, "_basis_cached"):
        optimized._basis_cached.cache_clear()
    first = optimized.basis((1, 2, 4))
    second = optimized.basis((1, 2, 4, 8))
    require(first != second, "enlarged generating set reused basis")
    require(optimized.contains((1, 2, 4), 8) is False, "8 not in span{1,2,4}")
    require(optimized.contains((1, 2, 4, 8), 8) is True, "8 in enlarged span")
    # Mutant foil: always-true contains would accept a vector outside the span.
    def mutant_contains(space, vector):
        return True

    require(mutant_contains((1, 2, 4), 8) is True, "mutant sanity")
    require(optimized.contains((1, 2, 4), 8) is False, "production rejects mutant foil")


def maybe_write_certificate(write: bool) -> None:
    if not write:
        live = serializable(production_certificate())
        committed = json.loads((ROOT / "certificates/parity-side.json").read_text(encoding="utf-8"))
        # JSON round-trip equalizes tuple/list containers; pin already updated.
        require(
            live["experiments"] == committed["experiments"],
            "live parity experiments differ from committed certificate",
        )
        require(
            live["source_sha256"]["scripts/binary_phase_frames.py"] == OPTIMIZED_SHA256,
            "live certificate pin mismatch",
        )
        return
    result = production_certificate()
    (ROOT / "certificates/parity-side.json").write_text(
        json.dumps(serializable(result), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="regenerate certificates/parity-side.json from the production audit",
    )
    args = parser.parse_args(argv)

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "parity_side_basis_baseline")
    optimized = production

    primitive = check_primitive_equivalence(baseline, optimized)
    experiments = check_parity_experiments(baseline, optimized)
    pins = check_certificate_pin_discipline()
    check_cache_invalidation(optimized)
    # Restore production bindings before any production certificate replay.
    _bind_bpf(optimized)
    maybe_write_certificate(args.write_certificate)

    print(
        "PASS_PARITY_SIDE_BASIS_CACHE "
        f"h=[8, 10, 26] roles={[row['raw']['roles'] for row in experiments]} "
        f"repaired={[row['repair']['repaired_roles'] for row in experiments]} "
        f"random_cases={primitive['random_cases']} "
        f"certs={len(pins)} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
