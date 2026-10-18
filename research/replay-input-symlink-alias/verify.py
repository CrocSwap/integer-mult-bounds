#!/usr/bin/env python3
"""Replay the source-bound dependency-alias counterexample. Apache-2.0."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNNER = "scripts/research_package.py"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(raw, label):
    module = ModuleType(label)
    module.__file__ = str(ROOT / RUNNER)
    # These are the authenticated historical source and the current artifact
    # under test. Neither load consults a bytecode cache.
    exec(compile(raw, module.__file__, "exec"), module.__dict__)
    return module


def historical_source():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    rows = [row for row in sources["files"] if row["path"] == RUNNER]
    require(len(rows) == 1 and rows[0]["usage"] == "provenance", "unique historical runner pin")
    raw = subprocess.run(
        ["git", "show", sources["base_commit"] + ":" + RUNNER],
        cwd=ROOT, check=True, capture_output=True, timeout=30).stdout
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    require(hashlib.sha256(raw).hexdigest() == rows[0]["sha256"], "historical runner SHA256")
    require(blob == rows[0]["git_blob"], "historical runner Git blob")
    return raw


def reject(operation):
    try:
        operation()
    except ValueError as exc:
        require("symlink" in str(exc), "must reject the filesystem alias explicitly")
        return
    raise ValueError("symlink alias unexpectedly accepted")


def main():
    before = load(historical_source(), "historical_runner")
    after = load((ROOT / RUNNER).read_bytes(), "current_runner")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        (root / "src").mkdir()
        (root / "src/dep.json").write_bytes(b'{"proof":1}')
        (root / "alias").symlink_to("src", target_is_directory=True)
        package = root / "research/fixture"
        package.mkdir(parents=True)
        (package / "VERIFY.json").write_text(json.dumps({"inputs": ["alias/dep.json"]}))
        require(before.relative_file(root, "alias/dep.json").read_bytes() == b'{"proof":1}',
                "predecessor accepts the parent alias")
        (root / "src/dep.json").write_bytes(b'{"proof":2}')
        require(before.plan(root, ["src/dep.json"]) == [], "predecessor skips target change")
        reject(lambda: after.relative_file(root, "alias/dep.json"))
        reject(lambda: after.plan(root, ["src/dep.json"]))
        (package / "VERIFY.json").write_text(json.dumps({"inputs": ["src/dep.json"]}))
        require(after.plan(root, ["src/dep.json"]) == ["research/fixture"], "target path selects")
        (root / "src/dep.json").unlink()
        (root / "src").rmdir()
        require(after.plan(root, ["src/dep.json"]) == ["research/fixture"], "deletion selects")
    print("PASS_REPLAY_INPUT_SYMLINK_ALIAS before=accepted-and-skipped after=rejected deletion=selected")


if __name__ == "__main__":
    main()
