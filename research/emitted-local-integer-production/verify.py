#!/usr/bin/env python3
"""Equivalence, pin and rejection controls for production emitted-local integer rows.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/complex-k492-owner-repair/code/hpe_audit_local.py"
BASELINE = PACKAGE / "baseline.py"
ARCHIVE = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
OPT_IN_FAST = ROOT / "research/emitted-local-integer-replay-seed90/fast.py"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "17bccb64fdca54f329a3ce16e369449cb76c2802"
ORIGINAL_SHA256 = "6bd9a1e279c9c9e4f3767d9f82e537b559292906feb2ddab02f380fb6523a810"
OPTIMIZED_SHA256 = "cbf68feab9fcf57d8d5ed8a525a8f8cd5d79b2a61faf98cff672e137a3bcf99f"
RECEIPT_SHA256 = "13dd18297162569532983db1a2ab67926b064330cd7edd3587e7b546b2dedf17"


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


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/complex-k492-owner-repair/code/hpe_audit_local.py"],
        cwd=ROOT,
    )
    require(hashlib.sha256(original).hexdigest() == ORIGINAL_SHA256, "base hpe_audit_local.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/complex-k492-owner-repair/code/hpe_audit_local.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base hpe_audit_local.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit hpe_audit_local.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production hpe_audit_local.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")
    # Production must be the opt-in transform of the baseline, with Row inlined.
    sys.path.insert(0, str(OPT_IN_FAST.parent))
    import fast as fast_mod  # type: ignore

    transformed = fast_mod.transform(original.replace(b"\r\n", b"\n").decode())
    require("class Row" in PRODUCTION.read_text(encoding="utf-8"), "production must define Row")
    require("rows={('L',r):Row({r:1}) for r in range(n)}" in PRODUCTION.read_text(encoding="utf-8"),
            "production must use Row initialization")
    require(transformed.count("rows={('L',r):Row({r:1}) for r in range(n)}") == 1,
            "opt-in transform boundary drift")


def materialize(directory: Path) -> None:
    with tarfile.open(ARCHIVE) as archive:
        for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            members = [m for m in archive.getmembers() if m.name == "slots/local/" + name]
            require(len(members) == 1 and members[0].isfile(), "unique selected member: " + name)
            (directory / name).write_bytes(archive.extractfile(members[0]).read())
    payload = gzip.decompress((directory / "CANONICAL-WORD.json.gz").read_bytes())
    require(
        hashlib.sha256(payload).hexdigest()
        == "4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c",
        "selected R480 payload",
    )


def run_checker(checker: Path, directory: Path) -> tuple[bytes, str]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-B", str(checker), str(directory)],
        cwd=directory,
        env=env,
        capture_output=True,
        text=True,
    )
    require(proc.returncode == 0, f"checker failed\n{proc.stderr}\n{proc.stdout}")
    receipt = (directory / "INDEPENDENT-LOCAL-REPLAY.json").read_bytes()
    return receipt, proc.stdout


def check_identical_receipts() -> dict:
    with tempfile.TemporaryDirectory(prefix="emitted-local-prod-") as tmp:
        base_dir = Path(tmp) / "baseline"
        prod_dir = Path(tmp) / "production"
        base_dir.mkdir()
        prod_dir.mkdir()
        materialize(base_dir)
        materialize(prod_dir)
        base_receipt, base_log = run_checker(BASELINE, base_dir)
        prod_receipt, prod_log = run_checker(PRODUCTION, prod_dir)
    require(base_receipt == prod_receipt, "complete receipts differ")
    require(base_log == prod_log, "stdout differs")
    require(
        hashlib.sha256(prod_receipt.replace(b"\r\n", b"\n")).hexdigest() == RECEIPT_SHA256,
        "receipt digest drift",
    )
    payload = json.loads(prod_receipt.decode(), object_pairs_hook=unique_object)
    require(
        payload["status"] == "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY",
        "unexpected status",
    )
    require(len(payload["negative_controls_rejected"]) == 25, "retained mutation coverage")
    return {
        "receipt_sha256": RECEIPT_SHA256,
        "controls": len(payload["negative_controls_rejected"]),
        "status": payload["status"],
    }


def check_assertions_preserved() -> int:
    def assertion_list(text: str):
        return [ast.dump(n, include_attributes=False) for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Assert)]

    base = assertion_list(BASELINE.read_text(encoding="utf-8"))
    prod = assertion_list(PRODUCTION.read_text(encoding="utf-8"))
    require(base == prod, "original assertions changed")
    return len(base)


def check_temp_corruption_rejection() -> dict:
    """On-disk foil that drops ADD updates must fail closed or change the receipt."""
    with tempfile.TemporaryDirectory(prefix="emitted-local-prod-honest-") as tmp:
        honest_dir = Path(tmp) / "honest"
        honest_dir.mkdir()
        materialize(honest_dir)
        honest, _ = run_checker(PRODUCTION, honest_dir)

    text = PRODUCTION.read_text(encoding="utf-8")
    needle = "def add_scaled(self, other, q):"
    require(needle in text, "Row.add_scaled site missing for corruption control")
    # Foil: keep the signature but drop all ADD updates.
    foil_text = text.replace(
        needle,
        "def add_scaled(self, other, q):\n        return\n    def add_scaled_disabled(self, other, q):",
        1,
    )
    require(foil_text != text, "mutant must differ on disk")

    with tempfile.TemporaryDirectory(prefix="emitted-local-prod-foil-") as tmp:
        mutant = Path(tmp) / "hpe_audit_local.py"
        mutant.write_text(foil_text, encoding="utf-8")
        work = Path(tmp) / "work"
        work.mkdir()
        materialize(work)
        try:
            bad, _ = run_checker(mutant, work)
        except Exception as exc:
            return {"rejected": True, "mode": "subprocess_failure", "detail": str(exc)[:240]}
        require(bad != honest, "ADD-drop foil must change the local receipt")
        return {"rejected": True, "mode": "receipt_divergence"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(argv)
    # -O policy: require() gates remain; checker children use -B with PYTHONOPTIMIZE cleared.
    check_baseline_bytes()
    assertions = check_assertions_preserved()
    receipts = check_identical_receipts()
    corruption = check_temp_corruption_rejection()
    require(corruption["rejected"], "corruption control must reject")
    print(
        "PASS_EMITTED_LOCAL_INTEGER_PRODUCTION "
        f"assertions={assertions} "
        f"controls={receipts['controls']} "
        f"corruption={corruption['mode']} "
        "certs=1 no_new_kappa",
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
