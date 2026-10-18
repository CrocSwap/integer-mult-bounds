"""Check PR-local source history and exact offline archive bytes. Apache-2.0."""

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path, PurePosixPath

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def source_specs(sources):
    rows = sources["files"]
    require(
        isinstance(rows, list) and 1 <= len(rows) <= 32, "source inventory capacity"
    )
    result = []
    for row in rows:
        name = row["path"]
        path = PurePosixPath(name)
        require(not path.is_absolute() and ".." not in path.parts, "source path")
        pin = row.get("pin", "base_commit:" + name)
        if pin == "base_commit:" + name:
            commit = sources["base_commit"]
        else:
            match = re.fullmatch(r"head:([0-9a-f]{40}):(.+)", pin)
            require(match is not None and match[2] == name, "source pin syntax")
            commit = match[1]
        require(re.fullmatch(r"[0-9a-f]{40}", commit) is not None, "source commit")
        result.append((row, commit, name))
    return result


def check_history(sources, root):
    specs = source_specs(sources)
    git = shutil.which("git")
    require(git is not None, "Git is required for source-history validation")
    for row, commit, name in specs:
        reachable = subprocess.run(
            [git, "merge-base", "--is-ancestor", commit, "HEAD"],
            cwd=root,
            capture_output=True,
            timeout=10,
            check=False,
        )
        require(
            reachable.returncode == 0,
            "source commit is not reachable from PR history: " + commit + ":" + name,
        )
        blob = subprocess.run(
            [git, "cat-file", "blob", commit + ":" + name],
            cwd=root,
            capture_output=True,
            timeout=10,
            check=True,
        ).stdout
        require(
            hashlib.sha256(blob).hexdigest() == row["sha256"],
            "committed source hash: " + name,
        )
    return len(specs)


def check_export(sources, root):
    archived = 0
    checked = 0
    for row, _, name in source_specs(sources):
        if "original_pin" not in row and row["usage"] != "input":
            continue
        data = (root / name).read_bytes()
        require(
            hashlib.sha256(data).hexdigest() == row["sha256"],
            "export source hash: " + name,
        )
        checked += 1
        archived += "original_pin" in row
    require(archived == 4, "four exact predecessor source archives required")
    return checked


def failure_controls(sources, root, export_only):
    corrupt = copy.deepcopy(sources)
    archived = next(row for row in corrupt["files"] if "original_pin" in row)
    archived["sha256"] = "0" * 64
    try:
        check_export(corrupt, root)
    except ValueError as error:
        require("export source hash" in str(error), "wrong archive failure control")
    else:
        raise ValueError("changed archive escaped source validation")
    if export_only:
        return
    foreign = copy.deepcopy(sources)
    row = foreign["files"][0]
    row["pin"] = "head:" + "0" * 40 + ":" + row["path"]
    try:
        check_history(foreign, root)
    except ValueError as error:
        require("not reachable" in str(error), "wrong unavailable-head failure control")
    else:
        raise ValueError("unavailable source head escaped ancestry validation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="check archived/input bytes without requiring Git history",
    )
    args = parser.parse_args()
    sources = json.loads((PACKAGE / "SOURCES.json").read_bytes())
    if not args.export_only:
        check_history(sources, ROOT)
    count = check_export(sources, ROOT)
    failure_controls(sources, ROOT, args.export_only)
    mode = "EXPORT" if args.export_only else "HISTORY"
    print(
        f"PASS_P112_A3_SOURCE_CLOSURE mode={mode} exported_sources={count} archives=4"
    )


if __name__ == "__main__":
    main()
