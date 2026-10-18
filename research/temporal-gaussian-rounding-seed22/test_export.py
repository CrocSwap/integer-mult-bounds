#!/usr/bin/env python3
"""Read-only sparse export and real file corruption controls. Apache-2.0."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


def need(ok, message):
    if not ok:
        raise ValueError(message)


with tempfile.TemporaryDirectory(prefix="temporal-gaussian-export-") as temporary:
    export = Path(temporary) / "relocated"
    target = export / PACKAGE
    target.mkdir(parents=True)
    for source in HERE.iterdir():
        if source.is_file():
            shutil.copyfile(source, target / source.name)
    manifest = json.loads((HERE / "VERIFY.json").read_text())
    for name in manifest["inputs"]:
        destination = export / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)

    def run(expected):
        child = subprocess.run([sys.executable, "-I", "-O", "-B", str(target / "verify.py")],
                               cwd=temporary, text=True, capture_output=True, timeout=180)
        output = child.stdout + child.stderr
        need((child.returncode == 0) == (expected == "PASS_"), "unexpected child exit: " + output[-1500:])
        need(expected in output, "missing expected diagnostic: " + output[-1500:])

    files = [p for p in export.rglob("*") if p.is_file()]
    directories = [p for p in export.rglob("*") if p.is_dir()] + [export]
    try:
        for p in files:
            p.chmod(0o444)
        for p in directories:
            p.chmod(0o555)
        run("PASS_")
        receipt = target / "RESULT.json"
        original = receipt.read_bytes()
        wrong = json.loads(original)
        wrong["complete_fixtures"]["forward"]["gaussian"]["scalar_primitives"] += 1
        receipt.chmod(0o644)
        receipt.write_text(json.dumps(wrong))
        receipt.chmod(0o444)
        run("saved result mismatch")
        receipt.chmod(0o644)
        receipt.write_bytes(original)
        receipt.chmod(0o444)
        source = export / "research/complex-dyadic-lowering/lower.py"
        original = source.read_bytes()
        source.chmod(0o644)
        source.write_bytes(original + b"\n")
        source.chmod(0o444)
        run("source SHA256 research/complex-dyadic-lowering/lower.py")
        source.chmod(0o644)
        source.write_bytes(original)
        source.chmod(0o444)
        pins = target / "SOURCES.json"
        wrong = json.loads(pins.read_text())
        wrong["files"] = [r for r in wrong["files"] if r["path"] != "research/community-frontier1094-audit/selected-replay.tar.gz"]
        pins.chmod(0o644)
        pins.write_text(json.dumps(wrong))
        pins.chmod(0o444)
        run("input inventory")
    finally:
        for p in directories:
            p.chmod(0o755)
        for p in files:
            p.chmod(0o644)
print("PASS_TEMPORAL_GAUSSIAN_EXPORT read_only=1 corruptions=3 optimized=1")
