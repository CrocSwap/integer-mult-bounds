#!/usr/bin/env python3
"""Relocated CLI replay, tamper rejection and output-preservation controls."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = HERE.relative_to(ROOT)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    files = [Path(name) for name in sources["base_files_sha256"]]
    files += [path.relative_to(ROOT) for path in HERE.iterdir() if path.is_file()]
    with tempfile.TemporaryDirectory(prefix="common-flag-check-") as directory:
        relocated = Path(directory)
        for name in files:
            target = relocated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        command = [sys.executable, "-I", "-O", "-B", str(relocated / PACKAGE / "verify.py")]

        def run(success, message, *extra):
            result = subprocess.run(command + list(extra), cwd=relocated.parent,
                                    text=True, capture_output=True, check=False)
            output = result.stdout + result.stderr
            require((result.returncode == 0) == success and message in output, output)

        def hashes():
            return {str(name): hashlib.sha256((relocated / name).read_bytes()).hexdigest()
                    for name in files}

        before = hashes()
        run(True, "PASS_COMMON_FLAG_OBSTRUCTION")
        require(before == hashes(), "read-only replay modified an input")
        source = relocated / "scripts/finite_bit_contract.py"
        original = source.read_bytes()
        source.write_bytes(original + b"\n")
        run(False, "source pin mismatch")
        source.write_bytes(original)

        certificate = relocated / PACKAGE / "EXPECTED.json"
        original = certificate.read_bytes()
        changed = json.loads(original)
        changed["cases"]["sharp_untouched"]["rank_mass"] = 5
        certificate.write_text(json.dumps(changed), encoding="utf-8")
        run(False, "certificate mismatch")
        certificate.write_bytes(original)

        sentinel = relocated / "existing.json"
        sentinel.write_bytes(b"KEEP")
        run(False, "FileExistsError", "--emit", str(sentinel))
        require(sentinel.read_bytes() == b"KEEP", "existing output overwritten")
        fresh = relocated / "regenerated.json"
        run(True, "PASS_COMMON_FLAG_OBSTRUCTION", "--emit", str(fresh))
        require(fresh.read_bytes() == certificate.read_bytes(), "regenerated receipt differs")
    print("PASS_COMMON_FLAG_CLI_CONTROLS relocated optimized read-only source-tamper certificate-tamper no-overwrite regeneration")


if __name__ == "__main__":
    main()
