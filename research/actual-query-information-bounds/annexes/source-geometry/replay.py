"""Replay the seven exact source-geometry checks with one process at a time."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
PARENT = HERE.parents[1]


def require(test, reason):
    if not test:
        raise ValueError(reason)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_files(root, records):
    for relative, record in records.items():
        path = root / relative
        require(path.is_file(), "Missing file: " + str(path))
        require(path.stat().st_size == record["bytes"], "File size: " + str(path))
        require(digest(path) == record["sha256"], "File hash: " + str(path))


def compare(actual, expected, location="$"):
    require(type(actual) is type(expected), "JSON type: " + location)
    if isinstance(actual, dict):
        require(actual.keys() == expected.keys(), "JSON keys: " + location)
        for key in actual:
            compare(actual[key], expected[key], location + "/" + key)
    elif isinstance(actual, list):
        require(len(actual) == len(expected), "JSON length: " + location)
        for index, (left, right) in enumerate(zip(actual, expected)):
            compare(left, right, location + "/" + str(index))
    else:
        require(actual == expected, "JSON value: " + location)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    out = arguments.out.resolve()
    require(not out.is_relative_to(PARENT), "The output must be outside the package")
    require(not out.exists(), "Use a new output directory")
    require(shutil.disk_usage(HERE).free >= 3 * 1024**3, "At least 3 GiB must be free")
    manifest = json.loads((HERE / "ANNEX-MANIFEST.json").read_bytes())
    parent = json.loads((HERE / "PARENT-SNAPSHOT.json").read_bytes())
    portability = json.loads((HERE / "PORTABILITY.json").read_bytes())
    check_files(HERE, manifest["files"])
    check_files(PARENT, parent["files"])
    actual_paths = {str(p.relative_to(HERE)) for p in HERE.rglob("*") if p.is_file()}
    require(actual_paths == set(manifest["files"]) | {"ANNEX-MANIFEST.json"},
            "The annex manifest must list every file")
    out.mkdir(parents=True)
    env = dict(os.environ)
    env.update({key: "1" for key in ["OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS",
                                    "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"]})
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    flags = ["-I", "-B"] + (["-O"] if sys.flags.optimize else [])
    results = []
    started = time.monotonic()
    for job in portability["checks"]:
        script = HERE / job["portable_script"]
        destination = out / job["name"]
        command = [sys.executable, *flags, str(script), "--out", str(destination)]
        begin = time.monotonic()
        run = subprocess.run(command, text=True, capture_output=True, env=env,
                             cwd=out, check=False)
        (out / (job["name"] + ".stdout.txt")).write_text(run.stdout)
        (out / (job["name"] + ".stderr.txt")).write_text(run.stderr)
        require(run.returncode == 0, job["name"] + " failed: " + run.stderr)
        require(any(line.startswith(job["expected_status"]) for line in run.stdout.splitlines()),
                "Expected PASS status: " + job["name"])
        receipts = []
        for relative in job["receipts"]:
            expected = json.loads((HERE / relative).read_bytes())
            actual_path = destination / Path(relative).name
            actual = json.loads(actual_path.read_bytes())
            metadata = []
            if "checker_sha256" in expected:
                expected["checker_sha256"] = digest(script)
                metadata.append("checker_sha256")
            compare(actual, expected, relative)
            receipts.append({"frozen_receipt": relative, "output": str(actual_path.relative_to(out)),
                             "sha256": digest(actual_path), "typed_json_equal": True,
                             "declared_metadata_updates": metadata})
        seconds = time.monotonic() - begin
        results.append({"name": job["name"], "status": job["expected_status"],
                        "seconds": seconds, "receipts": receipts})
        print(job["expected_status"], flush=True)
    check_files(HERE, manifest["files"])
    check_files(PARENT, parent["files"])
    result = {"status": "PASS_SOURCE_GEOMETRY_ANNEX", "checks": results,
              "seconds": time.monotonic() - started, "optimized": bool(sys.flags.optimize),
              "python": sys.version, "interpreter": sys.executable,
              "annex_manifest_sha256": digest(HERE / "ANNEX-MANIFEST.json"),
              "parent_files_unchanged": len(parent["files"]),
              "annex_files_unchanged": len(manifest["files"]),
              "execution": "Seven serial standard-library checks; no external tools, Git, network, or solver."}
    (out / "REPLAY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
