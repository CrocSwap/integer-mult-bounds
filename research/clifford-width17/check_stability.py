"""Check the inherited spectrum receipt and the dyadic stability corollary.

apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_constants():
    path = Path(__file__).parent / "references" / "conditioning-result.json"
    raw = path.read_bytes()
    digest = "d032d5e63820f4ffe246d21adcd8d272f04dfd635a6fc519c4a81a366ca41d49"
    require(hashlib.sha256(raw).hexdigest() == digest, "changed PR7772 result")
    receipt = json.loads(raw)
    levels = [Q(*row["eigenvalue"]) for row in receipt["rows"]]
    low, high = min(levels), max(levels)
    require(len(levels) == 81 and receipt["width"] == 13, "wrong spectral scope")
    require((low, high) == (Q(*receipt["minimum"]), Q(*receipt["maximum"])),
            "endpoints disagree with the retained rows")
    dimension = sum(row["regular_dimension"] for row in receipt["rows"])
    require(dimension == receipt["projective_order"] == 12128668876800, "wrong dimension")
    contraction = max(abs(1 - low / 4), abs(1 - high / 4))
    require(contraction < Q(63, 64) and Q(63, 64)**64 < Q(1, 2), "slow contraction")
    row_norm_squared = 73190789644335724
    require(dimension * row_norm_squared < (2**50 - 4)**2 and low > Q(1, 16),
            "initial error bound")
    canonical_bound = Q(302095, 100000)
    require(canonical_bound**2 * low > 1, "canonical norm margin")
    gap = Q(2**50, 2**(8192 // 64))
    require(gap == Q(1, 2**78) and canonical_bound + gap < Q(3021, 1000),
            "final norm margin")


def matmul(left, right):
    return [[sum(x*y for x, y in zip(row, col, strict=True)) for col in zip(*right)]
            for row in left]


def combine(left, right, multiplier):
    return [[x + multiplier*y for x, y in zip(a, b, strict=True)]
            for a, b in zip(left, right, strict=True)]


def check_iteration():
    # Two unit columns with overlap 1/2. Their pseudoinverse requires thirds.
    half = Q(1, 2)
    a = [[1, half], [0, half], [0, half], [0, half]]
    adjoint = list(zip(*a))
    identity = [[1, 0], [0, 1]]
    gram = matmul(adjoint, a)
    h = combine(identity, gram, -Q(1, 4))
    gram_inverse = [[Q(4, 3), -Q(2, 3)], [-Q(2, 3), Q(4, 3)]]
    canonical = matmul(gram_inverse, adjoint)
    current = [[1, -1, 0, 0], [0, 2, 0, 0]]
    error = combine(current, canonical, -1)
    for _ in range(9):
        require(matmul(current, a) == identity, "an iterate lost exact recovery")
        require(combine(current, canonical, -1) == error, "wrong error recurrence")
        require(all(v.denominator.bit_count() == 1 for row in current for v in row),
                "non-dyadic iterate")
        current = combine(matmul(h, current), adjoint, Q(1, 4))
        error = matmul(h, error)
    require(any(v for row in error for v in row), "fixture started at its fixed point")
    faulty = combine(matmul(h, current), adjoint, -Q(1, 4))
    require(matmul(faulty, a) != identity, "wrong-sign control escaped")


if __name__ == "__main__":
    check_constants()
    check_iteration()
    print("PASS_DYADIC_STABILITY spectral_rows=81 toy_left_inverses=9 norm_upper=3.021")
