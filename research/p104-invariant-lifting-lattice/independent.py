#!/usr/bin/env python3
"""Independent modular-image check of the common lifting period lattice.

No imports from the main checker or vendored implementation.  The finite
calculation uses dense integer congruence rows followed by modular Smith
elimination, rather than successive index-two changes of a lattice basis.
Apache-2.0.  AI-assisted independent mathematical review for batch member 03.
"""

from collections import Counter
from fractions import Fraction
from itertools import product
import json


def need(condition, message):
    """Keep every verification active under normal and optimized Python."""
    if not condition:
        raise ValueError(message)


def pair(a, b, inverse=False):
    """Literal Gaussian floor map, Gaussian integers represented by pairs."""
    dr, di = a[0] - b[0], a[1] - b[1]
    sr, si = b[0] + dr // 2, b[1] + di // 2
    dr, di = (di, -dr) if inverse else (-di, dr)
    b = sr - dr // 2, si - di // 2
    return (b[0] + dr, b[1] + di), b


def linear_pair(a, b, inverse=False):
    """Exact rational ideal map, independently written in sum/difference form."""
    sr, si = a[0] + b[0], a[1] + b[1]
    dr, di = a[0] - b[0], a[1] - b[1]
    dr, di = (di, -dr) if inverse else (-di, dr)
    return (
        (Fraction(sr + dr, 2), Fraction(si + di, 2)),
        (Fraction(sr - dr, 2), Fraction(si - di, 2)),
    )


def word(x, rank, inverse=False, literal=False):
    y = list(x)
    operation = pair if literal else linear_pair
    order = reversed(range(rank)) if inverse else range(rank)
    for bit in order:
        for a in range(1 << rank):
            if not (a >> bit) & 1:
                b = a ^ (1 << bit)
                y[a], y[b] = operation(y[a], y[b], inverse)
    return y


def member(x, rank, inverse=False):
    """Forward or inverse-prefix membership, with exact rational prefixes."""
    y = list(x)
    order = reversed(range(rank)) if inverse else range(rank)
    for bit in order:
        for a in range(1 << rank):
            if not (a >> bit) & 1:
                b = a ^ (1 << bit)
                if any((u - v) % 2 for u, v in zip(y[a], y[b])):
                    return False
                y[a], y[b] = linear_pair(y[a], y[b], inverse)
    return True


def common_member(x, rank):
    return member(x, rank) and member(x, rank, inverse=True)


def congruence_rows(rank, inverse=False):
    """Integer rows A with Gamma = ker(A mod 2**rank).

    Prefix numerator rows after k stages are 2**k times that prefix.
    The difference-even condition at stage k is therefore a congruence
    modulo 2**(k+1), scaled to the single common modulus 2**rank.
    """
    size = 2 << rank
    numerator = [[int(i == j) for j in range(size)] for i in range(size)]
    constraints = []
    order = list(reversed(range(rank))) if inverse else list(range(rank))
    for k, bit in enumerate(order):
        weight = 1 << (rank - k - 1)
        next_rows = [None] * size
        for a in range(1 << rank):
            if (a >> bit) & 1:
                continue
            b = a ^ (1 << bit)
            ar, ai, br, bi = (numerator[2 * a], numerator[2 * a + 1],
                              numerator[2 * b], numerator[2 * b + 1])
            constraints.extend(
                [[weight * (u - v) for u, v in zip(ar, br)],
                 [weight * (u - v) for u, v in zip(ai, bi)]]
            )
            sums_r = [u + v for u, v in zip(ar, br)]
            sums_i = [u + v for u, v in zip(ai, bi)]
            diffs_r = [u - v for u, v in zip(ar, br)]
            diffs_i = [u - v for u, v in zip(ai, bi)]
            if inverse:
                rot_r, rot_i = diffs_i, [-u for u in diffs_r]
            else:
                rot_r, rot_i = [-u for u in diffs_i], diffs_r
            for target, sums, rotation, sign in (
                (2 * a, sums_r, rot_r, 1),
                (2 * a + 1, sums_i, rot_i, 1),
                (2 * b, sums_r, rot_r, -1),
                (2 * b + 1, sums_i, rot_i, -1),
            ):
                next_rows[target] = [u + sign * v for u, v in zip(sums, rotation)]
        numerator = next_rows
    return constraints


def image_factors(rows, power):
    """Image invariant exponents over Z/(2**power), by independent elimination.

    Each nonzero pivot of least two-adic valuation v is normalized to 2**v
    by a unit row operation.  Entries beneath it can then be eliminated.
    A column operation clears the rest of its row without changing the
    lower-right block, since its column has just been cleared.  Its image
    factor is cyclic of order 2**(power-v).  All operations are invertible
    over the modular ring.  Zero pivots contribute no factor.
    """
    modulus = 1 << power
    matrix = [[x % modulus for x in row] for row in rows]
    width = len(matrix[0])
    factors = []
    for k in range(min(len(matrix), width)):
        best = None
        for i in range(k, len(matrix)):
            for j in range(k, width):
                value = matrix[i][j]
                if value:
                    valuation = (value & -value).bit_length() - 1
                    if best is None or valuation < best[0]:
                        best = valuation, i, j
                        if valuation == 0:
                            break
            if best is not None and best[0] == 0:
                break
        if best is None:
            break
        valuation, pivot_row, pivot_column = best
        matrix[k], matrix[pivot_row] = matrix[pivot_row], matrix[k]
        if pivot_column != k:
            for row in matrix:
                row[k], row[pivot_column] = row[pivot_column], row[k]
        scale = pow(matrix[k][k] >> valuation, -1, modulus)
        pivot = matrix[k]
        for j in range(k, width):
            pivot[j] = pivot[j] * scale % modulus
        need(pivot[k] == 1 << valuation, "Smith pivot normalization")
        for row in matrix[k + 1:]:
            need(row[k] % (1 << valuation) == 0, "Smith pivot divisibility")
            multiplier = row[k] >> valuation
            if multiplier:
                for j in range(k + 1, width):
                    row[j] = (row[j] - multiplier * pivot[j]) % modulus
            row[k] = 0
        factors.append(power - valuation)
    return sorted(factors)


def modular_member(x, rows, rank):
    flattened = [part for value in x for part in value]
    modulus = 1 << rank
    return all(sum(a * b for a, b in zip(row, flattened)) % modulus == 0
               for row in rows)


def gaussian_power(exponent):
    z = (1, 0)
    for _ in range(exponent):
        z = z[0] - z[1], z[0] + z[1]
    return z


def witnesses(rank):
    count = 1 << rank
    zero = [(0, 0)] * count
    ones = [(1, 0)] * count
    need(common_member(ones, rank), "constant array membership")
    coordinate_add = ones.copy()
    coordinate_add[0] = (2, 0)
    need(not common_member(coordinate_add, rank), "coordinate ADD rejection")
    local_i = ones.copy()
    local_i[0] = (0, 1)
    need(not common_member(local_i, rank), "local i phase rejection")
    for bit in range(rank):
        half_phase = [(0, 1) if (a >> bit) & 1 else (1, 0)
                      for a in range(count)]
        need(not common_member(half_phase, rank), "half-address phase rejection")
    local_minus = ones.copy()
    local_minus[0] = (-1, 0)
    need(common_member(local_minus, rank) == (rank == 1),
         "local negation rank threshold")
    spike = zero.copy()
    spike[0] = gaussian_power(rank + 1)
    need(common_member(spike, rank), "axial spike membership")
    need(word(spike, rank) == word(spike, rank, literal=True),
         "axial spike literal forward equality")
    u_spike = word(spike, rank)
    need(common_member(u_spike, rank), "axial ideal-image membership")
    need(word(u_spike, rank, inverse=True, literal=True) == spike,
         "axial spike literal inverse equality")
    quantum = 1 << ((rank + 2) // 2)
    quarter_scalar = max(4, quantum)
    quarter_input = zero.copy()
    quarter_input[0] = (quarter_scalar, 0)
    quarter_output = zero.copy()
    quarter_output[0] = (quarter_scalar // 4, 0)
    need(common_member(quarter_input, rank), "quarter entrance membership")
    need(not common_member(quarter_output, rank), "quarter output rejection")
    for exponent in range(rank + 3):
        axial = zero.copy()
        axial[0] = gaussian_power(exponent)
        need(common_member(axial, rank) == (exponent >= rank + 1),
             "axial divisibility threshold")
    return {"coordinate_add_rejected": True, "local_i_rejected": True,
            "half_address_i_phase_rejected": True,
            "local_minus_preserved": rank == 1,
            "integral_quarter_output_rejected": True,
            "quarter_input_scalar": quarter_scalar,
            "quarter_output_scalar": quarter_scalar // 4,
            "axial_uniform_real_quantum": quantum}


def finite_membership_crosscheck(rank, forward, reverse):
    """Cross-check every {0,1} real input at ranks 1 and 2.

    This is a finite exhaustive check of only the stated binary cube,
    not exhaustive membership for the integer lattice.
    """
    size = 2 << rank
    for bits in range(1 << size):
        flat = [(bits >> k) & 1 for k in range(size)]
        x = list(zip(flat[::2], flat[1::2]))
        need(member(x, rank) == modular_member(x, forward, rank),
             "binary-cube forward congruence agreement")
        need(member(x, rank, inverse=True) == modular_member(x, reverse, rank),
             "binary-cube inverse congruence agreement")
        if common_member(x, rank):
            ux = word(x, rank)
            need(common_member(ux, rank), "binary-cube ideal-image membership")
            need(word(x, rank, literal=True) == ux,
                 "binary-cube literal forward equality")
            need(word(ux, rank, inverse=True, literal=True) == x,
                 "binary-cube literal inverse equality")
    return 1 << size


def controls():
    """Defect controls distinguish Gamma, U Gamma, and their intersection."""
    # An exact forward period with nonperiodic ideal image at rank 2.
    rank = 2
    # Search the bounded domain {-2,...,2}^8 until finding a witness.
    # This stops at the first witness; it is not exhaustive coverage.
    witness = None
    for flat in product(range(-2, 3), repeat=8):
        value = list(zip(flat[::2], flat[1::2]))
        if member(value, rank) and not common_member(value, rank):
            witness = value
            break
    need(witness is not None, "forward-only noninvariance witness exists")
    need(not member(word(witness, rank), rank), "forward-only image rejection")
    need(word(word(witness, rank), rank) == list(reversed(witness)),
         "ideal square address complement")
    # Replacing the reverse constraints with a duplicate forward block must
    # give the smaller forward index and fail the independent common index.
    f = congruence_rows(rank)
    b = congruence_rows(rank, inverse=True)
    need(sum(image_factors(f + f, rank)) == 6, "duplicate-forward defect index")
    need(sum(image_factors(f + b, rank)) == 7, "correct common-lattice index")
    # Check modular Smith's output against direct image enumeration on all
    # 256 two-by-two matrices over Z/4 and all 16 inputs for each matrix.
    for entries in product(range(4), repeat=4):
        rows = [entries[:2], entries[2:]]
        direct = {tuple(sum(a * b for a, b in zip(row, value)) % 4
                        for row in rows)
                  for value in product(range(4), repeat=2)}
        need(len(direct) == 1 << sum(image_factors(rows, 2)),
             "modulo-four exhaustive Smith image cardinality")
    # Rank-one state exactness can hold beyond the full period group.
    # Exhaust the stated bounded cube; the unrestricted result is written
    # in INDEPENDENT.md and follows directly from the pair defect formula.
    larger_exactness_cases = 0
    for ar, ai, br, bi in product(range(-2, 3), repeat=4):
        value = [(ar, ai), (br, bi)]
        if ((ar - br) - (ai - bi)) % 2 == 0:
            larger_exactness_cases += 1
            ideal = word(value, 1)
            need(word(value, 1, literal=True) == ideal,
                 "larger rank-one lattice literal forward equality")
            need(word(ideal, 1, inverse=True, literal=True) == value,
                 "larger rank-one lattice literal inverse equality")
            need(((ideal[0][0] - ideal[1][0])
                  - (ideal[0][1] - ideal[1][1])) % 2 == 0,
                 "larger rank-one lattice ideal-image membership")
    need(common_member([(1, 0), (0, 1)], 1) is False,
         "larger rank-one lattice witness outside period lattice")
    need(word([(1, 0), (0, 1)], 1, literal=True) == word([(1, 0), (0, 1)], 1),
         "larger rank-one lattice witness literal equality")
    return {"forward_only_noninvariant_witness": witness,
            "duplicate_forward_defect_index": 6,
            "correct_common_index": 7,
            "mod4_smith_exhaustive_2_by_2_matrices": 256,
            "rank1_larger_exactness_bounded_inputs": larger_exactness_cases,
            "rank1_larger_exactness_witness": [[1, 0], [0, 1]]}


def main():
    result = {"method": "integer-congruence image via modular Smith elimination",
              "rank_domain": [1, 7], "ranks": [], "controls": controls()}
    for rank in range(1, 8):
        forward = congruence_rows(rank)
        reverse = congruence_rows(rank, inverse=True)
        f_factors = image_factors(forward, rank)
        common_factors = image_factors(forward + reverse, rank)
        record = {"rank": rank,
                  "forward_index_log2": sum(f_factors),
                  "common_index_log2": sum(common_factors),
                  "common_quotient_factors": dict(sorted(Counter(common_factors).items())),
                  "witness_checks": witnesses(rank)}
        if rank <= 2:
            record["exhaustive_binary_inputs"] = finite_membership_crosscheck(
                rank, forward, reverse)
        result["ranks"].append(record)
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
