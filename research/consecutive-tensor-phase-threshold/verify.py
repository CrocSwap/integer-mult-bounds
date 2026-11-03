"""Exact corroboration of the consecutive tensor-power phase threshold.

For a unitary U = A*B with eigenphase 2*pi*phi, the width-j defect of the
scalar pair is |1 - exp(2*pi*i*j*phi)|; it is at most eps = 2 sin(pi*alpha)
exactly when ||j*phi|| <= alpha, where ||.|| is the distance to the nearest
integer. PROOF.md reduces arbitrary unitaries to this scalar problem.

This checker computes the exact sublevel set
    S_k(alpha) = {phi in [0, 1/2] : ||j*phi|| <= alpha for j = 2..k}
as a finite union of closed rational intervals and checks the theorem's
threshold, jump point and small branch for k = 3..K_MAX. Standard library only.
"""
from fractions import Fraction as F
import sys

STATUS = 'PASS_CONSECUTIVE_TENSOR_PHASE_THRESHOLD'
K_MAX = 64
HALF = F(1, 2)


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def width_set(j, alpha):
    """{phi in [0,1/2] : ||j phi|| <= alpha} as sorted disjoint closed intervals."""
    out = []
    for n in range(0, j // 2 + 2):
        lo, hi = max(F(0), (n - alpha) / j), min(HALF, (n + alpha) / j)
        if lo <= hi:
            out.append((lo, hi))
    merged = []
    for lo, hi in sorted(out):
        if merged and lo <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(hi, merged[-1][1]))
        else:
            merged.append((lo, hi))
    return merged


def intersect(xs, ys):
    out, i, j = [], 0, 0
    while i < len(xs) and j < len(ys):
        lo, hi = max(xs[i][0], ys[j][0]), min(xs[i][1], ys[j][1])
        if lo <= hi:
            out.append((lo, hi))
        if xs[i][1] < ys[j][1]:
            i += 1
        else:
            j += 1
    return out


def sublevel(k, alpha):
    need(k >= 2 and 0 <= alpha < HALF, 'domain')
    cur = [(F(0), HALF)]
    for j in range(2, k + 1):
        cur = intersect(cur, width_set(j, alpha))
    return cur


def nearest_distance(x):
    x -= x.numerator // x.denominator
    return min(x, 1 - x)


def g(k, phi):
    return max(nearest_distance(j * phi) for j in range(2, k + 1))


def theorem(k):
    """(threshold alpha*, farthest phi at alpha*) claimed in PROOF.md."""
    if k == 3:
        return F(1, 5), F(2, 5)
    if k in (4, 5):
        return F(2, 7), F(3, 7)
    if k in (6, 7):
        return F(1, 3), F(4, 9)
    return F(1, 3), F(1, 3)


def check_k(k):
    star, far = theorem(k)
    # Below the threshold the set is exactly the small branch [0, alpha/k].
    for m in (3, 7, 20, 60, 200):
        alpha = star - F(1, 2 ** m)
        need(sublevel(k, alpha) == [(F(0), alpha / k)], 'small branch k=%d m=%d' % (k, m))
    for alpha in (F(0), star / 2, star * F(9, 10)):
        need(sublevel(k, alpha) == [(F(0), alpha / k)], 'small branch k=%d alpha=%s' % (k, alpha))
    # At the threshold the farthest feasible point is the claimed jump point.
    at = sublevel(k, star)
    need(at[0] == (F(0), star / k), 'small branch at threshold k=%d' % k)
    need(max(hi for _, hi in at) == far, 'jump point k=%d: %s' % (k, at))
    need(all(lo == hi for lo, hi in at[1:]), 'isolated far points at threshold k=%d' % k)
    need(g(k, far) == star, 'exact witness value k=%d' % k)
    need(far > star / k, 'genuine jump k=%d' % k)
    return len(at)


def check_universal_lemmas():
    # phi = 1/3 has ||j/3|| <= 1/3 for every j: one witness for every k.
    need(all(nearest_distance(F(j, 3)) <= F(1, 3) for j in range(1, 10000)), 'one-third witness')
    # 4/9 survives through width 7 and fails at width 8; 3/7 fails at width 6.
    need(g(7, F(4, 9)) == F(1, 3) and nearest_distance(F(32, 9)) == F(4, 9), '4/9 boundary')
    need(g(5, F(3, 7)) == F(2, 7) and nearest_distance(F(18, 7)) == F(3, 7), '3/7 boundary')
    need(g(3, F(2, 5)) == F(1, 5), 'PR5916 equal-budget witness 2/5')


def controls():
    rejected = 0
    # Width two alone: phi = 1/2 is always feasible, so no small branch exists.
    need(sublevel(2, F(1, 100))[-1][1] == HALF, 'k=2 control')
    rejected += 1
    # A false threshold claim is detected: 1/3 is not the first jump for k=5.
    try:
        need(sublevel(5, F(1, 3) - F(1, 1000)) == [(F(0), (F(1, 3) - F(1, 1000)) / 5)], 'x')
    except AssertionError:
        rejected += 1
    # A false jump point is detected: 4/9 is not feasible at k=8, alpha=1/3.
    try:
        need(max(hi for _, hi in sublevel(8, F(1, 3))) == F(4, 9), 'x')
    except AssertionError:
        rejected += 1
    # A falsely strict threshold is detected: alpha* itself already admits the jump.
    try:
        need(sublevel(9, F(1, 3)) == [(F(0), F(1, 27))], 'x')
    except AssertionError:
        rejected += 1
    need(rejected == 4, 'all four controls fail as designed')
    return rejected


def main():
    check_universal_lemmas()
    pieces = {k: check_k(k) for k in range(3, K_MAX + 1)}
    rejected = controls()
    print('%s k=3..%d thresholds and jump points exact; %d controls rejected; far components %s'
          % (STATUS, K_MAX, rejected, sorted(set(pieces.values()))))
    return 0


if __name__ == '__main__':
    sys.exit(main())
