#!/usr/bin/env python3
"""Verify the complete finite claim, independent partition and source binding."""
import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import census
import interval_oracle


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_sources():
    repo = HERE.parents[1]
    sources = json.loads((HERE / "SOURCES.json").read_text())
    for entry in sources["files"]:
        if entry["usage"] == "input":
            raw = (repo / entry["path"]).read_bytes()
            require(hashlib.sha256(raw).hexdigest() == entry["sha256"], "input source digest: " + entry["path"])
    for entry in sources["external_sources"]:
        raw = (HERE / entry["local_path"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == entry["sha256"], "predecessor source digest: " + entry["local_path"])


def compute_checked():
    check_sources()
    receipt, output_streams = census.certificate(with_outputs=True)
    rows = receipt["rows"] + [receipt["three_guard_positive_control"]]
    require(len(rows) == len(output_streams) == 16, "incomplete paired domain")
    for row, outputs in zip(rows, output_streams):
        independent, other_outputs = interval_oracle.interval_census(row["target"], row["guards"], with_outputs=True)
        require(outputs == other_outputs, "exact output-stream disagreement at p=" + str(row["target"]))
        require(row == independent, "independent interval disagreement at p=" + str(row["target"]))
    require(receipt["first_failing_target"] == 15, "first failure changed")
    require(len(receipt["rows"][-1]["failures"]) == 7, "complete failure locus changed")
    require(not receipt["three_guard_positive_control"]["failures"], "three-guard positive control failed")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a regenerated certificate to a new path only")
    args = parser.parse_args()
    if args.write and args.write.exists():
        parser.error("output already exists; refusing to overwrite it")
    result = compute_checked()
    if args.write:
        with args.write.open("x") as output:
            output.write(json.dumps(result, indent=2) + "\n")
    else:
        expected = json.loads((HERE / "CERTIFICATE.json").read_text())
        require(result == expected, "certificate disagrees with complete recomputation")
    print("PASS_RECIPROCAL_FIRST_FAILURE first_p=15 intervals=7 two_guard_cells=" +
          str(result["total_two_guard_cells"]) + " independent_partition=PASS no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("FAIL_RECIPROCAL_FIRST_FAILURE: " + str(exc), file=sys.stderr)
        raise SystemExit(1)
