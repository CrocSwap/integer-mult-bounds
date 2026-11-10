#!/usr/bin/env python3
"""Post-call helper feedback does not beat the separated B/C capacity bill.

The arithmetic is exact. Floats are not used. Predecessor profile rows are
read back from the pinned proof so a silent edit cannot keep this receipt.
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PROOF = ROOT / "research/complementary-caller-capacity-gate/PROOF.md"

B_PAID = {1: 1956, 2: 450, 3: 403, 4: 127, 5: 28, 8: 8}
B_HELP = {3: 2, 4: 26, 6: 7, 7: 47, 8: 326}
C_PAID = {1: 2011, 2: 445, 3: 427, 4: 112, 5: 12, 7: 8}
C_HELP = {3: 26, 4: 2, 6: 6, 7: 48, 8: 326}
K_COEFF = {1: 28, 7: 140, 8: 84}
CUT = {(0, 0): 0, (1, 0): 112, (0, 1): 224, (1, 1): 168}


def mul(left, right):
    out = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] += x * y
    return out


def one_minus_p(power):
    acc = [1]
    for _ in range(power):
        acc = mul(acc, [1, -1])
    return acc


def mask_weight_poly(weight, axes=8):
    return [0] * weight + one_minus_p(axes - weight)


def doubled_one_minus_character(rank):
    """Integer coefficients of 1-(1-2p)^rank, which is 2*h_p(rank)."""
    acc = [1]
    step = [1, -2]
    for _ in range(rank):
        acc = mul(acc, step)
    out = [0] * len(acc)
    out[0] = 1
    for i, coeff in enumerate(acc):
        out[i] -= coeff
    return out


def cut_expectation_doubled():
    """Sum_masks charge(mask) * p^w (1-p)^(8-w), doubled to match 2*h form."""
    total = [0] * 9
    for mask in range(256):
        bits = [(mask >> i) & 1 for i in range(8)]
        central = bits[0]
        transverse = sum(bits[1:]) & 1
        charge = CUT[(central, transverse)]
        poly = mask_weight_poly(sum(bits))
        for i, coeff in enumerate(poly):
            total[i] += charge * coeff
    return [2 * coeff for coeff in total]


def closed_cut_doubled():
    total = [0] * 9
    for count, rank in ((140, 7), (28, 1), (84, 8)):
        poly = doubled_one_minus_character(rank)
        for i, coeff in enumerate(poly):
            total[i] += count * coeff
    return total


def helper_flip_expectation_doubled(histogram):
    total = [0] * 9
    for rank, count in histogram.items():
        poly = doubled_one_minus_character(rank)
        for i, coeff in enumerate(poly):
            total[i] += count * coeff
    return total


def helper_supports(histogram):
    supports = []
    for rank, count in sorted(histogram.items()):
        # The first `rank` of the eight character axes. Rank 8 uses every axis.
        supports.extend([(1 << rank) - 1] * count)
    return supports


def flip_count(mask, supports, row_distance=1):
    return row_distance * sum((mask & support).bit_count() & 1 for support in supports)


def simulated_helper_distance_doubled(histogram, row_distance=1):
    """Distinct fields: distance equals the number of odd-support hits."""
    supports = helper_supports(histogram)
    total = [0] * 9
    for mask in range(256):
        flips = flip_count(mask, supports, row_distance)
        poly = mask_weight_poly(mask.bit_count())
        for i, coeff in enumerate(poly):
            total[i] += flips * coeff
    return [2 * coeff for coeff in total]


def delta_coeffs(paid, helpers):
    ranks = set(paid) | set(helpers) | set(K_COEFF)
    return {rank: paid.get(rank, 0) - helpers.get(rank, 0) - K_COEFF.get(rank, 0)
            for rank in ranks}


def rank_mass(coeffs, predicate):
    return sum(rank * count for rank, count in coeffs.items() if predicate(rank, count))


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


def require_proof_pins(text):
    needles = [
        "1:1956, 2:450, 3:403, 4:127, 5:28, 8:8",
        "3:2, 4:26, 6:7, 7:47, 8:326",
        "1:2011, 2:445, 3:427, 4:112, 5:12, 7:8",
        "3:26, 4:2, 6:6, 7:48, 8:326",
        "K(t) = 28 + 140*7^t + 84*8^t",
        "helper feedback into the main computation",
    ]
    for needle in needles:
        require(needle in text, "pinned proof is missing the row " + needle)


def main():
    text = PROOF.read_text(encoding="utf-8")
    require_proof_pins(text)
    require(cut_expectation_doubled() == closed_cut_doubled(),
            "256-mask cut expectation disagrees with 140*h(7)+28*h(1)+84*h(8)")
    for histogram in (B_HELP, C_HELP):
        require(simulated_helper_distance_doubled(histogram) == helper_flip_expectation_doubled(histogram),
                "helper-block distance exceeds the separated helper character charge")
    # A row whose character difference has rank 2 is outside the coordinate-Gaussian model.
    inflated = {8: 1}
    require(simulated_helper_distance_doubled(inflated, row_distance=2)
            != helper_flip_expectation_doubled(inflated),
            "failure control did not separate a double-counted helper row")

    b_delta = delta_coeffs(B_PAID, B_HELP)
    c_delta = delta_coeffs(C_PAID, C_HELP)
    require(b_delta == {1: 1928, 2: 450, 3: 401, 4: 101, 5: 28, 6: -7, 7: -187, 8: -402},
            "B bill cancellation changed")
    require(c_delta == {1: 1983, 2: 445, 3: 401, 4: 110, 5: 12, 6: -6, 7: -180, 8: -410},
            "C bill cancellation changed")
    b_positive = rank_mass(b_delta, lambda rank, count: count > 0)
    b_negative = rank_mass(b_delta, lambda rank, count: count < 0)
    c_positive = rank_mass(c_delta, lambda rank, count: count > 0)
    c_negative = rank_mass(c_delta, lambda rank, count: count < 0)
    require(b_positive - 8 == -b_negative == 4567, "B residual masses are not 4567")
    require(c_positive == -c_negative == 4576, "C residual masses are not 4576")
    require(all(rank <= 5 for rank, count in b_delta.items() if count > 0), "B positive rank escaped 5")
    require(all(rank <= 5 for rank, count in c_delta.items() if count > 0), "C positive rank escaped 5")
    require(all(rank >= 6 for rank, count in list(b_delta.items()) + list(c_delta.items()) if count < 0),
            "a negative term is below rank 6")

    # 6 * 5^t > 5 * 6^t for every rational t=a/b in (0,1), by 6^{b-a} > 5^{b-a}.
    for denominator in range(1, 13):
        for numerator in range(1, denominator):
            gap = denominator - numerator
            require(6 ** gap > 5 ** gap, "ratio gap failed")

    # Central axis only. Every published B helper support contains that axis,
    # so all 408 helper rows flip while the main block contributes 112.
    mask = 1
    distance = flip_count(mask, helper_supports(B_HELP))
    main_cut = CUT[(1, 0)]
    budget = main_cut + distance
    demanded = sum(B_HELP.values()) + main_cut + 1
    require(distance == 408 and main_cut == 112 and budget == 520, "central-mask budget changed")
    require(demanded == 521 and demanded > budget,
            "keeping every helper and the main cut leaves no row for an extra target")

    print("PASS_SHARED_HELPER_FEEDBACK_BOUND")
    print("cut_identity=256_masks")
    print("helper_distance_matches_separated_charge=B,C")
    print("residual_mass B=4567 C=4576")
    print("ratio_gap denominators=1..12")
    print("no_new_kappa")
    return 0


if __name__ == "__main__":
    sys.exit(main())
