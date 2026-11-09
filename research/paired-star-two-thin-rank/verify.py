#!/usr/bin/env python3
"""Two thin maps on the three-leaf F_2 paired star have total rank at least 8.

The polynomial control is independent of search.c. The census is the compiled
search. Failures are raised, so python -O still fails closed.
"""

import itertools
import os
import subprocess
import sys

G = 3
N = 8
I2 = ((1, 0), (0, 1))
Z2 = ((0, 0), (0, 0))
ZERO_EXP = (0,) * G


def require(ok, message):
    if not ok:
        raise SystemExit("FAIL: " + message)


def add2(left, right):
    return tuple(tuple(left[i][j] ^ right[i][j] for j in range(2)) for i in range(2))


def mul2(left, right):
    return tuple(
        tuple((left[i][0] & right[0][j]) ^ (left[i][1] & right[1][j]) for j in range(2))
        for i in range(2)
    )


def rank2(matrix):
    rows = [list(row) for row in matrix]
    rank = 0
    for col in range(2):
        pivot = next((i for i in range(rank, 2) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(2):
            if i != rank and rows[i][col]:
                for j in range(2):
                    rows[i][j] ^= rows[rank][j]
        rank += 1
    return rank


def mat2(bits):
    return tuple(tuple((bits >> (i * 2 + j)) & 1 for j in range(2)) for i in range(2))


def block_rows(matrix_a, matrix_b):
    mixed = add2(matrix_a, matrix_b)
    rows = []
    for left, right in ((mixed, matrix_b), (matrix_b, mixed)):
        for r in range(2):
            mask = 0
            for block_col, block in enumerate((left, right)):
                for c in range(2):
                    if block[r][c]:
                        mask |= 1 << (block_col * 2 + c)
            rows.append(mask)
    return tuple(rows)


def mul_bits(left, right):
    out = []
    for row in left:
        value = 0
        rest = row
        while rest:
            bit = rest & -rest
            value ^= right[bit.bit_length() - 1]
            rest ^= bit
        out.append(value)
    return tuple(out)


def resolutions():
    found = []
    seen = set()
    for bits_a in range(16):
        matrix_a = mat2(bits_a)
        if mul2(matrix_a, matrix_a) != matrix_a or rank2(matrix_a) != 1:
            continue
        complement = add2(I2, matrix_a)
        for bits_b in range(16):
            matrix_b = mat2(bits_b)
            first = block_rows(matrix_a, matrix_b)
            second = block_rows(complement, matrix_b)
            zero = (0, 0, 0, 0)
            if not (
                mul_bits(first, first) == first
                and mul_bits(second, second) == second
                and mul_bits(first, second) == zero
                and mul_bits(second, first) == zero
            ):
                continue
            key = tuple(sorted((first, second)))
            if key in seen:
                continue
            seen.add(key)
            found.append((matrix_a, matrix_b, complement))
    return tuple(found)


def embed(blocks):
    rows = [0] * N
    for (block_i, block_j), block in blocks.items():
        for r in range(2):
            for c in range(2):
                if block[r][c]:
                    rows[block_i * 2 + r] |= 1 << (block_j * 2 + c)
    return tuple(rows)


def matrix_p(stage, matrix_a, matrix_b):
    mixed = add2(matrix_a, matrix_b)
    leaf = stage + 1
    return embed({(0, 0): mixed, (0, leaf): matrix_b, (leaf, 0): matrix_b, (leaf, leaf): mixed})


def matrix_r(stage, matrix_a):
    leaf = stage + 1
    return embed(
        {
            (0, 0): matrix_a,
            (0, leaf): matrix_a,
            (leaf, 0): matrix_a,
            (leaf, leaf): matrix_a,
        }
    )


def matrix_e(stage):
    return embed({(0, 0): I2, (stage + 1, stage + 1): I2})


def eye():
    return tuple(1 << i for i in range(N))


def add_rows(left, right):
    return tuple(x ^ y for x, y in zip(left, right))


def poly_mul(left, right):
    out = {}
    right_items = tuple(right.items())
    for exp_l, mat_l in left.items():
        for exp_r, mat_r in right_items:
            if exp_l[0] + exp_r[0] > 1:
                continue
            exp = (exp_l[0] + exp_r[0], tuple(a + b for a, b in zip(exp_l[1], exp_r[1])))
            prod = mul_bits(mat_l, mat_r)
            prev = out.get(exp)
            if prev is None:
                if any(prod):
                    out[exp] = prod
            else:
                summed = add_rows(prev, prod)
                if any(summed):
                    out[exp] = summed
                else:
                    del out[exp]
    return out


def full_gate(stage, proj, read):
    degree = tuple(1 if i == stage else 0 for i in range(G))
    identity = eye()
    return {
        (0, ZERO_EXP): add_rows(identity, proj),
        (0, degree): proj,
        (1, degree): read,
    }


def thin_gate(mat):
    return {(0, ZERO_EXP): eye(), (1, ZERO_EXP): mat}


def stage_factor(stage):
    support = matrix_e(stage)
    degree = tuple(1 if i == stage else 0 for i in range(G))
    return {(0, ZERO_EXP): add_rows(eye(), support), (0, degree): support}


def target_word():
    word = {(0, ZERO_EXP): eye(), (1, ZERO_EXP): eye()}
    for stage in range(G):
        word = poly_mul(stage_factor(stage), word)
    return word


def eval_word(factors):
    word = {(0, ZERO_EXP): eye()}
    for factor in factors:
        word = poly_mul(factor, word)
    return word


def rank_rows(rows):
    rows = list(rows)
    rank = 0
    for col in range(N):
        mask = 1 << col
        pivot = next((i for i in range(rank, N) if rows[i] & mask), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_row = rows[rank]
        for i in range(N):
            if i != rank and (rows[i] & mask):
                rows[i] ^= pivot_row
        rank += 1
    return rank


def control_thin(stage):
    blocks = {}
    leaves = [stage] if stage + 1 == G else [stage, stage + 1]
    for leaf in leaves:
        block = leaf + 1
        blocks[(0, block)] = I2
        blocks[(block, 0)] = I2
    return embed(blocks)


def projector_checks(found):
    checked = 0
    for matrix_a, matrix_b, complement in found:
        for stage in range(G):
            for half in (matrix_a, complement):
                proj = matrix_p(stage, half, matrix_b)
                read = matrix_r(stage, half)
                require(mul_bits(proj, read) == read, "P R = R")
                require(mul_bits(read, proj) == read, "R P = R")
                checked += 1
    return checked


def noncommuting_resolution_pairs(found):
    count = 0
    for left, right in itertools.product(found, repeat=2):
        if mul2(left[0], right[0]) != mul2(right[0], left[0]):
            count += 1
    return count


def polynomial_control(found):
    matrix_a, matrix_b, complement = next(item for item in found if item[1] == Z2)
    factors = []
    for stage in range(G):
        factors.append(
            full_gate(stage, matrix_p(stage, matrix_a, matrix_b), matrix_r(stage, matrix_a))
        )
        factors.append(
            full_gate(stage, matrix_p(stage, complement, matrix_b), matrix_r(stage, complement))
        )
        if stage % 2 == 0:
            factors.append(thin_gate(control_thin(stage)))
    target = target_word()
    require(eval_word(factors) == target, "two-map control misses the endpoint")
    ranks = [rank_rows(control_thin(stage)) for stage in range(G) if stage % 2 == 0]
    require(ranks == [4, 4], "control ranks %s" % (ranks,))
    broken = list(factors)
    broken[2] = {(0, ZERO_EXP): eye()}
    require(eval_word(broken) != target, "deleting a thin map still met the endpoint")
    moved = list(factors)
    moved[2], moved[5] = moved[5], moved[2]
    require(eval_word(moved) != target, "moving a thin map into the other odd gap still met the endpoint")
    return ranks


EXPECT = {
    (0, 5): {
        "screened": "622080",
        "pure_hits": "85152",
        "both_hits": "85152",
        "slice000": "720",
        "consistent": "295688",
        "min_rank_sum": "8",
        "one_agree": "0",
    },
    (6, 11): {
        "screened": "622080",
        "pure_hits": "74832",
        "both_hits": "74832",
        "slice000": "0",
        "consistent": "273064",
        "min_rank_sum": "8",
        "one_agree": "0",
    },
    (0, 11): {
        "screened": "1244160",
        "pure_hits": "159984",
        "both_hits": "159984",
        "slice000": "720",
        "consistent": "568752",
        "min_rank_sum": "8",
        "one_agree": "0",
    },
}


def run_census(low, high):
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    source = os.path.join(root, "research", "paired-star-two-thin-rank", "search.c")
    binary = os.path.join("/tmp", "paired-star-two-thin-search-%d-%d" % (low, high))
    compile_run = subprocess.run(
        ["gcc", "-O3", "-march=native", "-std=c11", "-fopenmp", "-o", binary, source],
        cwd=root,
        capture_output=True,
        text=True,
    )
    require(compile_run.returncode == 0, "gcc failed: " + compile_run.stderr[-500:])
    env = dict(os.environ)
    env.setdefault("OMP_NUM_THREADS", "4")
    run = subprocess.run(
        [binary, "range", str(low), str(high)],
        cwd=root,
        capture_output=True,
        text=True,
        env=env,
    )
    sys.stderr.write(run.stderr)
    require(run.returncode == 0, "search exit %s\n%s" % (run.returncode, run.stdout[-1000:]))
    require("WITNESS" not in run.stdout and "ONE_WITNESS" not in run.stdout, "search reported a witness")
    summary = None
    for line in run.stdout.splitlines():
        if line.startswith("screened=") and "one_agree=" in line:
            summary = dict(part.split("=", 1) for part in line.split())
            break
    require(summary is not None, "missing census summary")
    expect = EXPECT.get((low, high))
    require(expect is not None, "no expected totals for range %s..%s" % (low, high))
    for key, value in expect.items():
        require(summary.get(key) == value, "%s=%s, expected %s" % (key, summary.get(key), value))
    try:
        os.remove(binary)
    except OSError as exc:
        require(False, "could not remove compiled search: %s" % exc)
    return summary


def main():
    found = resolutions()
    require(len(found) == 12, "resolution count %s" % (len(found),))
    require(sum(item[1] == Z2 for item in found) == 3, "diagonal resolution count")
    require(projector_checks(found) == 72, "projector check count")
    require(
        noncommuting_resolution_pairs(found) == 96,
        "noncommuting pair count %s" % (noncommuting_resolution_pairs(found),),
    )
    polynomial_control(found)
    if len(sys.argv) == 3:
        low, high = int(sys.argv[1]), int(sys.argv[2])
    else:
        low, high = 0, 11
    run_census(low, high)
    print("PASS_PAIRED_STAR_TWO_THIN_RANK")


if __name__ == "__main__":
    main()
