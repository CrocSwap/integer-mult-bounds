#!/usr/bin/env python3
"""Replay the exact-main omission and the live runner's Git-spelling repair.

Nick Petalas. Apache-2.0. This checks routing, not supplier mathematics.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ALIASES = ("SRC/dep.json", "src/DEP.json", "SRC/DEP.json")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, stderr=subprocess.PIPE, timeout=30)


def baseline():
    sources = json.loads((HERE / "SOURCES.json").read_bytes())
    row = next(row for row in sources["files"] if row["path"] == "scripts/research_package.py")
    expression = sources["base_commit"] + ":" + row["path"]
    raw = git(ROOT, "show", expression)
    require(git(ROOT, "rev-parse", expression).decode().strip() == row["git_blob"], "baseline blob drift")
    require(hashlib.sha256(raw).hexdigest() == row["sha256"], "baseline SHA256 drift")
    return raw


def fixture(root, runner):
    root.mkdir()
    git(root, "init", "-q")
    for key, value in (("user.name", "Fixture"), ("user.email", "fixture@example.invalid"),
                       ("core.autocrlf", "false")):
        git(root, "config", key, value)
    (root / "scripts").mkdir()
    (root / "scripts/research_package.py").write_bytes(runner)
    (root / "src").mkdir()
    (root / "src/dep.json").write_bytes(b"original\n")
    (root / "research/consumer").mkdir(parents=True)
    manifest = root / "research/consumer/VERIFY.json"
    manifest.write_text(json.dumps({"inputs": ["src/dep.json"]}), encoding="utf-8")
    git(root, "add", ".")
    git(root, "-c", "gc.auto=0", "commit", "-qm", "before")
    base = git(root, "rev-parse", "HEAD").decode().strip()
    (root / "src/dep.json").write_bytes(b"changed\n")
    git(root, "add", ".")
    git(root, "-c", "gc.auto=0", "commit", "-qm", "after")
    require(git(root, "diff", "--name-only", "-z", base, "HEAD") == b"src/dep.json\0", "fixture diff drift")
    return base, manifest


def check_version(root, runner, repaired):
    base, manifest = fixture(root, runner)
    output = root.parent / (root.name + "-output")
    for name in (*ALIASES, "src/dep.json"):
        manifest.write_text(json.dumps({"inputs": [name]}), encoding="utf-8")
        output.write_text("existing-output\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-B", str(root / "scripts/research_package.py"),
             "--changed-since", base, "--github-output", str(output)],
            cwd=root, capture_output=True, text=True, encoding="utf-8", timeout=30, check=False)
        if repaired and name in ALIASES:
            require(result.returncode == 1 and "exact Git-tracked input" in result.stderr,
                    "alias did not fail at the Git boundary: " + name)
            require(result.stdout == "" and output.read_text(encoding="utf-8") == "existing-output\n",
                    "failed plan published partial output")
        else:
            expected = {"include": [] if name in ALIASES else [{"package": "research/consumer"}]}
            require(result.returncode == 0 and json.loads(result.stdout) == expected,
                    "baseline omission or canonical positive control differs: " + result.stderr)
    return {"aliases": len(ALIASES), "canonical_controls": 1}


def main():
    old, live = baseline(), (ROOT / "scripts/research_package.py").read_bytes()
    with tempfile.TemporaryDirectory(prefix="replay-head-spelling-") as temporary:
        root = Path(temporary)
        before = check_version(root / "baseline", old, repaired=False)
        after = check_version(root / "live", live, repaired=True)
    require(before == after == {"aliases": 3, "canonical_controls": 1}, "fixture coverage differs")
    print("PASS_REPLAY_INPUT_HEAD_SPELLING baseline_omissions=3 repaired_rejections=3 canonical_controls=2")


if __name__ == "__main__":
    main()
