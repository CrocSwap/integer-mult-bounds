#!/usr/bin/env python3
"""Equivalence, rejection and receipt controls for production one-basis close.

Read-only by default. Timing is not a pass gate; see benchmark.py / RESULT.json.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = ROOT / "research/bit589-frame-optimum/frameopt.py"
BASELINE = PACKAGE / "baseline.py"
EXPECTED = ROOT / "research/bit-frame-closure-basis/EXPECTED.json"

BASE_COMMIT = "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2"
ORIGINAL_BLOB = "1622844ff90529c47e539f502c92b4f2371524e9"
ORIGINAL_SHA256 = "d18d5ed96a6d3146b2141b9bdd29900dd612defdcd5ebc7040542064ec89f237"
OPTIMIZED_SHA256 = "0cbcda715cfb9f9b17c8e2bd30f90f34fa08e3d467f262e6ba4837b20d17eced"

CASES = {
    "pr589": (
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
        "1733427039589844234749/1000000000000000000000000",
        False,
    ),
    "pr555": (
        "research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz",
        "1733052823330162099157/1000000000000000000000000",
        False,
    ),
    "degraded": (
        "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
        "1733427039589844234749/1000000000000000000000000",
        True,
    ),
}


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


def load_json_unique(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def run_frameopt(script: Path, case: str) -> tuple[dict, str]:
    """Run one checker under assertion-enabled -I -B (never inherit -O)."""
    word, endpoint, degraded = CASES[case]
    cmd = [
        sys.executable,
        "-I",
        "-B",
        str(script),
        str(ROOT / word),
        endpoint,
    ]
    if degraded:
        cmd.append("--degrade")
    env = dict(**{k: v for k, v in __import__("os").environ.items() if k != "PYTHONOPTIMIZE"})
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True)
    require(proc.returncode == 0, f"{script.name} case={case} failed\n{proc.stderr}\n{proc.stdout}")
    text = proc.stdout
    receipt = json.loads(text)
    return receipt, text


def check_baseline_bytes() -> None:
    original = subprocess.check_output(
        ["git", "show", f"{BASE_COMMIT}:research/bit589-frame-optimum/frameopt.py"],
        cwd=ROOT,
    )
    require(sha256(original).hexdigest() == ORIGINAL_SHA256, "base frameopt.py sha256 drift")
    blob = (
        subprocess.check_output(
            ["git", "rev-parse", f"{BASE_COMMIT}:research/bit589-frame-optimum/frameopt.py"],
            cwd=ROOT,
        )
        .decode()
        .strip()
    )
    require(blob == ORIGINAL_BLOB, "base frameopt.py blob drift")
    require(BASELINE.read_bytes() == original, "baseline.py must equal the base-commit frameopt.py")
    require(
        digest_file(PRODUCTION) == OPTIMIZED_SHA256,
        "production frameopt.py does not match the claimed optimized digest",
    )
    require(PRODUCTION.read_bytes() != original, "production must differ from the pairwise baseline")


def check_case_equivalence() -> list[dict]:
    expected = load_json_unique(EXPECTED)
    rows = []
    for case in CASES:
        base_receipt, base_text = run_frameopt(BASELINE, case)
        prod_receipt, prod_text = run_frameopt(PRODUCTION, case)
        require(base_receipt == prod_receipt, f"receipt mismatch case={case}")
        require(
            sha256(base_text.encode()).hexdigest()
            == sha256(prod_text.encode()).hexdigest()
            == expected[case]["stdout_sha256"],
            f"stdout digest mismatch case={case}",
        )
        require(prod_receipt == expected[case]["receipt"], f"EXPECTED receipt mismatch case={case}")
        rows.append(
            {
                "case": case,
                "stdout_sha256": expected[case]["stdout_sha256"],
                "improving_components": prod_receipt["improving_components"],
                "assignments_enumerated": prod_receipt["assignments_enumerated"],
            }
        )
    return rows


def check_temp_corruption_rejection() -> dict:
    """On-disk mutant in a temp copy must fail or diverge from the honest receipt.

    The foil forces `_in_span` to accept every live line. Catalogue frames then
    fail the inherited `close(m)[0] == m` assertion immediately, so the control
    stays bounded (a membership-omission foil can otherwise wander through a
    huge illegal search).
    """
    honest, _ = run_frameopt(PRODUCTION, "pr589")
    with tempfile.TemporaryDirectory(prefix="bit-frame-closure-prod-") as tmp:
        stage = Path(tmp)
        mutant = stage / "frameopt.py"
        text = PRODUCTION.read_text(encoding="utf-8")
        needle = "def _in_span(source, basis):\n    row = [x % P for x in source]\n"
        require(needle in text, "_in_span header missing for corruption control")
        foil = (
            "def _in_span(source, basis):\n"
            "    return True\n"
            "    row = [x % P for x in source]\n"
        )
        mutant.write_text(text.replace(needle, foil, 1), encoding="utf-8")
        require(mutant.read_bytes() != PRODUCTION.read_bytes(), "mutant must differ on disk")
        try:
            bad, _ = run_frameopt(mutant, "pr589")
        except AssertionError as exc:
            return {"rejected": True, "mode": "subprocess_failure", "detail": str(exc)[:240]}
        require(bad != honest, "always-admit mutant must change the pr589 receipt")
        return {
            "rejected": True,
            "mode": "receipt_divergence",
            "honest_improving": honest["improving_components"],
            "mutant_improving": bad["improving_components"],
        }


def check_verify_sh() -> None:
    env = dict(**{k: v for k, v in __import__("os").environ.items() if k != "PYTHONOPTIMIZE"})
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PY"] = sys.executable
    proc = subprocess.run(
        ["bash", str(ROOT / "research/bit589-frame-optimum/verify.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    require(proc.returncode == 0, f"verify.sh failed\n{proc.stderr}\n{proc.stdout}")
    require(proc.stdout.strip().splitlines()[-1] == "PASS_BIT589_FRAME_OPTIMUM", "verify.sh marker")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="unused placeholder; default verify is read-only and never writes certificates",
    )
    args = parser.parse_args(argv)
    require(not args.write_result, "default verify is read-only; do not pass --write-result")

    check_baseline_bytes()
    cases = check_case_equivalence()
    corruption = check_temp_corruption_rejection()
    check_verify_sh()

    print(
        "PASS_BIT_FRAME_CLOSURE_PRODUCTION "
        f"cases={[row['case'] for row in cases]} "
        f"corruption={corruption['mode']} "
        "certs=0 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
