"""Behavior and source-contract controls with private writable copies."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from common import PACKAGE, ROOT, authenticate, basis, require
from verify import echelon_spaces


def rejected(operation):
    try:
        operation()
    except ValueError:
        return
    raise ValueError("control accepted invalid input")


def main():
    authenticate()
    rejected(lambda: basis([True]))
    rejected(lambda: basis([512]))
    rejected(lambda: basis([0] * 121))
    rejected(lambda: tuple(echelon_spaces(9, 3)))
    require(len(basis([3, 5, 6])) == 2, "dependent binary rows")
    with tempfile.TemporaryDirectory(prefix="cut33-controls-") as directory:
        private = Path(directory)
        target = private / "research" / PACKAGE.name
        target.mkdir(parents=True)
        # Fresh copies have private inodes and writable modes. No chmod.
        for path in PACKAGE.rglob("*"):
            if path.is_file() and path.suffix != ".pyc":
                destination = target / path.relative_to(PACKAGE)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(path.read_bytes())
        geometry = Path("research/p112-root-simplex-exclusion/geometry.py")
        (private / geometry).parent.mkdir(parents=True)
        (private / geometry).write_bytes((ROOT / geometry).read_bytes())
        manifest = json.loads((target / "SOURCES.json").read_text())
        for field, value in [
            ("schema_version", True),
            ("files", []),
            ("retained_files", []),
        ]:
            mutant = dict(manifest)
            mutant[field] = value
            (target / "SOURCES.json").write_text(json.dumps(mutant))
            rejected(lambda: authenticate(target, private))
        (target / "SOURCES.json").write_text(json.dumps(manifest))
        proof = target / "vendor/pr3299-PROOF.md"
        proof.write_bytes(proof.read_bytes() + b"\nchanged\n")
        rejected(lambda: authenticate(target, private))
        result = subprocess.run(
            [sys.executable, "-O", "-B", str(target / "verify.py")],
            capture_output=True,
            text=True,
            timeout=30,
        )
        require(
            result.returncode != 0 and "source hash" in result.stderr,
            "actual optimized process rejects corrupt source",
        )
        require(
            (PACKAGE / "vendor/pr3299-PROOF.md").read_bytes() != proof.read_bytes(),
            "original untouched",
        )
        shutil.rmtree(target)
    print("PASS_CUT33_CONTROLS boundary=5 source=4 actual_process=1")


if __name__ == "__main__":
    main()
