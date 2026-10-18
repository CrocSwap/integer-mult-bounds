#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent exact neighborhood-rank oracle for the specified E8 punctures.

Python >= 3.10, standard library only; no imports from the main checker.
Representatives q are twice the usual norm-squared-two E8 roots. They are
lexicographically sorted after identifying q and -q by first-nonzero-positive.
The mask is q_i.q_j == 0 (mod 8), INCLUDING i == j.

For every target j in every live domain, an eight-row minor of its allowed
neighbors is certified nonsingular modulo the fixed prime 3. Its INTEGER
determinant therefore cannot vanish: the rank is exactly eight over Q and C.
This is an exact certificate, not a randomized finite-field rank estimate.
Seed 28 only fixes deterministic SHA-256 tie-breaking between root frames.

All 143584 domain/target assignments are recomputed and checked. The artifact
stores the 122 reused minors and a canonical digest of assignments, rather
than 143584 repetitive records. run() builds and validates the complete data.
Without options the CLI also compares it to TENSOR-CERTIFICATE.json. Use
--write PATH to write JSON, or --check PATH to compare a different artifact.
"""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


PRIME = 3
SEED = 28
DIM = 8
HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def canonical(value):
    return json.dumps(value, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def doubled_root_lines():
    """Build the 56 D8 and 64 half-integral lines, without a source data file."""
    lines = set()
    for a, b in itertools.combinations(range(DIM), 2):
        for sign in (-1, 1):
            root = [0] * DIM
            root[a], root[b] = 2, 2 * sign
            lines.add(tuple(root))
    for tail in itertools.product((-1, 1), repeat=DIM - 1):
        root = (1,) + tail
        if sum(value < 0 for value in root) % 2 == 0:
            lines.add(root)
    roots = sorted(lines)
    require(len(roots) == 120, "root-line count")
    require(all(dot(q, q) == 8 for q in roots), "root lengths")
    require(all(dot(q, r) in (-4, 0, 4)
                for i, q in enumerate(roots) for r in roots[i + 1:]),
            "off-diagonal true-root inner products")
    return roots


def fixed_frame(roots):
    """The eight lines 2(e_0 +/- e_1), ..., 2(e_6 +/- e_7)."""
    frame = []
    for a in range(0, DIM, 2):
        for sign in (-1, 1):
            root = [0] * DIM
            root[a], root[a + 1] = 2, 2 * sign
            frame.append(roots.index(tuple(root)))
    return tuple(sorted(frame))


def enumerate_frames(roots, live):
    """Exhaust all increasing size-eight cliques of the orthogonality graph."""
    neighbors = {}
    for i in live:
        neighbors[i] = sum(1 << j for j in live
                           if j > i and dot(roots[i], roots[j]) == 0)
    frames = []

    def extend(prefix, candidates):
        needed = DIM - len(prefix)
        if not needed:
            frames.append(prefix)
            return
        while candidates.bit_count() >= needed:
            bit = candidates & -candidates
            candidates ^= bit
            vertex = bit.bit_length() - 1
            extend(prefix + (vertex,), candidates & neighbors[vertex])

    extend((), sum(1 << i for i in live))
    require(len(frames) == 1260, "second-frame census must contain 1260 frames")
    require(frames == sorted(set(frames)), "duplicate or unordered frames")
    return frames


def geometry():
    roots = doubled_root_lines()
    first = fixed_frame(roots)
    live = tuple(i for i in range(len(roots)) if i not in first)
    frames = enumerate_frames(roots, live)
    domains = [("P112", ())]
    domains += [(f"P111-{i:03d}", (i,)) for i in live]
    domains += [(f"P104-{k:04d}", frame) for k, frame in enumerate(frames)]
    require(len(domains) == 1373, "finite domain size")
    return roots, first, live, frames, domains


def rank_and_determinant(rows, width):
    """Ordinary exact Gaussian elimination modulo the fixed prime 3."""
    matrix = [[x % PRIME for x in row] for row in rows]
    require(all(len(row) == width for row in matrix), "matrix width")
    rank = 0
    determinant = 1
    for column in range(width):
        pivot = next((r for r in range(rank, len(matrix))
                      if matrix[r][column]), None)
        if pivot is None:
            continue
        if pivot != rank:
            matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
            determinant = -determinant
        value = matrix[rank][column]
        determinant = determinant * value % PRIME
        inverse = pow(value, -1, PRIME)
        row = matrix[rank]
        for c in range(column, width):
            row[c] = row[c] * inverse % PRIME
        for r in range(rank + 1, len(matrix)):
            value = matrix[r][column]
            if value:
                other = matrix[r]
                for c in range(column, width):
                    other[c] = (other[c] - value * row[c]) % PRIME
        rank += 1
        if rank == len(matrix):
            break
    determinant = determinant % PRIME if len(matrix) == width and rank == width else 0
    return rank, determinant


def controls(roots, live, frame):
    """Semantic failures: losing diagonals, orientation, or row independence."""
    rows = [roots[i] for i in frame]
    require(rank_and_determinant(rows, DIM)[0] == DIM, "positive control")

    # For every target j, the nonzero coefficient vector q_j annihilates
    # EVERY allowed off-diagonal row. This also holds in all live subsets.
    all_off_diagonal = [(i, j) for i in live for j in live
                        if i != j and dot(roots[i], roots[j]) % 8 == 0]
    require(all(dot(roots[i], roots[j]) == 0 for i, j in all_off_diagonal),
            "q_j must lie in the diagonal-free neighborhood kernel")
    no_diagonal_rank = rank_and_determinant(rows[1:], DIM)[0]
    require(no_diagonal_rank == 7 and dot(rows[0], rows[0]) == 8,
            "diagonal-free rank and detected diagonal residual")

    # Secondary tensor control: ordered constraints matter for arbitrary,
    # non-symmetric bilinear coefficients. B=q_b q_a^T, b>a in this frame,
    # vanishes on every i<=j frame pair, but has residual 64 at (b,a).
    # This is a control on the frame witness, not a rank claim about the
    # complete upper-triangle-only mask on all 112 roots.
    def tensor(i, j):
        return [a * b for a in roots[i] for b in roots[j]]

    a, b = frame[0], frame[1]
    upper_pairs = [(i, j) for i in frame for j in frame if i <= j]
    upper_rank = rank_and_determinant([tensor(i, j) for i, j in upper_pairs], 64)[0]
    ordered_rank, ordered_determinant = rank_and_determinant(
        [tensor(i, j) for i in frame for j in frame], 64)
    upper_residuals = [dot(roots[i], roots[b]) * dot(roots[a], roots[j])
                       for i, j in upper_pairs]
    reverse_residual = dot(roots[b], roots[b]) * dot(roots[a], roots[a])
    require(upper_rank == 36 and all(x == 0 for x in upper_residuals)
            and reverse_residual == 64 and ordered_rank == 64
            and ordered_determinant != 0, "ordered-pair control")

    corrupt_rank, corrupt_determinant = rank_and_determinant(rows[:-1] + [rows[0]], DIM)
    require(corrupt_rank == 7 and corrupt_determinant == 0,
            "duplicate-row corruption must be rejected")
    return {
        "positive_neighborhood_rank": 8,
        "diagonal_free_kernel_checked_ordered_pairs": len(all_off_diagonal),
        "diagonal_free_frame_neighborhood_rank": no_diagonal_rank,
        "omitted_diagonal_residual": 8,
        "ordered_frame_tensor_rank": ordered_rank,
        "ordered_frame_tensor_determinant_mod_3": ordered_determinant,
        "upper_triangle_only_frame_tensor_rank": upper_rank,
        "omitted_reverse_pair_residual": reverse_residual,
        "duplicate_basis_row_rank": corrupt_rank,
        "duplicate_basis_row_determinant_mod_3": corrupt_determinant,
    }


def run():
    """Reconstruct all geometry and verify every live-target span exactly."""
    roots, first, live, frames, domains = geometry()
    ranked = sorted(frames, key=lambda frame: hashlib.sha256(
        (str(SEED) + ":" + ",".join(map(str, frame))).encode("ascii")).digest())
    by_target = {i: [frame for frame in ranked if i in frame] for i in live}
    require(all(len(by_target[i]) == 90 for i in live), "frames per live root")
    allowed = {j: sum(1 << i for i in live if dot(roots[i], roots[j]) % 8 == 0)
               for j in live}
    bank = []
    bank_bits = []
    available = {i: [] for i in live}
    uses = []
    assignment_hash = hashlib.sha256()
    target_counts = {"P112": 0, "P111": 0, "P104": 0}
    # The census determines every deletion explicitly; no sampled domains.
    for name, deleted in domains:
        removed = set(deleted)
        removed_bits = sum(1 << i for i in deleted)
        for target in live:
            if target in removed:
                continue
            chosen = next((k for k in available[target]
                           if not (bank_bits[k] & removed_bits)), None)
            if chosen is None:
                survivor = next((frame for frame in by_target[target]
                                 if removed.isdisjoint(frame)), None)
                require(survivor is not None, f"no surviving basis for {name}/{target}")
                chosen = len(bank)
                rank, determinant = rank_and_determinant([roots[i] for i in survivor], DIM)
                require(rank == DIM and determinant != 0, "singular neighborhood minor")
                bank.append({"root_ids": list(survivor), "rank_mod_3": rank,
                             "determinant_mod_3": determinant})
                bank_bits.append(sum(1 << i for i in survivor))
                uses.append(0)
                for i in survivor:
                    available[i].append(chosen)
            # Each target receives eight actual, live, allowed rows. Rank of
            # every reused minor was checked on creation, above.
            witness = bank_bits[chosen]
            require(witness.bit_count() == DIM, "witness distinctness")
            require(witness & (1 << target), "witness must contain its target")
            require(not (witness & removed_bits), "witness contains a deleted root")
            require(not (witness & ~allowed[target]), "witness uses a forbidden mask pair")
            uses[chosen] += 1
            target_counts[name.split("-")[0]] += 1
            assignment_hash.update(canonical([name, target, chosen]) + b"\n")
    require(target_counts == {"P112": 112, "P111": 12432, "P104": 131040},
            "incomplete live-target coverage")
    require(sum(uses) == 143584 and all(uses), "unused basis or incomplete assignment count")
    return {
        "schema": 2,
        "scope": "Exact allowed-neighborhood rank 8 at every live target in P112, all 112 P111 deletions, and all 1260 fixed-frame-pair P104 deletions; no supplier or kappa claim",
        "method": "independent orthogonality-clique enumeration and exact modular minors",
        "seed": SEED,
        "prime": PRIME,
        "root_convention": "lexicographic doubled E8 roots; first nonzero coordinate positive",
        "mask_convention": "dot(q_i,q_j) divisible by 8; diagonal included",
        "root_count": len(roots),
        "doubled_roots_sha256": digest(roots),
        "fixed_deleted_frame": list(first),
        "second_frames_sha256": digest(frames),
        "domain_counts": {"P112": 1, "P111": 112, "P104": 1260},
        "domains_sha256": digest(domains),
        "live_target_counts": target_counts,
        "assignment_count": sum(uses),
        "assignment_encoding": "one compact ASCII JSON [domain_name,target_root_id,witness_index] per line, LF terminated; domain order P112, increasing P111 deleted root, lexicographic P104 deleted frame; increasing live target",
        "assignments_sha256": assignment_hash.hexdigest(),
        "witnesses": bank,
        "witness_use_counts": uses,
        "controls": controls(roots, live, bank[0]["root_ids"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--write", type=Path, help="write deterministic JSON certificate")
    action.add_argument("--check", type=Path, help="compare another saved certificate")
    args = parser.parse_args()
    generated = run()
    if args.write:
        args.write.write_text(json.dumps(generated, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        path = args.check or HERE / "TENSOR-CERTIFICATE.json"
        supplied = json.loads(path.read_text(encoding="utf-8"))
        require(supplied == generated, "saved certificate differs from exact regeneration")
    print("PASS_TENSOR_ORACLE: 120 root lines; 1260 second frames; "
          f"1373 live domains; {generated['assignment_count']} target spans; "
          f"{len(generated['witnesses'])} exact 8-row minors; rank_Q=rank_C=8; "
          "3 semantic controls; no new kappa")


if __name__ == "__main__":
    main()
