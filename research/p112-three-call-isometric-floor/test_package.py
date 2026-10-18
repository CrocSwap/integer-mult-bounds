#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Relocation, no-write replay and reason-specific mutation checks in scratch.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def snapshot(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="p112-three-call-controls-") as directory:
        scratch = Path(directory)
        package = scratch / "research" / "renamed-package"
        shutil.copytree(HERE, package)
        # Git is used only to read historical provenance from the existing object store.
        git_directory = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--absolute-git-dir"],
                                       check=True, capture_output=True, text=True).stdout.strip()
        (scratch / ".git").write_text("gitdir: " + git_directory + "\n")
        for entry in manifest["files"]:
            if entry["usage"] == "input":
                destination = scratch / entry["path"]
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / entry["path"], destination)

        def execute():
            return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                  cwd=scratch, capture_output=True, text=True, timeout=60)

        before = snapshot(scratch)
        positive = execute()
        require(positive.returncode == 0, "relocated positive failed: " + positive.stderr)
        require("PASS_P112_THREE_CALL_ISOMETRIC_FLOOR" in positive.stdout, "missing positive marker")
        require(snapshot(scratch) == before, "default replay wrote files")

        def mutation(name, filename, change, expected):
            path = package / filename
            original = path.read_text()
            modified = change(original)
            require(modified != original, "mutation did not change input: " + name)
            try:
                path.write_text(modified)
                result = execute()
                require(result.returncode != 0 and expected in result.stderr,
                        "wrong mutation result: " + name + "\n" + result.stderr)
            finally:
                path.write_text(original)

        def receipt_change(text):
            data = json.loads(text)
            data["fixtures"][0]["cost"] -= 1
            return json.dumps(data)

        def source_change(text):
            data = json.loads(text)
            next(x for x in data["files"] if x["usage"] == "input")["sha256"] = "0" * 64
            return json.dumps(data)

        def replace_once(text, old, new):
            require(text.count(old) == 1, "mutation target is not unique")
            return text.replace(old, new)

        mutation("false receipt", "EXPECTED.json", receipt_change, "receipt mismatch")
        mutation("source digest", "SOURCES.json", source_change, "source sha256:")
        mutation("ignored chart", "verify.py",
                 lambda s: replace_once(s, "charts[s][label]", "label"),
                 "attainment / rank-seven fixture")
        mutation("false half-frequency", "verify.py",
                 lambda s: replace_once(s, "expected_sum = 3 if sum(a) == sum(c) == 1 else 4",
                                       "expected_sum = 3"),
                 "three-call deletion counts")
        mutation("duplicate receipt key", "EXPECTED.json",
                 lambda s: '{"schema_version": 1, ' + s[1:], "duplicate JSON key: schema_version")
        require(snapshot(scratch) == before, "controls did not restore scratch inputs")
    print("PASS_THREE_CALL_PACKAGE_CONTROLS relocated=1 read_only=1 mutations_rejected=5")


if __name__ == "__main__":
    main()
