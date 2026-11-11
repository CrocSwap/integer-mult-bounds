#!/usr/bin/env python3
"""Exact checks for the leaf-to-core every-stage bound.

The argument is the proof in PROOF.md. These checks are block identities,
one g=3 word, an exhaustive q=1 rank-one census, and a finite packing
comparison. They are not a heuristic search and they are not a word.
"""

from __future__ import annotations

import random
import sys

MAX_STAGES = 64
TARGET_G = 31
TARGET_Q = 26


def fail(message: str) -> None:
    raise SystemExit(message)


def rank_rows(rows: list[list[int]]) -> int:
    if not rows or not rows[0]:
        return 0
    matrix = [row[:] for row in rows]
    height = len(matrix)
    width = len(matrix[0])
    found = 0
    for col in range(width):
        pivot = next((row for row in range(found, height) if matrix[row][col]), None)
        if pivot is None:
            continue
        matrix[found], matrix[pivot] = matrix[pivot], matrix[found]
        for row in range(height):
            if row != found and matrix[row][col]:
                for entry in range(width):
                    matrix[row][entry] ^= matrix[found][entry]
        found += 1
    return found


def mul4(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    out = [[0] * 4 for _ in range(4)]
    for row in range(4):
        for mid in range(4):
            if left[row][mid]:
                for col in range(4):
                    out[row][col] ^= right[mid][col]
    return out


def add4(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[left[row][col] ^ right[row][col] for col in range(4)] for row in range(4)]


def eye4() -> list[list[int]]:
    return [[1 if row == col else 0 for col in range(4)] for row in range(4)]


def projectors_bi() -> tuple[list[list[int]], list[list[int]]]:
    """P_+ and P_- at B12 = B21 = I, in the 0/I block alphabet.

    Each entry stands for the q by q zero or identity, so the arithmetic is
    valid for every half width.
    """
    plus = [
        [1, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 1, 1],
        [1, 0, 1, 0],
    ]
    minus = [
        [0, 1, 0, 1],
        [1, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
    ]
    return plus, minus


def witness_blocks() -> dict[str, object]:
    """The core-output witness, checked in the 0/I block alphabet."""
    plus, minus = projectors_bi()
    if mul4(plus, plus) != plus or mul4(minus, minus) != minus:
        fail("B = I halves are not idempotent")
    if add4(plus, minus) != eye4() or mul4(plus, minus) != [[0] * 4 for _ in range(4)]:
        fail("B = I halves are not complementary")
    lam = [[1, 0], [1, 1]]
    core = [[0] * 4 for _ in range(2)]
    for row in range(2):
        for mid in range(2):
            if lam[row][mid]:
                for col in range(4):
                    core[row][col] ^= minus[mid][col]
    matrix = [core[0], core[1], [0, 0, 0, 0], [0, 0, 0, 0]]
    if mul4(matrix, plus) != [[0] * 4 for _ in range(4)]:
        fail("witness does not annihilate the first half")
    if mul4(minus, mul4(matrix, plus)) != [[0] * 4 for _ in range(4)]:
        fail("witness violates the square condition")
    pinching = add4(mul4(plus, mul4(matrix, plus)), mul4(minus, mul4(matrix, minus)))
    core_to_leaf = [row[2:] for row in pinching[:2]]
    leaf_to_core = [row[:2] for row in pinching[2:]]
    if leaf_to_core != [[1, 0], [0, 1]]:
        fail("own leaf-to-core block is not I")
    if core_to_leaf != [[1, 1], [1, 0]]:
        fail("own core-to-leaf block changed")
    image = [matrix[0][:2], matrix[1][:2]]
    if rank_rows(image) != 2 or matrix[2] != [0, 0, 0, 0] or matrix[3] != [0, 0, 0, 0]:
        fail("witness image is not the whole core")
    # pi_core P_+ and pi_core P_- on a core vector (c0, c1).
    plus_on_core = [[1, 1], [1, 0]]
    minus_on_core = [[0, 1], [1, 1]]
    if rank_rows(plus_on_core) != 2 or rank_rows(minus_on_core) != 2:
        fail("neighbor core projections are singular")
    degree_zero = mul4(plus, mul4(matrix, minus))
    degree_zero_leaf = [row[:2] for row in degree_zero[2:]]
    degree_zero_core = [row[2:] for row in degree_zero[:2]]
    if degree_zero_leaf != [[1, 0], [0, 1]] or degree_zero_core != [[1, 0], [0, 1]]:
        fail("degree-zero own blocks are not both I")
    return {"own_core_to_leaf_rank": rank_rows(core_to_leaf)}


def bit_mul(left: list[int], right: list[int]) -> list[int]:
    out = []
    width = len(right)
    for row in left:
        acc = 0
        rest = row
        index = 0
        while rest and index < width:
            if rest & 1:
                acc ^= right[index]
            rest >>= 1
            index += 1
        out.append(acc)
    return out


def embed4(local: list[list[int]]) -> list[int]:
    rows = []
    for row in range(8):
        value = 0
        if row < 4:
            for col in range(4):
                if local[row][col]:
                    value |= 1 << col
        rows.append(value)
    return rows


def q1_rank_one_coupling() -> dict[str, int]:
    """Every rank-one map on core, leaf t, and the two neighbours."""
    plus = [
        [1, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 1, 1],
        [1, 0, 1, 0],
    ]
    minus = [
        [0, 1, 0, 1],
        [1, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
    ]
    first = embed4(plus)
    second = embed4(minus)
    examined = 0
    square_zero = 0
    violations = 0
    for column_bits in range(1, 256):
        for row_bits in range(1, 256):
            examined += 1
            matrix = [column_bits if (row_bits >> row) & 1 else 0 for row in range(8)]
            square = bit_mul(second, bit_mul(matrix, first))
            core_rows = bit_mul(second, matrix)[:2]
            prev = rank_rows([[(row >> col) & 1 for col in range(4, 6)] for row in core_rows])
            # next leaf-to-core reads rows 6 and 7, columns of P_f on the core.
            nxt_rows = [bit_mul(matrix, first)[row] for row in (6, 7)]
            nxt_rank = rank_rows(
                [[(row >> col) & 1 for col in range(2)] for row in nxt_rows]
            )
            legal = all(entry == 0 for entry in square)
            if legal:
                square_zero += 1
                if prev + nxt_rank > 1:
                    violations += 1
            elif prev + nxt_rank > 1 and column_bits == 17 and row_bits == 65:
                pass
    if examined != 255 * 255:
        fail("rank-one domain changed")
    if violations:
        fail("square-free rank-one map broke the coupling")
    # Planted control: the recorded square-violating rank-one map has both blocks rank 1.
    control = [17 if (65 >> row) & 1 else 0 for row in range(8)]
    control_core = bit_mul(second, control)[:2]
    control_prev = rank_rows(
        [[(row >> col) & 1 for col in range(4, 6)] for row in control_core]
    )
    control_rows = [bit_mul(control, first)[row] for row in (6, 7)]
    control_next = rank_rows([[(row >> col) & 1 for col in range(2)] for row in control_rows])
    control_square = bit_mul(second, bit_mul(control, first))
    if control_prev + control_next <= 1 or all(entry == 0 for entry in control_square):
        fail("square-violating coupling control disappeared")
    return {
        "rank_one_maps": examined,
        "square_zero": square_zero,
        "square_violating_control": control_prev + control_next,
    }


def ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def packing_feasible(stages: int, core: list[int], leaf_side: list[int]) -> bool:
    def core_at(index: int) -> int:
        if 0 <= index < stages:
            return core[index]
        return 0

    def leaf_at(index: int) -> int:
        if 0 <= index < stages:
            return leaf_side[index]
        return 0

    for stage in range(stages):
        load = (
            core_at(stage)
            + leaf_at(stage)
            + core_at(stage + 1)
            + leaf_at(stage - 1)
            + max(core_at(stage - 1), leaf_at(stage + 1))
        )
        if load > 1:
            return False
    for gap in range(stages + 1):
        load = 0
        for leaf in (gap - 1, gap):
            load += core_at(leaf) + leaf_at(leaf)
        if load > 1:
            return False
    return True


def dual_weight(stages: int) -> int:
    core = [1 if leaf % 5 == 0 else 0 for leaf in range(stages)]
    leaf_side = [1 if leaf % 5 == 2 else 0 for leaf in range(stages)]
    if not packing_feasible(stages, core, leaf_side):
        fail("dual stage or external load exceeded 1")
    total = sum(core) + sum(leaf_side)
    if total != ceil_div(2 * stages, 5):
        fail("dual weight is not ceil(2g/5)")
    return total


def overweight_dual_rejected() -> None:
    """Both sides on leaf 0 overload the first external gap."""
    core = [1, 0, 0]
    leaf_side = [1, 0, 0]
    if packing_feasible(3, core, leaf_side):
        fail("overweight dual pattern was accepted")


def primal_value(stages: int) -> int:
    """Feasible internal block-rank point of value ceil(2g/5), in units of 2q.

    Each used stage pays at most one of the coupled blocks cp and ln.
    """
    rank = [0] * stages
    core_hit = [0] * stages
    leaf_hit = [0] * stages

    def pay_internal(stage: int, blocks: set[str]) -> None:
        if not 0 <= stage < stages:
            fail("primal stage out of range")
        rank[stage] = 1
        if "co" in blocks:
            core_hit[stage] += 1
        if "lo" in blocks:
            leaf_hit[stage] += 1
        if "cp" in blocks:
            if stage - 1 < 0:
                fail("previous block at an endpoint")
            core_hit[stage - 1] += 1
        if "lp" in blocks:
            if stage - 1 < 0:
                fail("previous leaf-to-core at an endpoint")
            leaf_hit[stage - 1] += 1
        if "cn" in blocks:
            if stage + 1 >= stages:
                fail("next block past the last leaf")
            core_hit[stage + 1] += 1
        if "ln" in blocks:
            if stage + 1 >= stages:
                fail("next leaf-to-core past the last leaf")
            leaf_hit[stage + 1] += 1
        if ("cp" in blocks) and ("ln" in blocks):
            fail("primal point uses both coupled blocks")

    groups = stages // 5
    for group in range(groups):
        pay_internal(5 * group + 1, {"co", "lo", "cp", "lp", "cn"})
        pay_internal(5 * group + 3, {"co", "lo", "lp", "cn", "ln"})
    start = 5 * groups
    remainder = stages - start
    if remainder == 1:
        pay_internal(start, {"co", "lo"})
    elif remainder == 2:
        pay_internal(start, {"co", "lo", "cn", "ln"})
    elif remainder == 3:
        pay_internal(start, {"co", "lo", "cn", "ln"})
        pay_internal(start + 2, {"co", "lo", "cp", "lp"})
    elif remainder == 4:
        pay_internal(start, {"co", "lo", "cn", "ln"})
        pay_internal(start + 3, {"co", "lo", "cp", "lp"})
    elif remainder != 0:
        fail("remainder out of range")
    if any(value < 1 for value in core_hit) or any(value < 1 for value in leaf_hit):
        fail("primal point misses a leaf")
    total = sum(rank)
    if total != ceil_div(2 * stages, 5):
        fail("primal value is not ceil(2g/5)")
    return total


def monomials(stages: int) -> None:
    def target(leaf: int) -> tuple[int, ...]:
        return tuple(1 if index <= leaf else 0 for index in range(stages))

    for stage in range(stages):
        hits = []
        for leaf in range(stages):
            for power in (0, 1, 2):
                vector = [1 if index < stage else 0 for index in range(stages)]
                vector[stage] += power
                if leaf > stage:
                    vector[leaf] += 1
                if tuple(vector) == target(leaf):
                    hits.append((leaf, power))
        expected = []
        if stage - 1 >= 0:
            expected.append((stage - 1, 0))
        expected.append((stage, 1))
        if stage + 1 < stages:
            expected.append((stage + 1, 1))
        if hits != expected:
            fail("internal leaf-to-core hits changed at stage " + str(stage))
    for gap in range(stages + 1):
        hits = []
        for leaf in range(stages):
            vector = [1 if index < gap else 0 for index in range(stages)]
            if leaf >= gap:
                vector[leaf] += 1
            if tuple(vector) == target(leaf):
                hits.append(leaf)
        expected = [leaf for leaf in (gap - 1, gap) if 0 <= leaf < stages]
        if hits != expected:
            fail("external leaf-to-core hits changed at gap " + str(gap))


def compare_bounds() -> dict[str, int]:
    equal = []
    for stages in range(1, MAX_STAGES + 1):
        joint = ceil_div(2 * stages, 5)
        old = ceil_div(stages, 3)
        if joint < old:
            fail("joint count fell below ceil(g/3)")
        if stages >= 15 and joint < old + 1:
            fail("large stage count did not rise")
        if joint == old:
            equal.append(stages)
        dual_weight(stages)
        primal_value(stages)
        monomials(stages)
    if equal != [1, 2, 4, 5, 7, 10]:
        fail("equality list changed: " + str(equal))
    old_target = 2 * TARGET_Q * ceil_div(TARGET_G, 3)
    joint_target = 2 * TARGET_Q * ceil_div(2 * TARGET_G, 5)
    if old_target != 572 or joint_target != 676 or not joint_target > old_target:
        fail("g=31, q=26 numbers changed")
    return {
        "old_g31_q26": old_target,
        "joint_g31_q26": joint_target,
        "equal_stages": len(equal),
    }


# --- direct g=3, q=1 word, B12 = B21 = 1, first half plus -----------------------

WIDTH = 2
LEAVES = 3
SPACE = (LEAVES + 1) * WIDTH


def g_zero() -> list[list[int]]:
    return [[0] * SPACE for _ in range(SPACE)]


def g_eye() -> list[list[int]]:
    matrix = g_zero()
    for index in range(SPACE):
        matrix[index][index] = 1
    return matrix


def g_mul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    out = g_zero()
    for row in range(SPACE):
        for mid in range(SPACE):
            if left[row][mid]:
                for col in range(SPACE):
                    out[row][col] ^= right[mid][col]
    return out


def g_add(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[left[row][col] ^ right[row][col] for col in range(SPACE)] for row in range(SPACE)]


def g_is_zero(matrix: list[list[int]]) -> bool:
    return not any(any(row) for row in matrix)


def poly_add(left: dict[tuple[int, ...], list[list[int]]], right: dict[tuple[int, ...], list[list[int]]]):
    out = dict(left)
    for key, matrix in right.items():
        summed = matrix if key not in out else g_add(out[key], matrix)
        if g_is_zero(summed):
            out.pop(key, None)
        else:
            out[key] = summed
    return out


def poly_mul(left, right):
    out: dict[tuple[int, ...], list[list[int]]] = {}
    for key_l, matrix_l in left.items():
        for key_r, matrix_r in right.items():
            key = tuple(a + b for a, b in zip(key_l, key_r))
            matrix = g_mul(matrix_l, matrix_r)
            if g_is_zero(matrix):
                continue
            summed = matrix if key not in out else g_add(out[key], matrix)
            if g_is_zero(summed):
                out.pop(key, None)
            else:
                out[key] = summed
    return out


def g_const(matrix: list[list[int]]):
    if g_is_zero(matrix):
        return {}
    return {tuple(0 for _ in range(LEAVES)): matrix}


def g_var(index: int) -> tuple[int, ...]:
    exponents = [0] * LEAVES
    exponents[index] = 1
    return tuple(exponents)


def local_halves() -> tuple[list[list[int]], list[list[int]]]:
    plus = [
        [1, 1, 0, 1],
        [1, 0, 1, 0],
        [0, 1, 1, 1],
        [1, 0, 1, 0],
    ]
    minus = [
        [0, 1, 0, 1],
        [1, 1, 1, 0],
        [0, 1, 0, 1],
        [1, 0, 1, 1],
    ]
    return plus, minus


def embed_local(local: list[list[int]], stage: int) -> list[list[int]]:
    matrix = g_zero()
    locs = [0, 1, WIDTH * (stage + 1), WIDTH * (stage + 1) + 1]
    for row in range(4):
        for col in range(4):
            matrix[locs[row]][locs[col]] = local[row][col]
    return matrix


def embed_sign(plus_sign: bool, stage: int) -> list[list[int]]:
    matrix = g_zero()
    locs = [0, 1, WIDTH * (stage + 1), WIDTH * (stage + 1) + 1]
    indices = (0, 2) if plus_sign else (1, 3)
    for row in indices:
        for col in indices:
            matrix[locs[row]][locs[col]] = 1
    return matrix


def full_call(projector: list[list[int]], image: list[list[int]], stage: int):
    pure = poly_add(g_const(g_add(g_eye(), projector)), {g_var(stage): projector})
    composed = g_mul(projector, image)
    coeff = poly_add(g_const(g_add(image, composed)), {g_var(stage): composed})
    return pure, coeff


def multiply_word(factors):
    pure = g_const(g_eye())
    coeff: dict[tuple[int, ...], list[list[int]]] = {}
    for factor_pure, factor_e in reversed(factors):
        coeff = poly_add(poly_mul(factor_pure, coeff), poly_mul(factor_e, pure))
        pure = poly_mul(factor_pure, pure)
    return pure, coeff


def stage_factors(stage: int, matrix: list[list[int]] | None):
    plus, minus = local_halves()
    factors = [
        full_call(embed_local(minus, stage), embed_sign(False, stage), stage),
    ]
    if matrix is not None:
        factors.append((g_const(g_eye()), g_const(matrix)))
    factors.append(full_call(embed_local(plus, stage), embed_sign(True, stage), stage))
    return factors


def block_of(matrix: list[list[int]], rows: list[int], cols: list[int]) -> list[list[int]]:
    return [[matrix[row][col] for col in cols] for row in rows]


def identity2() -> list[list[int]]:
    return [[1, 0], [0, 1]]


def core_cols() -> list[int]:
    return [0, 1]


def leaf_rows(leaf: int) -> list[int]:
    return [WIDTH * (leaf + 1), WIDTH * (leaf + 1) + 1]


def leaf_cols(leaf: int) -> list[int]:
    return leaf_rows(leaf)


def required_core(leaf: int) -> tuple[int, ...]:
    return tuple(1 if index >= leaf else 0 for index in range(LEAVES))


def required_leaf(leaf: int) -> tuple[int, ...]:
    return tuple(1 if index <= leaf else 0 for index in range(LEAVES))


def core_output_of(stage: list[list[int]], vector: list[int]) -> list[int]:
    image = [0, 0]
    for col in range(4):
        if vector[col]:
            image[0] ^= stage[0][col]
            image[1] ^= stage[1][col]
    return image


def actual_witness() -> list[list[int]]:
    """Rank-2 map at stage 1 with three core-to-leaf blocks equal to I.

    The own-leaf and previous-leaf degree-1 and degree-0 leaf-to-core blocks
    that the construction can set are filled in. The next-leaf leaf-to-core
    block stays zero because the map annihilates the first half.
    """
    plus, minus = local_halves()
    lam = [[1, 0], [1, 1]]
    stage = [[0] * 4 for _ in range(4)]
    for row in range(2):
        for mid in range(2):
            if lam[row][mid]:
                for col in range(4):
                    stage[row][col] ^= minus[mid][col]
    locs = [0, 1, 4, 5]
    matrix = g_zero()
    for row in range(4):
        for col in range(4):
            matrix[locs[row]][locs[col]] = stage[row][col]

    def output_for(projector: list[list[int]], target: int) -> list[int]:
        for code in range(4):
            vector = [code & 1, (code >> 1) & 1, 0, 0]
            image = [0, 0, 0, 0]
            for col in range(4):
                if vector[col]:
                    for row in range(4):
                        image[row] ^= projector[row][col]
            if image[0] == (target == 0) and image[1] == (target == 1):
                return vector
        fail("could not invert the core projection")
        return []

    for leaf, projector in ((0, minus), (2, plus)):
        for col_index in range(2):
            vector = output_for(projector, col_index)
            for row in range(4):
                matrix[locs[row]][leaf_cols(leaf)[col_index]] = vector[row]

    core_outputs = []
    desired = []
    for col in range(2):
        core_outputs.append(core_output_of(stage, [minus[row][col] for row in range(4)]))
        desired.append([1 if index == col else 0 for index in range(2)])
    if rank_rows(core_outputs) != 2:
        fail("Q core outputs are dependent")
    prev_map = None
    for code in range(16):
        candidate = [[(code >> (2 * row + col)) & 1 for col in range(2)] for row in range(2)]
        good = True
        for col in range(2):
            prod = [
                (candidate[row][0] & core_outputs[col][0]) ^ (candidate[row][1] & core_outputs[col][1])
                for row in range(2)
            ]
            if prod != desired[col]:
                good = False
                break
        if good:
            prev_map = candidate
            break
    if prev_map is None:
        fail("previous leaf-to-core map was not found")

    def write_previous(column: int, core_vector: list[int]) -> None:
        for row in range(2):
            value = (prev_map[row][0] & core_vector[0]) ^ (prev_map[row][1] & core_vector[1])
            matrix[leaf_rows(0)[row]][column] = value

    for col in range(4):
        write_previous(locs[col], [stage[0][col], stage[1][col]])
    for leaf, projector in ((0, minus), (2, plus)):
        for col_index in range(2):
            vector = [matrix[locs[row]][leaf_cols(leaf)[col_index]] for row in range(4)]
            write_previous(leaf_cols(leaf)[col_index], vector[:2])
    for col in range(2):
        source = [0] * SPACE
        for row in range(4):
            if minus[row][col]:
                source[locs[row]] = 1
        image = [0] * SPACE
        for mid in range(SPACE):
            if source[mid]:
                for row in range(SPACE):
                    image[row] ^= matrix[row][mid]
        expected = [1 if index == col else 0 for index in range(2)]
        got = [image[leaf_rows(0)[row]] for row in range(2)]
        if got != expected:
            fail("previous leaf-to-core block is not I")
    return matrix


def read_blocks(coeff, rows: list[int], cols: list[int]):
    found = {}
    for key, matrix in coeff.items():
        block = block_of(matrix, rows, cols)
        if any(any(row) for row in block):
            found[key] = block
    return found


def direct_word() -> dict[str, int]:
    bare_factors = []
    for stage in reversed(range(LEAVES)):
        bare_factors.extend(stage_factors(stage, None))
    _pure, bare = multiply_word(bare_factors)
    for leaf in range(LEAVES):
        core_blocks = read_blocks(bare, [0, 1], leaf_cols(leaf))
        leaf_blocks = read_blocks(bare, leaf_rows(leaf), core_cols())
        if list(core_blocks) != [required_core(leaf)] or core_blocks[required_core(leaf)] != identity2():
            fail("bare core-to-leaf block is not M_j I")
        if list(leaf_blocks) != [required_leaf(leaf)] or leaf_blocks[required_leaf(leaf)] != identity2():
            fail("bare leaf-to-core block is not N_j I")
    witness = actual_witness()
    if rank_rows(witness) != 2:
        fail("witness rank is not 2")
    factors = []
    for stage in reversed(range(LEAVES)):
        factors.extend(stage_factors(stage, witness if stage == 1 else None))
    _pure, coeff = multiply_word(factors)
    delta = poly_add(coeff, bare)
    # The rank-2 witness supplies I on M_0, M_2, N_0 and N_1. Its own core-to-leaf
    # block has rank 2 and is not I, so M_1 survives. Its next leaf-to-core block is 0.
    expected_identity = {
        (0, required_core(0)),
        (2, required_core(2)),
        (0, required_leaf(0)),
        (1, required_leaf(1)),
    }
    for leaf, key in expected_identity:
        rows = [0, 1] if key == required_core(leaf) else leaf_rows(leaf)
        cols = leaf_cols(leaf) if key == required_core(leaf) else core_cols()
        block = read_blocks(delta, rows, cols).get(key)
        if block != identity2():
            fail("witness missed an identity block at leaf " + str(leaf))
    own_core = read_blocks(delta, [0, 1], leaf_cols(1)).get(required_core(1))
    if own_core != [[1, 1], [1, 0]]:
        fail("own core-to-leaf contribution changed")
    if required_leaf(2) in read_blocks(delta, leaf_rows(2), core_cols()):
        fail("next leaf-to-core block was not zero")
    if required_core(1) not in read_blocks(coeff, [0, 1], leaf_cols(1)):
        fail("own core-to-leaf monomial was cancelled")
    if required_leaf(2) not in read_blocks(coeff, leaf_rows(2), core_cols()):
        fail("next leaf-to-core monomial disappeared")
    for leaf in (0, 1):
        if required_leaf(leaf) in read_blocks(coeff, leaf_rows(leaf), core_cols()):
            fail("leaf-to-core monomial N_" + str(leaf) + " was not cancelled")
    extra = read_blocks(coeff, leaf_rows(1), core_cols())
    if extra.get((1, 0, 0)) != identity2():
        fail("degree-zero own leaf-to-core monomial is not I")
    return {"cancelled_core_to_leaf": 2, "cancelled_leaf_to_core": 2, "remaining_leaf_to_core": 1}


def random_coupling(seed: int) -> int:
    """Seeded rank-bounded maps on the q=1 three-leaf space."""
    rng = random.Random(seed)
    plus, _minus = projectors_bi()
    first = embed4(plus)
    second = embed4(projectors_bi()[1])
    checked = 0
    legal = 0
    for _trial in range(300):
        budget = 1 + rng.randrange(4)
        left = [[rng.randrange(2) for _ in range(budget)] for _ in range(8)]
        right = [[rng.randrange(2) for _ in range(8)] for _ in range(budget)]
        matrix = [0] * 8
        for row in range(8):
            acc = 0
            for mid in range(budget):
                if left[row][mid]:
                    value = 0
                    for col in range(8):
                        if right[mid][col]:
                            value |= 1 << col
                    acc ^= value
            matrix[row] = acc
        square = bit_mul(second, bit_mul(matrix, first))
        core_rows = bit_mul(second, matrix)[:2]
        prev = rank_rows([[(row >> col) & 1 for col in range(4, 6)] for row in core_rows])
        nxt_rows = [bit_mul(matrix, first)[row] for row in (6, 7)]
        nxt = rank_rows([[(row >> col) & 1 for col in range(2)] for row in nxt_rows])
        total = rank_rows([[(row >> col) & 1 for col in range(8)] for row in matrix])
        checked += 1
        if all(entry == 0 for entry in square):
            legal += 1
            if prev + nxt > total:
                fail("seeded square-free map broke the coupling")
    if legal == 0:
        fail("seeded sample contained no square-free map")
    return checked


def main() -> int:
    witness = witness_blocks()
    if witness["own_core_to_leaf_rank"] != 2:
        fail("witness flags")
    census = q1_rank_one_coupling()
    bounds = compare_bounds()
    word = direct_word()
    if random_coupling(1729) != 300:
        fail("random control")
    overweight_dual_rejected()
    print(
        "PASS_LEAF_TO_CORE_EVERY_STAGE"
        f" old_g31_q26={bounds['old_g31_q26']}"
        f" joint_g31_q26={bounds['joint_g31_q26']}"
        f" rank_one_maps={census['rank_one_maps']}"
        f" square_zero={census['square_zero']}"
        f" word_cancelled_core={word['cancelled_core_to_leaf']}"
        " no_new_kappa"
    )
    print(
        "STATUS proof that leaf-to-core blocks raise the every-stage thin-rank"
        " bound from 2q ceil(g/3) to at least 2q ceil(2g/5) under the stated"
        " schedule hypotheses; not a word; not unrestricted nonexistence; no kappa change"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
