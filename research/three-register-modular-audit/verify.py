#!/usr/bin/env python3
"""Audit PR468's modular arithmetic kernels, not its full nine-call theorem."""
# SPDX-License-Identifier: Apache-2.0

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
import os
from pathlib import Path
import shlex
import subprocess
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE = "research/bit-three-register-lower-bound/f101.cpp"


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def det(a):
    """Laplace expansion, separate from the C++ oracle's Leibniz expansion."""
    if len(a) == 1:
        return a[0][0]
    return sum((-1) ** j * a[0][j] * det([
        row[:j] + row[j + 1:] for row in a[1:]
    ]) for j in range(len(a)))


def determinant_certificate():
    cube = {}
    for n in (1, 2, 3):
        counts = Counter()
        for entries in product((-1, 0, 1), repeat=n * n):
            a = [entries[i:i + n] for i in range(0, n * n, n)]
            counts[det(a)] += 1
        cube[str(n)] = {str(k): v for k, v in sorted(counts.items())}
        require(max(map(abs, counts)) == (1, 2, 4)[n - 1], "cube minor bound")
    # A multi-affine determinant attains its absolute maximum at sign vertices.
    # Enumerate all 4x4 vertices, not all 3^16 interior cube matrices.
    counts = Counter()
    witness = None
    for entries in product((-1, 1), repeat=16):
        a = [list(entries[i:i + 4]) for i in range(0, 16, 4)]
        value = det(a)
        counts[value] += 1
        if abs(value) == 16 and witness is None:
            witness = a
    require(max(map(abs, counts)) == 16, "four-row determinant bound")
    return {"cube_minor_histograms": cube,
            "four_by_four_sign_vertex_histogram": {str(k): v for k, v in sorted(counts.items())},
            "sharp_four_row_witness": witness}


def reconstruction_certificate():
    output = {}
    for bound in (4, 5):
        fractions = sorted({Fraction(n, d) for n in range(-bound, bound + 1)
                            for d in range(1, bound + 1)})
        residues = [int(q.numerator * pow(q.denominator, -1, 101) % 101)
                    for q in fractions]
        require(len(set(residues)) == len(fractions), "ambiguous reconstruction")
        output[str(bound)] = {"fractions": list(map(str, fractions)), "residues_mod_101": residues}
    return output


def mathematical_controls():
    # This cube matrix loses rank at p=5: a concrete failure outside the safe bound.
    bad_prime_matrix = [[0, 1, 1, 1], [1, 0, 1, -1], [1, -1, -1, 1], [1, 1, 0, 1]]
    require(abs(det(bad_prime_matrix)) == 5, "rank-loss fixture determinant")
    require(any(det([[row[j] for j in cols] for row in bad_prime_matrix[:3]]) % 5
                for cols in combinations(range(4), 3)), "rank-three prefix modulo five")
    # At p=19 rank tests are safe (19>16), but coefficient decoding is ambiguous.
    first, second = Fraction(-4), Fraction(3, 4)
    mod = lambda q, p: q.numerator * pow(q.denominator, -1, p) % p
    require(first != second and mod(first, 19) == mod(second, 19), "parity alias fixture")
    require(mod(Fraction(1, 2), 101) % 2 == 1, "residue fixture")
    return {"rank_loss_mod_5_matrix": bad_prime_matrix,
            "rank_loss_determinant": det(bad_prime_matrix),
            "rank_safe_but_reconstruction_ambiguous_mod_19": [str(first), str(second)],
            "same_residue_mod_19": mod(first, 19),
            "primitive_parities_mod_19_collision": [[1, 0], [0, 1]],
            "residue_parity_trap": {"rational_row": ["1", "1/2"],
                                    "residues": [1, 51], "wrong_parity": [1, 1],
                                    "primitive_integer_row": [2, 1], "correct_parity": [0, 1]}}


def validate_sources(pins, payloads):
    for name, digest in pins["files"].items():
        require(sha256(payloads[name]).hexdigest() == digest, f"Source pin mismatch: {name}")


def compile_and_run(directory, source, name):
    (directory / "audited_f101.cpp").write_text(source)
    binary = directory / name
    command = shlex.split(os.environ.get("CXX", "c++")) + [
        "-O2", "-std=c++17", "-I", str(directory), str(HERE / "kernel_probe.cpp"), "-o", str(binary)
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=120)
    require(result.returncode == 0, f"Probe compilation failed:\n{result.stderr}")
    return subprocess.run([str(binary)], capture_output=True, text=True, timeout=120)


def kernel_certificate(source):
    with TemporaryDirectory(prefix="three-register-modular-audit-") as tmp:
        directory = Path(tmp)
        baseline = compile_and_run(directory, source, "baseline")
        require(baseline.returncode == 0, f"Production kernel mismatch: {baseline.stderr}")
        result = json.loads(baseline.stdout)
        require(result["extended_cube_matrices"] == [6, 432, 318816], "incomplete small census")
        # Mutations touch temporary copies only. Each must compile and fail a
        # specific mathematical comparison, not merely crash or fail to compile.
        mutations = {
            "take_parity_of_residues": (
                "int primitive_parity(const Row& r) {",
                "int primitive_parity(const Row& r) { int wrong = 0; for (int j = 0; j < 8; ++j) wrong |= (r[j] & 1) << j; return wrong;",
                "primitive parity mismatch"),
            "accept_every_target_as_small": (
                "bool target_small(int mask, const Basis& b) {",
                "bool target_small(int mask, const Basis& b) { return true;",
                "target span mismatch"),
            "reject_every_target_as_small": (
                "bool target_small(int mask, const Basis& b) {",
                "bool target_small(int mask, const Basis& b) { return false;",
                "target span mismatch"),
            "drop_last_quotient_coordinate": (
                "Row residual(Row v, const Basis& b) {",
                "Row residual(Row v, const Basis& b) { v[7] = 0;",
                "Cramer entry mismatch"),
        }
        controls = {}
        for name, (old, new, diagnostic) in mutations.items():
            require(source.count(old) == 1, f"Mutation anchor changed: {name}")
            run = compile_and_run(directory, source.replace(old, new), name)
            require(run.returncode != 0 and diagnostic in run.stderr,
                    f"Mutation escaped its expected comparison: {name}: {run.stderr}")
            controls[name] = diagnostic
        return {"production_probe": result, "rejected_kernel_mutations": controls}


def verify():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    payloads = {name: (REPO / name).read_bytes() for name in pins["files"]}
    validate_sources(pins, payloads)
    damaged = {**payloads, SOURCE: payloads[SOURCE] + b"\n// altered source\n"}
    try:
        validate_sources(pins, damaged)
    except RuntimeError as error:
        require("Source pin mismatch" in str(error), "unexpected pin control error")
    else:
        raise RuntimeError("Changed source was accepted")
    return {"status": "PASS_PR468_MODULAR_ARITHMETIC_AUDIT", "sources": pins,
            "source_mutation_rejected": True,
            **determinant_certificate(), "reconstruction": reconstruction_certificate(),
            "mathematical_controls": mathematical_controls(),
            **kernel_certificate(payloads[SOURCE].decode())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true",
                        help="Explicitly regenerate this package's EXPECTED.json")
    args = parser.parse_args()
    result = verify()
    expected = HERE / "EXPECTED.json"
    if args.write_certificate:
        expected.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads(expected.read_text()), "Audit differs from EXPECTED.json")
    print(result["status"])
    print(json.dumps(result["production_probe"], sort_keys=True))


if __name__ == "__main__":
    main()
