#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bounded replay and adversarial certificate checks; Python standard library."""

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def run(script, certificate, expected_code, marker):
    result = subprocess.run(
        [sys.executable, "-I", "-O", "-B", str(script), "--certificate", str(certificate)],
        cwd=certificate.parent, capture_output=True, text=True, timeout=60)
    if result.returncode != expected_code or marker not in result.stdout + result.stderr:
        raise ValueError(f"unexpected result for {script.name}: {result.returncode}\n"
                         + result.stdout + result.stderr)
    if expected_code == 0:
        print(result.stdout.strip(), flush=True)


def main():
    source = HERE / "CERTIFICATE.json"
    original = source.read_bytes()
    certificate = json.loads(original)
    for name, marker in (("verify.py", "PASS_MASKED_STAR_FRAME_COMPATIBILITY"),
                         ("independent_check.py", "PASS_INDEPENDENT_MASKED_STAR")):
        run(HERE / name, source, 0, marker)
    with tempfile.TemporaryDirectory(prefix="masked star controls ") as temporary:
        root = Path(temporary)
        mutants = []
        mutant = copy.deepcopy(certificate)
        mutant["rank_histogram"]["7"] -= 1
        mutants.append(("under-counted-rank-seven", mutant))
        mutant = copy.deepcopy(certificate)
        mutant["maximum_nonorthogonal_clique"] = 9
        mutants.append(("false-nine-clique", mutant))
        mutant = copy.deepcopy(certificate)
        mutant["maximum_clique_witness"][1] = mutant["maximum_clique_witness"][0]
        mutants.append(("repeated-clique-vertex", mutant))
        for label, mutant in mutants:
            path = root / (label + ".json")
            path.write_text(json.dumps(mutant))
            for name, marker in (("verify.py", "FAIL_MASKED_STAR_FRAME_COMPATIBILITY"),
                                 ("independent_check.py", "FAIL_INDEPENDENT_MASKED_STAR")):
                run(HERE / name, path, 1, marker)
            print(f"PASS_MUTATION_REJECTED {label} both_checkers", flush=True)
        relocated = root / "standalone package with spaces"
        relocated.mkdir()
        for name in ("verify.py", "independent_check.py", "CERTIFICATE.json"):
            shutil.copyfile(HERE / name, relocated / name)
        run(relocated / "verify.py", relocated / "CERTIFICATE.json", 0,
            "PASS_MASKED_STAR_FRAME_COMPATIBILITY")
        run(relocated / "independent_check.py", relocated / "CERTIFICATE.json", 0,
            "PASS_INDEPENDENT_MASKED_STAR")
    if source.read_bytes() != original:
        raise ValueError("verification changed the committed certificate")
    print("PASS_MASKED_STAR_PACKAGE mutations=3 rejected_by_both=6 isolated_relocation=yes certificate_unchanged=yes")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(f"FAIL_MASKED_STAR_PACKAGE: {error}", file=sys.stderr)
        raise SystemExit(1)
