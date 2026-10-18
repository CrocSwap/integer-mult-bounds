#!/usr/bin/env python3
"""Exercise the actual portable commands and corrupted artifacts, without pytest.

Hanson Sun with OpenAI Codex assistance; Apache-2.0.
"""
import gzip
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
FILES = ("model.py", "verify.py", "independent.py", "CERTIFICATE.json",
         "CENSUS.json.gz", "INDEPENDENT.json", "SOURCES.json", "TASK.json",
         "VERIFY.json", "README.md")


def require(ok, message):
    if not ok:
        raise ValueError(message)


def run(script, root, expected, success=True):
    env = dict(os.environ, PYTHONHASHSEED="24")
    result = subprocess.run([sys.executable, "-I", "-O", "-B", str(script)],
                            cwd=root, env=env, text=True, capture_output=True, timeout=240)
    require((result.returncode == 0) == success and expected in result.stdout + result.stderr,
            "subprocess outcome: " + expected + "\n" + result.stdout[-2000:] + result.stderr[-2000:])


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def writable(root):
    for p in [root, *root.rglob("*")]:
        p.chmod(0o755 if p.is_dir() else 0o644)


def main():
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    with tempfile.TemporaryDirectory(prefix="gaussian-unit-package-") as temporary:
        root = Path(temporary)
        package = root / "research" / HERE.name
        package.mkdir(parents=True)
        for name in FILES:
            shutil.copyfile(HERE / name, package / name)
        for row in manifest["files"]:
            if row["usage"] != "input":
                continue
            path = root / row["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / row["path"], path)
        try:
            before = inventory(root)
            for p in root.rglob("*"):
                p.chmod(0o555 if p.is_dir() else 0o444)
            root.chmod(0o555)
            run(package / "verify.py", root, "PASS_GAUSSIAN_UNIT_COMMON_ROUNDING")
            run(package / "independent.py", root, "PASS_INDEPENDENT_LITERAL_GAUSSIAN_GRID")
            require(inventory(root) == before, "read-only export was changed")
            writable(root)

            path = package / "CERTIFICATE.json"
            original = path.read_bytes()
            bad = json.loads(original)
            bad["orientations"]["forward"]["odd_winner"]["delta"] -= 1
            path.write_text(json.dumps(bad))
            run(package / "verify.py", root, "certificate mismatch", success=False)
            path.write_bytes(original)

            path = package / "CENSUS.json.gz"
            original = path.read_bytes()
            payload = json.loads(gzip.decompress(original))
            # Header, compression and JSON whitespace are not mathematical data.
            path.write_bytes(gzip.compress(json.dumps(payload, indent=1).encode(), compresslevel=1, mtime=123456))
            run(package / "verify.py", root, "PASS_GAUSSIAN_UNIT_COMMON_ROUNDING")
            payload["forward"][0]["odd_best"][1] -= 1
            path.write_bytes(gzip.compress(json.dumps(payload).encode(), mtime=0))
            run(package / "verify.py", root, "census mismatch", success=False)
            path.write_bytes(original)

            lower = root / "research/complex-dyadic-lowering/lower.py"
            original = lower.read_bytes()
            lower.write_bytes(original + b"\n# source mutation must be rejected before import\n")
            run(package / "verify.py", root, "source SHA256", success=False)
            lower.write_bytes(original)
            require(inventory(root) == before, "mutation fixtures were not restored")
        finally:
            writable(root)
    print("PASS_GAUSSIAN_PACKAGE_CONTROLS read_only_export=2 corrupted_artifacts=3 equivalent_gzip=1")


if __name__ == "__main__":
    main()
