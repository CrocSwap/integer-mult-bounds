"""Two rational enclosures of the adjusted child cost c_k(b) = k^(1-b) - k (standard library only).

For the complex recurrence the width-k child contributes M_k = (k/(mW)) (m/k)^b, so
M_k - k M_1 = (m^b/(mW)) c_k with a positive common factor. Since every register's
total climb is fixed, minimising sum n_k M_k is minimising sum n_k c_k (c_0 = c_1 = 0).

Engine A: own atanh logarithm series and alternating exponential series.
Engine B: the pinned repository engine (research/complex-k492-owner-repair/vendor/multicold/engines/moment.py),
          via its exact moment() enclosures of M_k and M_1.
"""
import hashlib, importlib.util
from functools import lru_cache
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_ENGINE = ROOT / 'research/complex-k492-owner-repair/vendor/multicold/engines/moment.py'
REPO_ENGINE_SHA256 = '81cbc864e106418fc7854322746f72180cb8110ff39f74450a3b8d55a82c1482'
B_ACCEPTED = Q('65528268492323474503/40000000000000000000000')   # PR626 native complex endpoint
B_NEXT = Q('102387919519255428911/62500000000000000000000')      # next 10^-24 grid point, rejected by PR626
M_DIM, W_LIVE = 73, 7168
DEN = Q(1, 2 ** 200)


@lru_cache(None)
def _ln_bounds(k):
    """ln k = 2 atanh(z), z=(k-1)/(k+1): positive odd series; tail <= next term / (1 - z^2)."""
    if k == 1: return Q(0), Q(0)
    z = Q(k - 1, k + 1); s = Q(0); t = z; j = 1
    while True:
        s += t / j; t *= z * z; j += 2
        tail = t / j / (1 - z * z)
        if tail < DEN: return 2 * s, 2 * (s + tail)


def _down(x, bits=256):
    return Q((x.numerator << bits) // x.denominator, 1 << bits)


def _up(x, bits=256):
    return -_down(-x, bits)


def _exp_neg_bounds(x):
    """bounds of exp(-x) for 0 <= x < 1: alternating series with decreasing terms.
    Callers pass dyadic x; exp(-x) is decreasing, so outward rounding of x is done by the caller."""
    assert 0 <= x < 1
    s = Q(1); t = Q(1); j = 1; lo = hi = None
    while True:
        t = t * x / j; s = s - t if j % 2 else s + t
        if j % 2: lo = s
        else: hi = s
        if lo is not None and hi is not None and t < DEN: return lo, hi
        j += 1


def engine_a(b):
    out = {}
    for k in range(0, 10):
        if k < 2: out[k] = (Q(0), Q(0)); continue
        l, u = _ln_bounds(k)
        e_lo, _ = _exp_neg_bounds(_up(b * u)); _, e_hi = _exp_neg_bounds(_down(b * l))
        out[k] = (k * e_lo - k, k * e_hi - k)
    return out


def _repo():
    spec = importlib.util.spec_from_file_location('repo_moment', REPO_ENGINE)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m


def engine_b(b):
    """c_k scaled by (mW)/m^b: uses M_k enclosures; returns enclosures of (mW) (M_k - k M_1) / m^b."""
    R = _repo(); out = {}
    l1, u1 = R.moment({1: 1}, M_DIM, W_LIVE, b)
    # m^b bounds from the same engine: M_1 = (1/(mW)) m^b
    mb_lo, mb_hi = l1 * M_DIM * W_LIVE, u1 * M_DIM * W_LIVE
    for k in range(0, 10):
        if k < 2: out[k] = (Q(0), Q(0)); continue
        lk, uk = R.moment({k: 1}, M_DIM, W_LIVE, b)
        lo = (lk - k * u1) * M_DIM * W_LIVE; hi = (uk - k * l1) * M_DIM * W_LIVE
        # divide by m^b > 0 (both bounds are negative for k >= 2)
        assert hi < 0
        out[k] = (lo / mb_lo, hi / mb_hi)
    return out


def adjusted_bounds(b=B_NEXT):
    A = engine_a(b)
    return {k: A[k][0] for k in A}, {k: A[k][1] for k in A}


def nonnegative(v, engines):
    """sum_{k=2..9} v[k-2] c_k >= 0, proved by every engine (zero form accepted symbolically)"""
    if not any(v): return True
    for E in engines:
        s = Q(0)
        for k in range(2, 10):
            x = v[k - 2]
            if x: s += x * (E[k][0] if x > 0 else E[k][1])
        if s < 0: return False
    return True


def moment_a(H, b, m=M_DIM, W=W_LIVE):
    """engine-A enclosure of the native moment sum_r (r n/(mW)) (m/r)^b"""
    lo = hi = Q(0)
    lm_lo, lm_hi = _ln_bounds(m)
    for r, n in H.items():
        lr_lo, lr_hi = _ln_bounds(r)
        x_lo, x_hi = b * (lm_lo - lr_hi), b * (lm_hi - lr_lo)    # b ln(m/r) >= 0
        # exp(x) = 1/exp(-x)
        e1_lo, e1_hi = _exp_neg_bounds(_up(x_hi)); e2_lo, e2_hi = _exp_neg_bounds(_down(x_lo))
        p = Q(r * n, m * W); lo += p / e2_hi; hi += p / e1_lo
    return lo, hi
