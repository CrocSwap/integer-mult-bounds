#!/usr/bin/env python3
"""Independent exact replay of the alternating full-histogram recurrence.

Uses only stdlib integers/Fraction; imports no package or predecessor code.
The finite replay supports, and does not replace, REVIEW.md's all-depth proof.
"""

from fractions import Fraction as F
from itertools import product
from math import isqrt


M = 256
W = 1
PROFILES = {"A": {16: 1, 1: 2}, "B": {16: 4, 1: 32}}
ROOTS = {"A": F(1, 4), "B": F(3, 4)}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def nth_root_exact(n, d):
    lo, hi = 0, n + 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if mid**d <= n:
            lo = mid
        else:
            hi = mid
    require(lo**d == n, "nonrational exact power requested")
    return lo


def exact_power(q, p):
    q, p = F(q), F(p)
    return F(nth_root_exact(q.numerator, p.denominator),
             nth_root_exact(q.denominator, p.denominator)) ** p.numerator


def moment(name, p):
    return sum((F(n, W) * exact_power(F(r, M), p)
                for r, n in PROFILES[name].items()), F(0))


def step(rank):
    require(M % rank == 0, "rank must divide ambient width")
    denominator = M // rank
    count = 0
    while denominator > 1 and denominator % 16 == 0:
        denominator //= 16
        count += 1
    require(denominator == 1 and count > 0, "off-grid child ratio")
    return count


def recurrence(schedule, profiles=PROFILES):
    values = [F(1)]
    for index, name in enumerate(schedule, start=1):
        values.append(sum((F(n, W) * (values[index - step(r)]
                                      if index - step(r) > 0 else F(1))
                           for r, n in profiles[name].items()), F(0)))
    return values


def enumerate_histories(schedule):
    """Enumerate every distinct rank history, retaining its multiplicity weight."""
    pending = [(len(schedule), F(1), ())]
    total, leaves = F(0), 0
    while pending:
        index, weight, history = pending.pop()
        if index <= 0:
            require(len(history) <= len(schedule), "nondecreasing history")
            total += weight
            leaves += 1
            continue
        for rank, count in PROFILES[schedule[index - 1]].items():
            pending.append((index - step(rank), weight * F(count, W),
                            history + ((index, rank),)))
    return total, leaves


def periodic_schedule(n, swap=False):
    return tuple(("B" if i % 2 else "A") if swap else
                 ("A" if i % 2 else "B") for i in range(1, n + 1))


def matrix_product(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                       for j in range(2)) for i in range(2))


def characteristic(value):
    return value * value - 38 * value + 64


def main():
    for name, root in ROOTS.items():
        require(moment(name, root) == 1, "full-histogram seed root")
    require(sum(ROOTS.values()) / 2 == F(1, 2), "arithmetic root average")

    # All binary rank histories for the specified periodic schedule, n <= 20.
    periodic_histories = 0
    for n in range(21):
        schedule = periodic_schedule(n)
        expanded, leaves = enumerate_histories(schedule)
        require(expanded == recurrence(schedule)[-1], "periodic history mismatch")
        periodic_histories += leaves

    # All index-wise schedules through length 9, including every history in each.
    schedules, arbitrary_histories = 0, 0
    for n in range(10):
        for schedule in product(("A", "B"), repeat=n):
            values = recurrence(schedule)
            expanded, leaves = enumerate_histories(schedule)
            require(expanded == values[-1], "arbitrary history mismatch")
            for i, value in enumerate(values):
                # q_min=1/256, alpha=1/4, beta=3/4.
                require(F(2)**i <= value <= 64 * F(8)**i,
                        "finite-catalogue comparison bound")
            schedules += 1
            arbitrary_histories += leaves

    a = ((1, 2), (1, 0))
    b = ((4, 32), (1, 0))
    pair = matrix_product(b, a)
    require(pair == ((36, 8), (1, 2)), "ordered two-level matrix")
    require(pair[0][0] + pair[1][1] == 38, "matrix trace")
    require(pair[0][0] * pair[1][1] - pair[0][1] * pair[1][0] == 64,
            "matrix determinant")

    values = recurrence(periodic_schedule(120))
    require(values[:6] == [1, 3, 44, 50, 1608, 1708], "boundary/phase values")
    for parity in (0, 1):
        sequence = values[parity::2]
        for k in range(2, len(sequence)):
            require(sequence[k] == 38 * sequence[k - 1] - 64 * sequence[k - 2],
                    "two-level scalar recurrence")
    for k in range(61):
        require(values[2 * k] >= F(32)**k, "positive subeigenvector bound")
        require(values[2 * k] / F(16)**k >= F(2)**k,
                "unbounded error from root-only averaging")

    # The Perron root lies between these rationals, by monotonicity above 19.
    lower, upper = F(36233, 1000), F(36234, 1000)
    require(characteristic(lower) < 0 < characteristic(upper), "root bracket")
    require(32 < lower < upper < 37, "strict exponent comparison")
    require(37**3 < 256**2, "p_eff < 2/3")
    # A second, unrelated exact square-root enclosure verifies the closed form.
    denominator = 2**128
    root_floor = isqrt(33 * denominator**2)
    lambda_lo = F(19 * denominator + 3 * root_floor, denominator)
    lambda_hi = F(19 * denominator + 3 * (root_floor + 1), denominator)
    require(lower < lambda_lo < lambda_hi < upper, "closed-form root enclosure")

    # Positive phase moment matrix at p=1/2 has Perron root 17/8, not 1.
    t = F(1, 4)
    phase_moment = ((32 * t**2, 4 * t), (t, 2 * t**2))
    det_i_minus = ((1 - phase_moment[0][0]) * (1 - phase_moment[1][1])
                   - phase_moment[0][1] * phase_moment[1][0])
    require(det_i_minus == 1 - 38 * t**2 + 64 * t**4 == F(-9, 8),
            "periodic moment equation")
    require(phase_moment[0][0] * phase_moment[1][1]
            == phase_moment[0][1] * phase_moment[1][0], "rank-one moment control")
    require(phase_moment[0][0] + phase_moment[1][1] == F(17, 8),
            "wrong averaged-root Perron value")

    # Semantic controls must be observably rejected by a full-data comparison.
    lost_rank = {name: {16: profile[16]} for name, profile in PROFILES.items()}
    lost = recurrence(periodic_schedule(20), lost_rank)
    require(lost != values[:21] and lost[2] == 4 and values[2] == 44,
            "lost-rank control was not detected")
    reversed_phase = recurrence(periodic_schedule(20, swap=True))
    require(reversed_phase != values[:21] and reversed_phase[1] == 36,
            "wrong-phase control was not detected")
    require(matrix_product(a, b) != pair,
            "wrong-phase matrix control was not detected")
    root_only = [F(4)**i for i in range(21)]
    require(root_only != values[:21] and root_only[2] == 16,
            "root-only averaging control was not detected")

    print("PASS_INDEPENDENT_SCALE_DEPENDENT_MOMENT_AUDIT")
    print(f"periodic_indices=0..20; complete_rank_histories={periodic_histories}")
    print(f"all_schedules_length=0..9; schedules={schedules}; "
          f"complete_rank_histories={arbitrary_histories}")
    print("matrix_replay_indices=0..120; semantic_controls=3/3")
    print("lambda=19+3*sqrt(33); 36233/1000 < lambda < 36234/1000")
    print("p_eff=log_256(lambda); 5/8 < p_eff < 2/3; averaged_p=1/2")


if __name__ == "__main__":
    main()
