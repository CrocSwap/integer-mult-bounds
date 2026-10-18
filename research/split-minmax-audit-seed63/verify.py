#!/usr/bin/env python3
"""Exact primal/cut certificates for the split min-max. Standard library only.

No predecessor code or randomized field-rank evaluation is used. The primal
enumerates disjoint nonsingular minors; the dual enumerates all row/column cuts.
Every winning certificate is checked again using permutation determinants.
"""

import argparse
from collections import Counter
from functools import cache
import hashlib
from itertools import permutations, product
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parent
SEED = 63


def require(condition, message):
    if not condition:
        raise ValueError(message)


def indices(mask, n):
    return tuple(i for i in range(n) if mask & (1 << i))


def binary_rank(rows):
    """Row elimination, with each row represented by an integer bit vector."""
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row
                break
            row ^= pivots[pivot]
    return len(pivots)


def determinant_parity(rows, row_mask, col_mask):
    """Independent Leibniz determinant over F2; no elimination."""
    n = len(rows)
    rr, cc = indices(row_mask, n), indices(col_mask, n)
    require(len(rr) == len(cc), "determinant requires a square minor")
    parity = 0
    for ordering in permutations(cc):
        term = 1
        for r, c in zip(rr, ordering):
            term &= (rows[r] >> c) & 1
        parity ^= term
    return parity


@cache
def minor_rank(rows, row_mask, col_mask):
    """Rank by searching square minors and evaluating permutation determinants."""
    from itertools import combinations

    n = len(rows)
    rr, cc = indices(row_mask, n), indices(col_mask, n)
    for size in range(min(len(rr), len(cc)), 0, -1):
        for rs in combinations(rr, size):
            rm = sum(1 << r for r in rs)
            for cs in combinations(cc, size):
                cm = sum(1 << c for c in cs)
                if determinant_parity(rows, rm, cm):
                    return size
    return 0


@cache
def rank_table(rows):
    n = len(rows)
    return tuple(
        tuple(binary_rank(rows[i] & cm for i in indices(rm, n))
              for cm in range(1 << n))
        for rm in range(1 << n)
    )


def matrix(encoded, n):
    return tuple((encoded >> (n * r)) & ((1 << n) - 1) for r in range(n))


def masked_blocks(rows, row_supports, col_supports, colors=3):
    n = len(rows)
    return tuple(
        tuple(
            rows[r] & sum(1 << c for c in range(n) if col_supports[c] & (1 << color))
            if row_supports[r] & (1 << color) else 0
            for r in range(n)
        )
        for color in range(colors)
    )


@cache
def solve(blocks):
    """Return an attaining minor packing and an equal-valued cut, or fail."""
    require(bool(blocks), "at least one color is required")
    n = len(blocks[0])
    require(all(len(b) == n for b in blocks), "unequal matrix dimensions")
    require(all(0 <= row < (1 << n) for b in blocks for row in b), "nonbinary row")
    tables = tuple(rank_table(b) for b in blocks)
    # States record used original rows and columns, and one minor per color.
    states = {(0, 0): ()}
    for table in tables:
        minors = tuple(
            (rm, cm) for rm in range(1 << n) for cm in range(1 << n)
            if rm.bit_count() == cm.bit_count() == table[rm][cm]
        )
        following = {}
        for (used_r, used_c), witness in sorted(states.items()):
            for rm, cm in minors:
                if not (used_r & rm or used_c & cm):
                    following.setdefault((used_r | rm, used_c | cm), witness + ((rm, cm),))
        states = following
    used = max(sorted(states), key=lambda pair: pair[0].bit_count())
    primal = used[0].bit_count()
    dual, cut_r, cut_c = min(
        (2 * n - rm.bit_count() - cm.bit_count() + sum(t[rm][cm] for t in tables), rm, cm)
        for rm in range(1 << n) for cm in range(1 << n)
    )
    certificate = (primal, states[used], (cut_r, cut_c))
    require(primal == dual, f"MINMAX_MISMATCH: {blocks!r}: {primal} != {dual}")
    check_certificate(blocks, certificate)
    return certificate


def check_certificate(blocks, certificate):
    """Weak duality plus an attaining packing certify each instance exactly."""
    n = len(blocks[0])
    value, witness, (cut_r, cut_c) = certificate
    require(len(witness) == len(blocks), "wrong number of minor blocks")
    require(0 <= cut_r < (1 << n) and 0 <= cut_c < (1 << n), "cut outside universe")
    used_r = used_c = attained = 0
    for rows, (rm, cm) in zip(blocks, witness):
        require(0 <= rm < (1 << n) and 0 <= cm < (1 << n), "minor outside universe")
        require(not (used_r & rm or used_c & cm), "reused original row or column")
        require(rm.bit_count() == cm.bit_count(), "nonsquare minor")
        require(determinant_parity(rows, rm, cm) == 1, "singular minor")
        used_r |= rm
        used_c |= cm
        attained += rm.bit_count()
    upper = 2 * n - cut_r.bit_count() - cut_c.bit_count()
    upper += sum(minor_rank(rows, cut_r, cut_c) for rows in blocks)
    require(attained == value == upper, "primal/cut certificate values disagree")


class Sample:
    """Version-independent deterministic sampling, derived from assignment seed."""

    def __init__(self):
        self.counter = 0

    def below(self, limit):
        payload = f"split-minmax:{SEED}:{self.counter}".encode("ascii")
        self.counter += 1
        return int.from_bytes(hashlib.sha256(payload).digest(), "big") % limit


def rejection_controls():
    controls = []

    def rejects(name, blocks, certificate):
        try:
            check_certificate(blocks, certificate)
        except ValueError:
            controls.append(name)
        else:
            raise ValueError(f"negative control accepted: {name}")

    # Three independent colors may not each claim the same physical row/column.
    one = ((1,), (1,), (1,))
    require(solve(one)[0] == 1, "one-cell shared-capacity positive control")
    rejects("reuse_one_original_row", one, (3, ((1, 1),) * 3, (0, 0)))
    rejects("wrong_claimed_value", one, (0, solve(one)[1], solve(one)[2]))
    rejects("nonsharp_cut_is_not_an_optimality_certificate", one, (1, solve(one)[1], (0, 0)))
    rejects("out_of_universe_cut", one, (1, solve(one)[1], (2, 0)))

    # This cyclic binary matrix has determinant 2 over Q and 0 over F2.
    cyclic = ((3, 6, 5),)
    require(solve(cyclic)[0] == 2, "cyclic parity positive control")
    rejects("rational_rank_instead_of_binary_rank", cyclic, (3, ((7, 7),), (7, 7)))
    rejects("term_matching_instead_of_nonsingular_minor", ((3, 3),), (2, ((3, 3),), (3, 3)))

    # Separate row and column assignments are essential; an off-diagonal minor
    # is a valid split even when there are no usable diagonal entries.
    off_diagonal = ((2, 0), (0, 1), (0, 0))
    require(solve(off_diagonal)[0] == 2, "off-diagonal split positive control")
    rejects("force_same_row_and_column_minor", off_diagonal, (2, ((1, 1), (2, 2), (0, 0)), (0, 3)))

    # Sum of full block ranks is only an upper bound, not a packing optimum.
    require(sum(binary_rank(b) for b in one) == 3 > solve(one)[0], "naive sum control")
    controls.append("sum_of_full_ranks_overcounts_shared_capacity")
    # A zero specialization is not a generic-rank oracle, even for one cell.
    require(binary_rank((0,)) == 0 < solve(one)[0], "bad specialization control")
    controls.append("zero_field_specialization_loses_generic_rank")

    # Omitting either deletion penalty creates an invalid zero-cost cut.
    for omitted in ("row", "column"):
        wrong_cut_value = min(
            (1 - s.bit_count() if omitted != "row" else 0)
            + (1 - t.bit_count() if omitted != "column" else 0)
            + sum(rank_table(b)[s][t] for b in one)
            for s in range(2) for t in range(2)
        )
        require(wrong_cut_value == 0 < solve(one)[0], "cut deletion penalties are necessary")
    controls.append("cut_formula_without_deletion_penalties_is_false")

    asymmetric = ((0, 0), (1, 0), (1, 0))
    same_set_minimum = min(4 - 2 * s.bit_count() + sum(rank_table(b)[s][s] for b in asymmetric)
                           for s in range(4))
    require(solve(asymmetric)[0] == 1 < same_set_minimum == 2, "independent cuts are necessary")
    controls.append("forcing_S_equal_T_misses_the_optimal_cut")

    # Unit diagonal does not make the FULL cost alone sufficient. This is an
    # algebraic masked-matrix control, not a rational decoder counterexample.
    principal_gap = ((3, 6, 5, 8), (0, 0, 0, 8), (0, 0, 0, 8))
    require(sum(binary_rank(b) for b in principal_gap) == 5, "full cost control")
    require(sum(rank_table(b)[7][7] for b in principal_gap) == 2, "principal cost control")
    require(solve(principal_gap)[0] == 3 < 4, "principal-restriction hypothesis is necessary")
    controls.append("full_cost_alone_does_not_force_a_perfect_split")
    return controls


def check_source():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    source = sources["external_sources"][0]
    require(source["commit"] == "113a718265c62aec301c5695f4bfb9c421bef7ab", "changed audited head")
    actual = hashlib.sha256((PACKAGE / source["retained_excerpt"]).read_bytes()).hexdigest()
    require(actual == source["excerpt_sha256"], "audited statement digest mismatch")
    return source["excerpt_sha256"]


def run():
    source_digest = check_source()
    digest = hashlib.sha256()
    buckets = {}
    unique_blocks = set()
    principal_premise_cases = 0

    def case(bucket, descriptor, blocks):
        nonlocal principal_premise_cases
        certificate = solve(blocks)
        n = len(blocks[0])
        tables = tuple(rank_table(b) for b in blocks)
        principal_premise = all(sum(t[i][i] for t in tables) >= i.bit_count()
                                for i in range(1 << n))
        if principal_premise:
            principal_premise_cases += 1
            require(certificate[0] == n, "principal costs did not imply a perfect split")
        unique_blocks.add(blocks)
        buckets.setdefault(bucket, Counter())[certificate[0]] += 1
        payload = [bucket, descriptor, blocks, certificate, principal_premise]
        digest.update(json.dumps(payload, separators=(",", ":")).encode("ascii") + b"\n")

    # All B and all support masks for three colors, including empty supports.
    # n=0,1,2 counts: 1, 128, 65536. No symmetry reduction or pruning.
    for n in range(3):
        for encoded in range(1 << (n * n)):
            rows = matrix(encoded, n)
            for supports in product(range(8), repeat=2 * n):
                case(f"all_common_B_n{n}", [encoded, supports],
                     masked_blocks(rows, supports[:n], supports[n:]))

    # The proof also allows different matrices in the three blocks. Complete
    # this separate 16^3 domain; it is not another sample of common B masks.
    for encoded in product(range(16), repeat=3):
        case("all_distinct_blocks_n2", encoded, tuple(matrix(e, 2) for e in encoded))

    sampler = Sample()
    for n, count in ((3, 160), (4, 96), (5, 32)):
        for index in range(count):
            rows = matrix(sampler.below(1 << (n * n)), n)
            supports = tuple(sampler.below(8) for _ in range(2 * n))
            case(f"sample_common_B_n{n}", [index, rows, supports],
                 masked_blocks(rows, supports[:n], supports[n:]))
            blocks = tuple(matrix(sampler.below(1 << (n * n)), n) for _ in range(3))
            case(f"sample_distinct_blocks_n{n}", [index, blocks], blocks)

    controls = rejection_controls()
    return {
        "status": "PASS_SPLIT_MINMAX_AUDIT",
        "seed": SEED,
        "source_excerpt_sha256": source_digest,
        "input_cases": sum(sum(hist.values()) for hist in buckets.values()),
        "unique_block_tuples": len(unique_blocks),
        "principal_cost_premise_cases": principal_premise_cases,
        "coverage": {name: {str(k): hist[k] for k in sorted(hist)} for name, hist in buckets.items()},
        "instance_certificate_sha256": digest.hexdigest(),
        "controls": controls,
        "scope": "Exact finite primal/cut certificates; the general written proof is in PROOF.md. No kappa or full multiplication theorem.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-expected", action="store_true", help="regenerate the finite receipt")
    args = parser.parse_args()
    result = run()
    expected = PACKAGE / "EXPECTED.json"
    if args.write_expected:
        expected.write_text(json.dumps(result, indent=2) + "\n")
    else:
        require(result == json.loads(expected.read_text()), "finite receipt mismatch")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
