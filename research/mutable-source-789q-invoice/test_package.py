#!/usr/bin/env python3
"""Package fault controls for the 789Q invoice. Wentao Li + AI, Apache-2.0."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise SystemExit(f"FAIL_TEST: {message}")


def run(args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, text=True, capture_output=True)


def main():
    # 1) Quick verify against committed certificate.
    proc = run([sys.executable, "-I", "-B", str(HERE / "verify.py"), "--quick"])
    need(proc.returncode == 0, proc.stderr + proc.stdout)
    need("PASS_MUTABLE_SOURCE_789Q_QUICK" in proc.stdout, proc.stdout)

    # 2) -O quick admission.
    proc = run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"), "--quick"])
    need(proc.returncode == 0, proc.stderr + proc.stdout)

    # 3) Certificate drift rejection on a temp copy (quick path).
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        shutil.copytree(HERE, tmp_path / "pkg")
        cert = tmp_path / "pkg" / "CERTIFICATE.json"
        data = json.loads(cert.read_text())
        data["Q7"]["champion_invoice"]["tariff"] = 0
        cert.write_text(json.dumps(data, indent=2) + "\n")
        # Also copy pinned input so pins resolve relative to tmp root layout.
        pinned = tmp_path / "research" / "mutable-source-shear-cost"
        pinned.mkdir(parents=True)
        shutil.copy2(
            ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json",
            pinned / "CERTIFICATE.json",
        )
        # Move package under research/ for ROOT.parents[1] layout expected by verify.
        research = tmp_path / "research" / "mutable-source-789q-invoice"
        if research.exists():
            shutil.rmtree(research)
        shutil.copytree(tmp_path / "pkg", research)
        proc = run(
            [sys.executable, "-I", "-B", str(research / "verify.py"), "--quick"],
            cwd=tmp_path,
        )
        need(proc.returncode != 0, "corrupted certificate should fail quick verify")

    # 4) Source pin corruption rejection.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        pkg = tmp_path / "research" / "mutable-source-789q-invoice"
        shutil.copytree(HERE, pkg)
        pinned = tmp_path / "research" / "mutable-source-shear-cost"
        pinned.mkdir(parents=True)
        src = ROOT / "research" / "mutable-source-shear-cost" / "CERTIFICATE.json"
        (pinned / "CERTIFICATE.json").write_bytes(src.read_bytes() + b"\n")
        proc = run([sys.executable, "-I", "-B", str(pkg / "verify.py"), "--quick"], cwd=tmp_path)
        need(proc.returncode != 0, "source drift should fail")

    # 5) Independent checker.
    proc = run([sys.executable, "-I", "-B", str(HERE / "independent.py")])
    need(proc.returncode == 0, proc.stderr + proc.stdout)

    print("PASS_789Q_PACKAGE_TESTS groups=5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
