#!/usr/bin/env python3
"""Alternating fresh-process before/after timings for production emitted-local rows.

Timing is host-descriptive and is not a correctness gate.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASELINE = PACKAGE / "baseline.py"
PRODUCTION = ROOT / "research/complex-k492-owner-repair/code/hpe_audit_local.py"
ARCHIVE = ROOT / "research/community-frontier1042-audit/selected-replay.tar.gz"
RECEIPT_SHA256 = "13dd18297162569532983db1a2ab67926b064330cd7edd3587e7b546b2dedf17"


def unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise SystemExit(f"duplicate JSON key: {key}")
        out[key] = value
    return out


def materialize(directory: Path) -> None:
    with tarfile.open(ARCHIVE) as archive:
        for name in ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz"):
            members = [m for m in archive.getmembers() if m.name == "slots/local/" + name]
            (directory / name).write_bytes(archive.extractfile(members[0]).read())


def clean_env():
    env = {k: v for k, v in os.environ.items() if k != "PYTHONOPTIMIZE"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_once(engine: str, work: Path) -> dict:
    source = BASELINE if engine == "baseline" else PRODUCTION
    materialize(work)
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-B", str(source), str(work)],
        cwd=work,
        env=clean_env(),
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    if proc.returncode != 0:
        raise SystemExit(f"{engine} failed\n{proc.stderr}\n{proc.stdout}")
    receipt = (work / "INDEPENDENT-LOCAL-REPLAY.json").read_bytes()
    digest = hashlib.sha256(receipt.replace(b"\r\n", b"\n")).hexdigest()
    if digest != RECEIPT_SHA256:
        raise SystemExit(f"{engine} receipt digest {digest} != {RECEIPT_SHA256}")
    json.loads(receipt.decode(), object_pairs_hook=unique_object)
    return {"engine": engine, "seconds": elapsed, "receipt_sha256": digest}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument(
        "--write-result",
        action="store_true",
        help="write RESULT.json (default prints only; use explicitly to refresh the artifact)",
    )
    args = parser.parse_args(argv)
    samples = []
    with tempfile.TemporaryDirectory(prefix="emitted-local-bench-") as tmp:
        for round_index in range(args.rounds):
            order = ("baseline", "production") if round_index % 2 == 0 else ("production", "baseline")
            pair = []
            for engine in order:
                work = Path(tmp) / f"r{round_index}-{engine}"
                work.mkdir()
                pair.append(run_once(engine, work))
            samples.append(pair)

    def median_for(engine: str) -> float:
        values = [sample["seconds"] for pair in samples for sample in pair if sample["engine"] == engine]
        return statistics.median(values)

    baseline_median = median_for("baseline")
    production_median = median_for("production")
    ratio = baseline_median / production_median if production_median else None
    payload = {
        "status": "PASS_IDENTICAL_EMITTED_LOCAL_INTEGER_PRODUCTION_RECEIPTS",
        "python": sys.version,
        "platform": platform.platform(),
        "rounds": args.rounds,
        "receipt_sha256": RECEIPT_SHA256,
        "baseline_median_seconds": baseline_median,
        "production_median_seconds": production_median,
        "median_ratio": ratio,
        "samples": samples,
        "implementation_sha256": {
            "baseline.py": hashlib.sha256(BASELINE.read_bytes()).hexdigest(),
            "production": hashlib.sha256(PRODUCTION.read_bytes()).hexdigest(),
            "benchmark.py": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        },
    }
    text = json.dumps(payload, indent=2) + "\n"
    print(text, end="")
    print(
        f"PASS_IDENTICAL_EMITTED_LOCAL_INTEGER_PRODUCTION_RECEIPTS "
        f"median {baseline_median:.3f}->{production_median:.3f}s "
        f"({ratio:.3f}×)" if ratio else "ratio undefined",
        flush=True,
    )
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
