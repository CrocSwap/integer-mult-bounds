#!/usr/bin/env python3
"""Run the unchanged rank, local-word, grid, and reader checks in fresh copies."""

import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
FROZEN = HERE / "frozen"
HISTORICAL_ROOT = "/Users/aliromman/Projects/IntegerMultiplicationBounds/work/centre-encoding-campaign-20261014"
RANK = "lanes/independent-review-20261017/reciprocal-centre-rank-review-20261018"
NATIVE = "lanes/independent-review-20261017/reciprocal-native-review-20261018"
READER = "lanes/native-escape-20261017/reciprocal-reader-cuts-20261020"
REVIEW = "lanes/native-escape-20261017/owner-review/reciprocal-source-cut-review-20261020"
READER_INPUTS = {
    "model": "lanes/oblique-native-20261017/signed-metric-reciprocal-20261020/model-normal-v2/RESPONSE.json.gz",
    "native": "lanes/oblique-native-20261017/signed-metric-reciprocal-20261020/native-normal/NATIVE.json.gz",
    "views": "lanes/bridge-access-20261017/matched-stage-access-20261018/DIMENSION25-VIEWS.json",
    "scalar_tariff": "lanes/new-core-transfer-20261017/low-displacement-20261020/check_response.py",
}
JOBS = [
    ("rank", RANK, "check_reciprocal.py", False, RANK, ["CHECKS.json"]),
    ("grid", RANK, "check_grid.py", False, RANK, ["GRID-CHECKS.json"]),
    ("original_j_words", NATIVE, "check_words.py", False, NATIVE, ["CHECKS.json"]),
    ("reader_producer", READER, "check_cuts.py", True, READER + "/bound-normal", ["CHECKS.json", "READERS.json.gz"]),
    ("reader_independent", REVIEW, "check_review.py", True, REVIEW, ["CHECKS.json", "SOURCE-MANIFEST.json", "ORDERED-CONTENTS.json", "ANCHOR-TYPES.json", "CONDITIONAL-READER.json"]),
    ("reader_binding", REVIEW, "check_binding.py", True, REVIEW + "/binding-normal", ["CHECKS.json", "SOURCE-MANIFEST.json"]),
]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def check_sources():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        data = (FROZEN / row["path"]).read_bytes()
        need(len(data) == row["bytes"] and digest(data) == row["sha256"], "Frozen source: " + row["path"])
        if "decompressed_sha256" in row:
            need(digest(gzip.decompress(data)) == row["decompressed_sha256"], "Frozen payload: " + row["path"])
    return manifest


def path_manifest(data, root):
    """Change only absolute manifest keys to campaign-relative keys."""
    result = {}
    prefix = str(root) + "/"
    for key, value in json.loads(data).items():
        need(key.startswith(prefix), "Manifest path is inside its declared campaign")
        relative = key[len(prefix):]
        need((FROZEN / relative).is_file(), "Manifest path has a retained source")
        result["$CAMPAIGN/" + relative] = value
    return encoded(result)


def reader_outputs(directory, root):
    """Bind the raw payload, then normalize its four source-path strings."""
    payload_bytes = gzip.decompress((directory / "READERS.json.gz").read_bytes())
    payload = json.loads(payload_bytes)
    receipt = json.loads((directory / "CHECKS.json").read_bytes())
    need(digest(payload_bytes) == receipt["payload_decompressed_sha256"], "Reader raw payload matches its receipt")
    payload, receipt = deepcopy(payload), deepcopy(receipt)
    for obj in (payload, receipt):
        need(set(obj["source_pins"]) == set(READER_INPUTS), "Exactly four reader source pins")
        for name, relative in READER_INPUTS.items():
            pin = obj["source_pins"][name]
            need(pin["path"] == str(root) + "/" + relative, "Exact reader source path: " + name)
            source = (FROZEN / relative).read_bytes()
            content = gzip.decompress(source) if relative.endswith(".gz") else source
            need(pin["sha256"] == digest(content), "Reader source hash: " + name)
            pin["path"] = "$CAMPAIGN/" + relative
    canonical_payload = encoded(payload)
    receipt["payload_decompressed_sha256"] = digest(canonical_payload)
    return {"READERS.json.gz": canonical_payload, "CHECKS.json": encoded(receipt)}


def comparable(job, directory, root, names):
    if job == "reader_producer":
        return reader_outputs(directory, root)
    return {name: path_manifest((directory / name).read_bytes(), root)
            if name == "SOURCE-MANIFEST.json" else (directory / name).read_bytes()
            for name in names}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    need(not out.is_relative_to(HERE), "Output must be outside the source annex")
    out.parent.mkdir(parents=True, exist_ok=True)
    need(shutil.disk_usage(out.parent).free >= 3 * 1024**3, "At least 3 GiB free disk space is required")
    out.mkdir(exist_ok=False)
    sources = check_sources()
    checks = []
    for job, relative, script, has_out, expected_relative, names in JOBS:
        previous = None
        expected = comparable(job, FROZEN / expected_relative, HISTORICAL_ROOT, names)
        for mode in ("normal", "optimized"):
            result = out / job / mode
            result.mkdir(parents=True)
            work = result / "campaign"
            shutil.copytree(FROZEN, work)
            command = [sys.executable, "-I", "-B"] + (["-O"] if mode == "optimized" else [])
            command.append(str(work / relative / script))
            produced = result / "generated" if has_out else work / relative
            if has_out:
                command += ["--out", str(produced)]
            start = time.monotonic()
            with (result / "stdout.log").open("w") as log:
                run = subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT, check=False)
            need(run.returncode == 0, "Failed " + job + " " + mode + "; read " + str(result / "stdout.log"))
            actual = comparable(job, produced, work, names)
            need(actual == expected, "Frozen result comparison: " + job + " " + mode)
            need(previous is None or actual == previous, "Normal and optimized comparison: " + job)
            previous = actual
            files = {}
            for name in names:
                data = (produced / name).read_bytes()
                shutil.copyfile(produced / name, result / name)
                files[name] = {"raw_sha256": digest(data), "comparison_sha256": digest(actual[name])}
                if name.endswith(".gz"):
                    files[name]["decompressed_sha256"] = digest(gzip.decompress(data))
            check = {"check": job, "mode": mode, "status": "PASS", "seconds": round(time.monotonic() - start, 3),
                     "files": files, "all_result_fields_compared": True}
            checks.append(check)
            shutil.rmtree(work)
            if has_out:
                shutil.rmtree(produced)
            print(job + " " + mode + " PASS", flush=True)
    check_sources()
    report = {"status": "PASS_ORIGINAL_J_RANK_READERS_ANNEX", "checks": checks,
              "source_files": len(sources["files"]), "frozen_sources_unchanged": True,
              "source_manifest_sha256": digest((HERE / "SOURCES.json").read_bytes()),
              "runner_sha256": digest(Path(__file__).read_bytes()), "python": platform.python_version(),
              "platform": platform.platform(), "child_processes_run_concurrently": 1,
              "comparison": "Exact bytes except the four reader source paths and SOURCE-MANIFEST keys. The raw decompressed reader payload is first bound to its raw receipt; its canonical hash then replaces that receipt field. All other fields are compared.",
              "omitted": ["Producer native re-emission", "Original 3036-class phase sweep", "Reader native-event replay", "Accumulator supply, transport, and late erasure", "Global controller, recursive supplier, precision, and complete kappa calculation"]}
    (out / "REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
