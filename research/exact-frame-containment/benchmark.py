"""Alternating fresh-process measurements of identical complete audit payloads."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import tempfile
import time

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from verify import compare_payload, run_engine
from worker import check_sources


def main():
    if sys.flags.optimize:
        raise SystemExit("Run without -O: inherited circuit assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=9)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.pairs < 1 or args.out.exists():
        parser.error("use at least one pair and a fresh output path")
    check_sources()
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text())
    samples = []
    with tempfile.TemporaryDirectory(prefix="frame containment benchmark ") as temporary:
        for pair in range(args.pairs):
            # Seed 90 is even: reference first, then alternate to reduce order bias.
            order = ("reference", "equations") if (90 + pair) % 2 == 0 else ("equations", "reference")
            for engine in order:
                started = time.perf_counter()
                actual = run_engine(engine, Path(temporary) / f"{pair}-{engine}.json", args.cpu)
                wall = time.perf_counter() - started
                compare_payload(actual, expected)
                samples.append(dict(pair=pair, engine=engine, wall_seconds=wall,
                                    audit_seconds=float(actual["audit_seconds"]),
                                    peak_rss_kib=actual["peak_rss_kib"],
                                    payload_sha256=actual["result_sha256"]))
            print(f"PASS paired full audit {pair + 1}/{args.pairs}", flush=True)
    medians = {engine: statistics.median(s["wall_seconds"] for s in samples if s["engine"] == engine)
               for engine in ("reference", "equations")}
    rss = {engine: statistics.median(s["peak_rss_kib"] for s in samples if s["engine"] == engine)
           for engine in ("reference", "equations")}
    report = dict(status="PASS_EXACT_CONTAINMENT_BENCHMARK", assignment_seed=90,
                  pairs=args.pairs, environment=dict(python=sys.version, platform=platform.platform(),
                                                   pinned_cpu=args.cpu,
                                                   affinity=sorted(os.sched_getaffinity(0))
                                                   if hasattr(os, "sched_getaffinity") else None),
                  median_wall_seconds=medians, baseline_over_candidate=medians["reference"] / medians["equations"],
                  median_peak_rss_kib=rss, samples=samples,
                  input_manifest_sha256=hashlib.sha256((PACKAGE / "SOURCES.json").read_bytes()).hexdigest(),
                  code_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in sorted(PACKAGE.glob("*.py"))},
                  scope="Same source-pinned wrapper and complete h=10/h=12 audits; fresh interpreter per sample. "
                        "Wall time includes wrapper/import/source admission. No OS cache flush, hardware-wide "
                        "speed guarantee, selected-frontier replay, or multiplication runtime claim.")
    with args.out.open("x") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(report["status"], json.dumps(medians), f"ratio={report['baseline_over_candidate']:.4f}")


if __name__ == "__main__":
    main()
