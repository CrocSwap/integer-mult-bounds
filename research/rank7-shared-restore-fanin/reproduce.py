#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Run the unchanged PR3015 release recipe with the explicit R1+R2 edit list.

Credit Jeremy Kothe, Marius-Paul Dumitrean, Mason Hale, Jeremy Diviney and
all retained source authors. No predecessor file or acceptance gate is edited.
"""

import argparse
import contextlib
import gzip
import io
import json
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import time
from fractions import Fraction
from pathlib import Path, PurePosixPath

import rewrite as rw
import verify as v

HEAD = "e244296debb45fe6f4da84d29e4d64fbab55fda0"
PREFIX = "research/rank7-joint-endframes-restore-edit"
MANIFEST = "5e113822c0c36ee7dd9366578fbaf5daa108b8c51e37f4d10eda25dd6ed52cae"
NAMES = [
    "export-pr2894",
    "export-pr2833",
    "fresh-retained-bootstrap",
    "four-kernel-stage",
    "preload-stage",
    "parent-paired-stage",
    "paired-extension-stage",
    "rank7-overlay-stage",
    "declared-edit-stage",
    "derive-closed-adapters",
    "fresh-current-native",
    "complete-admission",
]


def authenticate_tree(path):
    files = list(path.rglob("*"))
    rw.need(
        len(files) <= 10000 and not any(p.is_symlink() for p in files),
        "bounded regular source tree",
    )
    actual = {
        p.relative_to(path).as_posix(): v.digest(p)
        for p in files
        if p.is_file() and p != path / "MANIFEST.json"
    }
    rw.need(actual == v.read(path / "MANIFEST.json"), "complete source inventory")


def export(repo, out):
    result = subprocess.run(
        ["git", "-C", str(repo), "archive", HEAD, PREFIX],
        capture_output=True,
        check=True,
        timeout=60,
    )
    rw.need(len(result.stdout) < 10_000_000, "bounded source export")
    out.mkdir()
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        members = archive.getmembers()
        rw.need(len(members) <= 256, "bounded package entries")
        for member in members:
            name = PurePosixPath(member.name)
            rw.need(not name.is_absolute() and ".." not in name.parts, "archive path")
            rw.need(member.isfile() or member.isdir(), "regular archive entries")
            if member.isdir():
                continue
            rw.need(name.is_relative_to(PurePosixPath(PREFIX)), "exact package prefix")
            target = out / name.relative_to(PurePosixPath(PREFIX))
            target.parent.mkdir(parents=True, exist_ok=True)
            stream = archive.extractfile(member)
            rw.need(stream is not None, "source stream")
            with stream:
                target.write_bytes(stream.read())
    rw.need(v.digest(out / "MANIFEST.json") == MANIFEST, "exact PR3015 manifest")
    authenticate_tree(out)


def parameters(source, work):
    """Only declared data change. Both stage programs remain byte-identical."""
    out = work / "parameters"
    (out / "edits").mkdir(parents=True)
    (out / "data").mkdir()
    frames = v.load(v.PARENT / "vendor/preload_move.py", "release_frames")
    edits = {}
    for variant in ("base", "extra"):
        words = v.words(variant, frames)
        old, new = words["parent"], words["R1R2"]
        rw.need(
            v.canonical(new)
            == v.read(v.PACKAGE / "evidence/FINITE.json")["variants"][variant]["R1R2"][
                "canonical_sha256"
            ],
            "release word equals checked finite word",
        )
        edits[variant] = rw.stage_spec(old, new)
        shutil.copy2(
            source / f"data/WORD-{variant}.json.gz",
            out / f"data/WORD-{variant}.json.gz",
        )
        payload = json.dumps(new, sort_keys=True, separators=(",", ":")).encode()
        (out / f"edits/FINAL-WORD-{variant}.json.gz").write_bytes(
            gzip.compress(payload, compresslevel=1, mtime=0)
        )
    v.save(
        out / "edits/EDITS.json",
        {
            "edits": edits,
            "declared": {"local_profile": rw.LOCAL, "width_inventory": rw.INVENTORY},
        },
    )
    for name in ("declared_edits.py", "edits_review.py"):
        shutil.copy2(source / "edits" / name, out / "edits" / name)
    pins = {
        p.relative_to(out).as_posix(): v.digest(p)
        for p in sorted((out / "edits").iterdir())
    }
    v.save(out / "EDIT-PINS.json", pins)
    return out


def stage(name, command, work, env, stages):
    log, started = work / (name + ".log"), time.monotonic()
    with log.open("w") as stream:
        process = subprocess.Popen(
            command,
            cwd=work,
            env=env,
            stdin=subprocess.DEVNULL,
            stdout=stream,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        try:
            code = process.wait(timeout=1800)
        finally:
            try:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=5)
            except ProcessLookupError:
                pass
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=5)
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
    stages.append(
        {
            "stage": name,
            "exit_code": code,
            "seconds": time.monotonic() - started,
            "log_sha256": v.digest(log),
        }
    )
    v.save(work / "STAGES.json", stages)
    rw.need(code == 0, "failed " + name + "; see " + str(log))
    print("PASS", name, flush=True)


def retarget(recipe, parameters):
    changes = []
    for name, command in recipe:
        if name == "declared-edit-stage":
            flag, value = "--local-package", str(parameters)
        elif name in ("derive-closed-adapters", "complete-admission"):
            flag, value = "--source-profile", "rank7-shared-restore-fanin"
        else:
            continue
        index = command.index(flag) + 1
        changes.append(
            {"stage": name, "flag": flag, "old": command[index], "new": value}
        )
        command[index] = value
        if name == "derive-closed-adapters":
            index = command.index("--source-commit") + 1
            changes.append(
                {
                    "stage": name,
                    "flag": "--source-commit",
                    "old": command[index],
                    "new": value,
                }
            )
            command[index] = value
    rw.need(len(changes) == 4, "only explicit stage data and source labels change")
    return changes


def check_admission(work, source):
    run = work / "run"
    admission = v.read(run / "candidate/RESULT.json")
    receipt_path = run / "candidate/release/RELEASE-RECEIPT.json"
    receipt = v.read(receipt_path)
    rw.need(
        admission["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE",
        "full admission",
    )
    rw.need(receipt["status"] == "PASS_RELEASE", "modern outer release")
    rw.need(
        {int(k): n for k, n in admission["profile"].items()} == v.EXPECTED,
        "complete R1+R2 bill",
    )
    rw.need(
        admission["fill_sha256"] == v.digest(source / "allocation/FILL.json.gz"),
        "unchanged literal fill",
    )
    rw.need(
        admission["order_sha256"] == v.digest(source / "allocation/ORDER.json"),
        "unchanged order",
    )
    rw.need(
        admission["dispatch_sha256"] == v.digest(source / "allocation/DISPATCH.json"),
        "unchanged dispatch",
    )
    rw.need(
        admission["release_receipt_sha256"] == v.digest(receipt_path), "release binding"
    )
    rw.need(
        admission["package_manifest_sha256"] == receipt["manifest_sha256"],
        "same admitted package",
    )
    rw.need(
        Fraction(admission["kappa"]) == Fraction(receipt["kappa_decimal"]),
        "same released endpoint",
    )
    finite = v.read(v.PACKAGE / "evidence/FINITE.json")
    rw.need(
        Fraction(admission["kappa"]) > Fraction(finite["moment"]["PR3030_root"][1]),
        "gain beyond PR3030",
    )
    return admission, receipt_path, finite


def check_source(work, source, admission, finite):
    run = work / "run"
    edited = run / "source-edits"
    authenticate_tree(edited)
    authenticate_tree(source)
    manifest = v.digest(edited / "MANIFEST.json")
    native = v.read(run / "native/NATIVE-RECEIPT.json")
    rw.need(
        native["manifest_sha256"] == admission["source_manifest_sha256"] == manifest,
        "exact new source",
    )
    rw.need(
        v.digest(run / "native/NATIVE-RECEIPT.json")
        == admission["native_receipt_sha256"],
        "native binding",
    )
    rw.need(native["fresh_current_provider_count"] == 2, "both fresh providers")
    for variant in ("base", "extra"):
        path = edited / f"new/borrow/words/BORROW-WORD-43{variant}.json.gz"
        rw.need(
            v.canonical(v.read(path))
            == finite["variants"][variant]["R1R2"]["canonical_sha256"],
            "actual checked word",
        )
        rw.need(
            native["providers"][variant]["word_sha256"] == v.digest(path),
            "native exact word",
        )
    return manifest


def check(work, source, stages):
    admission, receipt_path, finite = check_admission(work, source)
    manifest = check_source(work, source, admission, finite)
    rw.need(
        [s["stage"] for s in stages] == ["source-preflight", *NAMES],
        "all source stages",
    )
    rw.need(all(s["exit_code"] == 0 for s in stages), "successful complete recipe")
    return {
        "status": "PASS_SHARED_RESTORE_COMPLETE_RELEASE",
        "kappa": admission["kappa"],
        "source_manifest_sha256": manifest,
        "admission_sha256": v.digest(work / "run/candidate/RESULT.json"),
        "release_receipt_sha256": v.digest(receipt_path),
        "fresh_retained_bootstrap": True,
        "profile": v.EXPECTED,
        "scope": "Conditional finite release; inherited theorem hypotheses remain.",
    }


def environment(work):
    env = dict(
        os.environ,
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPYCACHEPREFIX=str(work / "bytecode"),
        OPENBLAS_NUM_THREADS="1",
        OMP_NUM_THREADS="1",
        PYTHONINTMAXSTRDIGITS="0",
    )
    for name in (
        "PYTHONPATH",
        "PYTHONOPTIMIZE",
        "WITNESS_SPEC",
        "WITNESS_RECORD",
        "WITNESS_DISCOVER",
    ):
        env.pop(name, None)
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    work = args.work.resolve()
    rw.need(
        os.name == "posix" and sys.flags.optimize == 0,
        "POSIX and enabled inherited assertions",
    )
    rw.need(
        not work.exists() and not work.is_relative_to(v.ROOT),
        "fresh external workspace",
    )
    v.authenticate()
    work.mkdir(parents=True)
    sys.dont_write_bytecode, sys.pycache_prefix = True, str(work / "bytecode")
    source = work / "pr3015"
    export(args.repo.resolve(), source)
    data = parameters(source, work)
    env = environment(work)
    stages = []
    command = [
        sys.executable,
        "-B",
        str(source / "reproduce.py"),
        "--repo",
        str(args.repo.resolve()),
        "--work",
        str(work / "run"),
        "--jobs",
        "1",
        "--dry-run",
    ]
    stage("source-preflight", command, work, env, stages)
    recipe = v.read(work / "run/PREFLIGHT.json")["commands"]
    rw.need([name for name, _ in recipe] == NAMES, "exact complete predecessor recipe")
    v.save(
        work / "RECIPE.json", {"commands": recipe, "changes": retarget(recipe, data)}
    )
    if args.dry_run:
        print("PREFLIGHT_ONLY_NOT_A_RELEASE", flush=True)
        return
    for name, command in recipe:
        stage(name, command, work, env, stages)
    result = check(work, source, stages)
    v.save(work / "RESULT.json", result)
    print(result["status"], result["kappa"], flush=True)


if __name__ == "__main__":
    main()
