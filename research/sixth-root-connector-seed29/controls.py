#!/usr/bin/env python3
"""Isolated certificate/source corruption and read-only relocation checks.

Hanson Sun (@bbMisk), with OpenAI Codex assistance. Apache-2.0.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent
REPO = PACKAGE.parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(package, script):
    return subprocess.run([sys.executable, "-I", "-O", "-B", str(package / script)],
                          cwd=package.parents[1], text=True, capture_output=True, timeout=120)


def main():
    with tempfile.TemporaryDirectory(prefix="sixth-root-controls-") as tmp:
        root = Path(tmp)
        package = root / "research" / PACKAGE.name
        shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns("__pycache__"))
        pins = json.loads((PACKAGE / "SOURCES.json").read_text())
        for source in pins["files"]:
            if source["usage"] == "input":
                target = root / source["path"]
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(REPO / source["path"], target)

        cert = package / "CERTIFICATE.json"
        original = cert.read_bytes()
        changed = json.loads(original)
        # Preserve the total count while claiming a short solution; the full
        # histogram comparison must fail, not just the total-coverage check.
        changed["census"]["13_B2"]["row_coverage_histogram"][0] -= 1
        changed["census"]["13_B2"]["row_coverage_histogram"][7] += 1
        cert.write_text(json.dumps(changed))
        for script, reason in (("verify.py", "certificate mismatch"),
                               ("independent_check.py", "independent histogram mismatch")):
            result = run(package, script)
            require(result.returncode != 0 and reason in result.stderr,
                    "corrupt receipt accepted or wrong rejection: " + script)
        cert.write_bytes(original)

        source_path = root / "research/weighted-signed-connector-seed58/CERTIFICATE.json"
        raw = source_path.read_bytes()
        source_path.write_bytes(raw + b"\n")
        for script in ("verify.py", "independent_check.py"):
            result = run(package, script)
            require(result.returncode != 0 and "source drift" in result.stderr,
                    "source corruption accepted or wrong rejection: " + script)
        source_path.write_bytes(raw)

        paths = [root, *root.rglob("*")]
        before = {str(p.relative_to(root)): p.read_bytes() for p in paths if p.is_file()}
        try:
            for p in paths:
                p.chmod(0o555 if p.is_dir() else 0o444)
            for script, marker in (("verify.py", "PASS_SIXTH_ROOT_CONNECTOR"),
                                   ("independent_check.py", "PASS_INDEPENDENT_SIXTH_ROOT_CONNECTOR")):
                result = run(package, script)
                require(result.returncode == 0 and marker in result.stdout,
                        "read-only relocated replay failed: " + result.stderr[-1000:])
            after = {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}
            require(before == after, "replay mutated its inputs or wrote artifacts")
        finally:
            for p in paths:
                p.chmod(0o755 if p.is_dir() else 0o644)
    print("PASS_SIXTH_ROOT_PACKAGE_CONTROLS receipt_rejections=2 source_rejections=2 "
          "read_only_replays=2 files_unchanged")


if __name__ == "__main__":
    main()
