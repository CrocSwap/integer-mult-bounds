#!/usr/bin/env python3
"""Check the saved eight parabolic certificates without discovery search."""
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
certificate = json.loads((ROOT / "historical/work/p518-next/bit/weighted/rank9/quick.json").read_text())
if sorted(item["node"] for item in certificate["parabolics"]) != list(range(1, 9)):
    raise SystemExit("The certificate must cover each deleted node once.")
shutil.copytree(ROOT / "historical", build)
relative = Path("work/p518-next/bit/weighted/rank9/parabolic")
command = [sys.executable, "-E", "-B", str(build / relative / "independent_check.py")]
print("Run:", " ".join(command), flush=True)
with (build / "check.stdout.log").open("w") as out, (build / "check.stderr.log").open("w") as err:
    subprocess.run(command, check=True, stdout=out, stderr=err)
result = json.loads((build / relative / "INDEPENDENT.json").read_text())
expected = json.loads((ROOT / "historical" / relative / "INDEPENDENT.json").read_text())
if result != expected:
    raise SystemExit("The finite result differs from the saved receipt.")
(build / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print("PASS_E8_HYPERPLANE_MINRANK 240 8 13")
