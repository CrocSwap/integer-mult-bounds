#!/usr/bin/env python3
"""Exercise relocated entry points and proof-relevant corruptions.
Sricharan Vagvala with substantial OpenAI Codex assistance. Apache-2.0.
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


def need(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    with tempfile.TemporaryDirectory(prefix="r439-package-control-") as directory:
        root = Path(directory)
        package = root / "research" / HERE.name
        package.mkdir(parents=True)
        names = ("verify.py", "independent.py", "CERTIFICATE.json", "SOURCES.json")
        for name in names:
            shutil.copyfile(HERE / name, package / name)
        for row in sources["files"]:
            if row["usage"] == "input":
                path = root / row["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / row["path"], path)

        def entry(name, passes, marker):
            result = subprocess.run([sys.executable, "-I", "-O", "-B", str(package / name)],
                                    cwd=root, capture_output=True, text=True, timeout=90)
            need((result.returncode == 0) == passes, "entry-point exit: " + name + result.stderr)
            need(marker in result.stdout + result.stderr, "entry-point reason: " + name + result.stderr)

        before = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in root.rglob("*") if p.is_file()}
        entry("verify.py", True, "PASS_R439_INTERLEAVED_COLUMN_FLOOR")
        entry("independent.py", True, "PASS_INDEPENDENT_INTERLEAVING_FLOOR")
        after = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in root.rglob("*") if p.is_file()}
        need(before == after, "relocated read-only replay changed its inputs")

        source = root / "research/r439-bsection-stars-seed01/candidate.json.gz"
        saved = source.read_bytes()
        source.write_bytes(saved + b"corruption")
        entry("verify.py", False, "source SHA-256")
        entry("independent.py", False, "source SHA-256")
        source.write_bytes(saved)

        exporter = root / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
        saved = exporter.read_bytes()
        exporter.unlink()
        entry("verify.py", False, "FileNotFoundError")
        exporter.write_bytes(saved)

        path = package / "CERTIFICATE.json"
        saved = path.read_text()
        certificate = json.loads(saved)
        certificate["problems"]["ideal303"]["minimum_taps"] = 6
        path.write_text(json.dumps(certificate))
        entry("verify.py", False, "certificate differs")
        entry("independent.py", False, "claimed exact minimum")

        certificate = json.loads(saved)
        certificate["problems"]["ideal303"]["taps"][0][1] += 1
        path.write_text(json.dumps(certificate))
        entry("independent.py", False, "forward five-tap witness")
        path.write_text(saved)
    print("PASS_INTERLEAVING_PACKAGE_CONTROLS relocation=git-free-read-only "
          "source_corruption=both missing_exporter=rejected false_minimum=both wrong_tap=rejected")


if __name__ == "__main__":
    main()
