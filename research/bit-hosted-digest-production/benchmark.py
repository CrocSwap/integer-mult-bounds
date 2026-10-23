#!/usr/bin/env python3
"""Alternating fresh-process hosted-audit timings for production digest.

Timing is host-descriptive and is not a correctness gate.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PRODUCTION = (
    ROOT
    / "research/e8-bit-p111-tuned/vendor/pr510/e8-r480-nine-stage"
    / "vendor/e8-r715-eleven-stage-whole/code/audit_hosted_k.py"
)
FIXTURE = ROOT / "research/community-hyperplane599-audit/pr589/bit589"
EMITTED = "96c7ad2e744e9a503a4ef5ecd52d0f6a8899bdb5efac2e3aafa0db18adf99523"

WORKER = r'''
import contextlib, gzip, hashlib, io, json, sys, time, types, ast
from pathlib import Path

ROOT = Path(sys.argv[1])
SOURCE = Path(sys.argv[2])
PARENT = Path(sys.argv[3])
HOSTED = Path(sys.argv[4])
OUT = Path(sys.argv[5])
PARAMETERIZER = ROOT / "research/e8-bit-p111-tuned/code/adapt9p.py"

def load_parameterized(source_path):
    original = source_path.read_text(encoding="utf-8")
    adapter = PARAMETERIZER.read_text(encoding="utf-8")
    assignments = [n for n in ast.parse(adapter).body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == "EDITS" for t in n.targets)]
    edits_dict = assignments[0].value
    entries = [v for k, v in zip(edits_dict.keys, edits_dict.values)
               if ast.literal_eval(k) == "audit_hosted_k.py"]
    edits = ast.literal_eval(entries[0].elts[1])
    for old, new in edits:
        assert original.count(old) == 1
        original = original.replace(old, new)
    module = types.ModuleType("auditor")
    module.__file__ = str(source_path)
    exec(compile(original, module.__file__, "exec"), module.__dict__)
    return module

auditor = load_parameterized(SOURCE)
argv = sys.argv
sys.argv = [auditor.__file__, str(PARENT), str(HOSTED), str(OUT)]
start = time.perf_counter()
with contextlib.redirect_stdout(io.StringIO()):
    auditor.main()
elapsed = time.perf_counter() - start
sys.argv = argv
receipt = json.loads(OUT.read_text(encoding="utf-8"))
assert receipt["emitted_program_sha256"] == %r
print(json.dumps({"seconds": elapsed, "digest": receipt["emitted_program_sha256"],
                  "events": receipt["emitted_events"],
                  "mutations": len(receipt["mutations_rejected"])}))
''' % EMITTED


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run_once(engine: str, parent: Path, out: Path) -> dict:
    source = PACKAGE / "baseline.py" if engine == "baseline" else PRODUCTION
    cmd = [
        sys.executable,
        "-I",
        "-B",
        "-c",
        WORKER,
        str(ROOT),
        str(source),
        str(parent),
        str(FIXTURE / "v9/hosted"),
        str(out),
    ]
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    # Optional single-CPU pin when taskset exists.
    wrapper = []
    if Path("/usr/bin/taskset").exists():
        wrapper = ["taskset", "-c", "0"]
    start = time.perf_counter()
    proc = subprocess.run(wrapper + cmd, cwd=ROOT, capture_output=True, text=True, env=env, check=False)
    wall = time.perf_counter() - start
    require(proc.returncode == 0, f"{engine} failed: {proc.stdout}\n{proc.stderr}")
    payload = json.loads(proc.stdout.strip().splitlines()[-1])
    payload["process_wall_seconds"] = wall
    payload["engine"] = engine
    return payload


def prepare_parent(work: Path) -> Path:
    import shutil

    parent = work / "parent"
    shutil.copytree(
        FIXTURE / "v9/nine",
        parent / "nine",
        ignore=shutil.ignore_patterns("AUDIT.json", "GEOMETRY.json"),
    )
    shutil.copytree(FIXTURE / "records", parent / "records")
    return parent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rounds", type=int, default=5)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args(argv)
    require(args.rounds > 0, "rounds must be positive")

    samples = []
    with tempfile.TemporaryDirectory(prefix="bit-hosted-digest-bench-") as tmp:
        work = Path(tmp)
        parent = prepare_parent(work)
        order = []
        for round_index in range(args.rounds):
            # Alternate starting engine each round.
            engines = ("baseline", "production") if round_index % 2 == 0 else ("production", "baseline")
            order.append(list(engines))
            for engine in engines:
                out = work / f"{round_index}-{engine}.json"
                sample = run_once(engine, parent, out)
                sample["round"] = round_index
                samples.append(sample)
                print(
                    f"round={round_index} engine={engine} "
                    f"audit={sample['seconds']:.6f}s wall={sample['process_wall_seconds']:.6f}s",
                    flush=True,
                )

    by_engine = {
        "baseline": [s["seconds"] for s in samples if s["engine"] == "baseline"],
        "production": [s["seconds"] for s in samples if s["engine"] == "production"],
    }
    med_base = statistics.median(by_engine["baseline"])
    med_prod = statistics.median(by_engine["production"])
    speedup = med_base / med_prod
    for sample in samples:
        require(sample["digest"] == EMITTED, "timed receipt digest drifted")
        require(sample["events"] == 7843392, "timed receipt events drifted")
        require(sample["mutations"] == 16, "timed receipt mutations drifted")

    result = {
        "status": "PASS_IDENTICAL_BIT_HOSTED_DIGEST_PRODUCTION_RECEIPTS",
        "base_commit": "0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "executable": sys.executable,
        "rounds": args.rounds,
        "alternating_order": order,
        "median_audit_seconds": {"baseline": med_base, "production": med_prod},
        "median_speedup": speedup,
        "emitted_program_sha256": EMITTED,
        "emitted_events": 7843392,
        "samples": samples,
        "scope": "complete parameterized PR589 hosted audit including 16 mutants; no new kappa",
        "measurement_note": "Host-descriptive paired medians; not a correctness gate or cold-replay claim.",
    }
    text = json.dumps(result, indent=2) + "\n"
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(text, encoding="utf-8")
    print(text)
    print(
        f"PASS_IDENTICAL_BIT_HOSTED_DIGEST_PRODUCTION_RECEIPTS "
        f"median {med_base:.6f} → {med_prod:.6f} s ({speedup:.3f}×)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
