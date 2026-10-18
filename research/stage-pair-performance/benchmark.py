#!/usr/bin/env python3
"""Benchmark the optimized stage-pair audit and check identical receipts.

Runs the complete historical two-invocation frame search in fresh
subprocesses (no certificate file write) and compares the returned
certificate to the committed baseline, allowing only the expected
implementation-source hash change for scripts/audit_stage_pair.py.

Timing is descriptive, not a pass threshold. OS caches are not flushed;
the machine is not an isolated benchmark host. No frontier replay or
multiplication runtime is measured.

Reproduce with standard-library Python 3.11+ from the repository root:

    python3 -B research/stage-pair-performance/benchmark.py --rounds 3

Expected: PASS_IDENTICAL_STAGE_PAIR_RECEIPTS
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE_CERT = "certificates/stage-pair-audit.json"


def run_certificate():
    cmd = [sys.executable, "-B", "-c",
           "import sys; sys.path.insert(0,'scripts');"
           "from audit_stage_pair import certificate;"
           "import json; print(json.dumps(certificate(), default=str))"]
    t0 = time.monotonic()
    out = subprocess.check_output(cmd, cwd=ROOT, text=True)
    dt = time.monotonic() - t0
    return json.loads(out), dt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rounds", type=int, default=3)
    a = ap.parse_args()
    base = json.loads((ROOT / BASE_CERT).read_bytes())
    times = []
    result = None
    for _ in range(a.rounds):
        result, dt = run_certificate()
        times.append(dt)
    assert set(result.keys()) == set(base.keys()), "certificate keys changed"
    for key in result:
        if key == "source_sha256":
            assert result[key].keys() == base[key].keys(), "source list changed"
            for path in result[key]:
                if path == "scripts/audit_stage_pair.py":
                    assert result[key][path] != base[key][path], \
                        "expected changed implementation hash missing"
                else:
                    assert result[key][path] == base[key][path], \
                        "unexpected source change: " + path
            continue
        assert json.dumps(result[key], sort_keys=True, default=str) == \
            json.dumps(base[key], sort_keys=True, default=str), \
            "mathematical content changed: " + key
    assert result["rank_sum"] == 8684, "baseline rank sum changed"
    assert len(result["candidates"]) == 64, "candidate count changed"
    assert len(result["improved_candidates"]) == 6, "improved count changed"
    times.sort()
    median = times[len(times) // 2]
    print(f"PASS_IDENTICAL_STAGE_PAIR_RECEIPTS rounds={a.rounds} "
          f"median_seconds={median:.3f} samples={','.join(f'{t:.2f}' for t in times)}")


if __name__ == "__main__":
    main()
