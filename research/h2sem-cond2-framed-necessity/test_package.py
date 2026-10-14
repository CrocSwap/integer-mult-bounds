#!/usr/bin/env python3
"""Relocation and mutation controls for the F4 condition-2 necessity package."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = "research/h2sem-cond2-framed-necessity"


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("FAIL_PACKAGE_CONTROL: " + message)


def run(argv, cwd: Path, check: bool = True):
    return subprocess.run(
        argv,
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def main() -> None:
    need(sys.version_info[:2] == (3, 12), "Python 3.12 required")
    with tempfile.TemporaryDirectory(prefix="h2sem-cond2-") as tmp:
        dest = Path(tmp) / "repo"
        # Copy only what the verifier needs plus the package.
        needed = [
            "research/h2sem-cond2-framed-necessity",
            "research/e8-bit-p111-tuned/code/xcheck_p.py",
            "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz",
            "research/r439-copy-path-sharing-barrier/CERTIFICATE.json",
            "research/r439-semantic-d-contract-seed10/PROOF.md",
            "certificates/selected-result.json",
            "docs/research/agent-task-catalog.json",
        ]
        for rel in needed:
            src = ROOT / rel
            out = dest / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            if src.is_dir():
                shutil.copytree(src, out)
            else:
                shutil.copy2(src, out)

        good = run([sys.executable, "-I", "-B", f"{PACKAGE}/verify.py"], cwd=dest)
        need(
            "PASS_H2SEM_COND2_FRAMED_NECESSITY" in good.stdout,
            "relocation replay failed:\n" + good.stdout + good.stderr,
        )

        # Mutate a live input pin target's bytes without updating SOURCES.json.
        word = dest / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
        original = word.read_bytes()
        word.write_bytes(original + b"\x00")
        bad_src = run([sys.executable, "-I", "-B", f"{PACKAGE}/verify.py"], cwd=dest, check=False)
        need(bad_src.returncode != 0, "mutated source pin was accepted")
        word.write_bytes(original)

        # Mutate EXPECTED.json receipt.
        expected = dest / PACKAGE / "EXPECTED.json"
        data = json.loads(expected.read_text(encoding="utf-8"))
        data["f4_bill"]["ADDS"] = 0
        expected.write_text(json.dumps(data, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        bad_exp = run([sys.executable, "-I", "-B", f"{PACKAGE}/verify.py"], cwd=dest, check=False)
        need(bad_exp.returncode != 0, "mutated EXPECTED.json was accepted")

    print("PASS_H2SEM_COND2_PACKAGE_CONTROLS relocation+source_pin+expected_mutation")


if __name__ == "__main__":
    main()
