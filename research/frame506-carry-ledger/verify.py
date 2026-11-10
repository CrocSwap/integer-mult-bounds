#!/usr/bin/env python3
"""Sharp carry envelope for the frozen frame-506 matcher.

The all-q argument is exact linear arithmetic, not a sample of primes.
The q=3 statement is an exhaustive census of every length-8 digit row.
"""
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRAMES = ROOT / "research/bit-completed-backend-api/independent/inputs/frames.json"
WORD = ROOT / "research/bit-completed-backend-api/independent/inputs/WORD.json.gz"
FRAMES_SHA = "d006b3bfe0c04afecfea7aecfa59dfe4298b99501c70da3938e40289bc2f5010"
WORD_SHA = "69fc50430f0062c040e0686f59ad32ee5af2387ae9a97d7d11b4af1aa994ed5b"

# S = [B^T | A^T] for frozen frame 506. Rows are the source matrix.
EXPECTED_S = (
    (0, 0, 0, 0, 1, 0, 0, 0),
    (0, 0, 1, 1, 0, -1, 0, 0),
    (0, 0, 1, 1, 0, 1, 0, 0),
    (0, 0, 0, 0, 0, 0, 1, 0),
    (0, 0, 1, 0, 0, 0, 0, 1),
    (2, 0, 0, 1, 0, 0, 0, 0),
    (0, 2, 0, 1, 0, 0, 0, 0),
    (0, 0, -1, 0, 0, 0, 0, 1),
)
# r(q) = SLOPE * q + CONST, with every coordinate in {0,...,q-1} for q >= 5.
SLOPE = (0, 1, 1, 0, 1, 1, 1, 0)
CONST = (0, -1, -2, 0, -1, -1, -1, 1)
# value = a*q + b, quotient exactly CARRY, for every integer q >= 5.
FORWARD = (
    (2, -2, 1),
    (2, -2, 1),
    (3, -5, 2),
    (4, -5, 3),
    (0, 0, 0),
    (0, -1, -1),
    (0, 0, 0),
    (1, 0, 1),
)
# Child low type u(q) = U_SLOPE * q + U_CONST, already reduced.
U_SLOPE = (1, 1, 1, 1, 0, 1, 0, 0)
U_CONST = (-2, -2, -5, -5, 0, -1, 0, 0)
RETURN = (
    Fraction(0),
    Fraction(-3, 2),
    Fraction(-1, 2),
    Fraction(0),
    Fraction(-1, 2),
    Fraction(-1, 2),
    Fraction(-1, 2),
    Fraction(-1, 2),
)
# h(q) = H_SLOPE * q + H_CONST is the reduced residue of the return dot.
H_SLOPE = (0, 1, 1, 0, 1, 1, 1, 0)
H_CONST = (0, -1, -2, 0, -1, -1, -1, 1)


def need(cond, message):
    if not cond:
        raise SystemExit("FAIL: " + message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def columns(matrix):
    return [tuple(matrix[i][j] for i in range(len(matrix))) for j in range(len(matrix[0]))]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def inverse(matrix):
    n = len(matrix)
    work = [row[:] + [Fraction(int(i == j)) for j in range(n)] for i, row in enumerate(matrix)]
    for j in range(n):
        k = next(i for i in range(j, n) if work[i][j])
        if k != j:
            work[j], work[k] = work[k], work[j]
        pivot = work[j][j]
        need(pivot != 0, "singular pivot")
        work[j] = [x / pivot for x in work[j]]
        for i in range(n):
            if i != j and work[i][j]:
                scale = work[i][j]
                work[i] = [x - scale * y for x, y in zip(work[i], work[j])]
    return [row[n:] for row in work]


def determinant(matrix):
    tri = [row[:] for row in matrix]
    det = Fraction(1)
    for j in range(8):
        k = next(i for i in range(j, 8) if tri[i][j])
        if k != j:
            tri[j], tri[k] = tri[k], tri[j]
            det = -det
        det *= tri[j][j]
        pivot = tri[j][j]
        for i in range(j + 1, 8):
            if tri[i][j]:
                scale = tri[i][j] / pivot
                tri[i] = [x - scale * y for x, y in zip(tri[i], tri[j])]
    return det


def affine_dots(cols, slope, const):
    out = []
    for col in cols:
        linear = sum(Fraction(slope[i]) * col[i] for i in range(8))
        fixed = sum(Fraction(const[i]) * col[i] for i in range(8))
        out.append((linear, fixed))
    return out


def in_digit_range(slope, const):
    """slope*q + const lies in {0,...,q-1} for every integer q >= 5."""
    if slope == 0:
        return 0 <= const <= 4
    return slope == 1 and -5 <= const <= -1


def prove_forward_quotient(linear, fixed, carry):
    need(linear.denominator == 1 and fixed.denominator == 1, "forward form not integral")
    rem_linear = int(linear) - carry
    rem_fixed = int(fixed)
    # remainder = rem_linear*q + rem_fixed is in {0,...,q-1} for every integer q >= 5,
    # so the integer quotient is exactly carry, including when carry is negative.
    need(in_digit_range(rem_linear, rem_fixed), "forward remainder leaves 0..q-1")


def prove_return_quotient(linear, fixed):
    # value = linear*q + fixed = h(q) + q*carry, with h(q) in {0,...,q-1}.
    # An integer fixed term in [-5, 4] is either h itself or h - q.
    need(fixed.denominator == 1, "return constant is not an integer")
    beta = int(fixed)
    if 0 <= beta <= 4:
        height, carry = 0, linear
    elif -5 <= beta <= -1:
        height, carry = 1, linear - 1
    else:
        raise SystemExit("FAIL: return constant is outside the uniform residue range")
    need(in_digit_range(height, beta), "return residue leaves 0..q-1")
    need(carry.denominator in (1, 2), "return carry is not in Z[1/2]")
    # For odd q, 2*carry in {-3,-1,0,1,3} decides zero in F_q: q >= 5 divides none of ±1, ±3.
    twice = 2 * carry
    need(twice.denominator == 1 and abs(int(twice)) in (0, 1, 3), "return carry is ambiguous mod q")
    return height, beta, carry


def load_matcher():
    need(sha256(FRAMES) == FRAMES_SHA, "frame bank hash")
    need(sha256(WORD) == WORD_SHA, "word hash")
    frames = json.loads(FRAMES.read_text(encoding="utf-8"))["frames"]
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    need(word["start"][462] == 0 and word["final"][462] == 506, "helper 462 endpoints")
    frame = frames["506"]
    need(frame["dim"] == 4 and len(frame["A"]) == 4 and len(frame["B"]) == 4, "frame 506 shape")
    stacked = [tuple(int(x) for x in row) for row in frame["B"] + frame["A"]]
    matcher = [list(col) for col in zip(*stacked)]
    need(tuple(tuple(row) for row in matcher) == EXPECTED_S, "frame 506 is not the stated matcher")
    return [[Fraction(x) for x in row] for row in matcher]


def prove_closed_forms(matcher):
    need(determinant(matcher) == -16, "det S = -16")
    inverse_s = inverse(matcher)
    identity = [[Fraction(int(i == j)) for j in range(8)] for i in range(8)]
    need(matmul(matcher, inverse_s) == identity, "S S^{-1} = I")
    need(all(x.denominator in (1, 2, 4) for row in inverse_s for x in row), "denominator divides 4")
    forward_cols = columns(matcher)
    return_cols = columns(inverse_s)
    need(forward_cols[4] == (1, 0, 0, 0, 0, 0, 0, 0), "forward column 4 is e0")
    need(forward_cols[6] == (0, 0, 0, 1, 0, 0, 0, 0), "forward column 6 is e3")
    need(return_cols[0] == (0, 0, 0, 0, 1, 0, 0, 0), "return column 0 is e4")
    need(return_cols[3] == (0, 0, 0, 0, 0, 0, 1, 0), "return column 3 is e6")

    forms = affine_dots(forward_cols, SLOPE, CONST)
    remainders = []
    for (linear, fixed), (want_a, want_b, carry) in zip(forms, FORWARD):
        need((linear, fixed) == (want_a, want_b), "forward form drifted")
        prove_forward_quotient(linear, fixed, carry)
        remainders.append((linear - carry, fixed))
    need(remainders == list(zip(U_SLOPE, U_CONST)), "child low type is not the forward remainder")
    for slope, const in remainders:
        need(in_digit_range(int(slope), int(const)), "child digit leaves 0..q-1")

    returns = []
    residues = affine_dots(return_cols, U_SLOPE, U_CONST)
    for (linear, fixed), want, height, residue in zip(residues, RETURN, H_SLOPE, H_CONST):
        got_height, got_residue, carry = prove_return_quotient(linear, fixed)
        need((got_height, got_residue, carry) == (height, residue, want), "return split drifted")
        returns.append(carry)
    need(sum(carry != 0 for _, _, carry in FORWARD) == 6, "forward weight")
    need(sum(c != 0 for c in returns) == 6, "return weight")
    need([c for _, _, c in FORWARD].count(0) == 2, "two structural forward zeros")
    need(returns.count(0) == 2, "two structural return zeros")
    return forward_cols, return_cols


def direct_forward(row, cols, q):
    carries = []
    image = []
    for col in cols:
        value = sum(digit * entry for digit, entry in zip(row, col))
        residue = int(value) % q
        carries.append((int(value) - residue) // q)
        image.append(residue)
    return carries, tuple(image)


def direct_return(row, cols, q):
    carries = []
    for col in cols:
        value = sum(digit * entry for digit, entry in zip(row, col))
        residue = (value.numerator * pow(value.denominator, -1, q)) % q
        carries.append((value - residue) / q)
    return carries


def instantiate(forward_cols, return_cols):
    for q in (5, 7, 11, 401):
        row = tuple(SLOPE[i] * q + CONST[i] for i in range(8))
        need(all(0 <= digit < q for digit in row), "witness digits")
        carries, image = direct_forward(row, forward_cols, q)
        need(carries == [carry for _, _, carry in FORWARD], "forward instantiation")
        child = tuple(U_SLOPE[i] * q + U_CONST[i] for i in range(8))
        need(image == child, "child instantiation")
        need(direct_return(child, return_cols, q) == list(RETURN), "return instantiation")


def census_q3(forward_cols, return_cols):
    max_forward = max_return = max_joint = 0
    seen = 0
    for digits in range(3 ** 8):
        row = tuple((digits // (3 ** i)) % 3 for i in range(8))
        forward, image = direct_forward(row, forward_cols, 3)
        backward = direct_return(image, return_cols, 3)
        weight_f = sum(carry != 0 for carry in forward)
        weight_r = sum(carry != 0 for carry in backward)
        max_forward = max(max_forward, weight_f)
        max_return = max(max_return, weight_r)
        max_joint = max(max_joint, weight_f + weight_r)
        seen += 1
    need(seen == 6561, "q=3 domain size")
    need((max_forward, max_return, max_joint) == (6, 6, 11), "q=3 census")


def controls(forward_cols, return_cols):
    q = 5
    zero = tuple(0 for _ in range(8))
    zero_forward, zero_image = direct_forward(zero, forward_cols, q)
    need(all(carry == 0 for carry in zero_forward), "zero forward")
    need(all(carry == 0 for carry in direct_return(zero_image, return_cols, q)), "zero return")

    row = tuple(SLOPE[i] * q + CONST[i] for i in range(8))
    forward, _ = direct_forward(row, forward_cols, q)
    mutated = list(forward_cols)
    mutated[4] = (2, 0, 0, 0, 0, 0, 0, 0)
    # This witness has a zero on the unit column, so use a nonzero digit there.
    probe = (q - 1, 0, 0, q - 1, 0, 0, 0, 0)
    real, _ = direct_forward(probe, forward_cols, q)
    doubled, _ = direct_forward(probe, mutated, q)
    need(real[4] == 0 and doubled[4] == 1, "doubled forward column carries")
    need(forward[4] == 0 and forward[6] == 0, "witness keeps the structural zeros")

    child = (0, 0, 0, 0, q - 1, 0, 0, 0)
    mutated_return = list(return_cols)
    mutated_return[0] = tuple(2 * entry for entry in return_cols[0])
    real_return = direct_return(child, return_cols, q)
    doubled_return = direct_return(child, mutated_return, q)
    need(real_return[0] == 0 and doubled_return[0] == 1, "doubled return column carries")

    # Floors of u*(4 S^{-1}) are not the inverse carry. One finite row separates them.
    old = tuple((1, 0, 0, 1, 1, 1, 1, 1)[i] * q + (-1, 1, 0, -1, -3, -1, -1, -1)[i] for i in range(8))
    _, old_image = direct_forward(old, forward_cols, q)
    true = direct_return(old_image, return_cols, q)
    cleared = [[4 * entry for entry in row] for row in inverse([list(col) for col in zip(*forward_cols)])]
    floors = [sum(digit * entry for digit, entry in zip(old_image, col)) // q for col in columns(cleared)]
    need(sum(carry != 0 for carry in true) == 5, "true weight on the separating row")
    need(sum(floor != 0 for floor in floors) == 8, "cleared-denominator weight differs")


def main():
    matcher = load_matcher()
    forward_cols, return_cols = prove_closed_forms(matcher)
    instantiate(forward_cols, return_cols)
    census_q3(forward_cols, return_cols)
    controls(forward_cols, return_cols)
    print("PASS_FRAME506_CARRY_LEDGER")


if __name__ == "__main__":
    main()
