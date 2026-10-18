#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Compose two exact sources and run PR3015's fresh finite release recipe.

The source recipes and all their mathematical checks remain unchanged. Only
the complete-admission --fill argument is replaced by the journal-derived fill.
Source credit: Jeremy Kothe, Marius-Paul Dumitrean and the retained lineage.
"""

import argparse
import gzip
import hashlib
import io
import json
import os
import signal
import subprocess
import sys
import tarfile
import time
from fractions import Fraction
from pathlib import Path, PurePosixPath

PACKAGE = Path(__file__).resolve().parent
HEAD = "e244296debb45fe6f4da84d29e4d64fbab55fda0"
PREFIX = "research/rank7-joint-endframes-restore-edit"
EXPECTED = {1: 1644352, 2: 470862, 3: 159472, 4: 71928,
            5: 13710, 8: 5328, 14: 1, 48: 28190}
RECIPE_NAMES = ["export-pr2894", "export-pr2833", "fresh-retained-bootstrap",
                "four-kernel-stage", "preload-stage", "parent-paired-stage",
                "paired-extension-stage", "rank7-overlay-stage", "declared-edit-stage",
                "derive-closed-adapters", "fresh-current-native", "complete-admission"]
DEPENDENCY_MANIFESTS = {
    "pr2908": "9dba3fe371602ec023a54e26c0fd66f69eb7a74be86aab89923529083c14b36f",
    "pr2917": "55c46ddf2e3edc87dfe1ba3320947466d36980d457eb37f6cd6fba341dae0192",
    "pr2942": "23bd270f440c4c7ad0d106990ae391e1af799a61ef3601d00e27f1824ae8ba69",
    "pr2957": "9cd226a2bf7391e7fbf4a23741bb1934afafbd596aef06f2999a935cd6e44e28",
    "pr2966": "9e410c244efb370e20a5f9dc366550e11bcb14ebcecf8f2cb850512e82573914",
    "pr2969": "797c55c560dec5b5a657296f49d918fc5db708b7bed3eba046b3358b1666e55b",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def authenticate_tree(directory):
    manifest = read(directory / "MANIFEST.json")
    paths = list(directory.rglob("*"))
    need(len(paths) <= 10000 and len(manifest) <= 5000, "source tree bound")
    need(not any(p.is_symlink() for p in paths), "regular source tree")
    actual = {p.relative_to(directory).as_posix(): digest(p) for p in paths
              if p.is_file() and p != directory / "MANIFEST.json"}
    need(actual == manifest, "complete source inventory: " + str(directory))


def export(repo, out):
    """Export only bounded regular files, then authenticate the whole package."""
    raw = subprocess.run(
        ["git", "-C", str(repo), "archive", HEAD, PREFIX],
        check=True, capture_output=True, timeout=60,
    ).stdout
    need(len(raw) < 10_000_000, "bounded source archive")
    out.mkdir()
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        members = archive.getmembers()
        need(len(members) <= 256, "source file bound")
        for member in members:
            name = PurePosixPath(member.name)
            need(not name.is_absolute() and ".." not in name.parts, "archive path")
            need(member.isfile() or member.isdir(), "regular source entries")
            if member.isdir():
                continue
            need(name.is_relative_to(PurePosixPath(PREFIX)), "source prefix")
            target = out / name.relative_to(PurePosixPath(PREFIX))
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = archive.extractfile(member)
            need(stream is not None, "source file stream")
            with stream:
                target.write_bytes(stream.read())
    manifest = out / "MANIFEST.json"
    need(digest(manifest) == digest(PACKAGE / "vendor/pr3015/MANIFEST.json"),
         "exact PR3015 source manifest")
    authenticate_tree(out)


def fill_from_journal(source, target):
    fill = read(source / "allocation/FILL.json.gz")
    need(digest(source / "allocation/FILL.json.gz") == read(source / "CLAIM.json")["fill_sha256"],
         "PR3015 literal baseline fill")
    journal = read(PACKAGE / "vendor/pr3018/EXCHANGE.json")
    need(len(journal["edits"]) == 103, "exact 103-row journal")
    rows, seen = list(fill["rows"]), set()
    for index, old, new in journal["edits"]:
        need(type(index) is int and 0 <= index < len(rows), "journal index")
        need(index not in seen and rows[index] == old, "unique literal preimage")
        need(len(new) == 6 and old[:2] == new[:2], "same call and helper")
        seen.add(index)
        rows[index] = new
    candidate = {**fill, "rows": rows}
    raw = (json.dumps(candidate, sort_keys=True, separators=(",", ":")) + "\n").encode()
    target.write_bytes(gzip.compress(raw, compresslevel=1, mtime=0))
    return digest(target)


def run_stage(name, command, work, env, stages, timeout):
    log = work / (name + ".log")
    started = time.monotonic()
    with log.open("w") as stream:
        process = subprocess.Popen(
            list(map(str, command)), cwd=work, env=env, stdin=subprocess.DEVNULL,
            stdout=stream, stderr=subprocess.STDOUT, start_new_session=True,
        )
        try:
            code = process.wait(timeout=timeout)
        finally:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
    stages.append(dict(stage=name, exit_code=code,
                       seconds=time.monotonic() - started, log_sha256=digest(log)))
    save(work / "STAGES.json", stages)
    need(code == 0, "failed " + name + "; see " + str(log))
    print("PASS", name, flush=True)


def execute(repo, work, dry_run):
    need(not work.exists(), "refusing an existing replay workspace")
    need(not work.is_relative_to(PACKAGE), "replay outside published package")
    need(sys.flags.optimize == 0, "inherited source requires enabled assertions")
    need(os.name == "posix", "full replay process-group cleanup requires POSIX")
    for entry in read(PACKAGE / "VENDOR.json"):
        need(digest(PACKAGE / entry["path"]) == entry["sha256"], "frozen vendor input")
    work.mkdir(parents=True)
    source, run = work / "pr3015", work / "run"
    export(repo, source)
    fill_path = work / "COMPOSED-FILL.json.gz"
    fill_hash = fill_from_journal(source, fill_path)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
               PYTHONPYCACHEPREFIX=str(work / "bytecode"),
               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1", PYTHONINTMAXSTRDIGITS="0")
    for key in ("PYTHONPATH", "PYTHONOPTIMIZE", "WITNESS_SPEC", "WITNESS_RECORD", "WITNESS_DISCOVER"):
        env.pop(key, None)
    py = [sys.executable, "-B"]
    stages = []
    run_stage("source-preflight", py + [source / "reproduce.py", "--repo", repo,
              "--work", run, "--jobs", "1", "--dry-run"], work, env, stages, 120)
    recipe = read(run / "PREFLIGHT.json")["commands"]
    need([name for name, _ in recipe] == RECIPE_NAMES, "complete source recipe")
    changes = []
    for name, command in recipe:
        if name == "complete-admission":
            position = command.index("--fill") + 1
            need(command[position] == str(source / "allocation/FILL.json.gz"), "source fill preimage")
            changes.append(dict(stage=name, argument="--fill", old=command[position], new=str(fill_path)))
            command[position] = str(fill_path)
    need(len(changes) == 1, "exactly one recipe argument changes")
    save(work / "RECIPE.json", dict(commands=recipe, changes=changes, fill_sha256=fill_hash))
    if dry_run:
        return {"status": "PREFLIGHT_ONLY_NOT_A_RELEASE", "fill_sha256": fill_hash}
    for name, command in recipe:
        run_stage(name, command, work, env, stages, 1800)
    return check_release(work, source, fill_hash, stages)


def check_release(work, source, fill_hash, stages):
    candidate = work / "run/candidate"
    need(digest(work / "COMPOSED-FILL.json.gz") == fill_hash, "unchanged admitted fill bytes")
    admission = read(candidate / "RESULT.json")
    release = read(candidate / "release/RELEASE-RECEIPT.json")
    need(admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "complete admission")
    need(release["status"] == "PASS_RELEASE", "outer release")
    need(admission["fill_sha256"] == fill_hash, "new literal fill admission binding")
    need({int(k): v for k, v in admission["profile"].items()} == EXPECTED,
         "exact complete composed profile")
    need(admission["source_manifest_sha256"] == read(source / "CLAIM.json")["source_manifest_sha256"],
         "unchanged PR3015 edited source")
    need(Fraction(admission["kappa"]) == Fraction(release["kappa_decimal"]), "same released endpoint")
    need(Fraction(admission["kappa"]) > Fraction(read(source / "CLAIM.json")["kappa"]),
         "strict improvement over PR3015")
    need(admission["release_receipt_sha256"] == digest(candidate / "release/RELEASE-RECEIPT.json"),
         "admission authenticates release")
    need(admission["package_manifest_sha256"] == release["manifest_sha256"], "same admitted package")
    check_source_chain(work, source, admission, stages)
    return dict(status="PASS_RESTORE_PACKING_COMPLETE_RELEASE", kappa=admission["kappa"],
                comparison_kappa=read(source / "CLAIM.json")["kappa"],
                gain=str(Fraction(admission["kappa"]) - Fraction(read(source / "CLAIM.json")["kappa"])),
                fill_sha256=fill_hash, fresh_retained_bootstrap=True,
                fill_payload_sha256=hashlib.sha256((json.dumps(
                    read(work / "COMPOSED-FILL.json.gz"), sort_keys=True,
                    separators=(",", ":")) + "\n").encode()).hexdigest(),
                admission_result_sha256=digest(candidate / "RESULT.json"),
                release_receipt_sha256=digest(candidate / "release/RELEASE-RECEIPT.json"),
                stages=stages, scope="Conditional finite release; inherited theorem hypotheses remain.")


def check_source_chain(work, source, admission, stages):
    run = work / "run"
    need([s["stage"] for s in stages] == ["source-preflight", *RECIPE_NAMES], "all fresh stages")
    need(all(s["exit_code"] == 0 for s in stages), "successful source stages")
    edited = run / "source-edits"
    need(digest(edited / "MANIFEST.json") == admission["source_manifest_sha256"], "actual edited source")
    authenticate_tree(edited)
    native_path = run / "native/NATIVE-RECEIPT.json"
    native = read(native_path)
    need(digest(native_path) == admission["native_receipt_sha256"], "fresh native binding")
    need(native["manifest_sha256"] == admission["source_manifest_sha256"], "native source")
    need(native["fresh_current_provider_count"] == 2, "two fresh current providers")
    need(native["status"] == "PASS_COMPOSED_FRESH_NATIVE_PROVIDERS_AND_AUTHENTICATED_CACHE",
         "complete native receipt")
    for tag in ("base", "extra"):
        actual = edited / ("new/borrow/words/BORROW-WORD-43" + tag + ".json.gz")
        expected = source / ("edits/FINAL-WORD-" + tag + ".json.gz")
        need(read(actual) == read(expected), "exact edited provider word")
        need(native["providers"][tag]["word_sha256"] == digest(actual), "native provider word")
    need(digest(source / "MANIFEST.json") == digest(PACKAGE / "vendor/pr3015/MANIFEST.json"),
         "unchanged pinned PR3015 manifest")
    authenticate_tree(source)
    for name, expected in DEPENDENCY_MANIFESTS.items():
        need(digest(run / name / "MANIFEST.json") == expected, "pinned predecessor " + name)
        authenticate_tree(run / name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    result = execute(args.repo.resolve(), args.work.resolve(), args.dry_run)
    save(args.work / "RESULT.json", result)
    print(result["status"], result.get("kappa", ""), flush=True)


if __name__ == "__main__":
    main()
