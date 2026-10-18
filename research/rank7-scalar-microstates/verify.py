# SPDX-License-Identifier: Apache-2.0
"""Replay actual A-stage scalar microstates under three source-pinned policies."""

import argparse
import gzip
import hashlib
import json
import sys
import tempfile
from pathlib import Path

from audit import compare
from integer import trace
from microstates import stage
from vendor import lower
from vendor.format_source import format as f

PACKAGE = Path(__file__).resolve().parent


def authenticate():
    records = json.loads((PACKAGE / "VENDOR.json").read_text())["files"]
    f.require(len(records) == 25, "complete bounded frozen manifest")
    actual = {
        p.relative_to(PACKAGE).as_posix()
        for p in (PACKAGE / "vendor").rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    }
    f.require(actual == {r["path"] for r in records}, "complete frozen file inventory")
    for record in records:
        path = PACKAGE / record["path"]
        f.require(
            not path.is_symlink() and path.stat().st_size <= 8_000_000, "source size"
        )
        raw = path.read_bytes()
        f.require(
            hashlib.sha256(raw).hexdigest() == record["sha256"],
            "frozen source bytes: " + record["path"],
        )
        git_object = b"blob " + str(len(raw)).encode() + b"\0" + raw
        f.require(
            hashlib.sha1(git_object, usedforsecurity=False).hexdigest()
            == record["git_blob"],
            "frozen Git blob identity",
        )
    return len(records)


def combined(scalar, native):
    ledger = f.Ledger(True)
    for name, report in (("scalar", scalar), ("native", native)):
        ledger.observe(
            report["fractional_bits"],
            f.Q(report["symmetric_amplitude_in_input_L"]),
            0,
            name,
        )
    report = ledger.result(64)
    f.capacity(report, 64, 7, 84)
    return report


def provider(work, name, reference):
    native = work / "reference" / name / "native"
    word = json.loads(gzip.decompress((native / "CANONICAL-WORD.json.gz").read_bytes()))
    programs = json.loads(
        gzip.decompress((native / "LOCAL-PROGRAMS.json.gz").read_bytes())
    )
    reports = {}
    for direction in ("forward", "backward"):
        baseline = reference["providers"][name]["streams"][direction]
        policies = {}
        for policy in lower.POLICIES:
            path = work / f"{name}-{direction}-{policy}.jsonl"
            with path.open("wb") as output:
                report = stage(programs[direction], word, policy, output)
            with path.open("rb") as literals:
                f.require(
                    trace(programs[direction], literals) == report["microstate_sha256"],
                    "independent integer prefixes",
                )
            f.require(
                report["normalized_rows_sha256"] == baseline["prefix_rows_sha256"],
                "reference every-prefix endpoints",
            )
            f.require(
                report["end_event"] == baseline["end_event"], "same covered A boundary"
            )
            report["combined_with_native"] = combined(
                report["envelope"], baseline["pair_first"]
            )
            policies[policy] = report
        reports[direction] = policies
    return reports


def run(work):
    count = authenticate()
    source = PACKAGE / "vendor/format_source"
    sys.path.insert(0, str(source))
    from vendor.format_source import verify as reference

    (work / "reference").mkdir()
    inherited = reference.run(work / "reference")
    f.require(
        inherited == json.loads((source / "RESULT.json").read_text()),
        "fresh complete reference replay",
    )
    reports = {name: provider(work, name, inherited) for name in ("base", "extra")}
    return {
        "status": "PASS_INDEPENDENT_3090_ARITHMETIC_AUDIT_NO_NEW_KAPPA",
        "input_precision": 64,
        "common_fractional_bits": 7,
        "common_signed_width": 84,
        "frozen_files": count,
        "reference_receipt_sha256": hashlib.sha256(f.canonical(inherited)).hexdigest(),
        "providers": reports,
        "claim_comparison": compare(
            reports, json.loads((PACKAGE / "vendor/CLAIM-3090.json").read_text())
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.work:
        work = args.work.expanduser().resolve()
        f.require(
            not work.exists() and not work.is_relative_to(PACKAGE.parents[1]),
            "fresh external work directory",
        )
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(
            prefix="rank7-scalar-microstates-"
        ) as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        f.require(
            result == json.loads(expected.read_text()),
            "deterministic committed evidence",
        )
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
