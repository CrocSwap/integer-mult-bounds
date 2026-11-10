#!/usr/bin/env python3
"""Two constant F_2 thin maps with one unsplit call per stage.

At g=3, d=2 the pure factors are I+x_j E_j. Every order and every pair of
gaps is solved entrywise. Eighteen gap pairs are impossible. The other
eighteen are leaf permutations of two affine families, both of minimum
rank sum 8. Failures raise SystemExit, so python -O still fails closed.
"""

from __future__ import annotations

import itertools
import os
import subprocess
import tempfile

N = 8
G = 3
MASK64 = (1 << 64) - 1
I2 = 0b1001


def fail(message):
    raise SystemExit("FAIL: " + message)


def require(ok, message):
    if not ok:
        fail(message)


def mon_mul(left, right):
    if left & right:
        fail("polynomial degree exceeded 1 in a stage variable")
    return left | right


def poly_mul(left, right):
    out = 0
    rest = left
    while rest:
        bit = rest & -rest
        src = bit.bit_length() - 1
        rest ^= bit
        other = right
        while other:
            bit2 = other & -other
            dst = mon_mul(src, bit2.bit_length() - 1)
            out ^= 1 << dst
            other ^= bit2
    return out


def eye():
    return tuple(tuple(1 if i == j else 0 for j in range(N)) for i in range(N))


def zero():
    return tuple(tuple(0 for _ in range(N)) for _ in range(N))


def madd(left, right):
    return tuple(tuple(left[i][j] ^ right[i][j] for j in range(N)) for i in range(N))


def mmul(left, right):
    out = [[0] * N for _ in range(N)]
    for i in range(N):
        for k in range(N):
            factor = left[i][k]
            if not factor:
                continue
            for j in range(N):
                if right[k][j]:
                    out[i][j] ^= poly_mul(factor, right[k][j])
    return tuple(tuple(row) for row in out)


def support_mon(block, stages):
    mask = 0
    for stage in stages:
        if block == 0 or block == stage + 1:
            mask |= 1 << stage
    return mask


def pure_q(stage):
    rows = []
    for index in range(N):
        row = [0] * N
        block = index // 2
        mon = (1 << stage) if (block == 0 or block == stage + 1) else 0
        row[index] = 1 << mon
        rows.append(tuple(row))
    return tuple(rows)


def query_s(stage):
    leaf = stage + 1
    mon = 1 << stage
    rows = [[0] * N for _ in range(N)]
    for lane in range(2):
        core = lane
        leaf_index = leaf * 2 + lane
        for row in (core, leaf_index):
            for col in (core, leaf_index):
                rows[row][col] = 1 << mon
    return tuple(tuple(row) for row in rows)


def thin_factor(bit_rows):
    extra = [[0] * N for _ in range(N)]
    for row, bits in enumerate(bit_rows):
        for col in range(N):
            if (bits >> col) & 1:
                extra[row][col] = 1
    return eye(), tuple(tuple(row) for row in extra)


def full_factor(stage):
    return pure_q(stage), query_s(stage)


def mul_pair(left, right):
    pure = mmul(left[0], right[0])
    extra = madd(mmul(left[1], right[0]), mmul(left[0], right[1]))
    return pure, extra


def word(factors):
    acc = (eye(), zero())
    for factor in factors:
        acc = mul_pair(factor, acc)
    return acc


def target_word():
    pure = word([(pure_q(stage), zero()) for stage in range(G)])
    return pure[0], pure[0]


def rank_rows(rows):
    work = list(rows)
    size = len(work)
    rank = 0
    width = N
    for col in range(width):
        mask = 1 << col
        pivot = next((i for i in range(rank, size) if work[i] & mask), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_row = work[rank]
        for i in range(size):
            if i != rank and (work[i] & mask):
                work[i] ^= pivot_row
        rank += 1
    return rank


def rank2(bits):
    rows = [((bits >> 0) & 1) | (((bits >> 1) & 1) << 1), ((bits >> 2) & 1) | (((bits >> 3) & 1) << 1)]
    rank = 0
    for col in range(2):
        mask = 1 << col
        pivot = next((i for i in range(rank, 2) if rows[i] & mask), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        if rows[1 - rank] & mask:
            rows[1 - rank] ^= rows[rank]
        rank += 1
    return rank


def mul2(left, right):
    out = 0
    for row in range(2):
        for col in range(2):
            bit = 0
            for mid in range(2):
                bit ^= ((left >> (2 * row + mid)) & 1) & ((right >> (2 * mid + col)) & 1)
            if bit:
                out |= 1 << (2 * row + col)
    return out


def put2(rows, bits, block_row, block_col):
    for lane_row in range(2):
        for lane_col in range(2):
            if (bits >> (2 * lane_row + lane_col)) & 1:
                rows[block_row * 2 + lane_row] |= 1 << (block_col * 2 + lane_col)


def add_identity(rows, block_row, block_col):
    for lane in range(2):
        rows[block_row * 2 + lane] |= 1 << (block_col * 2 + lane)


def family_a_pair_on_w(param_a, param_b, param_c, param_d):
    """Singleton leaf 0 on Z. Leaves 1 and 2 are the identity blocks of W."""
    left = [0] * N
    right = [0] * N
    put2(left, param_a, 0, 0)
    put2(right, param_a, 0, 0)
    put2(left, param_b, 1, 1)
    put2(right, param_b, 1, 1)
    put2(left, param_c, 2, 2)
    put2(right, param_c, 2, 2)
    put2(left, param_d, 3, 3)
    put2(right, param_d, 3, 3)
    add_identity(left, 0, 1)
    add_identity(left, 1, 0)
    add_identity(right, 0, 2)
    add_identity(right, 0, 3)
    add_identity(right, 2, 0)
    add_identity(right, 3, 0)
    return left, right


def family_a_pair_on_z(param_a, param_b, param_c, param_d):
    """Leaves 0 and 1 are the identity blocks of Z. Leaf 2 is the identity block of W."""
    left, right = family_a_pair_on_w(param_a, param_b, param_c, param_d)
    return right, left


def family_b(param_a, param_b, param_c, param_d, param_h, param_k, param_p, param_q):
    """Leaf 0 fixed on Z, leaf 1 free with difference I, leaf 2 fixed on W."""
    left = [0] * N
    right = [0] * N
    add_identity(left, 0, 1)
    add_identity(left, 1, 0)
    add_identity(right, 0, 3)
    add_identity(right, 3, 0)
    add_identity(right, 0, 2)
    add_identity(right, 2, 0)
    put2(left, param_a, 0, 0)
    put2(right, param_a, 0, 0)
    put2(left, param_b, 1, 1)
    put2(right, param_b, 1, 1)
    put2(left, param_c, 2, 2)
    put2(right, param_c, 2, 2)
    put2(left, param_d, 3, 3)
    put2(right, param_d, 3, 3)
    put2(left, param_h, 1, 3)
    put2(right, param_h, 1, 3)
    put2(left, param_k, 3, 1)
    put2(right, param_k, 3, 1)
    put2(left, param_p, 0, 2)
    put2(right, param_p, 0, 2)
    put2(left, param_q, 2, 0)
    put2(right, param_q, 2, 0)
    return left, right


def gap_monomial(order, gap, row, col):
    return mon_mul(support_mon(row // 2, order[gap:]), support_mon(col // 2, order[:gap]))


def full_e(order):
    matrix = [[0] * N for _ in range(N)]
    for index, stage in enumerate(order):
        left = order[index + 1 :]
        right = order[:index]
        leaf = stage + 1
        for block in (0, leaf):
            for other in (0, leaf):
                mon = mon_mul(1 << stage, mon_mul(support_mon(block, left), support_mon(other, right)))
                for lane in range(2):
                    matrix[block * 2 + lane][other * 2 + lane] ^= 1 << mon
    return matrix


def solve_entry(mon_left, mon_right, rhs):
    legal = []
    for bit_z in (0, 1):
        for bit_w in (0, 1):
            poly = 0
            if bit_z:
                poly ^= 1 << mon_left
            if bit_w:
                poly ^= 1 << mon_right
            if poly == rhs:
                legal.append((bit_z, bit_w))
    return tuple(legal)


def conjugation_defect(order):
    target = target_word()[1]
    extra = full_e(order)
    return [[extra[i][j] ^ target[i][j] for j in range(N)] for i in range(N)]


def entry_options(order, gaps):
    defect = conjugation_defect(order)
    options = []
    for row in range(N):
        for col in range(N):
            options.append(
                solve_entry(
                    gap_monomial(order, gaps[0], row, col),
                    gap_monomial(order, gaps[1], row, col),
                    defect[row][col],
                )
            )
    return tuple(options)


def fixed_pair(bit_z, bit_w):
    return ((bit_z, bit_w),)


def same_free():
    return ((0, 0), (1, 1))


def opposite_free():
    return ((0, 1), (1, 0))


def expect_family_a(z_leaf, w_leaves, row, col):
    block_row, lane_row = divmod(row, 2)
    block_col, lane_col = divmod(col, 2)
    same_lane = lane_row == lane_col
    if block_row == block_col:
        return same_free()
    pair = {block_row, block_col}
    if pair == {0, z_leaf}:
        return fixed_pair(1, 0) if same_lane else fixed_pair(0, 0)
    if pair == {0, w_leaves[0]} or pair == {0, w_leaves[1]}:
        return fixed_pair(0, 1) if same_lane else fixed_pair(0, 0)
    return fixed_pair(0, 0)


def expect_family_b(z_leaf, diff_leaf, w_leaf, row, col):
    block_row, lane_row = divmod(row, 2)
    block_col, lane_col = divmod(col, 2)
    same_lane = lane_row == lane_col
    if block_row == block_col:
        return same_free()
    pair = {block_row, block_col}
    if pair == {0, z_leaf}:
        return fixed_pair(1, 0) if same_lane else fixed_pair(0, 0)
    if pair == {0, w_leaf}:
        return fixed_pair(0, 1) if same_lane else fixed_pair(0, 0)
    if pair == {0, diff_leaf}:
        return opposite_free() if same_lane else same_free()
    if pair == {z_leaf, w_leaf}:
        return same_free()
    return fixed_pair(0, 0)


def matches(options, expected):
    return all(options[row * N + col] == expected(row, col) for row in range(N) for col in range(N))


def match_family_a(options):
    hits = []
    for z_leaf, other_a, other_b in itertools.permutations((1, 2, 3)):
        if matches(options, lambda row, col, z_leaf=z_leaf, other_a=other_a, other_b=other_b: expect_family_a(z_leaf, (other_a, other_b), row, col)):
            hits.append(("pair-on-w", z_leaf))
        # Singleton on W is family A with Z and W exchanged, which swaps the two arguments of each fixed pair.
        swapped = tuple(tuple((bit_w, bit_z) for bit_z, bit_w in legal) for legal in options)
        if matches(swapped, lambda row, col, z_leaf=z_leaf, other_a=other_a, other_b=other_b: expect_family_a(z_leaf, (other_a, other_b), row, col)):
            hits.append(("pair-on-z", z_leaf))
    return hits


def match_family_b(options):
    hits = []
    for z_leaf, diff_leaf, w_leaf in itertools.permutations((1, 2, 3)):
        if matches(
            options,
            lambda row, col, z_leaf=z_leaf, diff_leaf=diff_leaf, w_leaf=w_leaf: expect_family_b(
                z_leaf, diff_leaf, w_leaf, row, col
            ),
        ):
            hits.append((z_leaf, diff_leaf, w_leaf))
    return hits


def one_map_options(order, gap):
    defect = conjugation_defect(order)
    for row in range(N):
        for col in range(N):
            mon = gap_monomial(order, gap, row, col)
            legal = [bit for bit in (0, 1) if ((1 << mon) if bit else 0) == defect[row][col]]
            if not legal:
                return None
    return True


def enumerate_family_a():
    best_w = 99
    best_z = 99
    for params in itertools.product(range(16), repeat=4):
        left, right = family_a_pair_on_w(*params)
        best_w = min(best_w, rank_rows(left) + rank_rows(right))
        left, right = family_a_pair_on_z(*params)
        best_z = min(best_z, rank_rows(left) + rank_rows(right))
    return best_w, best_z


def slice_hashes():
    hash_diag = 0
    hash_free = 0
    for params in itertools.product(range(16), repeat=4):
        left, right = family_b(*params, 0, 0, 0, 0)
        hash_diag = (hash_diag * 1315423911 + rank_rows(left) + rank_rows(right)) & MASK64
    for params in itertools.product(range(16), repeat=4):
        left, right = family_b(0, 0, 0, 0, *params)
        hash_free = (hash_free * 1315423911 + rank_rows(left) + rank_rows(right)) & MASK64
    return hash_diag, hash_free


def run_census():
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), "search.c")
    with tempfile.TemporaryDirectory(prefix="unsplit-census-") as directory:
        binary = os.path.join(directory, "search")
        compiled = subprocess.run(
            ["gcc", "-O3", "-std=c11", "-o", binary, source],
            text=True,
            capture_output=True,
            check=False,
        )
        require(compiled.returncode == 0, "gcc failed: " + compiled.stderr[-500:])
        ran = subprocess.run([binary], text=True, capture_output=True, check=False)
        require(ran.returncode == 0, "census failed: " + ran.stderr[-500:] + ran.stdout)
        require(ran.stderr == "", "census reported a rank below 8: " + ran.stderr)
    parts = {}
    for item in ran.stdout.split():
        key, value = item.split("=")
        parts[key] = int(value)
    return parts


def formula_locks(target):
    probe_z = [0] * N
    probe_w = [0] * N
    probe_z[0] = 1 << 1
    probe_w[2] = 1 << 3
    for order in itertools.permutations(range(G)):
        factors = [full_factor(stage) for stage in order]
        got = word(factors)
        require(got[0] == target[0], "pure product depends on call order %s" % (order,))
        require(got[1] == tuple(tuple(row) for row in full_e(order)), "conjugation drifted at %s" % (order,))
        for gaps in itertools.combinations(range(4), 2):
            # Gap k sits after the first k calls. The factor list is chronological.
            placed = []
            if gaps[0] == 0:
                placed.append(thin_factor(probe_z))
            if gaps[1] == 0:
                placed.append(thin_factor(probe_w))
            for index, stage in enumerate(order):
                placed.append(full_factor(stage))
                if index + 1 == gaps[0]:
                    placed.append(thin_factor(probe_z))
                if index + 1 == gaps[1]:
                    placed.append(thin_factor(probe_w))
            got = word(placed)
            predicted = [row[:] for row in full_e(order)]
            for gap, probe in ((gaps[0], probe_z), (gaps[1], probe_w)):
                left = [support_mon(row // 2, order[gap:]) for row in range(N)]
                right = [support_mon(col // 2, order[:gap]) for col in range(N)]
                for row in range(N):
                    for col in range(N):
                        if (probe[row] >> col) & 1:
                            predicted[row][col] ^= 1 << mon_mul(left[row], right[col])
            require(got[1] == tuple(tuple(row) for row in predicted), "gap formula drifted at %s %s" % (order, gaps))


def same_gap_adds():
    left = [0] * N
    right = [0] * N
    left[0] = 1 << 1
    right[1] = 1 << 4
    right[0] = 1 << 1
    summed = [x ^ y for x, y in zip(left, right)]
    separate = word([thin_factor(left), thin_factor(right)])
    together = thin_factor(summed)
    require(separate == together, "two thin maps in one gap did not add")


def witness_controls(target):
    core_leaf = [0] * N
    for lane in range(2):
        core_leaf[lane] |= 1 << (2 + lane)
        core_leaf[2 + lane] |= 1 << lane
    other = [0] * N
    for leaf in (2, 3):
        for lane in range(2):
            other[lane] |= 1 << (2 * leaf + lane)
            other[2 * leaf + lane] |= 1 << lane
    factors = [thin_factor(core_leaf), full_factor(0), full_factor(1), thin_factor(other), full_factor(2)]
    require(word(factors) == target, "family A witness missed the endpoint")
    noise = [0] * N
    noise[0] |= 1
    noise[1] |= 2
    shared = word(
        [
            thin_factor([x ^ y for x, y in zip(core_leaf, noise)]),
            full_factor(0),
            full_factor(1),
            thin_factor([x ^ y for x, y in zip(other, noise)]),
            full_factor(2),
        ]
    )
    require(shared == target, "a shared diagonal block left the endpoint")
    only_one = word(
        [
            thin_factor([x ^ y for x, y in zip(core_leaf, noise)]),
            full_factor(0),
            full_factor(1),
            thin_factor(other),
            full_factor(2),
        ]
    )
    require(only_one != target, "noise on one map still met the endpoint")
    deleted = word([thin_factor(core_leaf), full_factor(0), full_factor(1), full_factor(2)])
    require(deleted != target, "deleting a thin map still met the endpoint")
    family_b_factors = [full_factor(0), thin_factor(core_leaf), full_factor(1), thin_factor(other), full_factor(2)]
    require(word(family_b_factors) == target, "family B witness missed the endpoint")
    ranks = family_a_pair_on_w(0, 0, 0, 0)
    require(rank_rows(ranks[0]) == 4 and rank_rows(ranks[1]) == 4, "family A zero ranks")
    ranks = family_b(0, 0, 0, 0, 0, 0, 0, 0)
    require(rank_rows(ranks[0]) == 4 and rank_rows(ranks[1]) == 4, "family B zero ranks")


def leaf_rows_ignore_core_parameters():
    for param_b, param_h, param_k, param_q in itertools.product((0, 9, 15), repeat=4):
        for param_c, param_d in ((0, 0), (15, 15)):
            low = family_b(0, param_b, param_c, param_d, param_h, param_k, 0, param_q)
            high = family_b(15, param_b, param_c, param_d, param_h, param_k, 15, param_q)
            require(low[0][2:] == high[0][2:] and low[1][2:] == high[1][2:], "A or P changed a leaf row")


def named_obstruction():
    order = (0, 1, 2)
    defect = conjugation_defect(order)
    require(defect[0][4] == 1 << 6, "core-to-leaf1 defect is not D1 D2")
    mon_early = gap_monomial(order, 0, 0, 4)
    mon_late = gap_monomial(order, 3, 0, 4)
    require(mon_early == 7 and mon_late == 2, "endpoint gap monomials moved")
    require(solve_entry(mon_early, mon_late, defect[0][4]) == (), "the named obstruction became solvable")


def lemma_two_by_two():
    for left in range(16):
        for right in range(16):
            require(rank2(left) + rank2(I2 ^ mul2(left, right)) >= 2, "rank(B)+rank(I+BA) dropped")
            require(rank2(left) + rank2(I2 ^ mul2(right, left)) >= 2, "rank(D)+rank(I+DA) dropped")


def main():
    target = target_word()
    require(target[0][0][0] == 1 << 7, "core target monomial")
    require(target[0][2][2] == 1 << 1, "leaf0 target monomial")
    require(target[0][0][2] == 0, "target acquired an off-diagonal pure entry")
    formula_locks(target)
    same_gap_adds()
    witness_controls(target)
    named_obstruction()
    lemma_two_by_two()
    leaf_rows_ignore_core_parameters()

    impossible = 0
    family_a = 0
    family_b = 0
    one_hits = 0
    for order in itertools.permutations(range(G)):
        for gap in range(4):
            if one_map_options(order, gap):
                one_hits += 1
        for gaps in itertools.combinations(range(4), 2):
            options = entry_options(order, gaps)
            if any(not legal for legal in options):
                impossible += 1
                require(gaps in ((0, 1), (0, 3), (2, 3)), "unexpected impossible gaps %s %s" % (order, gaps))
                continue
            if gaps in ((0, 2), (1, 3)):
                require(match_family_a(options), "family A shape missed %s %s" % (order, gaps))
                require(not match_family_b(options), "family A also matched family B")
                family_a += 1
            elif gaps == (1, 2):
                require(match_family_b(options), "family B shape missed %s %s" % (order, gaps))
                require(not match_family_a(options), "family B also matched family A")
                family_b += 1
            else:
                fail("solvable gaps outside the two families: %s %s" % (order, gaps))
    require(impossible == 18 and family_a == 12 and family_b == 6, "gap census counts")
    require(one_hits == 0, "a single unsplit gap admitted a constant thin map")

    best_w, best_z = enumerate_family_a()
    require(best_w == 8 and best_z == 8, "family A minimum %s %s" % (best_w, best_z))
    census = run_census()
    diag_hash, free_hash = slice_hashes()
    require(census["min"] == 8, "family B minimum")
    require(census["count"] == 1 << 32, "family B census count")
    require(census["slice_hash"] == diag_hash, "diagonal slice hash")
    require(census["free_hash"] == free_hash, "off-diagonal slice hash")
    print(
        "orders=6 gap_pairs=36 impossible=18 family_A=12 family_B=6 "
        "one_thin_hits=0 min_rank_sum_A=8 min_rank_sum_B=8 "
        "witness_ranks=4+4 family_B_count=4294967296 no_new_kappa=true"
    )
    print("PASS_PAIRED_STAR_UNSPLIT_TWO_THIN")


if __name__ == "__main__":
    main()
