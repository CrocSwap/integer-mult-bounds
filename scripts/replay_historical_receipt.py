#!/usr/bin/env python3
"""Explicit historical-only replay of two frozen source/credit receipts.

The generic live-input validator is unchanged. This adapter authenticates and
isolates original bytes; success never claims that today's inputs match them.
Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

import research_package as replay

ROOT = Path(__file__).resolve().parents[1]
FROZEN_COMMIT = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
# Changes to this explicit policy require review. No automatic historical
# fallback exists for other packages or for the default live validator.
POLICY = {
    "research/pr636-family-witness-manifest-receipt": {
        "package_commit": FROZEN_COMMIT,
        "package_tree": "23693de73801a0987c80fb0eed1c8e45a5206890",
        "base_commit": "1f7a934975e5eacaf83511c9ac870263bf095e05",
        "manifest_sha256": {
            "SOURCES.json": "9f18c9391184a197b338a1b3c7b43ddc571b2c49e5aac0f283e9e8e76d7d14f5",
            "VERIFY.json": "18a182e83005ee6b9745037f524098dbd8b28b389a6213ef98b1010f3e8adb38",
        },
        "inputs": ("docs/research/pr-ledger.json", "research/larger-gain/MANIFEST.json"),
        "git_inputs": ("research/larger-gain/NOTICE", "research/larger-gain/README.md"),
    },
    "research/pr1-retention-receipt": {
        "package_commit": FROZEN_COMMIT,
        "package_tree": "334d46aae47e139ca26229f8bf6e7d6556e585c8",
        "base_commit": "d8e0f83f00191df62174b641e9fff055c357f641",
        "manifest_sha256": {
            "SOURCES.json": "8460f7af7e1b89f2389fcb1870eec63fc220d65ff6b0db41d0e5e735ca3c524d",
            "VERIFY.json": "e070bc8ffc93911bdfc669671063f23dae1f0c290d5c72c82e1992a07beb4252",
        },
        "inputs": ("CITATION.cff", "CONTRIBUTORS.md", "Makefile", "NOTICE", "README.md",
                   "docs/reproducibility.md", "docs/research/pr-ledger.json",
                   "research/overnight-pr-review-20261009/dispositions.json",
                   "research/overnight-pr-review-20261009/source-inventory.json"),
        "git_inputs": (),
    },
}


ADAPTER = "scripts/replay_historical_receipt.py"
REGRESSION = "tests/test_research_historical_receipts.py"
WRAPPER_NOTICE = """
## Explicit historical-only registered replay

The registered command now authenticates and replays the original package at
`20ecf2891d80b5acf18d980b2164fb44ea7faa90` against its original pinned base.
It does not validate today's ledger, contributor list, or other live input
bytes. The original SOURCES.json, VERIFY.json, verifier and evidence are read
unchanged from that commit into an isolated temporary tree. Current source
rows keep their exact original commit/blob/SHA256 pins as historical provenance.

Only these three wrapper files (README.md, SOURCES.json and VERIFY.json) may
differ from the frozen package, and the adapter checks their exact approved
transformation. All current verifier and evidence bytes must still equal the
original tree. The original positive and negative controls run without edits;
materialized and live package/input files must remain unchanged afterward.
`PASS_HISTORICAL_RECEIPT_ONLY` is a historical source/credit result, not a
current-state validation, new scientific acceptance, or closure decision.

Run the historical adapter with Python 3.12:

```sh
python3 -B scripts/replay_historical_receipt.py --package {package}
```

The generic runner's default live-input contract is unchanged. To inspect the
original live contract, replay the original frozen package metadata against live
inputs: it correctly rejects later byte drift. The registered wrapper declares
the adapter and its focused tests as inputs, so changes select these two
consumers without a global shared-workflow invalidation. See
[the replay guide](../../docs/research/research-package-guide.md#historical-sourcecredit-receipt-adapters).
"""


def wrapper_files(files, package):
    """Exact, reviewable transformation; never accept arbitrary metadata drift."""
    sources = json.loads(files[package + "/SOURCES.json"][1])
    for row in sources["files"]:
        row["usage"] = "provenance"
    original = json.loads(files[package + "/VERIFY.json"][1])
    manifest = copy.deepcopy(original)
    manifest["inputs"] = [*original["inputs"], ADAPTER, REGRESSION]
    manifest["commands"] = [
        {"argv": ["{python}", "-B", ADAPTER, "--package", "{package}"],
         "timeout_seconds": 480,
         "checks": "Historical-only replay: authenticate the exact frozen package and original source pins, "
                   "run unchanged original commands and failure controls in an isolated Git snapshot, "
                   "and require historical/live bytes unchanged; does not validate today's input bytes."},
        {"argv": ["{python}", "-B", "-m", "unittest", "discover", "-s", "tests",
                  "-p", "test_research_historical_receipts.py", "-v"],
         "timeout_seconds": 120,
         "checks": "Focused historical-adapter regression controls for wrong history/pins, path aliases, "
                   "missing inputs, wrapper/code/evidence drift, isolation and unchanged-file gates; "
                   "the generic live-input validator remains strict."},
    ]
    result = {package + "/" + name: ("100644", (json.dumps(value, indent=2) + "\n").encode())
              for name, value in (("SOURCES.json", sources), ("VERIFY.json", manifest))}
    readme = files[package + "/README.md"][1]
    result[package + "/README.md"] = ("100644", readme + WRAPPER_NOTICE.format(package=package).encode())
    return result


def need(condition, message):
    if not condition:
        raise ValueError(message)


def safe_path(name):
    path = replay.canonical_relative_path(name)
    need(".git" not in [part.lower().rstrip(" .") for part in path.parts]
         and not name.startswith(":") and not any(ord(char) < 32 for char in name), "unsafe historical path: " + name)
    return path


def git_environment():
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_CONFIG_NOSYSTEM="1",
               GIT_CONFIG_GLOBAL=os.devnull, GIT_OPTIONAL_LOCKS="0", GIT_NO_LAZY_FETCH="1")
    return env


def git(root, *args, **kwargs):
    return subprocess.run(["git", "--no-replace-objects", "--literal-pathspecs", *args],
                          cwd=root, env=git_environment(), check=True, timeout=60,
                          stderr=subprocess.PIPE, **kwargs)


def output(root, *args):
    return git(root, *args, stdout=subprocess.PIPE).stdout


def object_bytes(root, oid, kind):
    need(isinstance(oid, str) and re.fullmatch(r"[0-9a-f]{40}", oid), "invalid historical object ID")
    need(output(root, "cat-file", "-t", oid).strip() == kind.encode(), "wrong Git object type: " + oid)
    raw = output(root, "cat-file", kind, oid)
    actual = hashlib.sha1(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    need(actual == oid, "Git object bytes do not match their ID: " + oid)
    return raw


def tree_rows(root, commit, path=None, recursive=False):
    argv = ["ls-tree", "-z"] + (["-r", "-t"] if recursive else []) + [commit]
    if path is not None:
        safe_path(path)
        argv += ["--", path]
    rows = {}
    for record in output(root, *argv).split(b"\0"):
        if not record:
            continue
        header, raw_path = record.split(b"\t", 1)
        mode, kind, oid = header.decode("ascii").split()
        name = raw_path.decode("utf-8")
        safe_path(name)
        need(name not in rows, "duplicate Git tree path: " + name)
        rows[name] = (mode, kind, oid)
    return rows


def pinned_file(root, commit, name):
    rows = tree_rows(root, commit, name)
    need(set(rows) == {name}, "missing exact historical input: " + name)
    mode, kind, oid = rows[name]
    need(mode in ("100644", "100755") and kind == "blob", "non-regular historical input: " + name)
    return mode, oid, object_bytes(root, oid, "blob")


def package_snapshot(root, package):
    safe_path(package)
    directory = replay.symlink_free_relative_path(root, package)
    need(directory.is_dir(), "missing live package: " + package)
    names = []
    for parent, dirs, files in os.walk(directory, followlinks=False):
        for name in dirs + files:
            path = Path(parent) / name
            need(not path.is_symlink(), "symlink in live package: " + str(path))
        names += [(Path(parent) / name).relative_to(root).as_posix() for name in files]
    return file_snapshot(root, names)


def file_snapshot(root, names):
    result = {}
    for name in names:
        safe_path(name)
        path = replay.relative_file(root, name)
        mode = path.stat().st_mode
        need(stat.S_ISREG(mode), "non-regular live file: " + name)
        result[name] = (stat.S_IMODE(mode), hashlib.sha256(path.read_bytes()).hexdigest())
    return result


def authenticate(root, package, policy):
    package_commit, base = policy["package_commit"], policy["base_commit"]
    # Grafts are rejected, not trusted as evidence; replacement objects and
    # inherited Git config/environment are disabled in every Git operation.
    grafts = Path(output(root, "rev-parse", "--git-path", "info/grafts").decode().strip())
    if not grafts.is_absolute():
        grafts = root / grafts
    need(not grafts.exists() or not grafts.read_bytes().strip(), "legacy Git grafts are not supported")
    objects = set()
    for commit in {package_commit, base}:
        raw = object_bytes(root, commit, "commit")
        root_tree = raw.split(b"\n", 1)[0].decode().removeprefix("tree ")
        object_bytes(root, root_tree, "tree")
        objects.update((commit, root_tree))
        objects.update(row[2] for row in tree_rows(root, commit, recursive=True).values() if row[1] == "tree")
    package_entry = tree_rows(root, package_commit, package).get(package)
    need(package_entry == ("040000", "tree", policy["package_tree"]), "frozen package tree mismatch")
    files = {}
    for name, (mode, kind, oid) in tree_rows(root, package_commit, package, recursive=True).items():
        if kind == "tree":
            continue
        need(name.startswith(package + "/") and mode in ("100644", "100755") and kind == "blob",
             "non-regular frozen package entry: " + name)
        files[name] = (mode, object_bytes(root, oid, "blob"))
        objects.add(oid)
    for name, expected in policy["manifest_sha256"].items():
        need(hashlib.sha256(files[package + "/" + name][1]).hexdigest() == expected,
             "frozen original manifest digest mismatch: " + name)
    approved = {**files, **wrapper_files(files, package)}
    live = package_snapshot(root, package)
    need(set(live) == set(files), "live package inventory differs from the frozen original")
    for name, (mode, raw) in approved.items():
        need(live[name][1] == hashlib.sha256(raw).hexdigest()
             and bool(live[name][0] & 0o111) == (mode == "100755"), "live package drift: " + name)
    sources = json.loads(files[package + "/SOURCES.json"][1])
    manifest = json.loads(files[package + "/VERIFY.json"][1])
    need(sources["base_commit"] == base, "historical base differs from approved policy")
    need(manifest["inputs"] == list(policy["inputs"]), "historical input list differs from approved policy")
    source_names = set()
    for row in sources["files"]:
        name = row["path"]
        safe_path(name)
        need(name not in source_names and name not in files, "duplicate or overlapping historical source: " + name)
        source_names.add(name)
        need(replay.source_pin(row, base) == base + ":" + name, "only approved base-commit source pins are supported")
        mode, oid, raw = pinned_file(root, base, name)
        need(oid == row["git_blob"], "historical input Git blob mismatch: " + name)
        need(hashlib.sha256(raw).hexdigest() == row["sha256"], "historical input SHA256 mismatch: " + name)
        files[name] = (mode, raw)
        objects.add(oid)
    need({row["path"] for row in sources["files"] if row["usage"] == "input"} == set(policy["inputs"]),
         "historical live-input pins differ from approved policy")
    for name in policy["git_inputs"]:
        _, oid, _ = pinned_file(root, base, name)
        objects.add(oid)
    # These live bytes may differ from history. Keep them intact, never replace
    # them with old contributors, ledger rows, or other historical input data.
    live_inputs = file_snapshot(root, [*policy["inputs"], ADAPTER, REGRESSION])
    return files, objects, live, live_inputs


def materialize(root, temporary, files, objects, package_commit):
    git(temporary, "init", "--quiet", "--template=")
    # Self-contained object copy: no worktree, alternates, shared object store,
    # links, hooks, refs, or config from the live repository are exposed.
    with tempfile.TemporaryFile() as pack:
        git(root, "pack-objects", "--stdout", input=("\n".join(sorted(objects)) + "\n").encode(), stdout=pack)
        pack.seek(0)
        git(temporary, "index-pack", "--stdin", stdin=pack, stdout=subprocess.PIPE)
    git(temporary, "update-ref", "--no-deref", "HEAD", package_commit)
    for name, (mode, raw) in files.items():
        safe_path(name)
        path = temporary / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        path.chmod(0o755 if mode == "100755" else 0o644)


@contextmanager
def replay_environment():
    previous = os.environ.copy()
    clean = {key: value for key, value in git_environment().items() if not key.startswith("PYTHON")}
    clean["PYTHONDONTWRITEBYTECODE"] = "1"
    os.environ.clear()
    os.environ.update(clean)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(previous)


def run(root, package, check_only=False):
    need(package in POLICY, "package is not approved for historical-only replay: " + package)
    policy = POLICY[package]
    files, objects, live_package, live_inputs = authenticate(root, package, policy)
    print("HISTORICAL_INPUTS_ONLY package=" + package + " base=" + policy["base_commit"]
          + " package_commit=" + policy["package_commit"]
          + " (no validation of today's input bytes)", flush=True)
    try:
        with tempfile.TemporaryDirectory(prefix="historical-receipt-") as directory:
            isolated = Path(directory)
            materialize(root, isolated, files, objects, policy["package_commit"])
            before = file_snapshot(isolated, files)
            before_package = package_snapshot(isolated, package)
            try:
                with replay_environment():
                    if check_only:
                        replay.validate(isolated, package)
                    else:
                        replay.run_package(isolated, package)
            finally:
                need(file_snapshot(isolated, files) == before
                     and package_snapshot(isolated, package) == before_package,
                     "historical replay changed its materialized source/evidence files")
    finally:
        need(package_snapshot(root, package) == live_package
             and file_snapshot(root, live_inputs) == live_inputs,
             "live package or inputs changed during historical replay")
    label = "PASS_HISTORICAL_METADATA_ONLY" if check_only else "PASS_HISTORICAL_RECEIPT_ONLY"
    print(label + " " + package + " base=" + policy["base_commit"]
          + " package_commit=" + policy["package_commit"]
          + " live_inputs_validated=false")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package", required=True)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    try:
        run(ROOT, args.package, args.check_only)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        parser.exit(1, str(exc) + "\n")


if __name__ == "__main__":
    main()
