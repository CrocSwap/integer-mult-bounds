#!/usr/bin/env python3
"""Replay the unchanged PR3563 finding on its authenticated historical inputs.

This adapter does not apply the old previous_record assertion to a new frontier.
Current navigation remains checked by tests/test_research_current_status.py.
Apache-2.0; prepared for Clear1nsight with substantial OpenAI assistance.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
# Canonical upstream introduction, reachable from a clean upstream checkout.
# The fork publication f4657a0... carries the same manifest blob, but is not
# upstream ancestry and must not be supplied only by a developer's object cache.
PUBLICATION = "d11655a9fd1c7eedc52e0e9720158bd17d29192a"
PACKAGE = "research/historical-1042-link"
ORIGINAL = {
    "verify.py": "12170922e5cd84746089d022f103bfe931fb8a15",
    "test_verify.py": "140840530cbd9b4fdd80d8fa067334b61bfa4c17",
    "RESULT.json": "a9d58d28814fc4a7c9b50a165b48d1a4f52d1892",
    "SOURCES.json": "c6119ca5a8233edd0f8ed3a2e606de5b088d9fcf",
}
INPUTS = {
    "docs/research/current-status.md",
    "certificates/selected-result.json",
    "certificates/checkpoints/frontier1042.json",
}


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def blob_id(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def checked_path(path: str) -> str:
    require(isinstance(path, str), "Non-text historical path")
    p = PurePosixPath(path)
    require(not p.is_absolute() and str(p) == path and ".." not in p.parts
            and "\\" not in path and "\0" not in path, "Unsafe historical path")
    return path


def git_bytes(root: Path, spec: str) -> bytes:
    env = dict(os.environ)
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    result = subprocess.run(
        ["git", "--no-replace-objects", "cat-file", "blob", spec], cwd=root,
        env=env, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        timeout=30,
    )
    return result.stdout


def authenticated_input(root: Path, base: str, row: dict) -> bytes:
    path = checked_path(row["path"])
    require(len(base) == 40 and all(c in "0123456789abcdef" for c in base),
            "Invalid historical base")
    data = git_bytes(root, base + ":" + path)
    require(blob_id(data) == row["git_blob"], "Historical Git blob mismatch: " + path)
    require(hashlib.sha256(data).hexdigest() == row["sha256"],
            "Historical SHA256 mismatch: " + path)
    return data


def collect(root: Path = ROOT, here: Path = HERE) -> tuple[dict[str, bytes], dict]:
    raw = git_bytes(root, PUBLICATION + ":" + PACKAGE + "/SOURCES.json")
    require(blob_id(raw) == ORIGINAL["SOURCES.json"], "Original manifest changed")
    manifest = json.loads(raw)
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    require(len(rows) == len(INPUTS) and {r["path"] for r in rows} == INPUTS,
            "Original input inventory changed")
    payload = {PACKAGE + "/SOURCES.json": raw}
    for name in ("verify.py", "test_verify.py", "RESULT.json"):
        path = here / name
        require(path.is_file() and not path.is_symlink(), "Missing/aliased frozen file: " + name)
        data = path.read_bytes()
        require(blob_id(data) == ORIGINAL[name], "Frozen implementation/receipt changed: " + name)
        payload[PACKAGE + "/" + name] = data
    for row in rows:
        data = authenticated_input(root, manifest["base_commit"], row)
        payload[row["path"]] = data
        if row["path"] == "certificates/checkpoints/frontier1042.json":
            require((root / row["path"]).read_bytes() == data, "Live 1042 checkpoint drift")
    return payload, manifest


def main() -> None:
    payload, manifest = collect()
    with tempfile.TemporaryDirectory(prefix="historical-1042-replay-") as directory:
        root = Path(directory)
        for relative, data in payload.items():
            path = root / checked_path(relative)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        flags = ["-I", "-B"] + (["-O"] if sys.flags.optimize else [])
        for name in ("verify.py", "test_verify.py"):
            subprocess.run([sys.executable, *flags, str(root / PACKAGE / name)],
                           cwd=root, check=True, timeout=30)
        require(all((root / p).read_bytes() == b for p, b in payload.items()),
                "Historical replay changed its inputs or receipt")
    print("PASS_HISTORICAL_1042_SNAPSHOT base=" + manifest["base_commit"]
          + " current_frontier_not_asserted=true")


if __name__ == "__main__":
    main()
