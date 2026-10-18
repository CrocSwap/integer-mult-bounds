#!/usr/bin/env python3
"""Independent finite Gaussian-window length and working-precision check.

Standard library only; no production or sibling verifier imports. This does
not prove the analytic, rounding, tape or multiplication theorems. Written
uniform arguments, source pins and attribution are in INDEPENDENT-REVIEW.md.
Prepared with substantial OpenAI Codex assistance for Effy's research sprint.
"""

from fractions import Fraction as Q
import json
from math import isqrt


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_pair(p, alpha, forward_precision=None, correction_precision=None,
               correction_window=None):
    require(type(p) is int and type(alpha) is int, "integer parameters required")
    require(p >= 101 and alpha >= 2 and alpha * alpha < p, "outside source domain")
    root = isqrt(p)
    m_s = (root + (root * root < p)) * alpha
    # Independent of the main checker's nested ceiling formula: first m
    # whose squared endpoint reaches p is one beyond floor(sqrt(p-1)/(2a)).
    m_e = isqrt(p - 1) // (2 * alpha) + 1
    if correction_window is not None:
        m_e = correction_window
    require((2 * alpha * m_e) ** 2 >= p and
            (2 * alpha * (m_e - 1)) ** 2 < p, "incorrect correction window")
    l_s, l_e = 3 * m_s + 3, 3 * m_e + 1
    gamma_s = (7 * p + 4) // 5
    b = (57 * alpha * alpha + 49) // 50
    log_s, log_e = (l_s - 1).bit_length(), (l_e - 1).bit_length()
    require(l_s < 4 * p and l_e <= p, "input length envelope")
    require(4 * log_s <= p and log_e <= p - 1, "logarithm envelope")
    require(100 * b <= 115 * p, "shifted input magnitude envelope")
    require(m_s < 2 * p and m_e < 2 * p, "window size envelope")
    p_s = 3 * p if forward_precision is None else forward_precision
    p_e = 34 * p if correction_precision is None else correction_precision
    require(gamma_s <= 2 * p_s and 29 * p <= 2 * p_e, "Gamma precondition")
    slack_s = p_s - (p + gamma_s + log_s + 11)
    slack_e = p_e - (p + 29 * p + b + log_e + 11)
    require(slack_s >= 0 and slack_e >= 0, "insufficient sufficient precision")
    return slack_s, slack_e


def must_reject(*args, **kwargs):
    try:
        check_pair(*args, **kwargs)
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def main():
    c = Q(891, 196)
    require(2 * (Q(1, 3) + Q(1, 81)) == Q(56, 81), "log series arithmetic")
    require(c * Q(121, 400) < Q(7, 5), "forward Gamma enclosure")
    require(c * Q(25, 4) < 29, "correction Gamma enclosure")
    require(c / 4 < Q(57, 50), "input scale enclosure")
    for p in range(101, 105):
        require(4 * p <= 2 ** (p // 4 - 1), "four-residue induction endpoint")
    require(Q(53, 20) * 101 + 12 < 3 * 101, "forward uniform endpoint")
    require(Q(1607, 50) * 101 + 11 < 34 * 101, "correction uniform endpoint")

    count = 0
    minimum_s = minimum_e = None
    for p in range(101, 4097):
        for alpha in range(2, isqrt(p - 1) + 1):
            slack_s, slack_e = check_pair(p, alpha)
            candidate_s, candidate_e = (slack_s, p, alpha), (slack_e, p, alpha)
            minimum_s = candidate_s if minimum_s is None else min(minimum_s, candidate_s)
            minimum_e = candidate_e if minimum_e is None else min(minimum_e, candidate_e)
            count += 1
    require(count == 168093, "coverage changed")
    require(minimum_s == (40, 101, 8) and minimum_e == (277, 101, 10),
            "minimum precision slacks changed")

    # Insufficient-P controls reject a sufficient enclosure, not the actual
    # numerical algorithm. The window control must fail its squared endpoint.
    must_reject(100, 2)
    must_reject(121, 11)
    must_reject(101, 8, forward_precision=202)
    must_reject(101, 10, correction_precision=3131)
    must_reject(101, 2, correction_window=2)
    result = {
        "finite_only": True,
        "p_inclusive": [101, 4096],
        "alpha_domain": "2 <= alpha <= floor(sqrt(p-1)); integer",
        "pairs_checked": count,
        "minimum_forward_slack_bits_p_alpha": minimum_s,
        "minimum_correction_slack_bits_p_alpha": minimum_e,
        "negative_controls_rejected": 5,
        "stopping_rule": "complete the fixed integer domain",
    }
    print("PASS_INDEPENDENT_GAUSSIAN_BUDGETS pairs=168093 controls=5")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
