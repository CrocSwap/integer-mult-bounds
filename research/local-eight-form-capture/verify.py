#!/usr/bin/env python3
"""Repeat the fixed local capture and its independent scalar checks."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
if not __debug__:
    raise SystemExit("Run this verifier without -O. Historical sources use assert.")
ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--build", type=Path, required=True)
args = parser.parse_args()
build = args.build.resolve()
if build.exists():
    raise SystemExit("The build directory exists.")
for item in json.loads((ROOT / "SOURCE-MANIFEST.json").read_text())["files"]:
    if hashlib.sha256((ROOT / item["package"]).read_bytes()).hexdigest() != item["sha256"]:
        raise SystemExit("Source hash: " + item["package"])
shutil.copytree(ROOT / "historical", build)
pipeline = build / "work/next-track/complex/pipeline"
audit = Path("work/doubling-architecture/rank-independent/live-capture")
def run(name, command):
    print("Run:", " ".join(map(str, command)), flush=True)
    output = build / (name + ".stdout.log")
    with output.open("w") as out, (build / (name + ".stderr.log")).open("w") as err:
        subprocess.run(list(map(str, command)), stdout=out, stderr=err, check=True)
    return output
run("primary", [sys.executable, "-E", "-B", ROOT / "primary.py", "--base", pipeline,
                "--output", build / "primary-result.json"])
dense = run("dense-columns", [sys.executable, "-E", "-B", ROOT / "dense_columns.py", "--base", pipeline])
run("independent", [sys.executable, "-E", "-B", build / audit / "check.py"])
run("endpoint-limits", [sys.executable, "-E", "-B", build / audit / "check_endpoint.py"])
checks = [(build / "primary-result.json", "work/complex-next/structural/hosted-capture-receipt.json"),
          (dense, "work/complex-next/structural/hamming-factor/capture-independent-receipt.json"),
          (build / audit / "RESULT.json", str(audit / "RESULT.json")),
          (build / audit / "ENDPOINT-RESULT.json", str(audit / "ENDPOINT-RESULT.json"))]
results = []
for actual, expected in checks:
    value = json.loads(actual.read_text())
    if value != json.loads((ROOT / "historical" / expected).read_text()):
        raise SystemExit("Historical result differs: " + expected)
    results.append(value)
result = {"status": "PASS_LOCAL_EIGHT_FORM_CAPTURE", "checks": results,
          "source_manifest_sha256": hashlib.sha256((ROOT / "SOURCE-MANIFEST.json").read_bytes()).hexdigest()}
(build / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS_LOCAL_EIGHT_FORM_CAPTURE 800 8 11326")
