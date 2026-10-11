#!/usr/bin/env python3
"""Run the standalone certificate checks and optional JSON execution record.

No external dependency, download, Git checkout, solver, or network access.
Apache-2.0.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="optional full JSON run record")
    args = parser.parse_args()
    report = {
        "schema": "pr288-standalone-run-v1",
        "python": platform.python_version(),
        "system": platform.system(),
        "machine": platform.machine(),
        "implementation": platform.python_implementation(),
        "stages": [],
    }

    def run(label: str, arguments: list[str]) -> None:
        start = time.perf_counter()
        completed = subprocess.run([sys.executable, *arguments], cwd=ROOT,
                                   text=True, capture_output=True, check=False)
        stage = {
            "label": label,
            "command": ["python3", *arguments],
            "exit_code": completed.returncode,
            "elapsed_seconds": round(time.perf_counter() - start, 6),
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
        report["stages"].append(stage)
        print(f"{label}: {'PASS' if completed.returncode == 0 else 'FAIL'}")
        if completed.returncode:
            raise RuntimeError(label)

    try:
        run("independent exact certificate checker", ["-B", "check_certificate.py"])
        run("24 regression tests", ["-B", "-m", "unittest", "discover", "-s", "tests", "-v"])
        run("24 regression tests under optimization", ["-O", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"])
        with tempfile.TemporaryDirectory(prefix="pr288-certificate-") as temporary:
            generated = Path(temporary) / "certificate.json"
            run("deterministic rediscovery", ["-B", "produce_certificate.py", "--output", str(generated)])
            same = generated.read_bytes() == (ROOT / "certificate.json").read_bytes()
            report["regenerated_certificate_byte_identical"] = same
            if not same:
                raise RuntimeError("rediscovery differs from distributed certificate")
            run("check regenerated certificate", ["-B", "check_certificate.py", "--certificate", str(generated)])
        report["status"] = "ALL_OFFLINE_CHECKS_PASSED"
    except (OSError, RuntimeError) as error:
        report["status"] = "FAILED"
        report["error"] = str(error)
    report["checked_input_sha256"] = {
        str(path): hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        for path in ("instance.json", "certificate.json", "PROOF.md", "check_certificate.py",
                     "produce_certificate.py", "tests/test_certificate.py")
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["status"])
    return 0 if report["status"] == "ALL_OFFLINE_CHECKS_PASSED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
