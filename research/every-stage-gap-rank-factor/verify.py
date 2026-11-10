#!/usr/bin/env python3
"""Exact checks for the own-leaf rank factor of the every-stage paired-star gap.

Standard library only.  Every check raises on failure, so the script behaves
the same with and without ``-O``.  The written proof is in PROOF.md; this file
corroborates it on finite domains and evaluates the packing bound.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys

SEED = 20261110
CENSUS_FIELD = 2
ODD_PRIMES = (3, 5, 7)
RANDOM_HALF_WIDTHS = (2, 3, 4)
RANDOM_TRIALS = 1500
GENERAL_TRIALS = 400
SHARP_HALF_WIDTHS = (1, 2, 3, 5, 26)
MAX_STAGES = 64
TARGET_G = 31
TARGET_Q = 26
INVERSE_ATTEMPTS = 200


class CheckFailure(Exception):
    """A registered check did not hold."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


# ---------------------------------------------------------------- F_2 rows --
# A matrix over F_2 is a list of row integers; bit c of a row is column c.


def f2_mul(left: list[int], right: list[int]) -> list[int]:
    out = []
    for row in left:
        acc = 0
        for index in range(len(right)):
            if (row >> index) & 1:
                acc ^= right[index]
        out.append(acc)
    return out


def f2_add(left: list[int], right: list[int]) -> list[int]:
    require(len(left) == len(right), "row count mismatch")
    return [a ^ b for a, b in zip(left, right)]


def f2_rank(rows: list[int]) -> int:
    basis: list[int] = []
    for row in rows:
        current = row
        for vector in basis:
            current = min(current, current ^ vector)
        if current:
            basis.append(current)
    return len(basis)


def f2_identity(size: int) -> list[int]:
    return [1 << index for index in range(size)]


def f2_block(rows: list[int], row_ids: range, col_ids: range) -> list[int]:
    mask = (1 << len(col_ids)) - 1
    return [(rows[r] >> col_ids.start) & mask for r in row_ids]


def f2_random(rng: random.Random, n_rows: int, n_cols: int) -> list[int]:
    return [rng.getrandbits(n_cols) for _ in range(n_rows)]


def stage_projectors(q: int, b12: list[int], b21: list[int]) -> tuple[list[int], list[int]]:
    """P_plus and P_minus of the paired-star stage on core + leaf, d = 2q."""
    d = 2 * q
    require(len(b12) == q and len(b21) == q, "B blocks must be q by q")
    a_rows = [(1 << i) if i < q else 0 for i in range(d)]
    a_prime = [0 if i < q else (1 << i) for i in range(d)]
    b_rows = [b12[i] << q for i in range(q)] + [b21[i] for i in range(q)]
    plus, minus = [], []
    for i in range(d):
        diag_plus = a_rows[i] ^ b_rows[i]
        diag_minus = a_prime[i] ^ b_rows[i]
        plus.append(diag_plus | (b_rows[i] << d))
        minus.append(diag_minus | (b_rows[i] << d))
    for i in range(d):
        diag_plus = a_rows[i] ^ b_rows[i]
        diag_minus = a_prime[i] ^ b_rows[i]
        plus.append(b_rows[i] | (diag_plus << d))
        minus.append(b_rows[i] | (diag_minus << d))
    return plus, minus


def check_complementary_f2(p_first: list[int], p_second: list[int]) -> None:
    size = len(p_first)
    zero = [0] * size
    require(f2_mul(p_first, p_first) == p_first, "first half is not idempotent")
    require(f2_mul(p_second, p_second) == p_second, "second half is not idempotent")
    require(f2_add(p_first, p_second) == f2_identity(size), "halves do not sum to I")
    require(f2_mul(p_first, p_second) == zero, "halves are not orthogonal")
    require(f2_mul(p_second, p_first) == zero, "halves are not orthogonal")


def pinching_f2(z: list[int], p_first: list[int], p_second: list[int]) -> tuple[list[int], list[int]]:
    """Return (P_f Z P_f, P_s Z P_s)."""
    return (
        f2_mul(f2_mul(p_first, z), p_first),
        f2_mul(f2_mul(p_second, z), p_second),
    )


def lemma_holds_f2(z: list[int], p_first: list[int], p_second: list[int], d: int) -> tuple[int, int]:
    """Check the lemma on one Z with P_s Z P_f = 0.  Return (rank Z, block rank)."""
    size = 2 * d
    require(f2_mul(f2_mul(p_second, z), p_first) == [0] * size, "square condition missing")
    pzp, qzq = pinching_f2(z, p_first, p_second)
    diagonal = f2_add(pzp, qzq)
    two_sandwich = f2_add(f2_mul(z, p_first), f2_mul(p_second, z))
    require(diagonal == two_sandwich, "pinching differs from the two-sandwich form")
    rank_z = f2_rank(z)
    require(f2_rank(diagonal) == f2_rank(pzp) + f2_rank(qzq), "pinching rank is not additive")
    require(f2_rank(diagonal) <= rank_z, "pinching outranks Z")
    block_rank = f2_rank(f2_block(diagonal, range(0, d), range(d, size)))
    require(block_rank <= rank_z, "own-leaf block outranks Z")
    return rank_z, block_rank


def census_q1() -> dict[str, object]:
    """Every 4 by 4 matrix over F_2, every B, both half orders."""
    d, size = 2, 4
    histogram: dict[str, int] = {}
    legal = 0
    total = 0
    for b_bits in range(4):
        plus, minus = stage_projectors(1, [b_bits & 1], [(b_bits >> 1) & 1])
        for p_first, p_second in ((plus, minus), (minus, plus)):
            check_complementary_f2(p_first, p_second)
            for code in range(1 << (size * size)):
                total += 1
                z = [(code >> (size * r)) & 15 for r in range(size)]
                if f2_mul(f2_mul(p_second, z), p_first) != [0] * size:
                    continue
                legal += 1
                rank_z, block_rank = lemma_holds_f2(z, p_first, p_second, d)
                key = f"{rank_z}:{block_rank}"
                histogram[key] = histogram.get(key, 0) + 1
    require(total == 8 * 65536, "census size changed")
    require(legal == 8 * 4096, "square-condition count changed")
    return {"matrices": total, "square_zero": legal, "rank_pairs": dict(sorted(histogram.items()))}


def excess_without_square_q1() -> dict[str, int]:
    """Control: a rank-one Z with P_s Z P_f != 0 can have block rank two."""
    d, size = 2, 4
    excess = 0
    examined = 0
    for b_bits in range(4):
        plus, minus = stage_projectors(1, [b_bits & 1], [(b_bits >> 1) & 1])
        for p_first, p_second in ((plus, minus), (minus, plus)):
            for u in range(1, 16):
                for v in range(1, 16):
                    examined += 1
                    z = [v if (u >> r) & 1 else 0 for r in range(size)]
                    two = f2_add(f2_mul(z, p_first), f2_mul(p_second, z))
                    block_rank = f2_rank(f2_block(two, range(0, d), range(d, size)))
                    square = f2_mul(f2_mul(p_second, z), p_first)
                    if block_rank == 2:
                        require(square != [0] * size, "excess with the square condition")
                        excess += 1
    require(examined == 8 * 225, "rank-one control size changed")
    require(excess > 0, "the factor-two control vanished")
    return {"rank_one_matrices": examined, "block_rank_two": excess}


def random_actual(rng: random.Random) -> dict[str, int]:
    """Random Z on the actual stage projectors for larger half widths."""
    checked = 0
    equalities = 0
    for q in RANDOM_HALF_WIDTHS:
        d, size = 2 * q, 4 * q
        for trial in range(RANDOM_TRIALS):
            plus, minus = stage_projectors(q, f2_random(rng, q, q), f2_random(rng, q, q))
            p_first, p_second = (plus, minus) if trial % 2 == 0 else (minus, plus)
            check_complementary_f2(p_first, p_second)
            width = 1 + rng.randrange(size)
            raw = f2_mul(f2_random(rng, size, width), f2_random(rng, width, size))
            z = f2_add(raw, f2_mul(f2_mul(p_second, raw), p_first))
            rank_z, block_rank = lemma_holds_f2(z, p_first, p_second, d)
            checked += 1
            equalities += int(rank_z == block_rank)
    return {"checked": checked, "block_rank_equals_rank": equalities}


def sharpness() -> dict[str, int]:
    """Z = identity from the leaf into the core attains block rank = rank Z = 2q."""
    attained = {}
    for q in SHARP_HALF_WIDTHS:
        d, size = 2 * q, 4 * q
        plus, minus = stage_projectors(q, [0] * q, [0] * q)
        z = [(1 << (d + r)) if r < d else 0 for r in range(size)]
        for p_first, p_second in ((plus, minus), (minus, plus)):
            rank_z, block_rank = lemma_holds_f2(z, p_first, p_second, d)
            require(rank_z == d and block_rank == d, "sharpness witness lost")
        attained[str(q)] = d
    return attained


def three_leaf_q1() -> dict[str, int]:
    """Rank-one maps that meet leaves t-1, t and t+1 at rank one each (q = 1).

    Z has rows on core + leaf t and columns core, leaf t, leaf t-1, leaf t+1.
    """
    d, size = 2, 4
    examined = 0
    full = 0
    for b_bits in range(4):
        plus, minus = stage_projectors(1, [b_bits & 1], [(b_bits >> 1) & 1])
        for p_first, p_second in ((plus, minus), (minus, plus)):
            for u in range(1, 16):
                for w in range(1, 256):
                    examined += 1
                    rows = [w if (u >> r) & 1 else 0 for r in range(size)]
                    z_stage = [row & 15 for row in rows]
                    if f2_mul(f2_mul(p_second, z_stage), p_first) != [0] * size:
                        continue
                    own = f2_add(*pinching_f2(z_stage, p_first, p_second))
                    own_rank = f2_rank(f2_block(own, range(0, d), range(d, size)))
                    before = f2_mul(p_second, [(row >> 4) & 3 for row in rows])
                    after = f2_mul(p_first, [(row >> 6) & 3 for row in rows])
                    ranks = (own_rank, f2_rank(before[:d]), f2_rank(after[:d]))
                    require(max(ranks) <= 1, "a block outranks a rank-one map")
                    full += int(ranks == (1, 1, 1))
    require(examined == 8 * 15 * 255, "three-leaf domain changed")
    require(full > 0, "no rank-one map meets all three leaves")
    return {"rank_one_maps": examined, "meeting_three_leaves": full}


# ------------------------------------------------------------ general F_p --


def fp_mul(left: list[list[int]], right: list[list[int]], p: int) -> list[list[int]]:
    cols = len(right[0])
    return [
        [sum(row[k] * right[k][c] for k in range(len(right))) % p for c in range(cols)]
        for row in left
    ]


def fp_sub(left: list[list[int]], right: list[list[int]], p: int) -> list[list[int]]:
    return [[(a - b) % p for a, b in zip(ra, rb)] for ra, rb in zip(left, right)]


def fp_add(left: list[list[int]], right: list[list[int]], p: int) -> list[list[int]]:
    return [[(a + b) % p for a, b in zip(ra, rb)] for ra, rb in zip(left, right)]


def fp_eliminate(matrix: list[list[int]], p: int) -> tuple[int, list[list[int]]]:
    """Reduced row echelon form.  Return (rank, reduced copy)."""
    rows = [list(row) for row in matrix]
    rank = 0
    n_cols = len(rows[0]) if rows else 0
    for col in range(n_cols):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][col] % p), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inv = pow(rows[rank][col], -1, p)
        rows[rank] = [(x * inv) % p for x in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][col] % p:
                factor = rows[r][col]
                rows[r] = [(x - factor * y) % p for x, y in zip(rows[r], rows[rank])]
        rank += 1
    return rank, rows


def fp_rank(matrix: list[list[int]], p: int) -> int:
    return fp_eliminate(matrix, p)[0]


def fp_random(rng: random.Random, n_rows: int, n_cols: int, p: int) -> list[list[int]]:
    return [[rng.randrange(p) for _ in range(n_cols)] for _ in range(n_rows)]


def fp_random_idempotent(rng: random.Random, size: int, p: int) -> list[list[int]]:
    """S diag(1^a, 0) S^-1 for a random invertible S and random a."""
    for _ in range(INVERSE_ATTEMPTS):
        s = fp_random(rng, size, size, p)
        augmented = [row + [int(i == j) for j in range(size)] for i, row in enumerate(s)]
        rank, reduced = fp_eliminate(augmented, p)
        if rank == size and all(reduced[i][i] == 1 for i in range(size)):
            s_inv = [row[size:] for row in reduced]
            kept = rng.randrange(size + 1)
            diag = [[int(i == j and i < kept) for j in range(size)] for i in range(size)]
            return fp_mul(fp_mul(s, diag, p), s_inv, p)
    raise CheckFailure("no invertible matrix found")


def general_field(rng: random.Random) -> dict[str, int]:
    """The lemma for arbitrary complementary idempotents over F_2, F_3, F_5, F_7."""
    checked = 0
    for p in (CENSUS_FIELD,) + ODD_PRIMES:
        for size in (4, 6):
            identity = [[int(i == j) for j in range(size)] for i in range(size)]
            for _ in range(GENERAL_TRIALS):
                proj = fp_random_idempotent(rng, size, p)
                comp = fp_sub(identity, proj, p)
                require(fp_mul(proj, proj, p) == proj, "P is not idempotent")
                raw = fp_random(rng, size, size, p)
                z = fp_sub(raw, fp_mul(fp_mul(comp, raw, p), proj, p), p)
                zero = [[0] * size for _ in range(size)]
                require(fp_mul(fp_mul(comp, z, p), proj, p) == zero, "QZP is not zero")
                pzp = fp_mul(fp_mul(proj, z, p), proj, p)
                qzq = fp_mul(fp_mul(comp, z, p), comp, p)
                diagonal = fp_add(pzp, qzq, p)
                rank_z = fp_rank(z, p)
                require(
                    fp_rank(diagonal, p) == fp_rank(pzp, p) + fp_rank(qzq, p),
                    "pinching rank is not additive",
                )
                require(fp_rank(diagonal, p) <= rank_z, "pinching outranks Z")
                row_ids = [r for r in range(size) if rng.getrandbits(1)] or [0]
                col_ids = [c for c in range(size) if rng.getrandbits(1)] or [0]
                sub = [[diagonal[r][c] for c in col_ids] for r in row_ids]
                require(fp_rank(sub, p) <= rank_z, "a submatrix outranks Z")
                checked += 1
    return {"checked": checked}


# ------------------------------------------------------------ packing bound --


def exponents_target(g: int, leaf: int) -> tuple[int, ...]:
    """M_j = product of D_k over k >= j."""
    return tuple(int(k >= leaf) for k in range(g))


def exponents_internal(g: int, stage: int, leaf: int, power: int) -> tuple[int, ...]:
    """lambda(t, j) * D_t^a from the source note, section 4."""
    vector = [int(k > stage) for k in range(g)]
    if leaf < stage:
        vector[leaf] += 1
    vector[stage] += power
    return tuple(vector)


def exponents_external(g: int, gap: int, leaf: int) -> tuple[int, ...]:
    """mu(gamma, j): stages >= gamma act on the core, stage j < gamma on leaf j."""
    vector = [int(k >= gap) for k in range(g)]
    if leaf < gap:
        vector[leaf] += 1
    return tuple(vector)


def contributors(g: int, leaf: int) -> set[tuple[str, int]]:
    """Gaps whose thin maps can contribute the monomial M_j on leaf j."""
    target = exponents_target(g, leaf)
    found: set[tuple[str, int]] = set()
    for stage in range(g):
        for power in range(3):
            if exponents_internal(g, stage, leaf, power) == target:
                require(power in (0, 1), "a squared monomial met the target")
                found.add(("internal", stage))
    for gap in range(g + 1):
        if exponents_external(g, gap, leaf) == target:
            found.add(("external", gap))
    expected = {("internal", t) for t in (leaf - 1, leaf, leaf + 1) if 0 <= t < g}
    expected |= {("external", leaf), ("external", leaf + 1)}
    require(found == expected, "contributor set differs from the stated one")
    return found


def disjoint(sets: list[set[tuple[str, int]]]) -> bool:
    seen: set[tuple[str, int]] = set()
    for item in sets:
        if seen & item:
            return False
        seen |= item
    return True


def covering_stages(g: int) -> list[int]:
    """Stages whose internal gaps cover every leaf (a feasible covering point)."""
    stages = list(range(1, g, 3))
    if g % 3 == 1:
        stages.append(g - 1)
    return stages


def covers_all(g: int, stages: list[int]) -> bool:
    chosen = {("internal", t) for t in stages}
    return all(contributors(g, leaf) & chosen for leaf in range(g))


def packing_bound(g: int, q: int) -> int:
    """Lower bound 2q * ceil(g/3), with the matching covering point."""
    leaves = list(range(0, g, 3))
    require(len(leaves) == -(-g // 3), "leaf count is not ceil(g/3)")
    require(disjoint([contributors(g, leaf) for leaf in leaves]), "chosen leaves share a gap")
    stages = covering_stages(g)
    require(covers_all(g, stages), "covering point misses a leaf")
    require(len(stages) == len(leaves), "covering and packing values differ")
    return 2 * q * len(leaves)


def packing_checks() -> dict[str, object]:
    for g in range(1, MAX_STAGES + 1):
        for q in (1, TARGET_Q):
            bound = packing_bound(g, q)
            require(bound == 2 * q * -(-g // 3), "closed form changed")
            require(3 * bound >= 2 * q * g, "packing bound fell below 2qg/3")
            require(2 * bound >= q * g, "packing bound fell below qg/2")
    target = packing_bound(TARGET_G, TARGET_Q)
    require(target == 572, "target bound changed")
    require(TARGET_Q * TARGET_G // 2 == 403, "source bound changed")
    require(-(-2 * TARGET_Q * TARGET_G // 3) == 538, "weight-count bound changed")
    require(5 * TARGET_Q == 130 and 130 < target, "five rank-26 maps are not excluded")
    # Rejection controls: adjacent packing leaves share a gap; a thinned cover misses a leaf.
    near = [contributors(TARGET_G, leaf) for leaf in range(0, TARGET_G, 2)]
    require(not disjoint(near), "spacing-two leaves were accepted")
    require(not covers_all(TARGET_G, covering_stages(TARGET_G)[1:]), "a thinned cover was accepted")
    return {
        "stages_checked": MAX_STAGES,
        "g": TARGET_G,
        "q": TARGET_Q,
        "packing_bound": target,
        "weight_count_bound": 538,
        "source_bound": 403,
        "five_rank_q_maps": 130,
    }


def main() -> int:
    rng = random.Random(SEED)
    result = {
        "census_q1": census_q1(),
        "factor_two_control_q1": excess_without_square_q1(),
        "random_actual": random_actual(rng),
        "general_field": general_field(rng),
        "sharpness_rank": sharpness(),
        "three_leaf_q1": three_leaf_q1(),
        "packing": packing_checks(),
    }
    text = json.dumps(result, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(text.encode("ascii")).hexdigest()[:16]
    print(json.dumps(result, sort_keys=True, indent=1))
    print(
        "PASS_EVERY_STAGE_GAP_RANK_FACTOR"
        f" factor=1 bound_g31_q26={result['packing']['packing_bound']}"
        f" certificate={digest} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
