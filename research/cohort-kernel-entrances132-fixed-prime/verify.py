#!/usr/bin/env python3
"""Replay PR254's native witness and certify its fixed-prime exponent refinement."""
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
PARENT = ROOT / "research/cohort-kernel-entrances132"
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
    assert manifest["schema"] == "cohort-kernel-entrances132-fixed-prime/1"
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob("*")
              if p.is_file() and p != manifest_path}
    assert not any(p.is_symlink() for p in HERE.rglob("*")), "symlinks are not admitted"
    assert actual == set(manifest["files"]), "missing or unpinned candidate file"
    for relative, expected_hash in manifest["files"].items():
        assert canonical_sha(HERE / relative) == expected_hash, "candidate hash mismatch: " + relative
    return canonical_sha(manifest_path), len(actual)


def source_pins():
    base = SOURCE["base_candidate"]
    assert canonical_sha(PARENT / "MANIFEST.json") == base["package_manifest_sha256"]
    assert canonical_sha(PARENT / "RESULT.json") == base["result_sha256"]
    assert canonical_sha(PARENT / "expected/COHORT-EXACT-PRICE.json") == base["price_sha256"]
    assert canonical_sha(PARENT / "expected/COHORT-FINITE-INVOICE.json") == base["finite_invoice_sha256"]
    for relative, expected_hash in SOURCE["arithmetic_sources"].items():
        assert canonical_sha(ROOT / relative) == expected_hash, "arithmetic source changed: " + relative
    subprocess.run(["git", "cat-file", "-e", base["commit"] + "^{commit}"],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "merge-base", "--is-ancestor", base["commit"], "HEAD"],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="new directory outside the checkout for all replay outputs")
    args = parser.parse_args()

    package_hash, package_files = integrity()
    source_pins()
    output = args.output.resolve()
    assert not output.is_relative_to(ROOT), "output must be outside the repository"
    assert not output.exists(), "output must be a new directory"
    output.mkdir(parents=True)
    native_output = output / "native"
    progress("Rebuilding PR254's pinned PR249 baseline and running all seven native witness checkers")
    subprocess.run([sys.executable, "-B", str(PARENT / "verify.py"),
                    "--output", str(native_output)], cwd=ROOT, check=True)
    native = json.loads((native_output / "CERTIFICATE.json").read_text(encoding="utf-8"))
    assert native["status"] == "PASS_ALL_SEVEN_NATIVE_CHECKERS_AND_PINNED_RECEIPTS"
    assert native["baseline_regenerated_from_source"] is True
    assert native["new_record_sha256"] == SOURCE["base_candidate"]["new_record_sha256"]
    assert native["kappa"] == SOURCE["base_candidate"]["kappa"]
    assert native["package_manifest_sha256"] == SOURCE["base_candidate"]["package_manifest_sha256"]

    native_price = json.loads((native_output / "lead/COHORT-EXACT-PRICE.json").read_text(encoding="utf-8"))
    native_invoice = json.loads((native_output / "temporal/COHORT-FINITE-INVOICE.json").read_text(encoding="utf-8"))
    progress("Recomputing fixed-prime moments with two independent rational interval engines")
    spec = importlib.util.spec_from_file_location("cohort_fixed_prime_math", HERE / "fixed_prime_math.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    mathematics = module.compute(native_price, ROOT)
    profile = native_price["cohort_candidate"]
    finite = module.audit_finite_admission(mathematics, profile, native_invoice, ROOT)
    assert mathematics == EXPECTED["mathematics"], "fixed-prime arithmetic differs from pinned certificate"
    assert finite == EXPECTED["finite_admission"], "finite cutoff or full cost differs from pinned certificate"
    assert module.RHO == module.Q(3456000, module.PRIME) < module.Q(1, 10**16)
    assert module.Q(mathematics["kappa"]) == module.Q(710465204542247142217249, 10**27)
    assert module.Q(mathematics["exact_gain"]) == module.Q(3909417142217249, 10**27)
    assert mathematics["ordinary_bootstrap"]["levels"] == 8
    assert len(mathematics["assembly"]["strict_constraints"]) == 47
    assert len(mathematics["assembly"]["margins"]) == 7
    assert finite["moment_gaps"]["full_fallback_kept"] is True

    candidate = dict(
        schema="cohort-kernel-entrances132-fixed-prime-candidate/1",
        parent=dict(commit=SOURCE["base_candidate"]["commit"],
                    kappa=SOURCE["base_candidate"]["kappa"],
                    package_manifest_sha256=native["package_manifest_sha256"],
                    result_sha256=native["new_record_sha256"],
                    native_status=native["status"],
                    native_checkers=7),
        prime=dict(value=module.PRIME, exponent=127, lucas_lehmer_residue=0,
                   kernel_certificate="Prime.lean; certifies prime/density, not multiplication"),
        mathematics=mathematics, finite_admission=finite)
    (output / "candidate-certificate.json").write_text(
        json.dumps(candidate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    final_hash, final_count = integrity()
    assert final_hash == package_hash and final_count == package_files
    result = dict(status="PASS_PR254_132_COHORT_FIXED_PRIME_REFINEMENT",
                  kappa=mathematics["kappa"], exact_gain=mathematics["exact_gain"],
                  parent_commit=SOURCE["base_candidate"]["commit"],
                  native_parent_status=native["status"],
                  candidate_manifest_sha256=package_hash, package_files=package_files,
                  inputs_unchanged=True)
    (output / "verification.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                                              encoding="utf-8")
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
