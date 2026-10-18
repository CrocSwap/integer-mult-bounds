"""Minimal-source relocation and corruption controls for this finite proof.

Prepared for Krishnendu Purohit (@Deftsalt-debug) with substantial OpenAI Codex
assistance. Apache-2.0. No source tree mutations or third-party dependencies.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RELATIVE = HERE.relative_to(ROOT)


def run():
    with tempfile.TemporaryDirectory(prefix="r439 package with spaces ") as tmp:
        root = Path(tmp) / "checkout"
        package = root / RELATIVE
        shutil.copytree(HERE, package, ignore=shutil.ignore_patterns("__pycache__"))
        pins = json.loads((HERE / "SOURCES.json").read_text())
        for name in pins["files"]:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, path)
        command = [sys.executable, "-I", "-B", "-O", str(package / "verify.py")]

        def call(extra=(), reason=None):
            proc = subprocess.run(command + list(extra), cwd=tmp, text=True, capture_output=True)
            output = proc.stdout + proc.stderr
            if reason is None:
                if proc.returncode or "PASS_R439_BLOCK1_SCHEDULE" not in output:
                    raise RuntimeError("relocated verifier failed: " + output)
            elif not proc.returncode or reason not in output:
                raise RuntimeError("wrong corruption outcome for " + reason + ": " + output)

        def corrupt(path, change, reason):
            saved = path.read_bytes()
            try:
                change(path)
                call(reason=reason)
            finally:
                path.write_bytes(saved)

        def change_json(path, change):
            value = json.loads(path.read_text())
            change(value)
            path.write_text(json.dumps(value) + "\n")

        call()
        corrupt(root / pins["execution_inputs"][0],
                lambda p: p.write_bytes(p.read_bytes() + b"\n"), "source hash mismatch")
        corrupt(package / "SOURCES.json",
                lambda p: change_json(p, lambda d: d.update(execution_inputs=[])),
                "source pin coverage mismatch")
        corrupt(package / "CANDIDATE.json",
                lambda p: change_json(p, lambda d: d["registers"].reverse()),
                "unexpected circuit registers")
        corrupt(package / "CANDIDATE.json",
                lambda p: change_json(p, lambda d: d["factors"][1].update(minimum=15)),
                "minimum certificate mismatch")
        corrupt(package / "CERTIFICATE.json",
                lambda p: change_json(p, lambda d: d.update(saved_with_cleanup=11)),
                "certificate mismatch")
        occupied = root / "occupied"
        occupied.mkdir()
        sentinel = occupied / "sentinel"
        sentinel.write_text("preserve me\n")
        call(["--output", str(occupied)], "FileExistsError")
        if sentinel.read_text() != "preserve me\n" or list(occupied.iterdir()) != [sentinel]:
            raise RuntimeError("existing output was modified")
        print("PASS_R439_BLOCK1_PACKAGE minimal_relocation=1 corruption_controls=5 output_preservation=1 optimized=1")


if __name__ == "__main__":
    run()
