#!/usr/bin/env python3
"""Replay PR259's 518-entrance physical witness and certify its fixed-prime refinement."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys

if sys.flags.optimize:
    raise SystemExit("assertions are required; refusing optimized Python")
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / "research/multicut-kernel-condensation"
SOURCE = json.loads((HERE / "SOURCE.json").read_text(encoding="utf-8"))
EXPECTED = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))


def progress(message):
    print(datetime.now(timezone.utc).strftime("%H:%M:%S UTC") + "  " + message, flush=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_sha(path):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def integrity():
    manifest_path = HERE / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema"] == "multicut-kernel-condensation-fixed-prime/1"
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob("*")
              if p.is_file() and p != manifest_path}
    assert not any(p.is_symlink() for p in HERE.rglob("*")), "symlinks are not admitted"
    assert actual == set(manifest["files"]), "missing or unpinned candidate file"
    for relative, expected_hash in manifest["files"].items():
        assert canonical_sha(HERE / relative) == expected_hash, "candidate hash mismatch: " + relative
    return canonical_sha(manifest_path), len(actual)


def source_pins():
    base = SOURCE["base_candidate"]
    assert canonical_sha(PARENT / "MANIFEST.json") == base["outer_manifest_sha256"]
    assert canonical_sha(PARENT / "RESULT.json") == base["result_sha256"]
    assert canonical_sha(PARENT / "expected/COHORT-EXACT-PRICE.json") == base["price_sha256"]
    assert canonical_sha(PARENT / "expected/COHORT-FINITE-INVOICE.json") == base["invoice_sha256"]
    result = json.loads((PARENT / "RESULT.json").read_text(encoding="utf-8"))
    assert result["new_record_sha256"] == base["physical_word_sha256"]
    assert result["kappa"] == base["kappa"]
    subprocess.run(["git", "cat-file", "-e", base["commit"] + "^{commit}"],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "merge-base", "--is-ancestor", base["commit"], "HEAD"],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="new directory outside the checkout for all replay outputs")
    parser.add_argument("--cxx", default="g++")
    parser.add_argument("--boost-include", type=Path)
    args = parser.parse_args()

    package_hash, package_files = integrity()
    source_pins()
    output = args.output.resolve()
    assert not output.is_relative_to(ROOT), "output must be outside the repository"
    assert not output.exists(), "output must be a new directory"
    progress("Regenerating PR259's pinned PR249 source and replaying all seven native checkers")
    command = [sys.executable, "-B", str(PARENT / "verify.py"),
               "--output", str(output), "--cxx", args.cxx]
    if args.boost_include:
        command.extend(["--boost-include", str(args.boost_include.resolve())])
    subprocess.run(command, cwd=ROOT, check=True)

    fresh = json.loads((output / "CERTIFICATE.json").read_text(encoding="utf-8"))
    parent = SOURCE["base_candidate"]
    assert fresh["status"] == "PASS_ALL_SEVEN_NATIVE_CHECKERS_AND_PINNED_RECEIPTS"
    assert fresh["baseline_regenerated_from_source"] is True
    assert fresh["new_record_sha256"] == parent["physical_word_sha256"]
    assert fresh["kappa"] == parent["kappa"]
    # The native verifier reports the raw-byte hash; the stable source pin above
    # separately checks the newline-normalized manifest identity.
    assert fresh["package_manifest_sha256"] == sha(PARENT / "MANIFEST.json")

    native_price = json.loads((output / "lead/COHORT-EXACT-PRICE.json").read_text(encoding="utf-8"))
    native_invoice = json.loads((output / "temporal/COHORT-FINITE-INVOICE.json").read_text(encoding="utf-8"))
    assert native_price == json.loads(
        (PARENT / "expected/COHORT-EXACT-PRICE.json").read_text(encoding="utf-8"))
    assert native_invoice == json.loads(
        (PARENT / "expected/COHORT-FINITE-INVOICE.json").read_text(encoding="utf-8"))
    profile = native_price["cohort_candidate"]
    expected_profile = parent["profile"]
    assert int(profile["stock"]) == expected_profile["stock"]
    assert int(profile["calls"]) == expected_profile["calls"]
    assert int(profile["rank_mass"]) == expected_profile["rank_mass"]
    assert int(profile["deficit"]) == expected_profile["deficit"]
    progress("Recomputing exact fixed-prime moments, finite cutoffs, and outer assembly")
    spec = importlib.util.spec_from_file_location(
        "multicut_fixed_prime_math", HERE / "fixed_prime_math.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mathematics = module.compute(native_price, output)
    finite = module.audit_finite_admission(mathematics, profile, native_invoice, output)
    assert mathematics == EXPECTED["mathematics"], "fixed-prime arithmetic differs from pinned certificate"
    assert finite == EXPECTED["finite_admission"], "finite invoice or cutoff differs from pinned certificate"
    assert mathematics["kappa"] == "711029389987426878345881/1000000000000000000000000000"
    assert mathematics["baseline_kappa"] == parent["kappa"]
    assert mathematics["exact_gain"] == "3933391878345881/1000000000000000000000000000"
    assert mathematics["ordinary_bootstrap"]["levels"] == 8
    assert len(mathematics["assembly"]["strict_constraints"]) == 47
    assert len(mathematics["assembly"]["margins"]) == 7
    assert finite["moment_gaps"]["full_fallback_kept"] is True

    candidate = dict(
        schema="multicut-kernel-condensation-fixed-prime-candidate/1",
        parent=dict(commit=parent["commit"], kappa=parent["kappa"],
                    result_sha256=parent["result_sha256"],
                    physical_word_sha256=parent["physical_word_sha256"],
                    native_checkers=7),
        prime=dict(value=module.PRIME, exponent=127, lucas_lehmer_residue=0,
                   kernel_certificate="Prime.lean; certifies prime/density, not multiplication"),
        mathematics=mathematics, finite_admission=finite)
    (output / "candidate-certificate.json").write_text(
        json.dumps(candidate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    final_hash, final_count = integrity()
    assert final_hash == package_hash and final_count == package_files
    source_pins()
    result = dict(status="PASS_PR259_MULTICUT_FIXED_PRIME_REFINEMENT",
                  kappa=mathematics["kappa"], exact_gain=mathematics["exact_gain"],
                  parent_commit=parent["commit"], parent_status=fresh["status"],
                  native_checkers=7, strict_outer_constraints=47,
                  candidate_manifest_sha256=package_hash, package_files=package_files,
                  inputs_unchanged=True)
    (output / "verification.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
