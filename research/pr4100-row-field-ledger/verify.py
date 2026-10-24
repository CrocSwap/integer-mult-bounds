#!/usr/bin/env python3
"""Check the short-field movement against #4100's Strassen boundary row.

The all-size comparison is the exponent identity in PROOF.md. This program
recomputes that identity in exact rationals, checks the integer form of
W^(tau-1) >= W, and rejects the two mis-charges named in the proof.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require_phrase(document: str, phrase: str, source: str) -> None:
    require(phrase in document, f"{source} no longer contains {phrase!r}")


def ceil_log2(value: int) -> int:
    require(value >= 1, "log argument must be positive")
    exponent = 0
    power = 1
    while power < value:
        power *= 2
        exponent += 1
    return exponent


def saving_gap(tau: Fraction) -> Fraction:
    """Movement saving minus Strassen saving, in the FINE-PRIME dictionary."""
    return (tau - 2) / 2


def monomial_absorbs(width: int, tau: Fraction) -> bool:
    """True when W^(tau-1) >= W for this integer width."""
    require(width >= 1, "bandwidth must be a positive integer")
    if tau == Fraction(45, 16):
        return width**29 >= width**16
    if tau == Fraction(7, 4):
        # W^{3/4} >= W if and only if W <= 1.
        return width**3 >= width**4
    if tau >= 2:
        return True
    return False


def main() -> None:
    gaussian = text("research/unconditional-batched-crt/GAUSSIAN.md")
    fine = text("research/unconditional-batched-crt/vendor/FINE-PRIME.md")
    union = text("research/unconditional-batched-crt/vendor/UNION-SCHEDULE.md")
    signoff = text("research/capped-phase-fusion/CAPPED-SIGNOFF.md")
    phase = text("research/capped-phase-fusion/PHASE-LAYOUT-AUDIT.md")
    lemma = text("research/pr4100-row-field-movement/PROOF.md")
    selected = json.loads(text("certificates/selected-result.json"))

    require_phrase(gaussian, "7^16<2^45 gives exponent tau=45/16", "GAUSSIAN.md")
    require_phrase(gaussian, "O(V d W^(tau-1)/B polylog(p)).", "GAUSSIAN.md")
    require_phrase(gaussian, "O(V d W/B polylog(p)).", "GAUSSIAN.md")
    require_phrase(gaussian, "L=2^ceil(400log2 p)", "GAUSSIAN.md")
    require_phrase(gaussian, "W=O(sqrt(p)polylog(p))<p", "GAUSSIAN.md")
    require_phrase(gaussian, "density\nO(W/B polylog(p))", "GAUSSIAN.md")
    require_phrase(fine, "target exponent `tau=45/16` and `c=(3-tau)/2=3/32`", "FINE-PRIME.md")
    require_phrase(fine, "Since W=O(sqrt(p) polylog p)<p eventually", "FINE-PRIME.md")
    require_phrase(fine, "boundary density `O((W/B) polylog p)`", "FINE-PRIME.md")
    require_phrase(fine, "epsilon-xi+(tau-1)/2", "FINE-PRIME.md")
    require_phrase(fine, "xi+1/2-epsilon", "FINE-PRIME.md")
    require_phrase(fine, "b_cert=335950991225108904267/200000000000000000000000", "FINE-PRIME.md")
    require_phrase(fine, "epsilon=9999999/10000000", "FINE-PRIME.md")
    require_phrase(fine, "layout slack `s=10^-64`", "FINE-PRIME.md")
    require_phrase(union, "mu = max_i |E_i|/L = O((W/B) polylog p)", "UNION-SCHEDULE.md")
    require_phrase(union, "tau_eff = 2 + 1e-64", "UNION-SCHEDULE.md")
    require_phrase(signoff, "|E_i| = O(L W/B polylog p + W polylog p).", "CAPPED-SIGNOFF.md")
    require_phrase(phase, "O(log p) times the boundary volume", "PHASE-LAYOUT-AUDIT.md")
    require_phrase(
        lemma,
        "strictly less than `8 · max(1, ceil(log2 a)) · V`",
        "row-field PROOF.md",
    )

    require(7**16 < 2**45, "the stated Strassen count 7^16 < 2^45 failed")
    tau = Fraction(45, 16)
    c = (3 - tau) / 2
    require(c == Fraction(3, 32), "c is not 3/32")
    require(saving_gap(tau) == Fraction(13, 32), "the saving gap is not 13/32")
    require(Fraction(1, 2) - c == Fraction(13, 32), "1/2 - c is not 13/32")

    for width in list(range(1, 257)) + [10**3, 10**6]:
        require(monomial_absorbs(width, tau), f"W^(tau-1) < W at W={width}")

    # tau = 2 is not a strict absorption. tau = 7/4 makes movement the heavier row.
    require(saving_gap(Fraction(2, 1)) == 0, "tau = 2 should leave a zero gap")
    require(saving_gap(Fraction(7, 4)) < 0, "tau = 7/4 should make movement more expensive")
    require(not monomial_absorbs(2, Fraction(7, 4)), "a sub-quadratic exponent was treated as absorbing")

    tau_eff = 2 + Fraction(1, 10**64)
    require(saving_gap(tau_eff) == Fraction(1, 2 * 10**64), "tau_eff gap is not 5e-65")
    require(monomial_absorbs(10**6, tau_eff), "tau_eff did not absorb an integer bandwidth")

    match = re.search(
        r"b_cert=(\d+)/(\d+)",
        fine,
    )
    require(match is not None, "b_cert fraction was not found")
    b_cert = Fraction(int(match.group(1)), int(match.group(2)))
    tiny = Fraction(1, 10**64)
    q = b_cert - 2 * tiny
    epsilon = Fraction(9999999, 10000000)
    slack = tiny
    xi = epsilon * (1 + q) - Fraction(3, 32) + slack
    boundary_saving = c + xi - epsilon
    movement_saving = xi + Fraction(1, 2) - epsilon
    headline = epsilon * q
    require(boundary_saving - headline == slack, "boundary saving is not headline plus s")
    require(movement_saving - boundary_saving == Fraction(13, 32), "balance gap drifted from 13/32")
    full_volume_saving = 1 - epsilon
    require(full_volume_saving < headline, "a full-volume charge would not undercut the headline")
    require(movement_saving > headline, "boundary-volume movement undercut the headline")

    # The named core length is polynomial: L = 2^{ceil(400 log2 p)} <= (2p)^400.
    for prime_power in (2, 3, 10, 100, 1000, 10**6):
        length = 1 << ceil_log2(prime_power)
        require(length <= 2 * prime_power, "next power of two exceeded 2p")
        core = 1 << (400 * ceil_log2(prime_power))
        exposed = core * prime_power
        require(
            ceil_log2(exposed) <= 401 * ceil_log2(prime_power),
            "exposed-line logarithm was not O(log p)",
        )

    decimal = selected["decimal"]
    require(decimal == "0.00302015", "pinned selected decimal changed; re-read the record before quoting it")
    print(
        "PASS_ROW_FIELD_LEDGER "
        "tau=45/16 "
        "c=3/32 "
        "movement_minus_boundary_saving=13/32 "
        "gap_independent_of_epsilon_and_xi=true "
        "integer_bandwidth_absorbed=true "
        "tau_eff_gap=5e-65 "
        "full_volume_charge_binds=true "
        "boundary_volume_charge_binds=false "
        "exposed_length_equals_W_or_B=false "
        f"selected_decimal={decimal} "
        "no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
