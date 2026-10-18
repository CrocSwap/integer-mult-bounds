# SPDX-License-Identifier: Apache-2.0
"""Code-disjoint check of the selected T37 moment endpoints and kappa reduction.

Usage: endpoints.py OUT.json

Independent of the retained engines (moment.py, base_two_moment.py, outer.py),
which are neither imported nor read. Standard library only.

* Logarithms: ln 2, ln 3, ln 5, ln 7 and ln 73 from the identities
    ln 2 = 2 atanh(1/3),        ln 3 = ln 2 + 2 atanh(1/5),
    ln 5 = 2 ln 2 + 2 atanh(1/9), ln 7 = 3 ln 2 - 2 atanh(1/15),
    ln 73 = 3 ln 2 + 2 ln 3 + 2 atanh(1/145),
  each atanh(t) = sum t^(2k+1)/(2k+1) with the geometric tail bound
  t^(2K+1) / ((2K+1)(1 - t^2)). Every needed ln(m/r) is a prime decomposition.
* Exponentials: exp(y) for 0 <= y < 1/100 by the Taylor polynomial of degree K,
  with remainder at most 2 y^(K+1)/(K+1)! (since e^y < 2).
* Intervals are exact rationals rounded outward to multiples of 2^-PREC.
"""
import gzip
import hashlib
import json
import sys
import tarfile
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PINS = json.loads((HERE / 'PINS.json').read_text())
PREC = 320
TERMS = 120            # atanh terms (t <= 1/3 gives tails far below 2^-320)
TAYLOR = 16


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def down(x):
    return Q((x.numerator << PREC) // x.denominator, 1 << PREC)


def up(x):
    return -down(-x)


class I:
    """Closed rational interval [lo, hi] with outward dyadic rounding."""
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi=None):
        hi = lo if hi is None else hi
        require(lo <= hi, 'interval order')
        self.lo, self.hi = down(Q(lo)), up(Q(hi))

    def __add__(self, o):
        o = o if isinstance(o, I) else I(o)
        return I(self.lo + o.lo, self.hi + o.hi)

    def __sub__(self, o):
        o = o if isinstance(o, I) else I(o)
        return I(self.lo - o.hi, self.hi - o.lo)

    def __mul__(self, o):
        o = o if isinstance(o, I) else I(o)
        p = (self.lo * o.lo, self.lo * o.hi, self.hi * o.lo, self.hi * o.hi)
        return I(min(p), max(p))

    __radd__ = __add__
    __rmul__ = __mul__


def atanh(t):
    t = Q(t)
    require(0 < t <= Q(1, 3), 'atanh argument')
    s, power = Q(0), t
    for k in range(TERMS):
        s += power / (2 * k + 1)
        power *= t * t
    tail = power / ((2 * TERMS + 1) * (1 - t * t))
    return I(s, s + tail)


LN2 = 2 * atanh(Q(1, 3))
LN3 = LN2 + 2 * atanh(Q(1, 5))
LN5 = 2 * LN2 + 2 * atanh(Q(1, 9))
LN7 = 3 * LN2 - 2 * atanh(Q(1, 15))
LN73 = 3 * LN2 + 2 * LN3 + 2 * atanh(Q(1, 145))
PRIME_LN = {2: LN2, 3: LN3, 5: LN5, 7: LN7, 73: LN73}


def ln_int(k):
    out = I(0)
    for p, lp in PRIME_LN.items():
        while k % p == 0:
            out = out + lp
            k //= p
    require(k == 1, 'unsupported prime factor')
    return out


def exp_small(y):
    """Enclosure of exp(y) for an interval 0 <= y < 1/100."""
    require(0 <= y.lo and y.hi < Q(1, 100), 'exp range')
    lo = hi = Q(1)
    tlo = thi = Q(1)
    for k in range(1, TAYLOR + 1):
        tlo = down(tlo * y.lo / k)
        thi = up(thi * y.hi / k)
        lo += tlo
        hi += thi
    rem = thi * y.hi / (TAYLOR + 1) * 2
    return I(lo, hi + rem)


def moment(H, m, W, z, surcharge):
    """sum_r (r n_r / (m W)) (m/r)^z, plus the inherited 32 m N_children / (10^16 W) m^z term."""
    total = I(0)
    lm = ln_int(m)
    for r, n in H.items():
        y = (lm - ln_int(r)) * I(z) if r > 1 else lm * I(z)
        total = total + I(Q(r * n, m * W)) * exp_small(y)
    if surcharge:
        total = total + I(Q(32 * m * sum(H.values()), 10 ** 16 * W)) * exp_small(lm * I(z))
    return total


def certify_endpoint(H, m, W, b, surcharge):
    at, nxt = moment(H, m, W, b, surcharge), moment(H, m, W, b + Q(1, 10 ** 24), surcharge)
    require(at.hi < 1, 'moment not below one at the endpoint')
    require(nxt.lo > 1, 'moment not above one at the next grid point')
    return dict(endpoint=str(b), moment_minus_one_at_endpoint=[float(at.lo - 1), float(at.hi - 1)],
                moment_minus_one_at_next=[float(nxt.lo - 1), float(nxt.hi - 1)])


def kappa_from(b, c):
    """The selected reduction: s = min(c, (1-beta) b) - 10^-27; seven bootstrap steps from
    384599/10^10; q = a7 (1 - 2 eta); kappa is the largest 10^-18 grid point strictly below
    (1 - eta) q / (1 + q), with eta = beta = 10^-24."""
    eta = beta = Q(1, 10 ** 24)
    s = min(c, (1 - beta) * b) - Q(1, 10 ** 27)
    a = Q(384599, 10 ** 10)
    for _ in range(7):
        a = (1 - s) * s + s * a
    q = a * (1 - 2 * eta)
    margin = (1 - eta) * q / (1 + q)
    t = margin * 10 ** 18
    ceil_t = -((-t.numerator) // t.denominator)
    k = Q(ceil_t - 1, 10 ** 18)                 # the largest grid point strictly below the margin
    require(k < margin <= k + Q(1, 10 ** 18), 'grid reduction')
    return k, margin


def pinned(key):
    data = (ROOT / PINS[key]['path']).read_bytes()
    require(sha256(data) == PINS[key]['sha256'], f'{key} digest')
    return json.loads(data)


def template_profile():
    """Complex profile recomputed from the hosted T37 payload: calls x local profile + idle children."""
    src = PINS['t37_archive']
    with tarfile.open(ROOT / src['path'], 'r:gz') as tar:
        require(sha256((ROOT / src['path']).read_bytes()) == src['sha256'], 'archive digest')
        raw = gzip.decompress(tar.extractfile(tar.getmember(src['template_member'])).read())
    require(sha256(raw) == src['template_payload_sha256'], 'template payload digest')
    t = json.loads(raw)
    (prov,) = t['local_providers'].values()
    local = Counter({int(k): v for k, v in prov['local_program_checks']['forward']['paid_profile'].items()})
    require(local == Counter({int(k): v for k, v in prov['local_program_checks']['backward']['paid_profile'].items()}),
            'both orientations pay the same profile')
    H = Counter()
    for _ in t['calls']:
        H.update(local)
    for c in t['idle_children']:
        H[c['rank']] += c['replicas']
    return H, t['live'], t['m']


def main():
    assembly = pinned('assembly')
    selected = pinned('selected')
    bit = pinned('bit_record')
    H, W, m = template_profile()
    require({str(k): v for k, v in sorted(H.items())} == assembly['complex_profile'], 'complex profile differs from the record')
    require(m * W - sum(r * n for r, n in H.items()) == 11840, 'complex deficit')
    Hb = Counter({int(k): v for k, v in bit['nine']['profile'].items()})
    Wb = bit['nine']['bit']['live']
    b, bc, c = Q(assembly['complex_lower']), Q(assembly['conservative_complex_lower']), Q(assembly['bit_lower'])
    out = dict(status='PASS_T37_ENDPOINTS_CODE_DISJOINT', base_commit=PINS['base_commit'],
               method='atanh prime decomposition, Taylor exp with Lagrange remainder, outward 2^-%d rounding' % PREC)
    out['native_complex'] = certify_endpoint(dict(H), m, W, b, False)
    out['conservative_complex'] = certify_endpoint(dict(H), m, W, bc, True)
    out['bit'] = certify_endpoint(dict(Hb), 64, Wb, c, True)
    # Consistency with the intervals the retained engines recorded (data only, no code).
    agree = 0
    for row in assembly['moments'] + assembly['conservative_moments']:
        key = {'complex': 'native_complex', 'conservative_complex': 'conservative_complex', 'bit': 'bit'}[row['side']]
        z = Q(row['endpoint'])
        Hx, mx, Wx = (dict(Hb), 64, Wb) if key == 'bit' else (dict(H), m, W)
        mine = moment(Hx, mx, Wx, z, row['surcharge'])
        for engine in ('mercator', 'base_two'):
            lo, hi = (Q(x) for x in row[engine])
            require(max(lo, mine.lo - 1) <= min(hi, mine.hi - 1), f'{key} {engine} interval disjoint from this enclosure')
            agree += 1
    require(agree == 12, 'twelve recorded engine intervals')
    out['recorded_engine_intervals_intersect'] = agree
    k, margin = kappa_from(b, c)
    kc, _ = kappa_from(bc, c)
    require(str(k) == assembly['kappa'] == selected['kappa'], 'kappa differs from the selected record')
    require(str(kc) == assembly['conservative_kappa'], 'conservative kappa differs')
    require((1 - Q(1, 10 ** 24)) * b < c, 'complex side binds')
    out['kappa'] = dict(kappa=str(k), conservative_kappa=str(kc), binding='complex',
                        margin_minus_kappa=float(margin - k), next_grid_point_rejected=True)
    out['profile'] = dict(source='hosted T37 template: 333 calls x local paid profile + idle children',
                          equals_selected_record=True, live=W, m=m, deficit=11840)
    with open(sys.argv[1], 'w') as f:
        f.write(json.dumps(out, indent=1, sort_keys=True) + '\n')
    print(out['status'])
    for key in ('native_complex', 'conservative_complex', 'bit'):
        print(f"{key:21s} endpoint {out[key]['endpoint']}  G-1 at b <= {out[key]['moment_minus_one_at_endpoint'][1]:.3e}"
              f"  G-1 at b+1e-24 >= {out[key]['moment_minus_one_at_next'][0]:.3e}")
    print('kappa', out['kappa']['kappa'], 'conservative', out['kappa']['conservative_kappa'])


if __name__ == '__main__':
    main()
