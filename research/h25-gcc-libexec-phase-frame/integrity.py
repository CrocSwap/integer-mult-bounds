# SPDX-License-Identifier: Apache-2.0
"""Read-only integrity check for this SOURCE-ARCHIVE; no scientific replay.

Prepared with substantial OpenAI Codex / GPT-6.1 Sol assistance.
Requires an external exact MANIFEST.json SHA256. Archived source is never
imported or executed. No subprocess, network, compiler, decoder or file writes.
Assumes a stable filesystem: separately named reads are not an atomic snapshot
or race-safe custody and do not establish full acquisition provenance.
"""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys


class IntegrityError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise IntegrityError(message)


def payload_identity(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return {
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "git_blob": hashlib.sha1(header + data).hexdigest(),
    }


def canonical_path(value):
    require(isinstance(value, str) and value, "Empty/non-string inventory path")
    parsed = PurePosixPath(value)
    require(not parsed.is_absolute(), "Absolute inventory path")
    require("\\" not in value, "Backslash in inventory path")
    require(parsed.as_posix() == value, "Noncanonical inventory path")
    require(all(part not in ("", ".", "..") for part in parsed.parts),
            "Dot/parent component in inventory path")
    return value


def read_regular(root, relative):
    path = root
    for component in PurePosixPath(relative).parts:
        path = path / component
        require(not path.is_symlink(), "Symlink rejected: " + relative)
    info = path.stat()
    require(stat.S_ISREG(info.st_mode), "Nonregular file: " + relative)
    require(not stat.S_IMODE(info.st_mode) & 0o111,
            "Executable payload rejected: " + relative)
    require(info.st_size <= 8 * 1024 * 1024, "Payload exceeds 8 MiB bound")
    return path.read_bytes()


def check(root, manifest_sha256):
    require(re.fullmatch(r"[0-9a-f]{64}", manifest_sha256) is not None,
            "Manifest SHA256 must be exactly 64 lowercase hex characters")
    require(not root.is_symlink(), "Package-root symlink rejected")
    manifest_raw = read_regular(root, "MANIFEST.json")
    require(len(manifest_raw) <= 2 * 1024 * 1024, "Manifest exceeds 2 MiB bound")
    require(hashlib.sha256(manifest_raw).hexdigest() == manifest_sha256,
            "External manifest SHA256 mismatch")
    manifest = json.loads(manifest_raw)
    require(manifest.get("schema") == "h25-gcc-libexec-phase-frame-manifest-v1",
            "Unexpected manifest schema")
    rows = manifest.get("files")
    require(isinstance(rows, list) and 0 < len(rows) <= 256,
            "Inventory must contain 1..256 rows")
    declared = {}
    total_bytes = 0
    for row in rows:
        require(isinstance(row, dict), "Non-object manifest row")
        relative = canonical_path(row.get("path"))
        require(relative != "MANIFEST.json", "Manifest cannot inventory itself")
        require(relative not in declared, "Duplicate inventory path: " + relative)
        require(row.get("git_mode") == "100644", "Unexpected Git mode: " + relative)
        data = read_regular(root, relative)
        identity = payload_identity(data)
        for key in ("bytes", "sha256", "git_blob"):
            require(row.get(key) == identity[key], key + " mismatch: " + relative)
        declared[relative] = row
        total_bytes += len(data)
    observed = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        require(not path.is_symlink(), "Symlink rejected: " + relative)
        info = path.stat()
        if stat.S_ISDIR(info.st_mode):
            continue
        require(stat.S_ISREG(info.st_mode), "Nonregular path: " + relative)
        observed.add(relative)
    expected = set(declared) | {"MANIFEST.json"}
    require(observed == expected,
            "Exact file inventory mismatch; missing=" + repr(sorted(expected-observed))
            + "; extra=" + repr(sorted(observed-expected)))
    require("VERIFY.json" not in observed, "This archive has no registered replay hook")
    source_map = json.loads(read_regular(root, "SOURCE-MAP.json"))
    require(source_map.get("schema") == "h25-gcc-libexec-phase-frame-source-map-v1",
            "Unexpected source-map schema")
    origin_rows = source_map.get("files")
    require(isinstance(origin_rows, list), "Invalid source-map files")
    origins = set()
    available_pins = 0
    unavailable_pins = 0
    pin_bytes = 0
    for row in origin_rows:
        require(isinstance(row, dict), "Non-object source-map row")
        origin = row.get("origin_path")
        require(isinstance(origin, str) and origin and origin not in origins,
                "Missing or duplicate origin identifier")
        origins.add(origin)
        if row.get("available") is False:
            require(row.get("package_path") is None, "Unavailable origin has payload")
            require(all(row.get(key) is None for key in ("bytes", "sha256", "git_blob")),
                    "Unavailable origin has invented identity")
            require(row.get("role") == "source-pin-body", "Unexpected unavailable role")
            unavailable_pins += 1
            continue
        require(row.get("available") is True, "Invalid availability label")
        relative = canonical_path(row.get("package_path"))
        require(relative in declared, "Source-map payload missing from manifest")
        inventory_row = declared[relative]
        for key in ("bytes", "sha256", "git_blob"):
            require(row.get(key) == inventory_row[key], "Source-map identity mismatch")
        require(row.get("package_git_mode") == inventory_row["git_mode"],
                "Source-map mode mismatch")
        if row.get("role") == "source-pin-body":
            require(relative.startswith("snapshots/pinned/") and relative.endswith(".txt"),
                    "Source-pin body is not an inert .txt snapshot")
            available_pins += 1
            pin_bytes += row["bytes"]
    require((available_pins, unavailable_pins, pin_bytes) == (21, 2, 880523),
            "Declared source-pin inventory mismatch")
    return {
        "status": "ARCHIVE_BYTE_INTEGRITY_ONLY",
        "manifest_sha256": manifest_sha256,
        "regular_files": len(observed),
        "inventoried_payload_files": len(declared),
        "inventoried_payload_bytes": total_bytes,
        "manifest_bytes": len(manifest_raw),
        "available_source_pin_bodies": available_pins,
        "unavailable_source_pin_bodies": unavailable_pins,
        "scientific_replay": False,
        "source_history_or_binary_correspondence_certified": False,
        "custody": "Separately named reads; stable filesystem assumed, no atomic/race-safe custody",
        "full_acquisition_provenance_certified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest-sha256", required=True,
                        help="Externally reviewed exact MANIFEST.json SHA256")
    args = parser.parse_args()
    root = Path(__file__).absolute().parent
    try:
        result = check(root, args.manifest_sha256)
    except (IntegrityError, OSError, ValueError, TypeError, KeyError) as error:
        print("ARCHIVE_INTEGRITY_FAILURE: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
