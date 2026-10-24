"""Replay the exact certificates for the historical fixed scalar word."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main(args):
    require(sys.version_info >= (3, 10), "Python 3.10 or later is required")
    manifest = json.loads((ROOT / "MANIFEST.json").read_text())
    for name, expected in manifest["files"].items():
        require(sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                "Package file pin: " + name)
    if args.integrity_only:
        print("PASS_FIXED_WORD_GAUGE_PACKAGE_INTEGRITY")
        return
    require(args.out is not None, "Use --out with a new external output directory")
    output = args.out.resolve()
    require(output != ROOT and ROOT not in output.parents, "Output must be outside the package")
    output.mkdir(parents=True, exist_ok=False)
    require(shutil.disk_usage(output).free >= 3 * 1024 ** 3, "Keep at least 3 GiB of free disk space")
    certificates = ROOT / "certificates"
    common = certificates / "WIRE-GAUGE-PAIRED-COMMON.json.gz"
    odd = [str(certificates / name) for name in
           ("WIRE-GAUGE-ODD-PATHS.json.gz", "WIRE-GAUGE-LINE42-PATHS.json.gz")]
    jobs = [
        ("common-rank", "review_wire_gauge.py", ["--certificate", str(common)],
         "PASS_INDEPENDENT_BOUNDARY_PAIRED_WIRE_GAUGE_CERTIFICATE"),
        ("common-thresholds", "review_threshold_certificate.py",
         ["--source-certificate", str(common), "--certificate",
          str(certificates / "THRESHOLD-GAUGE-COMMON.json.gz")],
         "PASS_INCREASING_CONCAVE_RANK_COST_OBSTRUCTION"),
        ("product-thresholds", "review_compound_gauge.py", ["--certificate",
         str(certificates / "THRESHOLD-MULTI-GAUGE-128-256.json.gz")],
         "PASS_COMPOUND_GAUGE_RANK_AND_RIGIDITY"),
        ("frame415-thresholds", "review_compound_gauge.py", ["--certificate",
         str(certificates / "THRESHOLD-MULTI-GAUGE-CENTRE415.json.gz")],
         "PASS_COMPOUND_GAUGE_RANK_AND_RIGIDITY"),
        ("four-state-thresholds", "review_four_state_gauge.py", ["--certificate",
         str(certificates / "THRESHOLD-MULTISTATE-GAUGE-128-256.json.gz")],
         "PASS_FOUR_STATE_GAUGE_RANK_AND_RIGIDITY"),
        ("all-lines-span", "verify_odd_paths.py", odd,
         "PASS_ALL_PAIRED_WIRE_LINE_RANKS"),
        ("all-lines-pairing", "check_line_paths.py", [],
         "ACCEPTED_INDEPENDENT_ALL_FIXED_LINE_RANK_MASS_OBSTRUCTION"),
        ("common-product-rank", "check_common_product_rank.py", [],
         "ACCEPTED_COMMON_PRODUCT_CENTRE_RANK_BOUND"),
        ("negative-controls", "gauge_negative_controls.py", ["--certificate", str(common)],
         "PASS_GAUGE_NEGATIVE_CONTROLS"),
    ]
    receipts, runs = {}, []
    started = time.monotonic()
    for name, script, options, expected in jobs:
        print("check " + name, flush=True)
        destination = output / (name + ".json")
        command = [sys.executable, "-I", "-O", "-B", str(ROOT / "checkers" / script),
                   *options, "--out", str(destination)]
        tick = time.monotonic()
        run = subprocess.run(command, capture_output=True, text=True, timeout=1800)
        (output / (name + ".stdout.txt")).write_text(run.stdout)
        (output / (name + ".stderr.txt")).write_text(run.stderr)
        require(run.returncode == 0, "Check failed: " + name + " (see output logs)")
        receipt = json.loads(destination.read_text())
        require(receipt["status"] == expected, "Receipt status: " + name)
        receipts[name] = receipt
        runs.append({"check": name, "status": expected, "seconds": round(time.monotonic() - tick, 3),
                     "receipt": destination.name, "receipt_sha256": sha256(destination.read_bytes()).hexdigest()})
    require(receipts["common-rank"]["all_common_odd_lines_reviewed"], "Common line coverage")
    require(receipts["common-rank"]["total_flow_cut_cases"] == 3384, "Common rank case count")
    require(receipts["common-thresholds"]["total_flow_cut_cases"] == 800, "Common threshold case count")
    require(receipts["all-lines-pairing"]["integer_paths"] == 10488, "Integer path count")
    counterexample = receipts["frame415-thresholds"]["thresholds"][0]["best"]
    require(counterexample["objective_delta"] == -1 and counterexample["rank_delta"] == 48,
            "Full-frame counterexample")
    result = {
        "status": "PASS_FIXED_WORD_GAUGE_LIMITS",
        "historical_source_commit": "bce54fb3f895cbe5cd4c0eb477c3afeed100190f",
        "python": platform.python_version(), "platform": platform.platform(),
        "optimized_checks": True, "parallel_workers": 1,
        "seconds": round(time.monotonic() - started, 3), "checks": runs,
        "all_fixed_translation_lines": 511,
        "independent_pairing_ranks": receipts["all-lines-pairing"]["independent_symplectic_pairing_rank_checks"],
        "integer_paths": 10488, "native_events": 5064, "rank_zero_wrappers": 1570,
        "common_rank_flow_cut_cases": 3384, "common_threshold_flow_cut_cases": 800,
        "negative_controls": len(receipts["negative-controls"]["controls"]) +
                             len(receipts["all-lines-pairing"]["negative_controls_under_optimized_python"]),
        "frame415_counterexample": counterexample,
        "kappa_change": "None. No new supplier or complete multiplication bound is claimed.",
        "not_run": ["selected current-construction cold replay", "changed native circuit emission",
                    "complete recursive repricing", "new mathematical search"],
    }
    (output / "REPLAY.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--integrity-only", action="store_true")
    main(parser.parse_args())
