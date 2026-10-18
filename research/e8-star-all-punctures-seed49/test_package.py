#!/usr/bin/env python3
"""Relocation, byte-identical regeneration, corruption, and predecessor replay tests."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise RuntimeError(msg)


def run_cmd(args: list[str], cwd: Path, expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        args,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        check=False,
    )
    if expect_success and proc.returncode != 0:
        raise RuntimeError(
            f"Command {args} failed in {cwd} (rc={proc.returncode}):\n"
            f"STDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
    if not expect_success and proc.returncode == 0:
        raise RuntimeError(
            f"Command {args} unexpectedly succeeded in {cwd}:\nSTDOUT:\n{proc.stdout}"
        )
    return proc


def main() -> int:
    pkg_dir = Path(__file__).resolve().parent
    orig_cert_bytes = (pkg_dir / "CERTIFICATE.json").read_bytes()

    with tempfile.TemporaryDirectory(prefix="e8_star_all_punctures_seed49_") as tmp_root:
        relocated = Path(tmp_root) / "package_copy"
        shutil.copytree(pkg_dir, relocated)

        # 1. Run primary verifier and independent checker in relocated directory under -I -O -B
        run_cmd([sys.executable, "-I", "-O", "-B", "verify.py"], cwd=relocated, expect_success=True)
        run_cmd([sys.executable, "-I", "-O", "-B", "independent_check.py"], cwd=relocated, expect_success=True)

        # 2. Verify byte-identical certificate regeneration in relocated directory
        cert_copy = relocated / "CERTIFICATE.json"
        cert_copy.unlink()
        run_cmd([sys.executable, "-I", "-O", "-B", "verify.py"], cwd=relocated, expect_success=False)
        run_cmd(
            [sys.executable, "-I", "-O", "-B", "verify.py", "--write-certificate"],
            cwd=relocated,
            expect_success=True,
        )
        regenerated_bytes = cert_copy.read_bytes()
        require(
            regenerated_bytes == orig_cert_bytes,
            "Regenerated CERTIFICATE.json is not byte-for-byte identical to committed CERTIFICATE.json",
        )

        # 3. Verify that both checkers reject a tampered CERTIFICATE.json (Orbit 2 star_cost 50 -> 49)
        tampered = json.loads(orig_cert_bytes.decode("utf-8"))
        tampered["proposition_2_p56_boundary_classification"]["orbit_2_root_nonorthogonality"]["analysis"][
            "star_cost"
        ] = 49
        cert_copy.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
        run_cmd([sys.executable, "-I", "-O", "-B", "verify.py"], cwd=relocated, expect_success=False)
        run_cmd([sys.executable, "-I", "-O", "-B", "independent_check.py"], cwd=relocated, expect_success=False)

        # 4. Verify that both checkers reject a tampered budget table row (p=72 min_cost_k9 35 -> 34)
        tampered2 = json.loads(orig_cert_bytes.decode("utf-8"))
        tampered2["theorem_4_all_puncture_ratio_certificate"]["budget_table"][72]["min_cost_k9"] = 34
        cert_copy.write_text(json.dumps(tampered2, indent=2) + "\n", encoding="utf-8")
        run_cmd([sys.executable, "-I", "-O", "-B", "verify.py"], cwd=relocated, expect_success=False)
        run_cmd([sys.executable, "-I", "-O", "-B", "independent_check.py"], cwd=relocated, expect_success=False)

        # Restore valid certificate bytes and test source-pin corruption rejection
        cert_copy.write_bytes(orig_cert_bytes)
        pinned_readme = relocated / "sources" / "pr631" / "README.md"
        orig_readme = pinned_readme.read_bytes()
        pinned_readme.write_bytes(orig_readme + b"\n")
        run_cmd([sys.executable, "-I", "-O", "-B", "verify.py"], cwd=relocated, expect_success=False)
        pinned_readme.write_bytes(orig_readme)

        # 5. Replay pinned PR #631 verifier (requires non-optimized mode for its assertions)
        run_cmd(
            [sys.executable, "-I", "-B", "sources/pr631/verify.py"],
            cwd=relocated,
            expect_success=True,
        )

    print(
        "PASS (test_package.py): relocation, -I -O -B execution, byte-identical regeneration, "
        "tampered-certificate rejection, source-pin corruption rejection, and PR #631 replay all succeeded."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
