#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production Clifford tables.

Timing is descriptive evidence for RESULT.json. Equivalence is enforced by
verify.py; this script fails only on unequal receipts or subprocess errors.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASELINE = PACKAGE / "baseline.py"
PRODUCTION = (
    ROOT
    / "research/complex-multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py"
)
CHECKER = ROOT / "scripts/verify_cold617_interface.py"
RUNS = [
    ROOT / "research/community-k492-audit/pr622/replay/ck-local",
    ROOT / "research/community-k492-audit/pr622/replay/jp8-local",
]
RECEIPT_SHA256 = "8e775e5927b2f05c1671902680e25995adba6a2d2236f5dc116683b18ac4a42c"


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["MULTICOLD_SOURCE"] = str(ROOT / "research/complex-multicold")
    return env


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise SystemExit(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def run_workload(engine: str, out: Path) -> dict:
    """Swap the live production evaluator for the timed image, then restore it.

    The helper-interface checker hardcodes MULTICOLD_SOURCE to the repository
    multicold tree, so temporary overlay trees are ignored.
    """
    image = BASELINE if engine == "baseline" else PRODUCTION
    original = PRODUCTION.read_bytes()
    PRODUCTION.write_bytes(image.read_bytes())
    try:
        start = time.perf_counter()
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
        elapsed = time.perf_counter() - start
    finally:
        PRODUCTION.write_bytes(original)
    if proc.returncode != 0:
        raise SystemExit(f"{engine} failed\n{proc.stderr}\n{proc.stdout}")
    receipt = out.read_bytes()
    digest = sha256(receipt).hexdigest()
    if digest != RECEIPT_SHA256:
        raise SystemExit(f"{engine} receipt digest {digest} != {RECEIPT_SHA256}")
    return {"elapsed": elapsed, "receipt_sha256": digest, "receipt_bytes": len(receipt)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="write RESULT.json (default prints only; use explicitly to refresh the artifact)",
    )
    parser.add_argument("--out", type=Path, help="optional explicit RESULT.json path")
    args = parser.parse_args(argv)
    if args.rounds < 3:
        raise SystemExit("Use at least three alternating rounds")

    records = []
    with __import__("tempfile").TemporaryDirectory(prefix="clifford-state-bench-") as tmp:
        tmp_path = Path(tmp)
        for pair in range(args.rounds):
            order = ("baseline", "production") if pair % 2 == 0 else ("production", "baseline")
            outputs = {}
            for engine in order:
                row = run_workload(engine, tmp_path / f"{pair}-{engine}.json")
                records.append(
                    {
                        "pair": pair,
                        "engine": engine,
                        "seconds": row["elapsed"],
                        "receipt_sha256": row["receipt_sha256"],
                    }
                )
                outputs[engine] = row["receipt_sha256"]
                print(
                    f"pair={pair} engine={engine} seconds={row['elapsed']:.6f}",
                    flush=True,
                )
            if outputs["baseline"] != outputs["production"]:
                raise SystemExit(f"pair {pair} receipts differ")

    medians = {
        engine: statistics.median(r["seconds"] for r in records if r["engine"] == engine)
        for engine in ("baseline", "production")
    }
    speedup = medians["baseline"] / medians["production"]
    result = {
        "status": "PASS_IDENTICAL_CLIFFORD_STATE_PRODUCTION_RECEIPTS",
        "no_new_kappa": True,
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "fixture": {
            "checker": "scripts/verify_cold617_interface.py",
            "runs": [str(p.relative_to(ROOT)) for p in RUNS],
            "entering": 36,
            "cold": 22,
            "receipt_sha256": RECEIPT_SHA256,
        },
        "production": str(PRODUCTION.relative_to(ROOT)),
        "baseline": str(BASELINE.relative_to(PACKAGE)),
        "rounds": args.rounds,
        "alternating_order": True,
        "medians_seconds": medians,
        "speedup": speedup,
        "samples": records,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "executable": sys.executable,
        },
    }
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(
        f"PASS_IDENTICAL_CLIFFORD_STATE_PRODUCTION_RECEIPTS "
        f"median {medians['baseline']:.6f} -> {medians['production']:.6f} "
        f"({speedup:.3f}×)",
        flush=True,
    )
    if args.write_result or args.out:
        target = args.out or (PACKAGE / "RESULT.json")
        if target.exists() and not args.write_result:
            raise SystemExit(f"refusing to overwrite {target} without --write-result")
        target.write_text(text, encoding="utf-8")
        print(f"wrote {target}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
