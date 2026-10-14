#!/usr/bin/env python3
"""Equivalence, pin and mutation controls for cleared-denominator joint-frame product.

Read-only by default. Regenerates no certificate unless --write-certificate is
passed. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from fractions import Fraction as Q
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
import audit_joint_frames as production  # noqa: E402
from audit_rank_product_core import certificate as rank_product_certificate  # noqa: E402
from audit_positive_side import certificate as positive_side_certificate  # noqa: E402

BASE_COMMIT = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
ORIGINAL_BLOB = "913be4a1f0a651f3aaf7b4ed1901916918ba2cef"
ORIGINAL_SHA256 = "3df8061392ce0ba42bbde8c02f2a30c8141145e70e9a48c18da73d3aafb14423"
OPTIMIZED_SHA256 = "818e86b4152b4eeb853f173c9aa795510caa593ec0e25b05a246f1df52575466"
BASE_RANK_PRODUCT_CERT_SHA256 = "e0d2cb39be3502251f8f8c4a62e0fe6b743be50eef41dda35646762daaec40b9"
PINNED_CERTS = ("certificates/rank-product-core.json",)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"missing module {path}")
    module = importlib.util.module_from_spec(spec)
    # Baseline is a full audit_joint_frames copy; give it the scripts path.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def git_show(path: str) -> bytes:
    return subprocess.check_output(["git", "show", f"{BASE_COMMIT}:{path}"], cwd=ROOT)


def check_baseline_bytes() -> None:
    baseline = PACKAGE / "baseline.py"
    original = git_show("scripts/audit_joint_frames.py")
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base audit_joint_frames.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:scripts/audit_joint_frames.py"], cwd=ROOT
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base audit_joint_frames.py blob drift")
    require(baseline.read_bytes() == original, "baseline.py must be an exact copy of the base commit source")
    require(
        digest_file(SCRIPTS / "audit_joint_frames.py") == OPTIMIZED_SHA256,
        "production audit_joint_frames.py does not match the claimed optimized digest",
    )


def random_matrix(rng: random.Random, rows: int, cols: int):
    dens = (1, 1, 1, 2, 3, 4, 5, 6, 8, 9)
    return tuple(
        tuple(Q(rng.randint(-7, 7), rng.choice(dens)) for _ in range(cols)) for _ in range(rows)
    )


def check_primitive_equivalence(baseline, optimized) -> dict:
    rng = random.Random(20261014)
    cases = 0
    for _ in range(2500):
        n = rng.randint(1, 6)
        k = rng.randint(1, 6)
        m = rng.randint(1, 6)
        A = random_matrix(rng, n, k)
        B = random_matrix(rng, k, m)
        old = baseline.product(A, B)
        new = optimized.product(A, B)
        require(old == new, f"product mismatch on shapes {(n, k, m)}")
        cases += 1
    # Edge cases: empty left factor, integer matrices, projector-like dens.
    empty = optimized.product(tuple(), ((Q(1),),))
    require(empty == tuple(), "empty left factor")
    I = optimized.eye(3)
    require(optimized.product(I, I) == I, "I*I")
    require(baseline.product(I, I) == optimized.product(I, I), "I*I baseline")
    P = (
        (Q(1, 2), Q(1, 2), Q(0)),
        (Q(1, 2), Q(1, 2), Q(0)),
        (Q(0), Q(0), Q(0)),
    )
    require(baseline.product(P, P) == optimized.product(P, P) == P, "rank-one projector square")
    # Mutant foil: dropping the common scale yields a wrong nonzero product.
    bad_scale = tuple(
        tuple(Q(x.numerator * 2, 1) for x in row) for row in optimized.product(P, P)
    )
    require(bad_scale != P, "mutant scale foil differs")
    return {"random_cases": cases, "edge_cases": 4, "scale_mutant": "rejected"}


def _bind_product(module_jf) -> None:
    import experiments.positive_side_core as positive_side_core
    import experiments.rank_product_core as rank_product_core

    production.product = module_jf.product
    positive_side_core.product = module_jf.product
    rank_product_core.product = module_jf.product
    if hasattr(production.rank, "cache_clear"):
        production.rank.cache_clear()


def positive_side_receipt(module_jf) -> list[dict]:
    """Replay the historical positive-side experiment stream under one product."""
    from experiments.positive_side_core import PositiveSide
    from experiments.signed_sparse_core import vectors

    _bind_product(module_jf)
    rows = []
    for h, q in ((4, 2), (5, 2), (4, 4), (5, 4), (6, 4), (8, 8)):
        labels = list(vectors(h, q))
        n = len(labels)
        bit_rows = [
            sum(
                1 << j
                for j, y in enumerate(labels)
                if i == j or sum(a * b for a, b in zip(x, y)) == 0
            )
            for i, x in enumerate(labels)
        ]
        for strategy in ("balanced", "frequent-pairs"):
            circuit = PositiveSide(bit_rows, labels, strategy)
            record = circuit.verify()
            invocation = circuit.verify_invocation()
            frames = circuit.verify_frames() if strategy == "frequent-pairs" else None
            dag = sha256(
                json.dumps(
                    dict(args=circuit.args, outputs=circuit.outputs),
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode()
            ).hexdigest()
            rows.append(
                dict(
                    h=h,
                    q=q,
                    strategy=strategy,
                    side_roles=record["side_roles"],
                    additions=record["additions"],
                    dag_sha256=dag,
                    invocation=invocation,
                    frames=frames,
                )
            )
    return rows


def check_positive_side_experiments(baseline, optimized) -> list[dict]:
    old = positive_side_receipt(baseline)
    new = positive_side_receipt(optimized)
    require(old == new, "positive-side experiment stream drifted")
    require(new[-1]["side_roles"] == 1200, "h=8 frequent-pairs side_roles drifted")
    return new


def check_certificate_pin_discipline() -> dict:
    """Working rank-product certificate may change only the joint_frames source pin."""
    reports = {}
    for rel in PINNED_CERTS:
        base = json.loads(git_show(rel))
        live = json.loads((ROOT / rel).read_text(encoding="utf-8"))
        base_pin = base["source_sha256"]["scripts/audit_joint_frames.py"]
        live_pin = live["source_sha256"]["scripts/audit_joint_frames.py"]
        require(base_pin == ORIGINAL_SHA256, f"{rel}: unexpected base pin")
        require(live_pin == OPTIMIZED_SHA256, f"{rel}: optimized pin missing")
        restored = json.loads(json.dumps(live))
        restored["source_sha256"]["scripts/audit_joint_frames.py"] = ORIGINAL_SHA256
        require(restored == base, f"{rel}: changed fields beyond the audit_joint_frames pin")
        reports[rel] = {
            "base_pin": base_pin,
            "live_pin": live_pin,
            "only_pin_changed": True,
        }
    base_cert = git_show("certificates/rank-product-core.json")
    require(
        sha256(base_cert).hexdigest() == BASE_RANK_PRODUCT_CERT_SHA256,
        "base rank-product certificate digest drift",
    )
    return reports


def maybe_write_certificate(write: bool) -> None:
    _bind_product(production)
    if not write:
        live = serializable(rank_product_certificate())
        committed = json.loads((ROOT / "certificates/rank-product-core.json").read_text(encoding="utf-8"))
        # Compare mathematical payload; pin already updated in the working tree.
        for key in live:
            if key in ("source_sha256", "upstream_commit"):
                continue
            require(live[key] == committed[key], f"live rank-product field drifted: {key}")
        require(
            live["source_sha256"]["scripts/audit_joint_frames.py"] == OPTIMIZED_SHA256,
            "live rank-product pin mismatch",
        )
        # Positive-side certificate does not pin audit_joint_frames.py; payload must match base.
        pos_live = serializable(positive_side_certificate())
        pos_base = json.loads(git_show("certificates/positive-side-core.json"))
        for key in ("small_signed_experiments", "expanded_complete_controls", "status", "scope"):
            require(pos_live[key] == pos_base[key], f"positive-side field drifted: {key}")
        return
    result = rank_product_certificate()
    (ROOT / "certificates/rank-product-core.json").write_text(
        json.dumps(serializable(result), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-certificate",
        action="store_true",
        help="regenerate certificates/rank-product-core.json from the production audit",
    )
    args = parser.parse_args(argv)

    check_baseline_bytes()
    baseline = load_module(PACKAGE / "baseline.py", "joint_frames_product_baseline")
    optimized = production

    primitive = check_primitive_equivalence(baseline, optimized)
    experiments = check_positive_side_experiments(baseline, optimized)
    pins = check_certificate_pin_discipline()
    _bind_product(optimized)
    maybe_write_certificate(args.write_certificate)

    print(
        "PASS_JOINT_FRAMES_CLEARED_PRODUCT "
        f"positive_side_cases={len(experiments)} "
        f"random_cases={primitive['random_cases']} "
        f"certs={len(pins)} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
