#!/usr/bin/env python3
"""Offline source-pin, evidence-integrity, and relocation controls. Apache-2.0."""
from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(script, *arguments):
    return subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, arguments)],
                          cwd="/", capture_output=True, text=True)


def main():
    with tempfile.TemporaryDirectory(prefix="triangle package controls ") as directory:
        root = Path(directory)
        package = root / HERE.relative_to(ROOT)
        package.mkdir(parents=True)
        for name in ("verify.py", "SOURCE.json", "EXPECTED.json"):
            shutil.copyfile(HERE / name, package / name)
        files = json.loads((HERE / "SOURCE.json").read_text())["files"]
        for name in files:
            destination = root / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, destination)
        script = package / "verify.py"
        result = run(script)
        require(result.returncode == 0 and "PASS:" in result.stdout, result.stderr)

        # A source edit must fail before the constructor executes.
        source = root / next(iter(files))
        original = source.read_bytes()
        source.write_bytes(original + b"\n# deliberate source mutation\n")
        result = run(script)
        require(result.returncode != 0 and "source pin failed:" in result.stderr, "source corruption escaped")
        source.write_bytes(original)

        # Keep valid JSON but change a proof-relevant count in the saved evidence.
        expected = package / "EXPECTED.json"
        original = expected.read_bytes()
        certificate = json.loads(original)
        certificate["counts"]["same_endpoints"] -= 1
        expected.write_text(json.dumps(certificate))
        result = run(script)
        require(result.returncode != 0 and "certificate mismatch" in result.stderr, "evidence corruption escaped")
        expected.write_bytes(original)

        # An explicit output request cannot replace existing evidence.
        destination = root / "keep.json"
        destination.write_text("sentinel\n")
        result = run(script, "--write", destination)
        require(result.returncode != 0 and "refuse to overwrite" in result.stderr, "overwrite control escaped")
        require(destination.read_text() == "sentinel\n", "existing output changed")

        result = subprocess.run([sys.executable, "-I", "-O", str(script)],
                                cwd="/", capture_output=True, text=True)
        require(result.returncode != 0 and "run without -O" in result.stderr, "optimized execution escaped")
    print("PASS: minimal offline checkout in path with spaces; source/evidence mutations rejected; output preserved; -O rejected.")


if __name__ == "__main__":
    main()
