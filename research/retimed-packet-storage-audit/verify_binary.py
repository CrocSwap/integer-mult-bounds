#!/usr/bin/env python3
"""Replay frozen binary owner/capacity authors and independent peers portably."""
import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "binary-census"
SOURCE = "dfd25d553a843a946ca0b94130a5ff8943e98fdd"
PINS = {
    "FROZEN.json": "ddc806cd1098c0703711894e1ae4a99bc91cb8d64ba9aa4257cf5ea9c0e1d2a0",
    "review/RECEIPT.json": "0490b61c59dfa07353e4865389266ee5910018ae7502d7f1a120cf60ded1298d",
    "capacity-review/RECEIPT.json": "c36c212cc450921ceb396a8aaac076f3d5ddd30131cbf541cbdf41c5088f2dbf",
    "STORAGE-APPLICATION.md": "8ad434e37ad23faae3e62595574854286f638eaa51b5f0235043863e136b896c",
    "PORTABLE-FILES.json": "827915df036f851ea7f1e47435044088cc64e5b48572fcd78338f4565010f9a8",
}


def need(condition, message):
    if not condition:
        raise ArithmeticError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def safe_path(root, relative):
    rel = Path(relative)
    need(not rel.is_absolute() and ".." not in rel.parts, "invalid retained path")
    path = root / rel
    need(path.is_file() and not path.is_symlink(), "missing or linked retained file: " + relative)
    need(path.resolve().is_relative_to(root.resolve()), "retained path leaves package")
    return path


def verify_rows(root, rows):
    for name, spec in rows.items():
        path = safe_path(root, name)
        expected = spec if isinstance(spec, str) else spec["sha256"]
        need(digest(path) == expected, "retained hash differs: " + name)
        if isinstance(spec, dict):
            size = spec.get("size", spec.get("bytes"))
            if size is not None:
                need(path.stat().st_size == size, "retained size differs: " + name)


def authenticate():
    verify_rows(PACKAGE, PINS)
    frozen = json.loads((PACKAGE / "FROZEN.json").read_text())
    need(frozen["source_commit"] == SOURCE, "wrong author source commit")
    verify_rows(PACKAGE, frozen["files"])
    source = json.loads((PACKAGE / "SOURCE-BINDINGS.json").read_text())
    need(source["commit"] == SOURCE, "wrong retained source commit")
    verify_rows(PACKAGE / "sources", source["files"])
    corollary = json.loads((PACKAGE / "COROLLARY-BINDINGS.json").read_text())
    need(corollary["scientific_source_commit"] == SOURCE, "wrong corollary source commit")
    need(corollary["publication_commit"] == "de02b59fa9a74d4958d0d114d25e9083ab91b022", "wrong accepted mass publication")
    verify_rows(PACKAGE, corollary["files"])
    review = json.loads((PACKAGE / "review/RECEIPT.json").read_text())
    need(review["decision"] == "ACCEPT_FIXED_BINARY_RAW_CONTEXT_OWNER_CENSUS", "census acceptance absent")
    need(review["source_commit"] == SOURCE, "wrong census review source")
    need(review["author_proof_sha256"] == digest(PACKAGE / "PROOF.md"), "reviewed census proof differs")
    verify_rows(PACKAGE / "review", review["files"])
    capacity = json.loads((PACKAGE / "capacity-review/RECEIPT.json").read_text())
    need(capacity["decision"] == "ACCEPT_BINARY_PRODUCTION_CAPACITY_COROLLARY", "capacity acceptance absent")
    verify_rows(PACKAGE, capacity["author_files"])
    verify_rows(PACKAGE / "review", capacity["census_acceptance"])
    verify_rows(PACKAGE / "capacity-review", capacity["review_files"])
    copied = json.loads((PACKAGE / "PORTABLE-FILES.json").read_text())
    need(copied["source_commit"] == SOURCE, "wrong portable source pin")
    verify_rows(PACKAGE, {row["path"]: row for row in copied["copied_files"]})
    need(len(copied["copied_files"]) == copied["count"] == 44, "incomplete exact export")
    need(sum(row["bytes"] for row in copied["copied_files"]) == copied["bytes"], "export byte total")
    verify_rows(HERE, {
        "JOINED-STORAGE.md": "d7c339e01d678aaa24c143cadf98946f8c9afd9a3940fb73c696198e0511a858",
        "census/sources/periodic.py": "6233e1806d29bd386ce39fab398fee4f6b73b11d4bdc1e3608bcccde15d71b19",
    })


def snapshot():
    result = {}
    for path in sorted(PACKAGE.rglob("*")):
        need(not path.is_symlink(), "linked package content")
        if path.is_file():
            result[str(path.relative_to(HERE))] = digest(path)
    result["verify_binary.py"] = digest(Path(__file__).resolve())
    return result


def comparable(record):
    # The peer reports its interpreter version as environment metadata.
    # All mathematical fields must equal the accepted receipt across versions.
    return {key: value for key, value in record.items() if key != "python"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    need(not output.is_relative_to(HERE), "receipts must be outside the research package")
    output.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    authenticate()
    before = snapshot()
    runs, parity = [], {}
    jobs = (
        ("census-author", "check.py", "RESULT.json", "PASS", False),
        ("corollary-author", "check_corollary.py", "COROLLARY-RESULT.json", "PASS", False),
        ("census-peer", "review/independent.py", "review/EVIDENCE.json", "PASS_INDEPENDENT_BINARY_OWNER_CENSUS", False),
        ("capacity-peer", "capacity-review/check.py", "capacity-review/EVIDENCE.json", "PASS_INDEPENDENT_BINARY_CAPACITY_COROLLARY", True),
    )
    for name, script, accepted_name, marker, file_output in jobs:
        accepted = json.loads((PACKAGE / accepted_name).read_text())
        pair = []
        for mode in ("normal", "optimized"):
            label = name + "-" + mode
            receipt = output / (label + ".json")
            remaining = 175 - (time.monotonic() - started)
            need(remaining > 0, "binary replay budget exhausted")
            with TemporaryDirectory(prefix="binary-bytecode-", dir=output) as cache:
                argv = [sys.executable, "-I", "-W", "error", "-B", "-X", "pycache_prefix=" + cache]
                if mode == "optimized":
                    argv.append("-O")
                argv.append(str(PACKAGE / script))
                if file_output:
                    argv.extend(("--author", str(PACKAGE), "--output", str(receipt)))
                env = dict(os.environ)
                env.pop("PYTHONOPTIMIZE", None)
                then = time.monotonic()
                completed = subprocess.run(argv, cwd=output, capture_output=True,
                                           timeout=min(90, remaining), env=env)
            (output / (label + ".log")).write_bytes(completed.stdout + completed.stderr)
            completed.check_returncode()
            stdout_record = json.loads(completed.stdout)
            if not file_output:
                receipt.write_bytes(completed.stdout)
            data = receipt.read_bytes()
            record = json.loads(data)
            need(record == stdout_record, "stdout and file receipt differ: " + label)
            need(record["status"] == marker, "missing successful status: " + label)
            need(comparable(record) == comparable(accepted), "result differs from accepted evidence: " + label)
            pair.append(data)
            runs.append({"label": label, "status": marker, "sha256": sha256(data).hexdigest(),
                         "seconds": round(time.monotonic() - then, 3)})
            print("PASS_BINARY_" + label.upper().replace("-", "_"), flush=True)
        need(pair[0] == pair[1], "normal/optimized receipt bytes differ: " + name)
        parity[name] = sha256(pair[0]).hexdigest()
    authenticate()
    need(snapshot() == before, "replay modified frozen package files")
    result = {"status": "PASS_PORTABLE_BINARY_OWNER_CAPACITY_JOIN", "source_commit": SOURCE,
              "commands": runs, "normal_optimized_parity": parity,
              "frozen_files_unchanged": True, "package_files": len(before) - 1,
              "seconds": round(time.monotonic() - started, 3),
              "application_sha256": PINS["STORAGE-APPLICATION.md"],
              "scope": "Accepted current binary local beta=2 applied to unchanged ordinary data-file coefficients; all complete canonical premises unchanged."}
    (output / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    main()
