#!/usr/bin/env python3
"""Attach the endpoint to the word that exists: price the realised census, keep the BIT cap.

The invoice assumes the designed frame basis (4 roles per intermediate rank, 2 full).  The
realised thinned operator has 3 and 11.  Rather than make the word imitate the model, this
receipt prices the word that is actually there:

    T = the realised row census plus the inherited helper block
    D = the inherited paid profile, unchanged

and then checks whether the endpoint still clears every guard and every ledger predicate.
A larger target moment can only relax those tests, so the question is whether anything
becomes *worse*: the delta guard's numerator grows with the total target mass, which is the
one place a wider census can hurt.

The endpoint is the BIT supplier 0.0034 minus five grid steps, as before; nothing about the
BIT chain, the compiler or the outer ledger's constants is touched.
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

KAPPA = Q(951999, 280000000)
GAP = Q(1, 1400000000)
TESTED = KAPPA + 7*GAP

def main():
    E = load('moment', ROOT/'research/higher-moment-strictification/verify.py')
    row = json.loads((HERE/'P19_ROWFRAME.json').read_text())
    main_phys = {int(k): v for k, v in row['derived_row_T'].items()}
    T = Counter(main_phys)
    for r, n in W.H.items(): T[r] += 19*n
    T.pop(0, None)
    p = 19
    _, D_raw = W.invoice(p, 'I'*9+'T'*9, frozenset(range(1, 2*p, 2)),
                         {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40})
    D = Counter()
    for k, v in D_raw.items(): D[int(k)] += v
    D.pop(0, None)

    def root(T, D):
        f = lambda c: sum(n*(r**(1-c)) for r, n in T.items()) - sum(n*(r**(1-c)) for r, n in D.items())
        need(f(0.0) > 0, 'f(0) > 0')
        lo, hi = 0.0, 0.05
        while f(hi) > 0:
            hi *= 2
            need(hi < 1.0, 'no root below 1')
        for _ in range(300):
            mid = (lo+hi)/2
            if f(mid) > 0: lo = mid
            else: hi = mid
        return lo
    r_c = root(T, D)
    print('realised-census complex root: %.12f' % r_c)

    tk = 1-KAPPA
    mtk = E.moment(T, tk)
    alpha = E.divide(E.moment(D, tk), mtk)
    gamma = E.divide(E.moment(D, tk+Q(1, 5)), E.mul(E.power(20, Q(1, 5)), mtk))
    mass_T = Q(sum(T.values())*21)
    delta = E.divide((mass_T,)*2, E.mul(E.power(20, KAPPA), mtk))
    lim_a, lim_g, lim_d = 1-Q(1, 10**9), Q(97, 100), Q(97, 100)
    print('at kappa %.10f: alpha %.8f (limit %.9f)' % (float(KAPPA), alpha[1], float(lim_a)))
    print('              gamma %.6f (limit %.2f), delta %.6f (limit %.2f)'
          % (gamma[1], float(lim_g), delta[1], float(lim_d)))
    ok_a, ok_g, ok_d = alpha[1] < lim_a, gamma[1] < lim_g, delta[1] < lim_d
    print('guards: alpha %s, gamma %s, delta %s' % (ok_a, ok_g, ok_d))
    mt = E.moment(T, 1-TESTED)[0] - E.moment(D, 1-TESTED)[1]
    print('raw moment sign at the tested saving: %s' % ('positive' if mt > 0 else 'NEGATIVE'))
    need(ok_a and ok_g and ok_d, 'the guards at kappa with the realised census')
    need(mt > 0, 'raw moment sign at the tested saving')

    out = {
        'status': 'PASS_REALISED_CENSUS_ENDPOINT',
        'T_realised': dict(sorted(T.items())),
        'T_mass': sum(T.values()), 'D_mass': sum(D.values()),
        'complex_root_realised': r_c,
        'complex_root_invoiced': 0.007578535190,
        'kappa': str(KAPPA), 'kappa_decimal': float(KAPPA),
        'tested_saving': str(TESTED),
        'guards': {'alpha': float(alpha[1]), 'gamma': float(gamma[1]), 'delta': float(delta[1]),
                   'alpha_limit': str(lim_a), 'gamma_limit': str(lim_g), 'delta_limit': str(lim_d),
                   'alpha_pass': ok_a, 'gamma_pass': ok_g, 'delta_pass': ok_d},
        'raw_moment_sign_at_tested': 'positive',
        'note': ('the realised census has a larger complex root than the invoice model, so the complex side has '
                 'more slack at the BIT-capped endpoint; the delta guard is the one test that can tighten, and it '
                 'is reported explicitly'),
        'D_status': 'inherited paid profile, unchanged and not derived'}
    (HERE/'P19_ATTACH.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status'], 'root': round(r_c, 9)}, sort_keys=True))

if __name__ == '__main__':
    main()
