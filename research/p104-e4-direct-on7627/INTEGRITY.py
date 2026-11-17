#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check archive byte inventories and optional pinned public predecessor bytes."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


ROOT = Path(__file__).resolve().parent


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def file_at(root, relative, prefix=None):
    posix = PurePosixPath(relative)
    if posix.is_absolute() or any(part in ("", ".", "..") for part in relative.split("/")):
        raise ValueError(f"invalid relative path: {relative}")
    if prefix is not None and not relative.startswith(prefix + "/"):
        raise ValueError(f"path outside {prefix}: {relative}")
    path = root
    for part in posix.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"symlink: {relative}")
    if not path.is_file():
        raise ValueError(f"missing regular file: {relative}")
    return path


def read(relative):
    return json.loads(file_at(ROOT, relative).read_bytes(), object_pairs_hook=unique_keys)


def verify(root, row, path_key, prefix=None):
    relative = row[path_key]
    data = file_at(root, relative, prefix).read_bytes()
    if len(data) != row["size"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
        raise ValueError(f"byte mismatch: {relative}")
    return relative


def local_files(directory):
    return {path.relative_to(ROOT).as_posix() for path in (ROOT / directory).rglob("*")
            if path.is_file() or path.is_symlink()}


def check_mapping(name, directory, count):
    rows = read(name)["entries"]
    paths = {verify(ROOT, row, "public", directory) for row in rows}
    if len(rows) != count or len(paths) != count or paths != local_files(directory):
        raise ValueError(f"incorrect file inventory: {name}")


def check_closure(name, directory, count, predecessor):
    rows = read(name)["entries"]
    local_paths = set()
    external = 0
    for row in rows:
        disposition = row["disposition"]
        if disposition == "published_object":
            local_paths.add(verify(ROOT, row, "public_object", directory))
        elif disposition == "external_predecessor_exact_bytes":
            external += 1
            if predecessor is not None:
                verify(predecessor, row, "public_predecessor_path", "research/p104-courier-restop-on7626")
        elif disposition != "local_original_withheld":
            raise ValueError(f"unknown disposition: {disposition}")
    if len(rows) != count or local_paths != local_files(directory):
        raise ValueError(f"incorrect binding inventory: {name}")
    return external


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predecessor-root", type=Path, help="checkout or byte export rooted at #7627")
    args = parser.parse_args()
    predecessor = args.predecessor_root
    if predecessor is not None and (predecessor.is_symlink() or not predecessor.is_dir()):
        raise ValueError("predecessor root must be a regular directory")
    pins = read("PINS.json")
    rows = pins["files"]
    indexed = {verify(ROOT, row, "path") for row in rows}
    if (pins["schema"] != "e4-export-inventory/v1" or not rows or len(rows) != len(indexed)
            or indexed != local_files(".") - {"PINS.json"}):
        raise ValueError("archive inventory mismatch")
    check_mapping("STATIC-MAP.json", "evidence", 46)
    check_mapping("SIGNED-MAP.json", "signed", 51)
    check_mapping("JOURNAL-SOURCE-MAP.json", "journal-source", 4)
    external = check_closure("SIGNED-CLOSURE-PARTIAL.json", "objects", 75, predecessor)
    external += check_closure("RESOURCE-CLOSURE-PARTIAL.json", "resource-objects", 30, predecessor)
    if external != 44:
        raise ValueError("external reference denominator")
    print(f"PASS {len(indexed)} local archive files; 75 signed and 30 resource binding entries")
    if predecessor is not None:
        print(f"PASS {external} public predecessor references by size and SHA-256")
    else:
        print(f"{external} public predecessor references can be checked with --predecessor-root")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        sys.exit(1)
