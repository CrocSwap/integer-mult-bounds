"""BIT supplier screen under the current productive-helper invoice (#4440/#4470 query-thinned controllers).
Same formulas as research/bit-ambient-quotient/verify.py (PR4633), which reproduces the frontier BIT kappa
0.003464248972 from PR589's local bill; here the helper count R and the local paid profile are parameters."""
from collections import Counter

STAGES, CALLS, SPLIT, PORTS, BLOCK = 16, 18, 7, 111, 7
TAIL_OFFSET, CUTOFF, TARGET_GAMMA = 0.2, 20.0, 0.97


def moment(profile, exponent):
    return sum(n * (r ** exponent) for r, n in profile.items() if n and r > 0)


def dual_ok(T, P, kappa, u=TAIL_OFFSET, c=CUTOFF, gamma=TARGET_GAMMA):
    t = 1.0 - kappa
    return moment(P, t) < moment(T, t) and moment(P, t + u) < gamma * (c ** u) * moment(T, t)


def admissible_kappa(T, P, lo=1e-7, hi=0.25, steps=2400):
    best = None
    prev = None
    for i in range(steps + 1):
        k = lo + (hi - lo) * i / steps
        if dual_ok(T, P, k):
            best, prev = k, k
        elif prev is not None and best == prev:
            a, b = prev, k
            for _ in range(90):
                mid = (a + b) / 2
                if dual_ok(T, P, mid):
                    a = mid
                else:
                    b = mid
            return a
    return best


def invoice(helper_widths, paid_profile, ports=PORTS):
    targets = Counter({r: CALLS * n for r, n in helper_widths.items()})
    paid = Counter({r: CALLS * n for r, n in paid_profile.items()})
    paid[1] += ports * (2 * STAGES + 1 - CALLS)
    targets[1 + BLOCK * (STAGES + 2)] += 2 * ports
    for length in (SPLIT, STAGES - 1 - SPLIT):
        for j in range(1, length + 1):
            targets[1 + BLOCK * (j + 1)] += 2 * ports
            paid[BLOCK * (j + 1)] += 2 * ports
    return targets, paid


def bit_kappa(R, profile, ports=PORTS):
    T, P = invoice({8: R}, Counter(profile), ports)
    return admissible_kappa(T, P)


if __name__ == "__main__":
    tuned = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
    untuned = {1: 1321, 2: 1342, 3: 80, 4: 47, 5: 102, 6: 10, 7: 18}
    print("PR589 tuned   R439", bit_kappa(439, tuned))
    print("PR555 untuned R439", bit_kappa(439, untuned))
    p = dict(tuned); p[1] += 8
    print("tuned + one helper paid as 8 rank-1 pieces", bit_kappa(440, p))
    p = dict(tuned); p[7] += 1; p[1] += 1
    print("tuned + one helper paid as 7+1", bit_kappa(440, p))
    p = dict(tuned); p[1] -= 8
    print("tuned - 8 rank-1 (R same)", bit_kappa(439, p))
