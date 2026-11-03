#!/usr/bin/env python3
"""Check bounded archive inventory/bytes only; never import archived sources."""

import hashlib
import json
import os
import re
import stat
import sys


MAX_FILES = 128
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 8 * 1024 * 1024
MAX_MANIFEST_BYTES = 512 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def main():
    require(len(sys.argv) == 1, "integrity checker accepts no arguments")
    script = os.path.abspath(__file__)
    root = os.path.dirname(script)
    require(stat.S_ISREG(os.lstat(script).st_mode), "checker is not a regular file")
    require(stat.S_ISDIR(os.lstat(root).st_mode), "archive root is not a directory")
    manifest_path = os.path.join(root, "MANIFEST.json")
    manifest_stat = os.lstat(manifest_path)
    require(stat.S_ISREG(manifest_stat.st_mode), "manifest is not a regular file")
    require(manifest_stat.st_size <= MAX_MANIFEST_BYTES, "manifest exceeds size bound")
    with open(manifest_path, "rb") as handle:
        manifest_bytes = handle.read(MAX_MANIFEST_BYTES + 1)
    require(len(manifest_bytes) <= MAX_MANIFEST_BYTES, "manifest grew beyond size bound")
    manifest = json.loads(manifest_bytes, object_pairs_hook=unique_object)
    require(type(manifest) is dict, "manifest is not an object")
    require(set(manifest) == {"schema", "scope", "files"}, "unexpected manifest fields")
    require(manifest["schema"] == "h25-passive-guard-archive-manifest-v1", "unsupported manifest schema")
    require(manifest["scope"] == "ARCHIVE_INTEGRITY_ONLY", "unsupported manifest scope")
    rows = manifest["files"]
    require(type(rows) is list and 1 <= len(rows) <= MAX_FILES, "invalid file count")
    expected = {}
    total_bytes = 0
    for row in rows:
        require(type(row) is dict and set(row) == {"path", "bytes", "sha256", "mode"}, "invalid file row")
        path = row["path"]
        require(type(path) is str and len(path) <= 300, "invalid path")
        require(re.fullmatch(r"[A-Za-z0-9._/-]+", path) is not None, "unsupported path spelling")
        parts = path.split("/")
        require(1 <= len(parts) <= 8 and all(part not in ("", ".", "..") for part in parts), "noncanonical path")
        require(path != "MANIFEST.json" and path not in expected, "duplicate or self-referential path")
        require(type(row["bytes"]) is int and 0 <= row["bytes"] <= MAX_FILE_BYTES, "invalid size")
        require(type(row["sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", row["sha256"]) is not None, "invalid SHA256")
        require(row["mode"] in ("100644", "100755"), "unsupported mode")
        expected[path] = row
        total_bytes += row["bytes"]
    require(total_bytes <= MAX_TOTAL_BYTES, "archive exceeds total size bound")
    expected_directories = set()
    for path in expected:
        parts = path.split("/")
        for index in range(1, len(parts)):
            expected_directories.add("/".join(parts[:index]))
    actual = set()
    for current, directories, files in os.walk(root, followlinks=False):
        require(len(actual) + len(files) <= MAX_FILES + 1, "actual file count exceeds bound")
        require(len(directories) <= len(expected_directories), "directory count exceeds bound")
        for name in directories:
            absolute = os.path.join(current, name)
            relative = os.path.relpath(absolute, root).replace(os.sep, "/")
            require(relative in expected_directories, "undeclared directory: " + relative)
            require(stat.S_ISDIR(os.lstat(absolute).st_mode), "directory alias or special entry")
        for name in files:
            absolute = os.path.join(current, name)
            info = os.lstat(absolute)
            require(stat.S_ISREG(info.st_mode), "nonregular file in archive")
            relative = os.path.relpath(absolute, root).replace(os.sep, "/")
            require(relative not in actual, "duplicate inventory path")
            actual.add(relative)
            if relative == "MANIFEST.json":
                continue
            require(relative in expected, "undeclared file: " + relative)
            row = expected[relative]
            require(info.st_size == row["bytes"], "size mismatch: " + relative)
            executable = bool(info.st_mode & 0o111)
            require(executable == (row["mode"] == "100755"), "mode mismatch: " + relative)
            digest = hashlib.sha256()
            read_bytes = 0
            with open(absolute, "rb") as handle:
                for chunk in iter(lambda: handle.read(65536), b""):
                    read_bytes += len(chunk)
                    require(read_bytes <= row["bytes"], "file grew: " + relative)
                    digest.update(chunk)
            require(read_bytes == row["bytes"], "file shrank: " + relative)
            require(digest.hexdigest() == row["sha256"], "SHA256 mismatch: " + relative)
    require(actual == set(expected) | {"MANIFEST.json"}, "missing declared archive files")
    print(json.dumps({
        "status": "PASS_ARCHIVE_INTEGRITY_ONLY",
        "files": len(expected),
        "payload_bytes": total_bytes,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "candidate_import_or_execution": False,
        "semantic_acceptance": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        result = main()
    except Exception as error:
        print(json.dumps({"status": "FAIL_ARCHIVE_INTEGRITY", "reason": str(error)}, sort_keys=True), file=sys.stderr)
        result = 1
    raise SystemExit(result)
