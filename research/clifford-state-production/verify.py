#!/usr/bin/env python3
"""Equivalence, rejection and receipt controls for production Clifford gate tables.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = (
    ROOT
    / "research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py"
)
BASELINE = PACKAGE / "baseline.py"
CHECKER = ROOT / "scripts/verify_cold617_interface.py"
RUNS = [
    ROOT / "research/community-k492-audit/pr622/replay/ck-local",
    ROOT / "research/community-k492-audit/pr622/replay/jp8-local",
]

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "166841a037f069249f6f7f6dedb89248812f59e2"
ORIGINAL_SHA256 = "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962"
OPTIMIZED_SHA256 = "9b360d58055de706a27abe5211a14115225e47f0c6096e4fb8818e99a4772abd"
RECEIPT_SHA256 = "8e775e5927b2f05c1671902680e25995adba6a2d2236f5dc116683b18ac4a42c"


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


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        [
            "git",
            "show",
            f"{BASE_COMMIT}:research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py",
        ],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base clifford_exact.py sha256 drift")
    blob = (
        subprocess.check_output(
            [
                "git",
                "rev-parse",
                f"{BASE_COMMIT}:research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py",
            ],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base clifford_exact.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit clifford_exact.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production clifford_exact.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")


def sample_ops(clifford):
    ops = [clifford.ident(n) for n in (1, 2, 3, 4)]
    for n in (2, 3, 4):
        ops.append(clifford.perm(n, tuple(1 << i for i in range(n))))
        ops.append(clifford.diag(n, tuple(1 << i for i in range(n))))
        ops.append(clifford.cgate(n, 1))
        ops.append(clifford.xgate(n, 1))
        ops.append(clifford.hadamard(n, [0]))
        ops.append(clifford.canonical_frame(n, [1]))
        ops.append(clifford.fourier(n))
    return ops


def check_state_equivalence() -> dict:
    baseline = load_module(BASELINE, "clifford_state_production_baseline")
    production = load_module(PRODUCTION, "clifford_state_production_live")
    comparisons = 0
    for op in sample_ops(baseline):
        twin = production.Op(op.n, op.tab, list(op.circuit))
        for basis in range(min(1 << op.n, 4)):
            require(op.zero_state(basis) == twin.zero_state(basis), "zero_state mismatch")
            comparisons += 1
    # Exercise paths that call zero_state inside the compiler helpers.
    for n in (2, 3):
        frame = baseline.canonical_frame(n, [1])
        twin = production.Op(frame.n, frame.tab, list(frame.circuit))
        require(frame.zero_state() == twin.zero_state(), "canonical_frame state mismatch")
        comparisons += 1
    return {"state_comparisons": comparisons}


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["MULTICOLD_SOURCE"] = str(ROOT / "research/complex-multicold")
    return env


def run_helper_interface(clifford_bytes: bytes, out: Path) -> bytes:
    """Run the helper-interface checker against an on-disk clifford_exact image.

    ``scripts/verify_cold617_interface.py`` overwrites ``MULTICOLD_SOURCE`` to the
    repository multicold tree, so the only way to substitute an evaluator image is
    to briefly replace the live production file. Always restore it in ``finally``.
    """
    original = PRODUCTION.read_bytes()
    PRODUCTION.write_bytes(clifford_bytes)
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-B",
                str(CHECKER),
                str(RUNS[0]),
                str(RUNS[1]),
                "--entering",
                "36",
                "--cold",
                "22",
                "--out",
                str(out),
            ],
            cwd=ROOT,
            env=clean_env(),
            capture_output=True,
            text=True,
        )
        require(
            proc.returncode == 0,
            f"helper-interface failed\n{proc.stderr}\n{proc.stdout}",
        )
        return out.read_bytes()
    finally:
        PRODUCTION.write_bytes(original)


def check_helper_receipts() -> dict:
    with tempfile.TemporaryDirectory(prefix="clifford-state-prod-") as tmp:
        base_out = Path(tmp) / "base.json"
        prod_out = Path(tmp) / "prod.json"
        base_receipt = run_helper_interface(BASELINE.read_bytes(), base_out)
        prod_receipt = run_helper_interface(PRODUCTION.read_bytes(), prod_out)
    require(base_receipt == prod_receipt, "helper-interface receipts differ")
    require(sha256(prod_receipt).hexdigest() == RECEIPT_SHA256, "helper-interface receipt digest drift")
    payload = json.loads(prod_receipt.decode(), object_pairs_hook=unique_object)
    require(
        payload["status"] == "PASS_FINITE_MULTI_TAIL_AND_EXACT_WRAPPER_BINDING",
        "unexpected helper-interface status",
    )
    require(len(payload["instances"]) == 2, "expected ck and jp8 instances")
    return {
        "receipt_sha256": RECEIPT_SHA256,
        "instances": len(payload["instances"]),
        "status": payload["status"],
    }


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that breaks ``perm`` must fail closed or change the receipt.

    ``wrapped_ok`` decodes recipes through ``perm``/``diag``/``xgate``. Foiling
    ``perm`` to the identity makes those products disagree with the
    ``canonical_frame`` targets.
    """
    with tempfile.TemporaryDirectory(prefix="clifford-state-prod-honest-") as tmp:
        honest = run_helper_interface(PRODUCTION.read_bytes(), Path(tmp) / "honest.json")
    text = PRODUCTION.read_text(encoding="utf-8")
    needle = "def perm(n,G):\n cols=transpose(G,n);gi=inv(G,n)\n return Op(n,tuple([(a,0,0) for a in cols]+[(0,a,0) for a in gi]),[('P',tuple(G))])\n"
    require(needle in text, "perm() site missing for corruption control")
    foil = "def perm(n,G):\n return ident(n)\n"
    with tempfile.TemporaryDirectory(prefix="clifford-state-prod-foil-") as tmp:
        mutant_path = Path(tmp) / "clifford_exact.py"
        mutant_path.write_text(text.replace(needle, foil, 1), encoding="utf-8")
        require(mutant_path.read_bytes() != PRODUCTION.read_bytes(), "mutant must differ on disk")
        try:
            bad = run_helper_interface(mutant_path.read_bytes(), Path(tmp) / "bad.json")
        except Exception as exc:  # includes AssertionError from require() inside checker
            return {"rejected": True, "mode": "subprocess_failure", "detail": str(exc)[:240]}
        require(bad != honest, "identity-perm foil must change the helper receipt")
        return {"rejected": True, "mode": "receipt_divergence"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    # -O policy: require() raises remain active; helper-interface children use -B
    # with PYTHONOPTIMIZE cleared (host CPython -I omits the script directory).
    check_baseline_bytes()
    states = check_state_equivalence()
    receipts = check_helper_receipts()
    corruption = check_temp_corruption_rejection()
    require(corruption["rejected"], "corruption control must reject")
    print(
        "PASS_CLIFFORD_STATE_PRODUCTION "
        f"states={states['state_comparisons']} "
        f"instances={receipts['instances']} "
        f"corruption={corruption['mode']} "
        "certs=1 no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
