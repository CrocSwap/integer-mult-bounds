#!/usr/bin/env python3
"""Read-only relocation and source/receipt controls; Apache-2.0, Davidson/Codex."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    with tempfile.TemporaryDirectory(prefix="deferred-package-") as tmp:
        root = Path(tmp) / "export"
        package = root / "research/r439-deferred-native"
        shutil.copytree(HERE, package)
        for row in json.loads((HERE / "SOURCES.json").read_text())["files"]:
            if row["usage"] == "input":
                dst = root / row["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], dst)
        before = tree(root)
        env = dict(os.environ, PYTHONOPTIMIZE="2")

        def run(expected=None):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / "verify.py")],
                                    cwd=tmp, env=env, capture_output=True, text=True)
            if expected:
                need(result.returncode != 0 and expected in result.stderr,
                     "wrong rejection for " + expected + ": " + result.stderr)
            else:
                need(result.returncode == 0 and "PASS_R439_DEFERRED_FINITE" in result.stdout,
                     "relocation failed: " + result.stderr)

        files = [p for p in root.rglob("*") if p.is_file()]
        dirs = sorted([p for p in root.rglob("*") if p.is_dir()], key=lambda p: len(p.parts), reverse=True)
        try:
            for p in files:
                p.chmod(0o444)
            for p in dirs + [root]:
                p.chmod(0o555)
            run()
            need(tree(root) == before, "read-only export changed")
        finally:
            for p in [root] + list(reversed(dirs)):
                p.chmod(0o755)
            for p in files:
                p.chmod(0o644)
        controls = 0
        for path, reason in ((package / "vendor/pr2115/candidate-1188.json.gz", "vendor source hash"),
                             (root / "research/e8-bit-carrier-skeleton/code/bit/checkers/columns_k.cpp", "source hash")):
            raw = path.read_bytes()
            try:
                path.write_bytes(raw + b"\n")
                run(reason)
                controls += 1
            finally:
                path.write_bytes(raw)
        receipt = package / "FINITE.json"
        raw = receipt.read_bytes()
        try:
            changed = json.loads(raw)
            changed["directions"] = 2.0
            receipt.write_text(json.dumps(changed))
            run("finite receipt")
            controls += 1
        finally:
            receipt.write_bytes(raw)
        need(tree(root) == before, "corruption control did not restore export")
        print(f"PASS_DEFERRED_PACKAGE readonly_git_free_files={len(before)} corruption_controls={controls}")


if __name__ == "__main__":
    main()
