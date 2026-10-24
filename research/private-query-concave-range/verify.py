#!/usr/bin/env python3
"""Check the scalar extension and its saved private-query inputs."""
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


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    args = parser.parse_args()
    build = args.build.resolve()
    require(not build.exists(), "The build directory exists.")
    manifest = read(ROOT / "SOURCE-MANIFEST.json")
    for item in manifest["files"]:
        require(hashlib.sha256((ROOT / item["package"]).read_bytes()).hexdigest()
                == item["sha256"], "Source hash: " + item["package"])
    build.mkdir(parents=True)
    shutil.copytree(ROOT / "historical", build / "historical")
    shutil.copytree(ROOT / "independent-review", build / "independent-review")
    old = build / "historical/work/autonomous-kappa-run"
    stages = []
    def run(name, command, expected=0):
        print("Run:", " ".join(map(str, command)), flush=True)
        result = subprocess.run(list(map(str, command)), capture_output=True, text=True)
        (build / (name + ".stdout.log")).write_text(result.stdout)
        (build / (name + ".stderr.log")).write_text(result.stderr)
        require(result.returncode == expected, "Exit code: " + name)
        stages.append({"name": name, "command": list(map(str, command)),
                       "exit_code": result.returncode})
    for name, option in [("scalar", []), ("scalar-optimized", ["-O"])]:
        run(name, [sys.executable, "-E", *option, "-B", ROOT / "verify_scalar_lemma.py",
                   build / (name + ".json")])
        require(read(build / (name + ".json"))["status"] ==
                "PASS_EXACT_FULL_CONCAVE_PRIVATE_COST_LEMMA", "Scalar result")
    run("scalar-independent", [sys.executable, "-E", "-B", build /
                                "independent-review/independent_calculation.py"])
    run("geometry", [sys.executable, "-E", "-B", old / "framework/private64_geometry.py",
                     old, old / "framework/PRIVATE64-GEOMETRY.json"])
    fresh = read(old / "framework/PRIVATE64-GEOMETRY.json")
    saved = read(ROOT / "historical/work/autonomous-kappa-run/framework/PRIVATE64-GEOMETRY.json")
    for key in saved:
        if key not in ["seconds", "source_sha256"]:
            require(fresh[key] == saved[key], "Geometry field: " + key)
    run("profiles", [sys.executable, "-E", "-B", old / "framework/private64_profiles.py",
                     old, old / "framework/PRIVATE64-PROFILES.json"])
    fresh_profiles = read(old / "framework/PRIVATE64-PROFILES.json")
    saved_profiles = read(ROOT / "historical/work/autonomous-kappa-run/framework/PRIVATE64-PROFILES.json")
    for key in saved_profiles:
        if key not in ["seconds", "source_sha256"]:
            require(fresh_profiles[key] == saved_profiles[key], "Profile field: " + key)
    run("rank-nine", [sys.executable, "-E", "-B", old /
                      "framework/private64-weighted/independent_max_rank.py",
                      build / "rank-nine.json"])
    rank_nine = read(build / "rank-nine.json")
    require(rank_nine["status"] == "PASS_INDEPENDENT_WEIGHTED_RANK_NINE_EXCLUSION",
            "Rank-nine result")
    receipt = {"status": "PASS_PRIVATE_QUERY_CONCAVE_RANGE_INPUTS", "stages": stages,
               "scalar_margin": read(build / "scalar.json")["strict_gap_lower"],
               "rank7_frames": fresh["rank7_planes"],
               "profiles_through_63": fresh_profiles["profile_counts"]["all"],
               "total64_partitions": rank_nine["partitions"],
               "rank9_partitions": rank_nine["rank_nine_partitions"],
               "scope": "Finite proof inputs only. The written real-variable argument, capacity bounds and two query-profile closures are required. No fitting-rigidity or physical supplier replay.",
               "source_manifest_sha256": hashlib.sha256((ROOT / "SOURCE-MANIFEST.json").read_bytes()).hexdigest()}
    (build / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], receipt["scalar_margin"], receipt["profiles_through_63"])


if __name__ == "__main__":
    main()
