#!/usr/bin/env python3
"""Capture immutable Git objects; never used by the offline verifier.

Ross Richardson, substantial OpenAI Codex assistance, Apache-2.0.
Run from any checkout containing the six source commits and the research base.
"""
import base64
import gzip
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "abdc6a7002abdbcd9e21bfc5e1a795784deacfdf"
OLD = "b8e829172fc92bbbd6b1eda560ab5d99aebee0df"
NEW = "830971b6b157374ebf941d0ca0b73fd2b956e3e0"
PACKAGE = "research/exact-dft-transfer"
WORKFLOW = ".github/workflows/exact-dft-transfer.yml"
CONTEXT = [
    "certificates/selected-result.json",
    "docs/research/pr-ledger.json",
    "research/community-round9-audit/review-ledger.json",
    "research/community-round9-audit/pr225-replay.log.txt",
]


def git(*args):
    return subprocess.check_output(["git", *args], cwd=HERE.parents[1])


def main():
    objects = {}

    def add(oid):
        if oid not in objects:
            kind = git("cat-file", "-t", oid).decode().strip()
            raw = git("cat-file", kind, oid)
            objects[oid] = {"type": kind, "data": base64.b64encode(raw).decode()}

    def paths(commit, names):
        add(commit)
        add(git("rev-parse", commit + "^{tree}").decode().strip())
        for name in names:
            parts = name.split("/")
            for length in range(1, len(parts) + 1):
                add(git("rev-parse", commit + ":" + "/".join(parts[:length])).decode().strip())

    for head in (OLD, NEW):
        names = git("ls-tree", "-r", "--name-only", head, "--", PACKAGE, WORKFLOW).decode().splitlines()
        paths(head, names)
    source = json.loads(git("show", NEW + ":" + PACKAGE + "/SOURCE.json"))
    for pin in source["suppliers"].values():
        paths(pin["commit"], [pin["path"]])
    paths(BASE, CONTEXT)
    payload = json.dumps({"format": "pr225-git-capsule-v1", "objects": objects}, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    (HERE / "sources.json.gz").write_bytes(gzip.compress(payload, mtime=0))
    print("captured", len(objects), "objects; payload_sha256", hashlib.sha256(payload).hexdigest())


if __name__ == "__main__":
    main()
