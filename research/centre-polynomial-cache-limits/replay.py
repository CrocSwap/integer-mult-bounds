"""Replay the two retained results from the local source closure."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def main(args):
    root = Path(__file__).resolve().parent
    sources = json.loads((root / "SOURCES.json").read_text())
    for item in sources["files"]:
        raw = (root / item["path"]).read_bytes()
        require(len(raw) == item["bytes"] and sha256(raw).hexdigest() == item["sha256"],
                "Source digest mismatch: " + item["path"])
    args.out.mkdir(parents=True, exist_ok=False)
    shutil.copytree(root / "frozen", args.out / "frozen")
    lanes = args.out / "frozen/work/centre-encoding-campaign-20261014/lanes"
    interface = lanes / "circuit-interface/INTERFACE.json"

    def run(name, script, *arguments):
        result = subprocess.run([sys.executable, "-I", "-B", str(script), *map(str, arguments)],
                                capture_output=True, text=True)
        (args.out / (name + "-stdout.txt")).write_text(result.stdout)
        (args.out / (name + "-stderr.txt")).write_text(result.stderr)
        require(result.returncode == 0, name + " failed; read its log")

    run("bell-producer", lanes / "history-encoding/certify_bell_gram_degree.py",
        "--interface", interface, "--out", args.out / "BELL-GRAM-DEGREE.json")
    require((args.out / "BELL-GRAM-DEGREE.json").read_bytes() ==
            (lanes / "history-encoding/BELL-GRAM-DEGREE.json").read_bytes(),
            "The Bell producer receipt must equal the retained receipt")
    run("bell-review", lanes / "interface-proof/review_bell_gram_degree.py")
    review_path = Path("work/centre-encoding-campaign-20261014/lanes/interface-proof/BELL-GRAM-DEGREE-REVIEW.json")
    require((args.out / "frozen" / review_path).read_bytes() ==
            (root / "frozen" / review_path).read_bytes(),
            "The separate Bell review receipt must equal the retained receipt")
    run("phase-cache", root / "check_phase_cache.py",
        "--interface", interface, "--out", args.out / "PHASE-CACHE-CHECK.json")
    import numpy
    report = {
        "status": "PASS_CENTRE_POLYNOMIAL_CACHE_LIMITS",
        "python_version": platform.python_version(),
        "numpy_version": numpy.__version__,
        "historical_source_commit": sources["historical_source_commit"],
        "source_files_checked": len(sources["files"]),
        "bell_producer_receipt_equal": True,
        "bell_independent_review_receipt_equal": True,
        "phase_cache_check": json.loads((args.out / "PHASE-CACHE-CHECK.json").read_text()),
        "not_run": ["Full supplier replay", "Native decoder", "Selected frontier replay", "Outer kappa calculation", "Formal-kernel proof"],
    }
    (args.out / "REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.out = arguments.out.resolve()
    main(arguments)
