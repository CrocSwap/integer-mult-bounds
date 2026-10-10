#!/usr/bin/env python3
"""Source-bound replay of the additional early-cut response-kernel entrances."""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

if not __debug__:
    raise SystemExit("assertions are required")
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / "research/multicut-kernel-condensation"
FIXED = ROOT / "research/multicut-kernel-condensation-descent-fixed-prime"
sys.path.insert(0, str(HERE))
from rebind_descent import rebind


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    Path(path).write_text(json.dumps(obj, sort_keys=True, indent=2) + "\n")


def normalize(obj):
    if isinstance(obj, dict):
        return {k: normalize(v) for k, v in obj.items()
                if k not in {"seconds", "local_scalar_stream", "elapsed_seconds"}}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    return obj


def integrity():
    manifest = load(HERE / "MANIFEST.json")
    files = {p.relative_to(HERE).as_posix(): sha(p) for p in HERE.rglob("*")
             if p.is_file() and p != HERE / "MANIFEST.json"}
    assert not any(p.is_symlink() for p in HERE.rglob("*"))
    assert files == manifest["files"], "candidate source files changed"
    source = load(HERE / "SOURCE.json")
    for relative, expected in source["baseline_files"].items():
        assert sha(ROOT / relative) == expected, "baseline source changed: " + relative
    for package in (PARENT, FIXED):
        for relative, expected in load(package / "MANIFEST.json")["files"].items():
            assert sha(package / relative) == expected, "inherited source changed: " + relative
    return sha(HERE / "MANIFEST.json")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cxx", default="g++")
    parser.add_argument("--boost-include", type=Path)
    args = parser.parse_args()
    assert sys.version_info >= (3, 11) and sys.byteorder == "little"
    original_manifest = integrity()
    out = args.output.resolve()
    assert not out.exists() and not out.is_relative_to(ROOT)
    out.mkdir(parents=True)
    logs = out / "logs"
    logs.mkdir()
    baseline = out / "baseline"
    lead = out / "candidate"
    lead.mkdir()
    bank = out / "bank"
    bank.mkdir()
    started = time.monotonic()

    def run(label, command):
        print(label, flush=True)
        with (logs / (label + ".log")).open("w") as stream:
            result = subprocess.run([str(x) for x in command], cwd=ROOT,
                                    stdout=stream, stderr=subprocess.STDOUT)
        if result.returncode:
            raise RuntimeError(label + " failed; see " + str(logs / (label + ".log")))

    command = [sys.executable, "-B", FIXED / "verify.py", "--output", baseline,
               "--cxx", args.cxx]
    if args.boost_include:
        command += ["--boost-include", args.boost_include.resolve()]
    run("01-fresh-baseline265", command)
    baseline_certificate = load(baseline / "candidate-certificate.json")
    baseline_verification = load(baseline / "verification.json")
    assert baseline_verification["status"] == "PASS_PR263_MULTICUT_DESCENT_FIXED_PRIME_REFINEMENT"
    source = load(HERE / "SOURCE.json")
    assert baseline_verification["kappa"] == source["baseline_kappa"]
    assert load(baseline / "CERTIFICATE.json")["baseline_regenerated_from_source"] is True

    old = json.loads(gzip.decompress((PARENT / "inputs/candidates.json.gz").read_bytes()))
    added = load(HERE / "inputs/additional-entrances.json")
    assert len(old) == 518 and len(added) == 369
    assert sum(x["dim"] for x in added) == 372
    combined = old + added
    assert len({x["a"] for x in combined}) == len(combined)
    assert sum(x["dim"] for x in combined) == 1716
    pivots = {x["a"] for x in combined}
    donors = {d for x in combined for d in x["partners"]}
    assert not pivots & donors
    save(out / "combined-candidates.json", combined)
    original = baseline / "temporal/CURRENT249-EXPORT"
    binary = baseline / "bin"
    run("02-original-transformer", [binary / "cohort-transform", original,
                                    out / "combined-candidates.json", lead])
    alignment = rebind(baseline / "lead/COHORT249-PRE-DESCENT-RECORDS.bin",
                       lead / "COHORT249-RECORDS.bin",
                       PARENT / "inputs/descent-selection.json",
                       lead / "descent-selection.json")
    save(lead / "DESCENT-REBIND-EVIDENCE.json", alignment)
    run("03-inherited-descent", [sys.executable, "-B", PARENT / "code/descent_retiming.py",
                                 original, lead, lead / "descent-selection.json"])
    # Any additional retiming is source-bound and independently checked below.
    if (HERE / "inputs/plateau-selection.json").is_file():
        bound = out / "bound-plateau-selection.json"
        run("04a-bind-connected-plateaus", [sys.executable, "-B", HERE / "rebind_plateaus.py",
                                            baseline / "lead/COHORT249-RECORDS.bin",
                                            HERE / "inputs/plateau-selection.json",
                                            lead / "COHORT249-RECORDS.bin", bound])
        plateau = out / "candidate-plateau"
        run("04b-connected-plateau-retiming", [sys.executable, "-B", HERE / "plateau_retiming.py",
                                               original, lead, bound, plateau])
        lead = plateau
        run("04c-exact-operand-source-spans", [sys.executable, "-B", HERE / "verify_plateau_spans.py",
                                               original, lead, lead / "PLATEAU-RETIMING.json"])
    run("04d-exact-frame-bases", [sys.executable, "-B", HERE / "verify_frame_tables.py",
                                  original, lead, "--output", lead / "FRAME-TABLE-AUDIT.json"])
    run("05-independent-legality", [binary / "cohort-legality-independent", original,
                                     lead, lead / "INDEPENDENT-LEGALITY.json"])
    run("06-independent-prefix", [binary / "cohort-prefix-independent", original,
                                   lead, lead / "INDEPENDENT-PREFIX.json"])
    run("07-bank-charts-and-assignments", [binary / "cohort-bank-review", original,
                                           lead / "COHORT249-INITIAL.json",
                                           lead / "COHORT249-FRAMES.json", bank, "crosscut_response_pairs"])
    run("08-all-five-stage-columns", [binary / "cohort-five-stage-columns",
                                       lead / "COHORT249-RECORDS.bin", lead / "COHORT-FIVE-STAGE-COLUMNS.json"])
    run("09-native-exact-price", [binary / "cohort-price", lead / "COHORT249-REPLAY.json",
                                   lead / "COHORT-EXACT-PRICE.json"])
    run("10-finite-invoice", [binary / "cohort-finite-invoice", lead / "COHORT249-RECORDS.bin",
                              lead / "COHORT-EXACT-PRICE.json", bank / "BANK-REVIEW.json",
                              lead / "COHORT-FIVE-STAGE-COLUMNS.json", lead / "COHORT-FINITE-INVOICE.json"])
    run("11-exact-fixed-prime-price", [sys.executable, "-B", HERE / "candidate_math.py",
                                      "--native-price", lead / "COHORT-EXACT-PRICE.json",
                                      "--invoice", lead / "COHORT-FINITE-INVOICE.json",
                                      "--repository", baseline,
                                      "--baseline-certificate", baseline / "candidate-certificate.json",
                                      "--output", lead / "FIXED-PRIME-CERTIFICATE.json"])
    expected = load(HERE / "EXPECTED.json")
    assert sha(lead / "COHORT249-RECORDS.bin") == expected["physical_word_sha256"]
    for filename in expected["receipts"]:
        matches = [folder / filename for folder in (lead, bank) if (folder / filename).is_file()]
        assert len(matches) == 1
        assert normalize(load(matches[0])) == load(HERE / "expected" / filename), filename
    actual_kappa = Fraction(load(lead / "FIXED-PRIME-CERTIFICATE.json")["kappa"])
    assert actual_kappa == Fraction(expected["kappa"])
    prior_kappa = Fraction(source["baseline_kappa"])
    assert actual_kappa > prior_kappa
    assert integrity() == original_manifest
    result = dict(status="PASS_SOURCE_BOUND_CROSSCUT_RESPONSE_PAIRS",
                  kappa=str(actual_kappa), baseline_kappa=str(prior_kappa),
                  exact_gain=str(actual_kappa-prior_kappa),
                  physical_word_sha256=expected["physical_word_sha256"],
                  candidate_manifest_sha256=original_manifest,
                  baseline_regenerated_from_source=True, all_original_native_checkers_passed=True,
                  inherited_all_size_hypotheses_retained=True, new_lean_certificate=False,
                  elapsed_seconds=time.monotonic()-started)
    save(out / "VERIFICATION.json", result)
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
