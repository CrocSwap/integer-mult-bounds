#!/usr/bin/env python3
"""Exact check of the one-axis shared-arena CRT bound.

The argument is PROOF.md. Every comparison below is an integer identity or
an induction with an explicit base. No new kappa is claimed.
"""

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
EVALUATOR = ROOT / "research" / "crt-uniform-evaluator" / "PROOF.md"
EVALUATOR_README = ROOT / "research" / "crt-uniform-evaluator" / "README.md"
VENDOR = PACKAGE / "vendor" / "pr4192-crt-benes-scan-PROOF.md"
VENDOR_SHA256 = "c3eb4e14dc5ee0102cbf77c4a0e61db9989c2b8a0eaf7f0659a6e39373197474"
CORNER_U = 38809248652
CORNER_E = 1099511627776
BATCH_U = 1241895956864


def need(condition, message):
    if not condition:
        raise ValueError(message)


def census(h):
    width = 1 << h
    records = width * (h * h + 3 * h + 1)
    accesses = width * width + 2 * width * h * h + 24 * width * h + 3 * width
    return width, records, accesses


def direct_charge(q, h, ell, networks=4, axes=1):
    """One-axis bill, then an optional batch of identical axes."""
    word = 4 * q
    width, records, accesses = census(h)
    tape = (
        accesses * (26 * word * records + 25 * word)
        + 30 * word * records
        + 3 * width * h
        + 6 * (2 * h - 1) * width
        + 3
    )
    scalar = tape * 8 * word * word
    rotation = 9 * (ell + 2) * (ell + 2) * width
    reconstruction = 65536 * q ** 3 + 1024 * q * ell ** 3 + 1024 * q * q
    return axes * (reconstruction + networks * (rotation + tape + scalar))


def allowance(q, ell):
    return (1 << (4 * ell)) * q ** 16


def polynomial_charge(q, h):
    """Same bill at ell = h, expanded as a cubic polynomial in q."""
    width, records, accesses = census(h)
    tape_linear = 4 * (accesses * (26 * records + 25) + 30 * records)
    tape_constant = 3 * width * h + 6 * (2 * h - 1) * width + 3
    rotation = 9 * (h + 2) * (h + 2) * width
    cubic = 512 * tape_linear + 65536
    quadratic = 512 * tape_constant + 1024
    linear = 4 * tape_linear + 1024 * (h ** 3)
    constant = 4 * rotation + 4 * tape_constant
    return (
        cubic * q ** 3
        + quadratic * q ** 2
        + linear * q
        + constant,
        cubic,
        quadratic,
        linear,
        constant,
    )


def bind_sources():
    evaluator = EVALUATOR.read_text(encoding="utf-8")
    readme = EVALUATOR_README.read_text(encoding="utf-8")
    vendor_bytes = VENDOR.read_bytes()
    need(hashlib.sha256(vendor_bytes).hexdigest() == VENDOR_SHA256, "vendor hash")
    need(len(vendor_bytes) == 12953, "vendor length")
    vendor = vendor_bytes.decode("utf-8")
    for needle in (
        "65536 q^3 + 1024 q ell^3 + 1024 q^2",
        "9(ell + 2)^2",
        "In every case the total is at most `8ab`.",
        "524288 q^4 + 8192 q^2 ell^3 + 8192 q^3",
    ):
        need(needle in evaluator, "evaluator sentence " + needle)
    need(
        "Replay one root-axis query on a single arena, in the sense of PR #4192,"
        in readme,
        "open-question sentence",
    )
    for needle in (
        "each field w=4p+8 bits.",
        "J = N(h²+3h+1) records,",
        "B = 5wJ arena cells.",
        "26wJ + 25w read/write/one-cell-head actions.",
        "erasure/returns add `6B`.",
        "protected input read/return costs `3Nh`",
        "Owned network writing/return costs `3(2h-1)N`.",
        "costs exactly `3(2h-1)N+3` tape actions.",
        "A <= N² + 2Nh² + 24Nh + 3N",
    ):
        need(needle in vendor, "arena sentence " + needle)
    dropped = vendor.replace("26wJ + 25w", "26wJ + 24w")
    need("26wJ + 25w read/write/one-cell-head actions." not in dropped, "binder control")


def prove_schoolbook_cap():
    """A w-bit by w-bit schoolbook product is at most 8 w^2 bit-steps for w >= 1."""
    # Touch formula from the pinned evaluator: 3ab + 3a + b.
    # At a = b = w this is 3w^2 + 4w, and 3w^2 + 4w <= 8w^2 iff 4 <= 5w.
    need(4 <= 5 * 1, "schoolbook at w=1")
    need(not (4 <= 5 * 0), "w=0 is outside the tariff")


def prove_census_bounds():
    """A <= 16 N^2, J <= 5 N h^2, and the tail comparisons, for every h >= 1."""
    # poly(h) = 2h^2 + 24h + 3. A = N^2 + N poly(h), N = 2^h.
    # A <= 16 N^2 iff poly(h) <= 15 N.
    # Expansion: poly(h+1) - poly(h) = 4h + 26.
    # 2(h+1)^2 - 2h^2 = 4h + 2 and 24(h+1) - 24h = 24, sum 4h + 26.
    need(4 + 2 + 24 == 4 + 26, "poly step coefficients")
    need(2 * 1 + 24 * 1 + 3 <= 15 * 2, "A bound h=1")
    need(2 * 4 + 24 * 2 + 3 <= 15 * 4, "A bound h=2")
    need(2 * 9 + 24 * 3 + 3 <= 15 * 8, "A bound h=3")
    # Auxiliary: 4h + 26 <= 15 * 2^h for h >= 3, by the base and
    # 4(h+1)+26 = 4h+30 <= 15*2^h + 4 <= 30*2^h once 4 <= 15*2^h.
    need(4 * 3 + 26 <= 15 * 8, "auxiliary base h=3")
    need(4 <= 15 * 2, "auxiliary increment")
    # J = N(h^2+3h+1) <= 5 N h^2 iff (h-1)(4h+1) >= 0.
    # (h-1)(4h+1) = 4h^2 - 3h - 1.
    need(4 - 3 - 1 == 0, "J discriminant at h=1")
    # 15 h <= 16 * 4^h for h >= 1. Base 15 <= 64.
    # 15(h+1) <= 16*4^h + 15 <= 64*4^h once 15 <= 48*4^h.
    need(15 <= 16 * 4, "width induction base")
    need(15 <= 48 * 4, "width induction increment")
    # Exact displayed census is at most the convenient bound:
    # (37h-35)/2 <= 24h+3 iff 0 <= 11h+41.
    need(11 * 1 + 41 > 0, "census domination")
    # J >= 10 and A >= 4 at the minimum h = 1, N = 2.
    width, records, accesses = census(1)
    need(records == 10 and accesses >= 4 and width == 2, "minimum census")


def prove_charge_constants():
    need(8 * 16 == 128, "scalar factor 8 w^2 = 128 q^2")
    need(129 * 37 * 4 == 19092, "one-network coefficient")
    need(4 * 19092 == 76368, "four-network coefficient")
    need(16 * 5 == 80, "access-record product")
    need(76368 * 80 == 6109440, "majorant coefficient")
    need(1024 + 16384 + 64 == 17472, "reconstruction coefficient")
    need(65536 == 16384 * 4, "cubic CRT term at q=4")
    need(1024 == 64 * 16, "quadratic CRT term at q=4")
    need(4 * 9 == 36, "four rotation tables")
    # Leading arena term 8 w^2 * A * (26 w J) equals (3328/5) A B q^2.
    need(8 * 16 * 26 == 3328, "leading coefficient")
    need(5 * 4 == 20, "B = 5 w J and w = 4q give 20 q J")


def prove_allowance_majorant():
    """For h >= 2 and q >= h+2, the majorant is at most 2^{4h} q^{16}."""
    # Split the majorant into three terms, each at most one third of the
    # allowance. The first two are smallest at N = 4, q = 4.
    need(3 * 17472 == 52416, "term one multiplier")
    need(3 * 36 == 108, "term two multiplier")
    need(3 * 6109440 == 18328320, "term three multiplier")
    need(52416 <= (1 << 32), "term one at N=4, q=4")
    need(108 <= (1 << 34), "term two at N=4, q=4")
    # Term three: 18328320 h^2 <= 2^h (h+2)^13 for every h >= 2.
    need(18328320 * 4 <= (1 << 2) * (4 ** 13), "term three h=2")
    need(18328320 * 9 <= (1 << 3) * (5 ** 13), "term three h=3")
    need(18328320 <= 6 ** 13, "term three h=4, where r(4) = 6^13")
    # For h >= 4, r(h) = 2^h (h+2)^13 / h^2 is strictly increasing because
    # r(h+1)/r(h) >= 2 (h/(h+1))^2 >= 32/25 > 1.
    need(5 * 4 >= 4 * (4 + 1), "h/(h+1) >= 4/5 at h=4")
    need(32 > 25, "32/25 > 1")


def prove_h1_cubic():
    """At h = ell = 1 and every q >= 4, U <= (sum of coefficients) q^3 <= E."""
    value, cubic, quadratic, linear, constant = polynomial_charge(4, 1)
    coefficient_sum = cubic + quadratic + linear + constant
    need(coefficient_sum == 37169148, "h=1 coefficient sum")
    need(value == direct_charge(4, 1, 1), "h=1 polynomial agrees")
    need(coefficient_sum <= 16 * (4 ** 13), "h=1 against 16 q^13 at q=4")
    for q in (4, 5, 9, 16):
        charged, *_rest = polynomial_charge(q, 1)
        need(charged == direct_charge(q, 1, 1), "h=1 agreement " + str(q))
        need(charged <= allowance(q, 1), "h=1 allowance " + str(q))


def prove_ell_step():
    """Raising ell by one multiplies the exact bill by less than 16."""
    # For ell >= 1, ell(ell-1) >= 0 and ell^2(ell-1) >= 0, so
    # ell^2 >= ell and ell^3 >= ell^2 >= 1. Thus
    # 3 ell^2 + 3 ell + 1 <= 7 ell^3, and
    # (ell+1)^3 - 16 ell^3 <= -8 ell^3 < 0.
    need(3 + 3 + 1 == 7, "cubic ell absorption")
    for ell in (1, 2, 5):
        need(ell * (ell - 1) >= 0, "ell squared")
        need((ell + 1) ** 3 - 16 * ell ** 3 <= -8 * ell ** 3, "ell cubic drop")
        need((ell + 3) ** 2 - 16 * (ell + 2) ** 2 < 0, "ell rotation drop")
    for h in (1, 2, 4):
        for ell in (h, h + 2):
            q = max(4, ell + 2)
            need(
                direct_charge(q, h, ell + 1) < 16 * direct_charge(q, h, ell),
                "ell step " + str((q, h, ell)),
            )


def prove_corner_and_batch():
    corner = direct_charge(4, 2, 2)
    bound = allowance(4, 2)
    need(corner == CORNER_U, "corner witness")
    need(bound == CORNER_E, "corner allowance")
    need(28 * corner <= bound < 29 * corner, "corner factor")
    need(bound // corner == 28, "corner quotient")
    batch = direct_charge(4, 2, 2, networks=4, axes=32)
    need(batch == BATCH_U, "batch witness")
    need(batch > bound, "full axis batch exceeds this majorant")
    # The predecessor's all-axis CRT display is the one-axis bill times 8q.
    one_axis_crt = 65536 * 4 ** 3 + 1024 * 4 * 8 + 1024 * 16
    eight_q = 32
    displayed = 524288 * 4 ** 4 + 8192 * 16 * 8 + 8192 * 4 ** 3
    need(eight_q * one_axis_crt == displayed, "CRT bill scales by 8q")


def prove_grid():
    worst_ratio = None
    worst_at = None
    for h in range(1, 9):
        for ell in range(h, h + 4):
            for q in range(max(4, ell + 2), max(4, ell + 2) + 4):
                charged = direct_charge(q, h, ell)
                bound = allowance(q, ell)
                need(charged <= bound, "grid " + str((q, h, ell)))
                if h >= 2 and ell == h:
                    width = 1 << h
                    majorant = (
                        17472 * q ** 4
                        + 36 * q * q * width
                        + 6109440 * q ** 3 * width ** 3 * h * h
                    )
                    need(charged <= majorant <= bound, "majorant " + str((q, h)))
                if ell == h:
                    ratio = (charged, bound)
                    if worst_ratio is None or charged * worst_ratio[1] > worst_ratio[0] * bound:
                        worst_ratio = ratio
                        worst_at = (q, h)
                polynomial, *_rest = polynomial_charge(q, h)
                need(polynomial == direct_charge(q, h, h), "polynomial " + str((q, h)))
    need(worst_at == (4, 2), "grid maximum " + str(worst_at))


def main():
    bind_sources()
    prove_schoolbook_cap()
    prove_census_bounds()
    prove_charge_constants()
    prove_allowance_majorant()
    prove_h1_cubic()
    prove_ell_step()
    prove_corner_and_batch()
    prove_grid()
    print(
        "PASS_CRT_ARENA_ROOT_AXIS"
        " four_networks=true"
        " corner_U=38809248652"
        " corner_E=1099511627776"
        " corner_quotient=28"
        " batch_U=1241895956864"
        " batch_exceeds=true"
        " no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
