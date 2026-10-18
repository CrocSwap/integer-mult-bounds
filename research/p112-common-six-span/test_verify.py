"""Behavioral, source, schema and actual Git-free CLI controls."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from common import (
    GEOMETRY,
    PACKAGE,
    authenticate,
    common_unions,
    direction_bound,
    expected_result,
    require,
)
from independent import direct_subsets_bound
from verify import caller_certificate, parse_census


def reject(action, label):
    try:
        action()
    except (ValueError, KeyError, TypeError, IndexError):
        return
    raise ValueError("control accepted: " + label)


def synthetic_controls():
    # Four different directions on one six-point cut violate the new theorem.
    bad = [[6, [[h, h, "63"] for h in range(4)]]]
    reject(lambda: direction_bound(bad), "four directions on common six")
    reject(lambda: direct_subsets_bound(bad), "reference four directions")
    separate = [[6, [[h, h, str(7 << (3 * h))] for h in range(4)]]]
    require(
        len(common_unions(separate[0][1])) == 11, "separate cuts must not be pooled"
    )
    reject(lambda: common_unions([[True, 0, "1"]]), "Boolean direction")
    reject(lambda: common_unions([[0, 0, str(1 << 112)]]), "oversized root mask")
    reject(lambda: common_unions([[0, 0, "127"]]), "seven-root cut")
    reject(lambda: common_unions([[0, 0, "1"]], True), "Boolean budget")
    reject(lambda: parse_census("C 0 0 0 0\n", [], [], []), "missing class")
    require(
        caller_certificate()["required_independent_directions"] == 6, "literal caller"
    )


def copy_regular_tree(source, target):
    for directory, subdirs, files in os.walk(source):
        require(len(subdirs) <= 16 and len(files) <= 64, "private copy capacity")
        relative = Path(directory).relative_to(source)
        (target / relative).mkdir(parents=True, exist_ok=True)
        for name in subdirs + files:
            require(not (Path(directory) / name).is_symlink(), "copy rejects links")
        for name in files:
            old = Path(directory) / name
            require(old.stat().st_nlink == 1, "copy rejects hard links")
            # Byte copies create fresh writable files; do not copy read-only modes.
            (target / relative / name).write_bytes(old.read_bytes())


def cli_reject(root, script):
    result = subprocess.run(
        [sys.executable, "-O", "-Werror", "-B", str(script)],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    require(result.returncode != 0 and result.stderr, "actual CLI corruption accepted")


def private_controls():
    with tempfile.TemporaryDirectory(
        prefix="common-six-controls-", dir=os.environ.get("TMPDIR")
    ) as tmp:
        root = Path(tmp)
        package = root / "research/p112-common-six-span"
        copy_regular_tree(PACKAGE, package)
        geometry = root / GEOMETRY
        geometry.parent.mkdir(parents=True)
        geometry.write_bytes((PACKAGE.parents[1] / GEOMETRY).read_bytes())
        script = package / "verify.py"
        for name in ("RETAINED.json", "SOURCES.json", "RESULT.json"):
            path = package / name
            original = path.read_bytes()
            data = json.loads(original)
            data["schema_version"] = True
            path.write_text(json.dumps(data))
            cli_reject(root, script)
            path.write_bytes(original)
        path = package / "RETAINED.json"
        original = path.read_bytes()
        data = json.loads(original)
        data["files"][0]["usage"] = "proof"
        path.write_text(json.dumps(data))
        cli_reject(root, script)
        path.write_bytes(original)
        for source in sorted((package / "vendor").iterdir()) + [geometry]:
            original = source.read_bytes()
            source.write_bytes(original + b"\n# corruption\n")
            cli_reject(root, script)
            source.write_bytes(original)


def run():
    authenticate()
    expected = expected_result()
    require(
        direction_bound(expected["classes"])["maximum_projective_directions"] == 3,
        "positive common-six table",
    )
    reject(
        lambda: direction_bound(expected["classes"], 2),
        "five-cut bound cannot substitute",
    )
    synthetic_controls()
    private_controls()
    return {
        "status": "PASS_P112_COMMON_SIX_CONTROLS",
        "groups": 7,
        "actual_corrupted_cli_runs": 10,
        "optimized": not __debug__,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
