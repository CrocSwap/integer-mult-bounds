#!/usr/bin/env python3
"""Replay PR244 from source, then certify its fixed-prime exact refinement."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction as Q

if not __debug__:
    raise SystemExit("assertions are required; refusing optimized Python")
ROOT = Path(__file__).resolve().parent
REPOSITORY = ROOT.parents[1]
BASE = REPOSITORY / "research/five-stage-source527-banks"
SOURCE = json.loads((ROOT / "SOURCE.json").read_text())
REQUIRED_BASE = {"raw", "bit", "scalar", "primes", "banks", "complex", "math", "finite"}

def progress(message):
    print(datetime.now(timezone.utc).strftime("%H:%M:%S UTC") + "  " + message, flush=True)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_math():
    spec = importlib.util.spec_from_file_location("source527_fixed_prime_math", ROOT / "fixed_prime_math.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def integrity():
    manifest_path = ROOT / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["schema"] == "source527-fixed-prime-package/1"
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
              if p.is_file() and p != manifest_path}
    assert not any(p.is_symlink() for p in ROOT.rglob("*")), "symlinks are not admitted"
    assert actual == set(manifest["files"]), "missing or unpinned candidate package file"
    for relative, expected in manifest["files"].items():
        assert sha(ROOT / relative) == expected, "candidate package hash mismatch: " + relative
    return sha(manifest_path)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    package_hash = integrity()
    base_manifest = BASE / "MANIFEST.json"
    expected_source = SOURCE["base_candidate"]
    expected_proof = SOURCE["fixed_prime_proof"]
    assert expected_source["commit"] == "a568d94f941929232ab393c7d33dc5a30e017892"
    assert sha(base_manifest) == expected_source["package_manifest_sha256"]
    assert sha(ROOT / "Prime.lean") == expected_proof["sha256"]
    assert (BASE / "verify.py").is_file()
    output = args.output.resolve()
    assert not output.is_relative_to(REPOSITORY), "output must be outside the repository"
    assert not output.exists(), "output must be a new directory"
    output.mkdir(parents=True)
    baseline_output = output / "baseline"

    progress("Running all eight PR244 retimed source527 verifier stages from scratch")
    subprocess.run([sys.executable, "-B", str(BASE / "verify.py"), "--output", str(baseline_output)], check=True)
    baseline_report = json.loads((baseline_output / "verification.json").read_text())
    assert baseline_report["status"] == "PASS_IMMUTABLE_PARITY_RETIMED_SOURCE527_FIVE_STAGE_BANKED_CONSTRUCTION"
    assert set(baseline_report["fresh_stages"]) == REQUIRED_BASE
    base_certificate = json.loads((baseline_output / "certificate.json").read_text())
    base_finite = json.loads((baseline_output / "finite.json").read_text())
    assert Q(base_certificate["kappa"]) == Q(expected_source["kappa"])

    progress("Recomputing fixed-prime moments, five finite levels and both outer backoffs")
    math = load_math()
    mathematics = math.compute(base_certificate, BASE)
    expected = json.loads((ROOT / "expected.json").read_text())
    assert mathematics == expected["mathematics"], "fresh fixed-prime mathematics differs from expected certificate"
    assert Q(mathematics["kappa"]) > Q(base_certificate["kappa"]), "candidate does not improve the freshly replayed base"
    comparison = expected["comparison"]
    assert Q(comparison["baseline_kappa"]) == Q(base_certificate["kappa"])
    final_eta = math.ETA
    assert final_eta == Q(1, 10**24)
    math.ETA = Q(1, 10**12)
    try:
        fixed_prime_only = math.compute(base_certificate, BASE)
    finally:
        math.ETA = final_eta
    assert Q(fixed_prime_only["kappa"]) == Q(comparison["fixed_prime_eta_1e_minus_12_kappa"])
    assert Q(mathematics["kappa"]) - Q(fixed_prime_only["kappa"]) == Q(comparison["eta_backoff_gain"])
    assert Q(mathematics["exact_gain"]) == Q(comparison["total_gain"])
    finite = math.audit_finite_admission(mathematics, base_certificate, base_finite, BASE)
    assert finite["status"] == "PASS_FIXED_PRIME_FINITE_ADMISSION"
    assert finite == expected["finite_admission"], "fresh finite admission differs from the exact certificate"

    candidate = dict(schema="source527-fixed-prime-candidate/1",
                     mathematics=mathematics, finite_admission=finite,
                     inherited_verification=dict(status=baseline_report["status"],
                         fresh_stages=baseline_report["fresh_stages"],
                         baseline_manifest_sha256=expected_source["package_manifest_sha256"],
                         baseline_certificate_sha256=sha(baseline_output / "certificate.json")))
    def save(name, value):
        (output / name).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")
    save("candidate-certificate.json", candidate)
    assert integrity() == package_hash, "candidate package changed during verification"
    assert sha(base_manifest) == expected_source["package_manifest_sha256"], "pinned base changed during verification"
    report = dict(status="PASS_SOURCE527_RETIMED_FIXED_PRIME_REFINEMENT",
                  kappa=mathematics["kappa"], exact_gain=mathematics["exact_gain"],
                  parent_commit=expected_source["commit"],
                  parent_stages=sorted(REQUIRED_BASE),
                  candidate_checks=["fixed-prime first rational moment", "independent second rational moment",
                                    "five finite bootstrap levels and cutoff gaps", "47 outer constraints",
                                    "seven margins", "adjacent grid point rejected",
                                    "eta backoff independently compared with eta=10^-12"],
                  candidate_manifest_sha256=package_hash, inputs_unchanged=True)
    save("verification.json", report)
    print(json.dumps(report, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
