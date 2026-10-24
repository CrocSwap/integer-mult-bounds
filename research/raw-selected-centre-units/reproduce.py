#!/usr/bin/env python3
"""Replay the frozen selected-centre unit checks in a new directory."""

from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import time


HERE = Path(__file__).resolve().parent
CAMPAIGN = Path("work/centre-encoding-campaign-20261014")
MANIFEST = HERE / "SOURCE-MANIFEST.json"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def check_inputs():
    files = read(MANIFEST)["files"]
    for name, item in files.items():
        raw = (HERE / name).read_bytes()
        require(len(raw) == item["bytes"], "Source size: " + name)
        require(sha256(raw).hexdigest() == item["sha256"], "Source hash: " + name)
        if "decompressed_sha256" in item:
            require(sha256(gzip.decompress(raw)).hexdigest() == item["decompressed_sha256"],
                    "Source payload: " + name)
    return len(files)


def mathematical(value):
    if isinstance(value, dict):
        return {key: mathematical(item) for key, item in value.items()
                if key not in {"seconds", "max_rss_bytes", "checker_sha256"}}
    if isinstance(value, list):
        return [mathematical(item) for item in value]
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--optimized", action="store_true")
    args = parser.parse_args()
    output = args.out.resolve()
    require(not output.exists(), "Use a new output directory")
    require(not output.is_relative_to(HERE), "Keep replay output outside the package")
    output.parent.mkdir(parents=True, exist_ok=True)
    require(shutil.disk_usage(output.parent).free >= 3 * 1024**3 + 100 * 1024**2,
            "Keep at least 3 GiB free during the replay")
    count = check_inputs()
    output.mkdir()
    started = time.monotonic()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OMP_NUM_THREADS="1",
               OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    report = {"schema": "raw-selected-centre-units-replay-v1", "source_files": count,
              "manifest_sha256": sha256(MANIFEST.read_bytes()).hexdigest(),
              "replay_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "python": sys.version, "platform": platform.platform(),
              "optimized_reviewers": args.optimized, "stages": []}
    with tempfile.TemporaryDirectory(prefix="selected-units-", dir=output) as temporary:
        workspace = Path(temporary) / "workspace"
        shutil.copytree(HERE / "frozen", workspace)
        c = workspace / CAMPAIGN
        lanes = c / "lanes"
        old_r = read(lanes / "circuit-interface/INTERFACE.json")["R"]
        new_r = read(lanes / "new-core-transfer-20261017/INTERFACE.json")["R"]
        require(old_r == new_r, "Historical and transferred centre rows are equal")
        report["old_new_R_equal"] = True

        def run(name, script, receipt, expected, arguments=(), fixed=False, optimize=True):
            require(shutil.disk_usage(output).free >= 3 * 1024**3,
                    "Keep at least 3 GiB free during the replay")
            command = [sys.executable, "-I", "-B"]
            if args.optimized and optimize:
                command.append("-O")
            command.extend([str(c / script), *map(str, arguments)])
            log = output / (name + ".log")
            tick = time.monotonic()
            print("RUN " + name, flush=True)
            with log.open("w") as stream:
                process = subprocess.run(command, cwd=workspace, env=env, stdout=stream,
                                         stderr=subprocess.STDOUT, check=False)
            require(process.returncode == 0, "Replay failed; read " + str(log))
            produced = c / receipt if fixed else output / receipt
            actual, original = read(produced), read(HERE / "frozen" / CAMPAIGN / expected)
            require(mathematical(actual) == mathematical(original),
                    "Mathematical receipt differs: " + name)
            if fixed:
                shutil.copyfile(produced, output / (name + ".json"))
            report["stages"].append({"name": name, "status": actual["status"],
                "seconds": time.monotonic() - tick, "log": log.name,
                "command": command,
                "mathematical_receipt_equal": True,
                "python_optimized": args.optimized and optimize})
            print(actual["status"], flush=True)

        run("irregular-unit", "root/check_irregular_split_20261017.py",
            "root/IRREGULAR-SPLIT-20261017.json", "root/IRREGULAR-SPLIT-20261017.json", fixed=True)
        run("dyadic-witness", "lanes/dyadic-subset-search-20261017/check_dyadic_subsets.py",
            "lanes/dyadic-subset-search-20261017/DYADIC-SUBSETS.json",
            "lanes/dyadic-subset-search-20261017/DYADIC-SUBSETS.json", fixed=True, optimize=False)
        run("complete-minors", "lanes/native-escape-20261017/check_raw_minor_subsets.py",
            "lanes/native-escape-20261017/RAW-MINOR-SUBSETS.json",
            "lanes/native-escape-20261017/RAW-MINOR-SUBSETS.json", fixed=True)
        regenerated = gzip.decompress((lanes / "native-escape-20261017/RAW-FIVE-MINOR-PROGRAM.json.gz").read_bytes())
        original = gzip.decompress((HERE / "frozen" / CAMPAIGN / "lanes/native-escape-20261017/RAW-FIVE-MINOR-PROGRAM.json.gz").read_bytes())
        require(regenerated == original, "Complete-minor regenerated payload differs")
        run("odd-grid", "lanes/bridge-review-20261017/odd-grid-a8-review-20261017/check_review.py",
            "lanes/bridge-review-20261017/odd-grid-a8-review-20261017/REVIEW.json",
            "lanes/bridge-review-20261017/odd-grid-a8-review-20261017/REVIEW.json", fixed=True)
        run("native-phases", "lanes/independent-review-20261017/check_new_native.py",
            "native-phases.json", "lanes/independent-review-20261017/NEW-CORE-NATIVE-REVIEW.json",
            ("--providers", "base", "extra", "--out", output / "native-phases.json"))
        run("serial-interfaces", "lanes/new-native-recipes-20261017/replay_serial_balanced.py",
            "serial-interfaces.json", "lanes/new-native-recipes-20261017/SERIAL-BALANCED-REVIEW.json",
            ("--out", output / "serial-interfaces.json"))
        run("irregular-native", "lanes/new-native-recipes-20261017/replay_irregular_38.py",
            "irregular-native.json", "lanes/new-native-recipes-20261017/IRREGULAR-38-REVIEW.json",
            ("--out", output / "irregular-native.json"))
        run("short-normalization", "lanes/new-native-recipes-20261017/reduced-transfer-review-20261018/check.py",
            "short-normalization/REVIEW.json",
            "lanes/new-native-recipes-20261017/reduced-transfer-review-20261018/verified-normal/REVIEW.json",
            ("--out", output / "short-normalization"))
    check_inputs()
    report.update(status="PASS_RAW_SELECTED_CENTRE_UNITS", frozen_inputs_unchanged=True,
                  seconds=time.monotonic() - started,
                  scope="Exact local units and native words. No complete supplier or kappa change.")
    (output / "REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"], flush=True)


if __name__ == "__main__":
    main()
