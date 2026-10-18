#!/usr/bin/env python3
"""Exact finite audit of the retained Fourier permutation interface.

Copyright 2026 Ross Richardson. SPDX-License-Identifier: Apache-2.0
Developed with substantial OpenAI Codex assistance. Standard library only.
The written all-group argument is in README.md; this is a finite replay.
"""

import argparse
from functools import cache
import hashlib
from itertools import permutations, product
import json
from math import factorial, gcd, lcm
from pathlib import Path
import random


PACKAGE = Path(__file__).resolve().parent
DOMAIN = ((2,), (3,), (4,), (5,), (6,), (7,), (8,),
          (2, 2), (2, 3), (2, 4), (2, 2, 2))
SEED = 68


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Group:
    def __init__(self, moduli):
        self.moduli = tuple(moduli)
        require(bool(self.moduli) and all(q >= 2 for q in self.moduli),
                "nontrivial cyclic factors required")
        self.points = tuple(product(*(range(q) for q in self.moduli)))
        self.index = {x: i for i, x in enumerate(self.points)}
        self.size = len(self.points)
        self.period = lcm(*self.moduli)
        self.phase = tuple(tuple(
            sum(a * b * (self.period // q)
                for a, b, q in zip(x, y, self.moduli)) % self.period
            for y in self.points) for x in self.points)
        self.generators = tuple(self.index[tuple(int(i == j)
            for j in range(len(self.moduli)))]
            for i in range(len(self.moduli)))

    def check_permutation(self, pi):
        require(sorted(pi) == list(range(self.size)), "not a permutation")

    def kernel_witness(self, pi, rho):
        """Literal matrix entries of P_rho F+ P_pi versus F+.

        The common factor 1/N is omitted. A primitive L-th root has distinct
        powers modulo L, so comparing these residues is exact.
        """
        inverse = [0] * self.size
        for i, j in enumerate(pi):
            inverse[j] = i
        for x in range(self.size):
            for z in range(self.size):
                actual = self.phase[rho[x]][inverse[z]]
                expected = self.phase[x][z]
                if actual != expected:
                    return x, z, actual, expected
        return None

    def structural(self, pi):
        """Reconstruct a homomorphism from generator images, not F entries."""
        columns = [self.points[pi[e]] for e in self.generators]
        if pi[0] != 0:
            return False, False
        for order, image in zip(self.moduli, columns):
            if any(order * value % modulus
                   for value, modulus in zip(image, self.moduli)):
                return False, False
        for x, image_index in zip(self.points, pi):
            reconstructed = tuple(sum(x[i] * columns[i][j]
                for i in range(len(x))) % q
                for j, q in enumerate(self.moduli))
            if reconstructed != self.points[image_index]:
                return False, False
        # <pi(e_i), e_j> = <e_i, pi(e_j)>, including unequal moduli.
        symmetric = all(columns[i][j] * self.moduli[i]
                        == columns[j][i] * self.moduli[j]
                        for i in range(len(columns))
                        for j in range(len(columns)))
        return True, symmetric

    def adjoint(self, pi):
        """Reconstruct pi^dagger using weighted generator coordinates."""
        columns = [self.points[pi[e]] for e in self.generators]
        result = []
        for x in self.points:
            row = []
            for q, column in zip(self.moduli, columns):
                residue = sum(a * b * (self.period // r)
                    for a, b, r in zip(x, column, self.moduli)) % self.period
                step = self.period // q
                require(residue % step == 0, "adjoint coordinate not integral")
                row.append(residue // step)
            result.append(self.index[tuple(row)])
        self.check_permutation(result)
        return tuple(result)


def monic_quotient(numerator, denominator):
    work = list(numerator)
    quotient = [0] * (len(work) - len(denominator) + 1)
    for degree in range(len(work) - 1, len(denominator) - 2, -1):
        coefficient = work[degree]
        shift = degree - len(denominator) + 1
        quotient[shift] = coefficient
        for j, value in enumerate(denominator):
            work[shift + j] -= coefficient * value
    require(not any(work), "nonexact cyclotomic division")
    return tuple(quotient)


@cache
def cyclotomic(n):
    poly = (-1,) + (0,) * (n - 1) + (1,)
    for divisor in range(1, n):
        if n % divisor == 0:
            poly = monic_quotient(poly, cyclotomic(divisor))
    return poly


class ExactRoots:
    """Integer polynomials in zeta_L modulo the monic cyclotomic Phi_L."""
    def __init__(self, period):
        self.period = period
        self.poly = cyclotomic(period)
        self.degree = len(self.poly) - 1
        self.zero = (0,) * self.degree
        self.one = (1,) + (0,) * (self.degree - 1)
        self.roots = tuple(self.reduce((0,) * i + (1,))
                           for i in range(period))
        require(len(set(self.roots)) == period, "root powers are not distinct")
        require(self.reduce((-1,) + (0,) * (period - 1) + (1,)) == self.zero,
                "root period sanity check failed")

    def reduce(self, values):
        work = list(values) + [0] * max(0, self.degree - len(values))
        for k in range(len(work) - 1, self.degree - 1, -1):
            c = work[k]
            for j, value in enumerate(self.poly):
                work[k - self.degree + j] -= c * value
        return tuple(work[:self.degree])

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def scale(self, a, value):
        return tuple(value * x for x in a)

    def multiply(self, a, b):
        values = [0] * (2 * self.degree - 1)
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                values[i + j] += x * y
        return self.reduce(values)


def transform(group, ring, values, sign):
    """Direct Fourier sum, without using the census character table."""
    output = []
    for frequency in group.points:
        total = ring.zero
        for point, value in zip(group.points, values):
            exponent = sum(a * b * (ring.period // q)
                for a, b, q in zip(frequency, point, group.moduli))
            term = ring.multiply(value, ring.roots[(sign * exponent) % ring.period])
            total = ring.add(total, term)
        output.append(total)
    return output


def direct_pipeline(group, ring, pi, rho, u, v, inverse_sign=1):
    # Each transform omits 1/N. The final common denominator is N^3.
    fu = transform(group, ring, [ring.scale(ring.one, x) for x in u], -1)
    fv = transform(group, ring, [ring.scale(ring.one, x) for x in v], -1)
    middle = [ring.multiply(fu[j], fv[j]) for j in pi]
    inverse = transform(group, ring, middle, inverse_sign)
    return [inverse[j] for j in rho]


def direct_convolution(group, u, v):
    result = [0] * group.size
    for x, a in zip(group.points, u):
        for y, b in zip(group.points, v):
            z = tuple((i + j) % q for i, j, q in zip(x, y, group.moduli))
            result[group.index[z]] += a * b
    return result


def pipeline_difference(group, ring, pi, rho, u, v, inverse_sign=1,
                        expected_numerator_factor=None):
    actual = direct_pipeline(group, ring, pi, rho, u, v, inverse_sign)
    factor = group.size if expected_numerator_factor is None else expected_numerator_factor
    expected = [ring.scale(ring.one, factor * x)
                for x in direct_convolution(group, u, v)]
    for i, (a, b) in enumerate(zip(actual, expected)):
        if a != b:
            return {"coordinate": list(group.points[i]),
                    "actual_numerator": list(a), "expected_numerator": list(b),
                    "denominator": group.size ** 3,
                    "root_order": ring.period}
    return None


def basis(n, index):
    return [int(i == index) for i in range(n)]


def census(moduli):
    group = Group(moduli)
    ring = ExactRoots(group.period)
    checked = automorphisms = accepted = rejected_fixing_zero = 0
    direct_basis_pairs = direct_dense_pairs = adjoint_pairs = 0
    digest = hashlib.sha256()
    rng = random.Random(SEED)
    for pi in permutations(range(group.size)):
        checked += 1
        auto, symmetric = group.structural(pi)
        witness = group.kernel_witness(pi, pi)
        passes = witness is None
        require(passes == symmetric, f"classification disagreement on {moduli}: {pi}")
        require(not symmetric or auto, "symmetric classification without homomorphism")
        digest.update(bytes(pi) + bytes((auto, passes)))
        if witness is not None:
            require(ring.roots[witness[2]] != ring.roots[witness[3]],
                    "kernel mismatch collapsed in exact ring")
            rejected_fixing_zero += int(pi[0] == 0)
        automorphisms += int(auto)
        if auto:
            rho = group.adjoint(pi)
            require(group.kernel_witness(pi, rho) is None, "adjoint repair failed")
            adjoint_pairs += 1
            # These are all automorphisms, including the ones rejected by
            # same-layout cancellation. Check their repaired direct programs.
            u = [rng.randrange(-2, 3) for _ in group.points]
            v = [rng.randrange(-2, 3) for _ in group.points]
            require(pipeline_difference(group, ring, pi, rho, u, v) is None,
                    "direct adjoint convolution failed")
            direct_dense_pairs += 1
        if passes:
            accepted += 1
            # All ordered basis pairs, not a scalar or sampled operator check.
            for a in range(group.size):
                for b in range(group.size):
                    require(pipeline_difference(group, ring, pi, pi,
                            basis(group.size, a), basis(group.size, b)) is None,
                            "direct same-layout basis convolution failed")
                    direct_basis_pairs += 1
    require(checked == factorial(group.size), "incomplete permutation census")
    return {"moduli": list(moduli), "permutations": checked,
            "automorphisms": automorphisms, "same_layout_accepted": accepted,
            "rejected_fixing_zero": rejected_fixing_zero,
            "adjoint_pairs_checked": adjoint_pairs,
            "direct_basis_pairs": direct_basis_pairs,
            "direct_dense_pairs": direct_dense_pairs,
            "classification_sha256": digest.hexdigest()}


def negative_control(name, moduli, pi, rho=None, inverse_sign=1,
                     expected_numerator_factor=None):
    group = Group(moduli)
    ring = ExactRoots(group.period)
    rho = pi if rho is None else rho
    group.check_permutation(pi)
    group.check_permutation(rho)
    # Deterministic first differing basis pair, with a complete exact output
    # witness. A failed search is an error, not evidence against the interface.
    for a in range(group.size):
        for b in range(group.size):
            witness = pipeline_difference(group, ring, pi, rho,
                basis(group.size, a), basis(group.size, b), inverse_sign,
                expected_numerator_factor)
            if witness is not None:
                return {"name": name, "moduli": list(moduli),
                        "forward_read_map": list(pi), "inverse_read_map": list(rho),
                        "inverse_sign": inverse_sign,
                        "expected_numerator_factor": (group.size if
                            expected_numerator_factor is None else expected_numerator_factor),
                        "u_basis": list(group.points[a]),
                        "v_basis": list(group.points[b]), "witness": witness}
    raise ValueError(f"negative control not detected: {name}")


def controls():
    # Lexicographic coordinate numbering is used throughout.
    shear = Group((3, 3))
    pi = tuple(shear.index[((x + y) % 3, y)] for x, y in shear.points)
    inverse = tuple(pi.index(i) for i in range(shear.size))
    cyclic5 = tuple(2 * i % 5 for i in range(5))
    negatives = [
        negative_control("translation does not cancel", (3,), (1, 2, 0)),
        negative_control("zero-fixing involutive bit reversal does not cancel",
                         (4,), (0, 2, 1, 3)),
        negative_control("an automorphism need not be self-adjoint",
                         (2, 2), (0, 3, 2, 1)),
        negative_control("inverse is not the adjoint", (3, 3), pi, inverse),
        negative_control("inverting a valid source multiplier is wrong",
                         (5,), cyclic5, tuple(cyclic5.index(i) for i in range(5))),
        negative_control("omitting Fourier-sign conjugation", (5,), cyclic5,
                         inverse_sign=-1),
        negative_control("one factor of N is missing from normalization",
                         (5,), cyclic5, expected_numerator_factor=25),
        negative_control("one extra factor of N in normalization",
                         (5,), cyclic5, expected_numerator_factor=1),
    ]
    nonunit = tuple(2 * i % 6 for i in range(6))
    try:
        Group((6,)).check_permutation(nonunit)
    except ValueError:
        admission = {"name": "nonunit multiplier rejected", "moduli": [6],
                     "map": list(nonunit), "reason": "not a permutation"}
    else:
        raise ValueError("nonunit multiplier accepted")
    positives = []
    for moduli, mapping, label in (
        ((5,), cyclic5, "valid multiplier need not be involutive"),
        ((2, 2), (0, 3, 1, 2), "self-adjoint mixing need not be involutive"),
        ((2, 4), tuple(Group((2, 4)).index[((x + y) % 2, (2*x + y) % 4)]
                      for x, y in Group((2, 4)).points),
         "unequal cyclic moduli need weighted adjoints"),
        ((3, 3), pi, "a distinct adjoint repairs the shear"),
    ):
        group = Group(moduli)
        group.check_permutation(mapping)
        require(group.structural(mapping)[0], "positive control not an automorphism")
        rho = group.adjoint(mapping)
        require(group.kernel_witness(mapping, rho) is None, "positive kernel failed")
        ring = ExactRoots(group.period)
        for a in range(group.size):
            for b in range(group.size):
                require(pipeline_difference(group, ring, mapping, rho,
                    basis(group.size, a), basis(group.size, b)) is None,
                    "positive control pipeline failed")
        positives.append({"name": label, "moduli": list(moduli),
                          "forward_read_map": list(mapping), "inverse_read_map": list(rho),
                          "direct_basis_pairs": group.size ** 2})
    return {"convolution_counterexamples": negatives,
            "admission_rejections": [admission], "positive_controls": positives}


def source_multipliers():
    count = 0
    for q in range(2, SEED + 1):
        group = Group((q,))
        for c in range(1, q):
            if gcd(c, q) == 1:
                pi = tuple(c * j % q for j in range(q))
                require(group.structural(pi) == (True, True), "source unit rejected")
                require(group.kernel_witness(pi, pi) is None, "source unit kernel failed")
                count += 1
    return {"cyclic_moduli_inclusive": [2, SEED], "unit_multipliers": count}


def check_sources(root):
    source = json.loads((PACKAGE / "SOURCE.json").read_text())
    for name, expected in source["files"].items():
        actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
        require(actual == expected, f"source pin mismatch: {name}")
    return source


def build_receipt(root):
    source = check_sources(root)
    rows = [census(dims) for dims in DOMAIN]
    return {"format": "source-permutation-audit-v1", "assignment_seed": SEED,
            "base_commit": source["base_commit"],
            "source_manifest_sha256": hashlib.sha256((PACKAGE / "SOURCE.json").read_bytes()).hexdigest(),
            "arithmetic": "integer character residues and exact cyclotomic integer polynomials",
            "census": rows, "source_multipliers": source_multipliers(),
            "controls": controls(),
            "total_permutations": sum(row["permutations"] for row in rows),
            "total_direct_basis_pairs": sum(row["direct_basis_pairs"] for row in rows),
            "total_direct_dense_pairs": sum(row["direct_dense_pairs"] for row in rows),
            "scope": "Finite replay plus written all-group proof; no formal proof, source defect or new kappa claimed."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PACKAGE.parents[1],
                        help="repository root for immutable source checks")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", type=Path, default=PACKAGE / "EXPECTED.json")
    mode.add_argument("--write", type=Path, help="write a fresh deterministic receipt")
    args = parser.parse_args()
    receipt = build_receipt(args.root)
    if args.write:
        args.write.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads(args.check.read_text())
        require(receipt == expected, "receipt mismatch")
    print(f"PASS_SOURCE_PERMUTATION: {receipt['total_permutations']} permutations; "
          f"{receipt['total_direct_basis_pairs']} census basis pairs; "
          f"{receipt['total_direct_dense_pairs']} dense adjoint pairs; "
          "8 exact counterexamples; 1 admission rejection; 4 positive controls")


if __name__ == "__main__":
    main()
