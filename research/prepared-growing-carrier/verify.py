#!/usr/bin/env python3
"""Repeat the saved construction and independent finite check."""
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


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    build = args.build.resolve()
    require(not build.exists(), "The build directory exists.")
    manifest = json.loads((ROOT / "SOURCE-MANIFEST.json").read_text())
    for item in manifest["files"]:
        require(hashlib.sha256((ROOT / item["package"]).read_bytes()).hexdigest()
                == item["sha256"], "Source hash: " + item["package"])
    shutil.copytree(ROOT / "historical", build)
    primary = build / "work/p518-next/complex/paired-five"
    independent = build / "work/autonomous-kappa-run/growing-cycle-independent"
    clifford = build / "work/p518-next/source/research/nodal-pair-async/inputs/work/odd-stages/clifford_exact.py"
    stages = []
    def run(name, command):
        print("Run:", " ".join(map(str, command)), flush=True)
        with (build / (name + ".stdout.log")).open("w") as out, (build / (name + ".stderr.log")).open("w") as err:
            subprocess.run(list(map(str, command)), stdout=out, stderr=err, check=True)
        stages.append(name)
    run("construct", [sys.executable, "-E", "-B", primary / "growing_cycle.py"])
    run("exits", [sys.executable, "-E", "-B", primary / "add_growing_exits.py"])
    for name in ["GROWING-CYCLE-WORD.json", "GROWING-CYCLE-RESULT.json",
                 "GROWING-CYCLE-LEGACY-EXITS-WORD.json", "GROWING-CYCLE-LEGACY-EXITS-RESULT.json"]:
        frozen = ROOT / "historical/work/p518-next/complex/paired-five" / name
        require((primary / name).read_bytes() == frozen.read_bytes(), "Saved construction: " + name)
    result_path = build / "independent-result.json"
    run("independent", [sys.executable, "-E", "-B", ROOT / "replay.py", "--word",
                        primary / "GROWING-CYCLE-WORD.json", "--clifford", clifford,
                        "--output", result_path])
    actual = json.loads(result_path.read_text())
    expected = json.loads((independent / "RESULT.json").read_text())
    for value in [actual, expected]:
        value.pop("checker_sha256")
    require(actual == expected, "Historical independent result")
    result = {"status": "PASS_PREPARED_GROWING_CARRIER", "stages": stages,
              "independent": actual,
              "source_manifest_sha256": hashlib.sha256((ROOT / "SOURCE-MANIFEST.json").read_bytes()).hexdigest(),
              "portable_checker_sha256": hashlib.sha256((ROOT / "replay.py").read_bytes()).hexdigest(),
              "legacy_exits": json.loads((primary / "GROWING-CYCLE-LEGACY-EXITS-RESULT.json").read_text())}
    (build / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS_PREPARED_GROWING_CARRIER 704 55 8")


if __name__ == "__main__":
    main()
