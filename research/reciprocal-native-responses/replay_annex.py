#!/usr/bin/env python3
"""Replay the frozen low-displacement matrix and scope checks."""

import argparse
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
SOURCE = "lanes/new-core-transfer-20261017/low-displacement-20261020"
REVIEW = "lanes/independent-review-20261017"


def verify_tree(root, records):
    for name, record in records.items():
        path = root / name
        raw = path.read_bytes()
        if len(raw) != record["bytes"] or sha256(raw).hexdigest() != record["sha256"]:
            raise ValueError("Frozen source changed: " + name)
        if path.suffix == ".gz":
            if sha256(gzip.decompress(raw)).hexdigest() != record["decompressed_sha256"]:
                raise ValueError("Frozen payload changed: " + name)


def tasks():
    return [
        ("rank30-matrix", REVIEW + "/rank-thirty-review-20261020/check_review.py", [],
         REVIEW + "/rank-thirty-review-20261020/CHECKS.json"),
        ("extension-matrices", REVIEW + "/response-extensions-review-20261020/check_extensions.py", [],
         REVIEW + "/response-extensions-review-20261020/CHECKS.json"),
        ("cross-gram", SOURCE + "/check_even_clique_gram.py", ["--out", "results/cross-gram.json"],
         SOURCE + "/gram-v2-normal.json"),
        ("paired-line", SOURCE + "/check_paired_line_scope.py", ["--out", "results/paired-line.json"],
         SOURCE + "/paired-line-scope-normal.json"),
    ]


def mathematical_receipt(path):
    result = json.loads(path.read_text())
    del result["python"]
    del result["elapsed_seconds"]
    return json.dumps(result, sort_keys=True, separators=(",", ":")).encode()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    output = args.out.resolve()
    output.mkdir(parents=True, exist_ok=False)
    core = json.loads((HERE / "SOURCES.json").read_text())
    annex = json.loads((HERE / "annex/SOURCES.json").read_text())
    publication = json.loads((HERE / "annex/PUBLICATION-CHECKS.json").read_text())
    records = {**core["frozen_files"], **annex["frozen_files"]}
    if set(core["frozen_files"]) & set(annex["frozen_files"]):
        raise ValueError("The two frozen trees must have distinct paths")
    if any(core["frozen_files"].get(name) != record
           for name, record in annex["shared_core_files"].items()):
        raise ValueError("Shared source manifest mismatch")

    def verify_sources():
        verify_tree(HERE / "frozen", core["frozen_files"])
        verify_tree(HERE / "annex/frozen", annex["frozen_files"])
        verify_tree(HERE / "annex", publication["files"])

    verify_sources()
    reports = []
    for mode, flags in (("normal", []), ("optimized", ["-O"])):
        work = output / mode
        shutil.copytree(HERE / "frozen", work)
        shutil.copytree(HERE / "annex/frozen", work, dirs_exist_ok=True)
        verify_tree(work, records)
        (work / "results").mkdir()
        (work / "publication-checks").mkdir()
        for name in publication["files"]:
            shutil.copy2(HERE / "annex" / name, work / "publication-checks" / name)
        for name, script, arguments, expected in tasks():
            command = [sys.executable, "-I", "-B", *flags, str(work / script), *arguments]
            start = time.monotonic()
            with (work / "results" / (name + ".log")).open("w") as log:
                subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT, check=True)
            produced = work / (arguments[-1] if arguments else expected)
            actual_hash = sha256(produced.read_bytes()).hexdigest()
            if actual_hash != records[expected]["sha256"]:
                raise ValueError("Receipt differs from frozen source: " + mode + "/" + name)
            reports.append({"mode": mode, "check": name,
                            "command": ["python3", "-I", "-B", *flags, script, *arguments],
                            "receipt_sha256": actual_hash,
                            "elapsed_seconds": round(time.monotonic() - start, 3)})
            print("PASS " + mode + " " + name, flush=True)
        script = "publication-checks/check_native.py"
        arguments = ["--source-root", ".", "--out", "results/native.json"]
        command = [sys.executable, "-I", "-B", *flags, str(work / script), *arguments]
        start = time.monotonic()
        with (work / "results/native.log").open("w") as log:
            subprocess.run(command, cwd=work, stdout=log, stderr=subprocess.STDOUT, check=True)
        produced = work / "results/native.json"
        content = mathematical_receipt(produced)
        if content != mathematical_receipt(HERE / "annex/NATIVE-CHECKS.json"):
            raise ValueError("Publication native check differs: " + mode)
        reports.append({"mode": mode, "check": "publication-native",
                        "command": ["python3", "-I", "-B", *flags, script, *arguments],
                        "receipt_sha256": sha256(produced.read_bytes()).hexdigest(),
                        "mathematical_receipt_sha256": sha256(content).hexdigest(),
                        "elapsed_seconds": round(time.monotonic() - start, 3)})
        print("PASS " + mode + " publication-native", flush=True)
    verify_sources()
    receipt = {
        "status": "PASS_LOW_DISPLACEMENT_RESPONSE_ANNEX",
        "python": sys.version, "platform": platform.platform(),
        "replay_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "core_manifest_sha256": sha256((HERE / "SOURCES.json").read_bytes()).hexdigest(),
        "annex_manifest_sha256": sha256((HERE / "annex/SOURCES.json").read_bytes()).hexdigest(),
        "publication_checker_manifest_sha256": sha256((HERE / "annex/PUBLICATION-CHECKS.json").read_bytes()).hexdigest(),
        "additional_frozen_source_count": len(annex["frozen_files"]),
        "shared_core_source_count": len(annex["shared_core_files"]),
        "runs": reports,
        "comparison": "Eight exact frozen receipt byte comparisons. Two publication-native comparisons omit only Python version and elapsed time. Compressed source files also have payload hashes.",
        "scope": "Independent matrices, scalar prices, native frame ledgers, 352 changed-exit phases, exact cross-Gram ranks, and finite paired-line checks. The historical raw native spatial replays are separate.",
    }
    (output / "REPLAY.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(receipt["status"], flush=True)


if __name__ == "__main__":
    main()
