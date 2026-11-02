"""Check retained package bytes and static metadata; never import pilot code.

Prepared for Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
This checks an archive and bounded fake controls, not native qualification.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import stat
import tempfile


class IntegrityError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise IntegrityError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def json_file(path):
    data = path.read_bytes()
    require(len(data) <= 4 * 1024 * 1024, "metadata size cap exceeded")
    return json.loads(data, object_pairs_hook=unique_object)


def canonical_path(name):
    require(isinstance(name, str) and bool(name), "empty/non-string path")
    path = PurePosixPath(name)
    require(not path.is_absolute() and path.as_posix() == name
            and all(part not in ("", ".", "..") for part in path.parts)
            and "\\" not in name and "\x00" not in name,
            "noncanonical package path: " + repr(name))
    return path


def inventory(root):
    names = set()
    for path in root.rglob("*"):
        require(not path.is_symlink(), "package symlink: " + str(path))
        mode = path.stat().st_mode
        if stat.S_ISDIR(mode):
            continue
        require(stat.S_ISREG(mode), "nonregular package entry: " + str(path))
        name = path.relative_to(root).as_posix()
        canonical_path(name)
        if name != "MANIFEST.json":
            names.add(name)
    return names


def validate_inventory(root, manifest):
    require(manifest.get("schema") == "h25-pilot-archive-manifest-v1", "manifest schema")
    rows = manifest.get("files")
    require(isinstance(rows, list) and 1 <= len(rows) <= 256, "manifest row count")
    names = []
    total = 0
    for row in rows:
        require(isinstance(row, dict), "manifest row type")
        name = row.get("path")
        canonical_path(name)
        require(name != "MANIFEST.json", "manifest cannot hash itself")
        names.append(name)
        require(type(row.get("bytes")) is int and 0 <= row["bytes"] <= 8 * 1024 * 1024,
                "file size domain")
        path = root / name
        for part in (path, *path.parents):
            if part == root.parent:
                break
            require(not part.is_symlink(), "symlink in declared file path")
        data = path.read_bytes()
        total += len(data)
        require(len(data) == row["bytes"], "byte count mismatch: " + name)
        require(hashlib.sha256(data).hexdigest() == row.get("sha256"),
                "SHA256 mismatch: " + name)
        require(hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
                == row.get("git_blob"), "Git blob mismatch: " + name)
    require(total <= 16 * 1024 * 1024, "archive size cap")
    require(len(names) == len(set(names)), "duplicate manifest path")
    require(set(names) == inventory(root), "missing or extra package files")
    return len(names), total


def negative_controls():
    """Independent synthetic payload faults; no archived code is loaded."""
    with tempfile.TemporaryDirectory(prefix="h25-static-integrity-") as temp:
        root = Path(temp)
        data = b"retained synthetic payload\n"
        row = {"path": "payload.txt", "bytes": len(data),
               "sha256": hashlib.sha256(data).hexdigest(),
               "git_blob": hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()}
        manifest = {"schema": "h25-pilot-archive-manifest-v1", "files": [row]}
        target = root / "payload.txt"
        target.write_bytes(data)
        validate_inventory(root, manifest)
        def rejected(action):
            try:
                action()
            except (IntegrityError, OSError, json.JSONDecodeError):
                return
            raise IntegrityError("synthetic invalid fixture was accepted")
        target.write_bytes(b"X" + data[1:])
        rejected(lambda: validate_inventory(root, manifest))
        target.write_bytes(data[:-1])
        rejected(lambda: validate_inventory(root, manifest))
        target.unlink()
        rejected(lambda: validate_inventory(root, manifest))
        target.write_bytes(data)
        extra = root / "extra.txt"
        extra.write_bytes(b"undeclared\n")
        rejected(lambda: validate_inventory(root, manifest))
        extra.unlink()
        rejected(lambda: validate_inventory(root, {**manifest, "files": [row, row]}))
        rejected(lambda: canonical_path("../outside"))
        rejected(lambda: json.loads('{"scope":1,"scope":2}', object_pairs_hook=unique_object))
        return 7


def main():
    root = Path(__file__).resolve().parent
    manifest = json_file(root / "MANIFEST.json")
    count, total = validate_inventory(root, manifest)
    source_map = json_file(root / "SOURCE-MAP.json")
    for row in source_map["files"]:
        canonical_path(row["package_path"])
        data = (root / row["package_path"]).read_bytes()
        require(len(data) == row["bytes"] and hashlib.sha256(data).hexdigest() == row["sha256"],
                "source-map byte identity mismatch")
        require(row["translation"].startswith("NONE;"), "unexpected source translation")
    scope = json_file(root / "SCOPE.json")
    for name in ("query_authorization", "native_execution", "reporter_qualified", "consumer_bridge_qualified",
                 "complete_intended_emission", "full_C05", "full_V03", "full_runtime", "new_budget"):
        require(scope[name] is False, "qualification boundary changed: " + name)
    require(scope["original_activities"] == "22/49" and scope["original_credit_added"] == 0,
            "original activity boundary changed")
    require(scope["policy_accounting"]["canonical_guarded_seconds"] == "94.550533479"
            and scope["policy_accounting"]["supplemental_fake_controls_seconds"] == "0.74"
            and scope["policy_accounting"]["combined_recorded_seconds"] == "95.290533479",
            "retained accounting boundary changed")
    commands = json_file(root / "VERIFY.json")["commands"]
    expected = [
        ["{python}", "-I", "-B", "{package}/verify_integrity.py"],
        ["{python}", "-I", "-B", "{package}/source/v3/test_pilot_controller_v3.py", "-v"],
        ["{python}", "-I", "-B", "-O", "{package}/source/v3/test_pilot_controller_v3.py", "-v"],
    ]
    require([row["argv"] for row in commands] == expected, "unreviewed execution command")
    require([row["timeout_seconds"] for row in commands] == [10, 10, 10], "command cap changed")
    controls = negative_controls()
    print(json.dumps({"status": "PASS_STATIC_ARCHIVE_INTEGRITY", "files": count, "bytes": total,
                      "negative_controls": controls, "controller_imported": False,
                      "native_qualified": False, "history_completeness_claimed": False}, sort_keys=True))


if __name__ == "__main__":
    main()
