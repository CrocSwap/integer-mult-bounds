#!/usr/bin/env python3
"""Replay PR251 and certify its fixed-prime, eight-level exact refinement."""
from datetime import datetime, timezone
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys

if sys.flags.optimize:
    raise SystemExit("assertions are required; refusing optimized Python")
sys.set_int_max_str_digits(0)
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = ROOT / "research/five-stage-source527-banks"
SOURCE = json.loads((HERE / "SOURCE.json").read_text())
EXPECTED = json.loads((HERE / "expected.json").read_text())
REQUIRED_STAGES = {"raw", "bit", "scalar", "primes", "banks", "complex", "math", "finite"}
PARENT_STATUS = "PASS_IMMUTABLE_PARITY_REGAUGED_SOURCE527_FIVE_STAGE_BANKED_CONSTRUCTION"


def progress(message):
    print(datetime.now(timezone.utc).strftime("%H:%M:%S UTC") + "  " + message, flush=True)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sha_package_file(path):
    data = Path(path).read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def integrity():
    manifest_path = HERE / "MANIFEST.json"
    manifest = json.loads(manifest_path.read_text())
    assert manifest["schema"] == "source527-37-entrance-fixed-prime-package/1"
    actual = {p.relative_to(HERE).as_posix() for p in HERE.rglob("*")
              if p.is_file() and p != manifest_path}
    assert not any(p.is_symlink() for p in HERE.rglob("*")), "symlinks are not admitted"
    assert actual == set(manifest["files"]), "missing or unpinned candidate file"
    for relative, expected_hash in manifest["files"].items():
        assert sha_package_file(HERE / relative) == expected_hash, "candidate hash mismatch: " + relative
    return sha_package_file(manifest_path), len(actual)


def load_math():
    spec = importlib.util.spec_from_file_location("source527_37_fixed_prime_math",
                                                  HERE / "fixed_prime_math.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def prime_certificate():
    q = (1 << 127) - 1
    assert all(127 % d for d in range(2, 12)), "127 must be prime"
    residues = [4]
    for _ in range(125):
        residues.append((residues[-1] ** 2 - 2) % q)
    assert residues[-1] == 0, "Lucas-Lehmer criterion failed"
    return dict(q=q, p=127, iterations=125, residues=residues,
                criterion="Lucas-Lehmer sufficiency; Prime.lean is separately kernel-checked",
                fixed_before_all_widths=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory outside the repository for all replay outputs")
    args = parser.parse_args()

    package_hash, package_files = integrity()
    parent = SOURCE["base_candidate"]
    parent_commit = parent["commit"]
    assert sha(PARENT / "MANIFEST.json") == parent["package_manifest_sha256"]
    assert sha(ROOT / parent["publication_audit"]) == parent["publication_audit_sha256"]
    subprocess.run(["git", "cat-file", "-e", parent_commit + "^{commit}"],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "merge-base", "--is-ancestor", parent_commit, "HEAD"],
                   cwd=ROOT, check=True, stdout=subprocess.DEVNULL)

    output = args.output.resolve()
    assert not output.is_relative_to(ROOT), "output must be outside the repository"
    assert not output.exists(), "output must be a new directory"
    output.mkdir(parents=True)
    base_output = output / "pr251"
    progress("Replaying all eight pinned PR251 physical and accounting stages")
    subprocess.run([sys.executable, "-B", str(PARENT / "verify.py"),
                    "--output", str(base_output)], cwd=ROOT, check=True)
    report = json.loads((base_output / "verification.json").read_text())
    assert report["status"] == PARENT_STATUS
    assert set(report["fresh_stages"]) == REQUIRED_STAGES
    assert report["inputs_unchanged"] is True
    assert report["manifest_sha256"] == parent["package_manifest_sha256"]
    base_certificate_path = base_output / "certificate.json"
    assert sha(base_certificate_path) == parent["published_certificate_sha256"]
    base_certificate = json.loads(base_certificate_path.read_text())
    base_finite = json.loads((base_output / "finite.json").read_text())
    assert Q(base_certificate["kappa"]) == Q(parent["kappa"])
    assert sha(ROOT / "certificates/five-stage-source527-banks-certificate.json") == parent["published_certificate_sha256"]

    math = load_math()
    prime = prime_certificate()
    assert prime["q"] == math.PRIME
    progress("Recomputing the exact fixed-prime rate with both rational moment engines")
    mathematics = math.compute(base_certificate, PARENT)
    finite = math.audit_finite_admission(mathematics, base_certificate, base_finite, PARENT)

    final_eta = math.ETA
    math.ETA = Q(1, 10**12)
    try:
        fixed_prime_old_eta = math.compute(base_certificate, PARENT)
    finally:
        math.ETA = final_eta

    profile = base_certificate["bit_profile"]
    comparison = dict(
        base_kappa=str(Q(base_certificate["kappa"])),
        profile={k: profile[k] for k in
                 ("m", "W", "calls", "rank_mass", "deficit", "normalization", "physical_replicas")},
        coarse=str(Q(mathematics["coarse_rate"]["exact_grid_rate"])),
        levels=mathematics["ordinary_bootstrap"]["levels"],
        fixed_prime_eta_1e_12_kappa=str(Q(fixed_prime_old_eta["kappa"])),
        eta_gain=str(Q(mathematics["kappa"]) - Q(fixed_prime_old_eta["kappa"])),
        kappa=str(Q(mathematics["kappa"])),
        gain=str(Q(mathematics["exact_gain"])),
        finite=finite)

    assert mathematics == EXPECTED["mathematics"], "fixed-prime arithmetic differs from pinned certificate"
    assert finite == EXPECTED["finite_admission"], "finite cutoff or full cost differs from pinned certificate"
    assert comparison == EXPECTED["comparison"], "baseline/gain comparison differs from pinned certificate"
    assert math.ETA == Q(1, 10**24) and math.BETA == Q(1, 10**9)
    assert Q(mathematics["kappa"]) == Q(710433690953069816941696, 10**27)
    assert Q(mathematics["exact_gain"]) == Q(3905186816941696, 10**27)
    assert mathematics["ordinary_bootstrap"]["levels"] == 8
    assert len(mathematics["assembly"]["strict_constraints"]) == 47
    assert len(mathematics["assembly"]["margins"]) == 7
    assert finite["moment_gaps"]["full_fallback_kept"] is True

    candidate = dict(
        schema="source527-37-entrance-fixed-prime-candidate/1",
        parent=dict(commit=parent_commit, kappa=parent["kappa"],
                    package_manifest_sha256=report["manifest_sha256"],
                    certificate_sha256=sha(base_certificate_path),
                    status=report["status"], fresh_stages=sorted(REQUIRED_STAGES)),
        prime=prime, mathematics=mathematics, finite_admission=finite, comparison=comparison)
    (output / "candidate-certificate.json").write_text(
        json.dumps(candidate, sort_keys=True, indent=2) + chr(10))
    final_hash, final_count = integrity()
    assert final_hash == package_hash and final_count == package_files
    assert sha(PARENT / "MANIFEST.json") == parent["package_manifest_sha256"]
    result = dict(status="PASS_PR251_37_ENTRANCE_FIXED_PRIME_REFINEMENT",
                  kappa=str(Q(mathematics["kappa"])), exact_gain=str(Q(mathematics["exact_gain"])),
                  parent_commit=parent_commit, parent_stages=sorted(REQUIRED_STAGES),
                  candidate_checks=["fresh immutable parent replay", "Lucas-Lehmer residue chain",
                                    "independent rational moment engines", "full 32*m^2 rare fallback",
                                    "q-power coefficient and eight finite cutoffs", "47 strict constraints",
                                    "seven margins", "adjacent 10^-27 grid point rejected",
                                    "eta backoff compared with 10^-12"],
                  candidate_manifest_sha256=package_hash, package_files=package_files,
                  inputs_unchanged=True)
    (output / "verification.json").write_text(json.dumps(result, sort_keys=True, indent=2) + chr(10))
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
