#!/usr/bin/env python3
"""Exact classification of plane-level signatures of invertible 4x4 bases.

Model of research/rational-joint-support-screen (PR3997): ports 0,1 form plane A
and ports 2,3 form plane B.  For an invertible P with inverse Q, message j has a
source support (nonzero entries of column j of P) and a reader support (nonzero
entries of row j of Q).  Each support is mapped to the set of planes it touches
(1 = A, 2 = B, 3 = both).  The signature of P is the 4-tuple of
(source mask, reader mask) pairs.  PR3997 prices only this signature.

This verifier proves nothing by search alone.  It recomputes the finite objects
used by PROOF.md:

1. the set N of signatures allowed by three necessary conditions (6,561
   candidates);
2. the exact plane-pair parametrization of the signature, checked against direct
   matrix inversion over F_2, F_3 and F_5 (all plane pairs) and over every
   matrix of GL_4(F_2);
3. explicit integer witnesses, verified by exact rational inversion, for every
   element of N;
4. equality of N with the 439 signature codes recorded by PR3997.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from fractions import Fraction
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
PREDECESSOR = ROOT / "research" / "rational-joint-support-screen"
RESULT_PATH = PACKAGE / "RESULT.json"
WITNESS_PATH = PACKAGE / "WITNESSES.json"
EXPECTED_SIGNATURES = 439
SCHEMA = "two-plane-signature-classes-v1"
PRIMES = (2, 3, 5)
EXTENDED_PRIMES = (7,)


class CheckFailure(ValueError):
    """A structural, enumerative or binding check failed."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Signatures, exactly as PR3997 defines them.
# ---------------------------------------------------------------------------

def plane_mask(port_support: int) -> int:
    """Planes touched by a 4-bit port support: bit 0 = ports 0,1; bit 1 = ports 2,3."""
    return (1 if port_support & 0b0011 else 0) | (2 if port_support & 0b1100 else 0)


def encode(signature) -> int:
    """PR3997's 16-bit signature code."""
    return sum((source * 4 + reader) << (4 * term)
               for term, (source, reader) in enumerate(signature))


def decode(code: int):
    return tuple((((code >> (4 * term)) & 15) >> 2, ((code >> (4 * term)) & 15) & 3)
                 for term in range(4))


def inverse_fraction(matrix):
    """Exact inverse of a 4x4 integer matrix over Q, or None when singular."""
    rows = [[Fraction(value) for value in row] + [Fraction(int(i == j)) for j in range(4)]
            for i, row in enumerate(matrix)]
    for column in range(4):
        pivot = next((r for r in range(column, 4) if rows[r][column] != 0), None)
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = 1 / rows[column][column]
        rows[column] = [value * scale for value in rows[column]]
        for r in range(4):
            if r != column and rows[r][column] != 0:
                factor = rows[r][column]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[column])]
    return [row[4:] for row in rows]


def inverse_mod(matrix, p: int):
    """Inverse of a 4x4 matrix over the prime field F_p, or None when singular."""
    rows = [[value % p for value in row] + [int(i == j) for j in range(4)]
            for i, row in enumerate(matrix)]
    for column in range(4):
        pivot = next((r for r in range(column, 4) if rows[r][column] % p), None)
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = pow(rows[column][column], -1, p)
        rows[column] = [(value * scale) % p for value in rows[column]]
        for r in range(4):
            if r != column and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [(a - factor * b) % p for a, b in zip(rows[r], rows[column])]
    return [row[4:] for row in rows]


def signature_direct(matrix, inverse):
    """The PR3997 signature from the actual zero patterns of P and P^-1."""
    signature = []
    for message in range(4):
        source_ports = sum((matrix[row][message] != 0) << row for row in range(4))
        reader_ports = sum((inverse[message][output] != 0) << output for output in range(4))
        signature.append((plane_mask(source_ports), plane_mask(reader_ports)))
    return tuple(signature)


# ---------------------------------------------------------------------------
# Lemma 1: the signature depends only on two complementary 2-planes of K^4.
# ---------------------------------------------------------------------------

def rule_signature(e_a: int, f_a: int, e_b: int, f_b: int):
    """Signature from incidence data of the row spaces W_A, W_B of P.

    e_x has bit j when the coordinate vector e_j lies in W_x.  f_x has bit j
    when W_x lies in the coordinate hyperplane x_j = 0.
    Source: plane A is touched by column j iff W_A is not inside x_j = 0.
    Reader: plane A is touched by row j of P^-1 iff e_j is not inside W_B, and
    plane B iff e_j is not inside W_A.
    """
    signature = []
    for j in range(4):
        bit = 1 << j
        source = (0 if f_a & bit else 1) | (0 if f_b & bit else 2)
        reader = (0 if e_b & bit else 1) | (0 if e_a & bit else 2)
        signature.append((source, reader))
    return tuple(signature)


def rule_signature_swapped(e_a: int, f_a: int, e_b: int, f_b: int):
    """Deliberately wrong reader rule, used only as a rejection control."""
    signature = []
    for j in range(4):
        bit = 1 << j
        source = (0 if f_a & bit else 1) | (0 if f_b & bit else 2)
        reader = (0 if e_a & bit else 1) | (0 if e_b & bit else 2)
        signature.append((source, reader))
    return tuple(signature)


# ---------------------------------------------------------------------------
# Necessary conditions and the candidate set N.
# ---------------------------------------------------------------------------

def violations(signature) -> set[str]:
    """Names of the necessary conditions that a signature breaks (see PROOF.md)."""
    broken = set()
    sources = [source for source, _ in signature]
    readers = [reader for _, reader in signature]
    # C1: a message cannot read only the plane that its source never touches.
    if any(pair in ((1, 2), (2, 1)) for pair in signature):
        broken.add("C1")
    # C2: at most two messages are confined to one plane, on either side.
    for mask in (1, 2):
        if sources.count(mask) > 2 or readers.count(mask) > 2:
            broken.add("C2")
    # C3: two confined messages on one side confine the other two on the other side.
    for mask, other in ((1, 2), (2, 1)):
        if sources.count(mask) == 2 and any(
                readers[k] != other for k in range(4) if sources[k] != mask):
            broken.add("C3")
        if readers.count(mask) == 2 and any(
                sources[k] != other for k in range(4) if readers[k] != mask):
            broken.add("C3")
    return broken


def candidate_signatures():
    types = [(source, reader) for source in (1, 2, 3) for reader in (1, 2, 3)]
    return list(itertools.product(types, repeat=4))


def necessary_set(dropped: frozenset = frozenset()):
    return {signature for signature in candidate_signatures()
            if not (violations(signature) - set(dropped))}


# ---------------------------------------------------------------------------
# Planes over F_p and the exhaustive plane-pair enumeration.
# ---------------------------------------------------------------------------

PAIR_SIGNS = {(i, j): (-1) ** (1 + i + j) for i in range(4) for j in range(i + 1, 4)}
COMPLEMENT = {(i, j): tuple(c for c in range(4) if c not in (i, j))
              for i in range(4) for j in range(i + 1, 4)}


def plucker(first, second):
    return {(i, j): first[i] * second[j] - first[j] * second[i]
            for i in range(4) for j in range(i + 1, 4)}


def stacked_determinant(pa: dict, pb: dict) -> int:
    """det of the 4x4 matrix with rows (a1, a2, b1, b2), by Laplace along rows 0,1."""
    return sum(PAIR_SIGNS[s] * pa[s] * pb[COMPLEMENT[s]] for s in PAIR_SIGNS)


def planes_mod(p: int):
    """All 2-dimensional subspaces of F_p^4, as reduced row echelon pairs."""
    planes = []
    for c1, c2 in itertools.combinations(range(4), 2):
        free1 = [c for c in range(c1 + 1, 4) if c != c2]
        free2 = list(range(c2 + 1, 4))
        for v1 in itertools.product(range(p), repeat=len(free1)):
            for v2 in itertools.product(range(p), repeat=len(free2)):
                first = [0] * 4
                first[c1] = 1
                for c, v in zip(free1, v1):
                    first[c] = v
                second = [0] * 4
                second[c2] = 1
                for c, v in zip(free2, v2):
                    second[c] = v
                planes.append((tuple(first), tuple(second)))
    need(len(planes) == (p * p + 1) * (p * p + p + 1), f"F_{p} plane count")
    return planes


def plane_data_mod(plane, p: int):
    first, second = plane
    vectors = {tuple((a * x + b * y) % p for x, y in zip(first, second))
               for a in range(p) for b in range(p)}
    e_mask = sum(1 << j for j in range(4)
                 if tuple(int(i == j) for i in range(4)) in vectors)
    f_mask = sum(1 << j for j in range(4) if first[j] == 0 and second[j] == 0)
    return e_mask, f_mask, plucker(first, second)


def enumerate_field(p: int, direct_stride: int):
    """Signatures of all complementary plane pairs over F_p.

    Every pair is priced by the rule; each direct_stride-th complementary pair
    (all of them when the stride is 1) is also priced by inverting the matrix
    whose rows are the two row-reduced bases, and the two signatures must agree.
    """
    planes = planes_mod(p)
    data = [plane_data_mod(plane, p) for plane in planes]
    realized = set()
    complementary = 0
    direct_checked = 0
    swapped_disagreements = 0
    for index_a, plane_a in enumerate(planes):
        e_a, f_a, pa = data[index_a]
        for index_b, plane_b in enumerate(planes):
            e_b, f_b, pb = data[index_b]
            if stacked_determinant(pa, pb) % p == 0:
                continue
            complementary += 1
            by_rule = rule_signature(e_a, f_a, e_b, f_b)
            realized.add(by_rule)
            if complementary % direct_stride == 0:
                matrix = [list(plane_a[0]), list(plane_a[1]),
                          list(plane_b[0]), list(plane_b[1])]
                inverse = inverse_mod(matrix, p)
                need(inverse is not None, f"F_{p}: complementary pair is singular")
                need(signature_direct(matrix, inverse) == by_rule,
                     f"F_{p}: plane rule differs from direct inversion")
                direct_checked += 1
                swapped_disagreements += (
                    rule_signature_swapped(e_a, f_a, e_b, f_b) != by_rule)
    return {
        "planes": len(planes),
        "complementary_pairs": complementary,
        "direct_inversions": direct_checked,
        "signatures_realized": len(realized),
        "swapped_rule_disagreements": swapped_disagreements,
    }, realized


def gl4_f2_signatures():
    """Direct census of every 4x4 matrix over F_2 (no plane parametrization)."""
    realized = set()
    invertible = 0
    for encoded in range(1 << 16):
        matrix = [[(encoded >> (4 * r + c)) & 1 for c in range(4)] for r in range(4)]
        inverse = inverse_mod(matrix, 2)
        if inverse is None:
            continue
        invertible += 1
        realized.add(signature_direct(matrix, inverse))
    need(invertible == 20160, "|GL_4(F_2)|")
    return invertible, realized


# ---------------------------------------------------------------------------
# Integer witnesses from planes spanned by ternary vectors.
# ---------------------------------------------------------------------------

def ternary_vectors():
    vectors = []
    for vector in itertools.product((-1, 0, 1), repeat=4):
        if any(vector) and next(x for x in vector if x) > 0:
            vectors.append(vector)
    return vectors


def normalized_plucker(pl: dict):
    values = [pl[key] for key in sorted(pl)]
    divisor = 0
    for value in values:
        divisor = gcd(divisor, value)
    if divisor == 0:
        return None
    values = [value // divisor for value in values]
    if next(v for v in values if v) < 0:
        values = [-v for v in values]
    return tuple(values)


def ternary_planes():
    """Distinct planes spanned by two ternary vectors, with their first spanning pair."""
    seen = {}
    planes = []
    for first, second in itertools.combinations(ternary_vectors(), 2):
        pl = plucker(first, second)
        key = normalized_plucker(pl)
        if key is None or key in seen:
            continue
        seen[key] = len(planes)
        e_mask = sum(1 << j for j in range(4)
                     if all(pl[(a, b)] == 0 for a in range(4) for b in range(a + 1, 4)
                            if j not in (a, b)))
        f_mask = sum(1 << j for j in range(4) if first[j] == 0 and second[j] == 0)
        planes.append((first, second, e_mask, f_mask, pl))
    return planes


def search_witnesses():
    """First ternary integer basis found for each signature, plus the full image."""
    planes = ternary_planes()
    witnesses = {}
    image = set()
    for first_a, second_a, e_a, f_a, pa in planes:
        for first_b, second_b, e_b, f_b, pb in planes:
            if stacked_determinant(pa, pb) == 0:
                continue
            signature = rule_signature(e_a, f_a, e_b, f_b)
            image.add(signature)
            if signature not in witnesses:
                witnesses[signature] = [list(first_a), list(second_a),
                                        list(first_b), list(second_b)]
    return len(planes), witnesses, image


def verify_witness(matrix, signature) -> None:
    """Exact check: integer entries, nonzero determinant, signature from P^-1."""
    need(len(matrix) == 4 and all(len(row) == 4 for row in matrix), "witness shape")
    need(all(type(v) is int for row in matrix for v in row), "witness entries are integers")
    inverse = inverse_fraction(matrix)
    need(inverse is not None, "witness matrix is singular")
    need(signature_direct(matrix, inverse) == signature, "witness signature mismatch")


# ---------------------------------------------------------------------------
# Binding to PR3997's recorded artifacts.
# ---------------------------------------------------------------------------

def predecessor_binding(necessary):
    receipt = (PREDECESSOR / "TERNARY-SCREEN.txt").read_bytes()
    lines = receipt.decode("ascii").splitlines()
    need(lines and lines[0].startswith("TERNARY_SCREEN_V1 "), "PR3997 receipt header")
    codes = set()
    for line in lines[1:]:
        fields = line.split()
        need(len(fields) == 17, "PR3997 receipt row shape")
        codes.add(int(fields[0], 16))
    need(len(codes) == len(lines) - 1, "PR3997 receipt has duplicate codes")
    mine = {encode(signature) for signature in necessary}
    need(codes == mine, "necessary set differs from the PR3997 signature codes")
    recorded = json.loads((PREDECESSOR / "RESULT.json").read_bytes())
    need(recorded["generic_source_reader_support_patterns"] == EXPECTED_SIGNATURES,
         "PR3997 RESULT.json generic pattern count")
    need(recorded["plane_pairs"] == 1540, "PR3997 RESULT.json plane pair count")
    need(recorded["minimum_copy_cost"] == 8 and recorded["baseline_copy_cost"] == 8,
         "PR3997 RESULT.json minimum copy cost")
    need(recorded["strict_improvements"] == 0, "PR3997 RESULT.json strict improvements")
    return {
        "receipt_codes": len(codes),
        "receipt_sha256": digest(receipt),
        "result_json_sha256": digest((PREDECESSOR / "RESULT.json").read_bytes()),
        "recorded_plane_pairs": recorded["plane_pairs"],
        "recorded_minimum_copy_cost": recorded["minimum_copy_cost"],
        "recorded_strict_improvements": recorded["strict_improvements"],
    }


# ---------------------------------------------------------------------------
# Assembly.
# ---------------------------------------------------------------------------

def witness_payload(witnesses):
    rows = []
    for signature in sorted(witnesses, key=encode):
        rows.append({"code": f"{encode(signature):04x}",
                     "signature": [list(term) for term in signature],
                     "matrix": witnesses[signature]})
    return rows


def compute(extended: bool = False) -> tuple[dict, list]:
    necessary = necessary_set()
    need(len(candidate_signatures()) == 9 ** 4, "candidate count")
    need(len(necessary) == EXPECTED_SIGNATURES, "necessary set size")

    ablation = {}
    for dropped in (("C1",), ("C2",), ("C3",), ("C1", "C2"), ("C1", "C3"),
                    ("C2", "C3"), ("C1", "C2", "C3")):
        ablation["+".join(dropped)] = len(necessary_set(frozenset(dropped)))
    kept_only = {name: len(necessary_set(frozenset({"C1", "C2", "C3"} - {name})))
                 for name in ("C1", "C2", "C3")}

    # Laplace/Pluecker determinant used for complement tests vs an independent determinant.
    probe = [[3, 1, 4, 1], [5, 9, 2, 6], [5, 3, 5, 8], [9, 7, 9, 3]]
    need(stacked_determinant(plucker(probe[0], probe[1]), plucker(probe[2], probe[3]))
         == integer_determinant(probe), "Laplace/Pluecker determinant control")

    finite = {}
    realized_by_field = {}
    for p in PRIMES + (EXTENDED_PRIMES if extended else ()):
        stride = 1 if p <= 3 else 61 if p == 5 else 997
        summary, realized = enumerate_field(p, stride)
        need(realized <= necessary, f"F_{p} realizes a signature outside N")
        summary["subset_of_necessary_set"] = True
        summary["direct_stride"] = stride
        finite[f"F_{p}"] = summary
        realized_by_field[p] = realized
    invertible, f2_direct = gl4_f2_signatures()
    need(f2_direct == realized_by_field[2],
         "GL_4(F_2) census differs from the F_2 plane-pair census")

    plane_count, witnesses, image = search_witnesses()
    need(image <= necessary, "a ternary plane pair realizes a signature outside N")
    need(set(witnesses) == necessary, "ternary planes do not realize all of N")
    for signature, matrix in witnesses.items():
        verify_witness(matrix, signature)
    witness_rows = witness_payload(witnesses)
    witness_bytes = (json.dumps(witness_rows, indent=1, sort_keys=True) + "\n").encode()

    binding = predecessor_binding(necessary)

    result = {
        "schema": SCHEMA,
        "candidate_signatures": 9 ** 4,
        "necessary_set_size": len(necessary),
        "necessary_set_codes_sha256": digest(b"".join(
            encode(s).to_bytes(2, "big") for s in sorted(necessary, key=encode))),
        "ablation_sizes_when_dropping": ablation,
        "size_keeping_only_condition": kept_only,
        "gl4_f2_invertible_matrices": invertible,
        "gl4_f2_signatures": len(f2_direct),
        "finite_field_plane_pair_census": finite,
        "ternary_planes": plane_count,
        "ternary_signatures_realized": len(image),
        "witness_count": len(witness_rows),
        "witnesses_sha256": digest(witness_bytes),
        "predecessor_binding": binding,
        "scope_limits": [
            "plane-level signatures of invertible 4x4 matrices over any field; two planes of two ports",
            "the copy-invoice consequence uses PR3997's recorded minimum 8 on 1540 plane pairs and its statement that pricing depends only on the signature",
            "overcomplete factorizations, three or more planes, coefficient scaling cost and physical routing are outside scope",
        ],
    }
    return result, witness_rows


def integer_determinant(matrix) -> int:
    total = 0
    for permutation in itertools.permutations(range(4)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(4) for j in range(i + 1, 4))
        product = 1
        for row, column in enumerate(permutation):
            product *= matrix[row][column]
        total += -product if inversions & 1 else product
    return total


def controls(necessary, witness_rows) -> int:
    """Rejection controls: each action must raise CheckFailure."""
    passed = 0

    def must_fail(action, message):
        nonlocal passed
        try:
            action()
        except CheckFailure:
            passed += 1
            return
        raise CheckFailure("control did not fail: " + message)

    first, second = witness_rows[0], witness_rows[1]
    first_signature = tuple(tuple(term) for term in first["signature"])
    second_signature = tuple(tuple(term) for term in second["signature"])
    need(first_signature != second_signature, "control witnesses must differ")

    tampered = [list(r) for r in first["matrix"]]
    tampered[0][0] += 1
    must_fail(lambda: verify_witness(tampered, first_signature), "tampered witness entry")
    must_fail(lambda: verify_witness([[1, 0, 0, 0]] * 4, first_signature),
              "singular witness matrix")
    must_fail(lambda: verify_witness(first["matrix"], second_signature),
              "witness paired with another signature")
    must_fail(lambda: verify_witness([[1.0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0],
                                      [0, 0, 0, 1]], first_signature),
              "non-integer witness entry")
    missing = sorted(necessary, key=encode)[0]
    must_fail(lambda: predecessor_binding(necessary - {missing}),
              "necessary set missing one recorded signature")
    must_fail(lambda: need(not violations(((1, 2),) * 4),
                           "signature with every reader outside its source plane"),
              "impossible signature (A source, B reader) four times")
    must_fail(lambda: need(not violations(((1, 1),) * 4),
                           "four messages confined to plane A"),
              "four messages confined to one plane")
    mismatch, _ = enumerate_field(2, 1)
    must_fail(lambda: need(mismatch["swapped_rule_disagreements"] == 0,
                           "wrong reader rule agrees with direct inversion"),
              "wrong reader rule must disagree with direct inversion")
    for dropped in ("C1", "C2", "C3"):
        must_fail(lambda dropped=dropped: need(
            len(necessary_set(frozenset({dropped}))) == EXPECTED_SIGNATURES,
            f"dropping {dropped} leaves the size at 439"),
            f"dropping {dropped} must enlarge the candidate set")
    return passed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="regenerate RESULT.json and WITNESSES.json")
    parser.add_argument("--extended", action="store_true",
                        help="also enumerate every plane pair over F_7 (slow, opt-in)")
    args = parser.parse_args()
    result, witness_rows = compute(extended=args.extended)
    necessary = necessary_set()
    result["controls_passed"] = controls(necessary, witness_rows)
    result_bytes = (json.dumps(result, indent=1, sort_keys=True) + "\n").encode()
    witness_bytes = (json.dumps(witness_rows, indent=1, sort_keys=True) + "\n").encode()
    if args.write:
        RESULT_PATH.write_bytes(result_bytes)
        WITNESS_PATH.write_bytes(witness_bytes)
    elif not args.extended:
        need(RESULT_PATH.read_bytes() == result_bytes, "RESULT.json differs from recomputation")
        need(WITNESS_PATH.read_bytes() == witness_bytes,
             "WITNESSES.json differs from recomputation")
    if args.extended:
        print(json.dumps(result["finite_field_plane_pair_census"], indent=1, sort_keys=True))
    print(json.dumps({"necessary": len(necessary),
                      "witnesses": len(witness_rows),
                      "controls": result["controls_passed"]}, sort_keys=True))
    print("PASS_TWO_PLANE_SIGNATURE_CLASSES")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckFailure as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)
