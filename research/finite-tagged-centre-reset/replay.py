"""Check the frozen local reset and complete policy family in sequence."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


HERE = Path(__file__).resolve().parent
REVIEW = Path("frozen/work/centre-encoding-campaign-20261014/lanes/paired-package-review")
CHECKS = (
    ("tagged-grid", REVIEW / "tagged-grid-review/check_tagged_grid.py",
     "PASS_INDEPENDENT_TAGGED_GRID_LOCAL_CONTRACT"),
    ("reset-policies", REVIEW / "exact-reset-policy-review/check_policies.py",
     "PASS_INDEPENDENT_ALL_PURE_RESET_POLICIES"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path,
                        help="A new directory for the receipts and logs")
    args = parser.parse_args()
    out = args.out.resolve()
    require(not out.exists(), "The output directory must be new")
    require(out.parent.is_dir(), "The output parent must exist")
    require(not out.is_relative_to(HERE), "Keep output outside the frozen package")
    require(shutil.disk_usage(out.parent).free >= 3 * 1024**3,
            "Keep at least 3 GiB of free disk space")

    manifest = json.loads((HERE / "MANIFEST.json").read_text())
    found = {str(path.relative_to(HERE)) for path in HERE.rglob("*")
             if path.is_file() and path.name != "MANIFEST.json"}
    require(found == set(manifest["files"]), "The package file inventory changed")
    for name, pin in manifest["files"].items():
        path = HERE / name
        require(not path.is_symlink(), "A package input must not be a symlink")
        require(sha256(path.read_bytes()).hexdigest() == pin, "Package pin: " + name)

    out.mkdir()
    env = os.environ.copy()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
        env[key] = "1"
    results = []
    started = time.monotonic()
    for label, relative, status in CHECKS:
        receipt = out / (label + ".json")
        command = [sys.executable, "-I", "-O", "-B", str(HERE / relative),
                   "--out", str(receipt)]
        begin = time.monotonic()
        with (out / (label + ".stdout.txt")).open("w") as stdout:
            with (out / (label + ".stderr.txt")).open("w") as stderr:
                process = subprocess.run(command, cwd=out, env=env,
                                         stdout=stdout, stderr=stderr, check=False)
        require(process.returncode == 0, "Checker failed; read its output: " + label)
        actual = json.loads(receipt.read_text())
        expected = json.loads((HERE / relative.parent / "CHECKS.json").read_text())
        require(actual.get("status") == status, "Checker status: " + label)
        require(actual == expected, "The complete reviewed receipt changed: " + label)
        results.append({"check": label, "status": status,
                        "seconds": round(time.monotonic() - begin, 6),
                        "receipt_sha256": sha256(receipt.read_bytes()).hexdigest(),
                        "complete_receipt_matches_frozen_review": True,
                        "command": command})
        print(status, flush=True)

    report = {
        "status": "PASS_FINITE_TAGGED_CENTRE_RESET_PACKAGE",
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "seconds": round(time.monotonic() - started, 6),
        "manifest_sha256": sha256((HERE / "MANIFEST.json").read_bytes()).hexdigest(),
        "package_files_checked": len(found),
        "execution": "Two standard-library checkers run in sequence, one process at a time",
        "checks": results,
        "inherited_checks_not_run": [
            "Complete native phase and wrapper audit",
            "Physical canonical phase and grid review",
            "Historical row and tape precision review",
        ],
        "unproved_obligations": [
            "Entry conversion from finer caller records",
            "Complete node endpoint and owner admission",
            "Complete finite bit and tape invoice",
            "Admission to the PR4470 selected construction",
        ],
        "kappa_improvement": False,
    }
    (out / "REPLAY.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
