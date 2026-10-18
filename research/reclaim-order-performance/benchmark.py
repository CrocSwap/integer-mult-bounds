#!/usr/bin/env python3
"""Compare complete compilation with the pinned reference on the same inputs.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COMPILER = "scripts/experiments/joint_dual_reclaim_compiler.py"
WRAPPER = "scripts/experiments/joint_dual_compiler.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", type=int, default=3)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not sys.flags.optimize, "Run with assertions enabled")
    require(args.pairs >= 1, "Need at least one pair")
    require(not args.out.exists(), "Output already exists")
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for name, digest in pins["files"].items():
        require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest,
                "Source changed: " + name)
    require(hashlib.sha256((HERE / "reference.py").read_bytes()).hexdigest()
            == pins["reference_sha256"], "Reference changed")
    runs = []
    with tempfile.TemporaryDirectory(prefix="reclaim-order-") as temporary:
        work = Path(temporary)
        for variant in ("reference", "filtered"):
            checkout = work / variant
            (checkout / "scripts/experiments").mkdir(parents=True)
            shutil.copyfile(ROOT / WRAPPER, checkout / WRAPPER)
            source = HERE / "reference.py" if variant == "reference" else ROOT / COMPILER
            shutil.copyfile(source, checkout / COMPILER)
            for prior in (48, 55):
                relative = Path("references/frame-compiler") / ("pr" + str(prior))
                shutil.copytree(ROOT / relative, checkout / relative)
        for pair in range(args.pairs):
            order = ("reference", "filtered") if pair % 2 == 0 else ("filtered", "reference")
            for h in (23, 25):
                outputs = {}
                for variant in order:
                    tag = "%s-%d-%d" % (variant, pair, h)
                    receipt, word, log = [work / (tag + suffix) for suffix in (".json", ".json.gz", ".log")]
                    command = [sys.executable, "-B", WRAPPER, "--h", str(h),
                               "--output", str(receipt), "--word", str(word)]
                    start = time.perf_counter()
                    with log.open("w") as stream:
                        result = subprocess.run(command, cwd=work / variant, stdout=stream,
                                                stderr=subprocess.STDOUT)
                    seconds = time.perf_counter() - start
                    require(result.returncode == 0, tag + " failed:\n" + log.read_text()[-4000:])
                    raw = gzip.decompress(word.read_bytes())
                    outputs[variant] = (raw, json.loads(receipt.read_text()))
                    expected = gzip.decompress((ROOT / ("certificates/joint-dual-word-%d.json.gz" % h)).read_bytes())
                    require(raw == expected, tag + " differs from the accepted physical word")
                    recorded = json.loads((ROOT / "certificates/joint-dual-compiler.json").read_text())
                    require(json.dumps(outputs[variant][1], sort_keys=True)
                            == json.dumps(recorded["axes"][str(h)]["compiled"], sort_keys=True),
                            tag + " differs from the accepted compiler receipt")
                    run = dict(pair=pair, variant=variant, h=h, seconds=seconds,
                               word_sha256=hashlib.sha256(raw).hexdigest(),
                               receipt_sha256=hashlib.sha256(receipt.read_bytes()).hexdigest())
                    runs.append(run)
                    print(json.dumps(run), flush=True)
                require(outputs["reference"] == outputs["filtered"], "Before/after output differs")
    summary = {}
    for h in (23, 25):
        medians = {variant: statistics.median(r["seconds"] for r in runs
                                            if r["h"] == h and r["variant"] == variant)
                   for variant in ("reference", "filtered")}
        summary[str(h)] = dict(medians, speedup=medians["reference"] / medians["filtered"])
    result = dict(status="PASS_IDENTICAL_RECLAIM_WORDS_AND_RECEIPTS", pairs=args.pairs,
                  platform=platform.platform(), python=sys.version, runs=runs, summary=summary,
                  source_manifest_sha256=hashlib.sha256((HERE / "SOURCES.json").read_bytes()).hexdigest(),
                  scope="Complete scalar compilation and both dirty orientations; not the full repository suite.")
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
