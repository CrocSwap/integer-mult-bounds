#!/usr/bin/env python3
"""SEPAUDIT checker: the compiler's separation hypothesis r_max < k_min holds after strictification for the frontier invoices.

Own code (DreamingOfClouds with Claude Opus 5.5), standard library only (decimal, 60 digits).

FINITE-PRECOMPILATION.md:51-52 and :205-207 require r_max (largest paid child rank) < k_min (smallest productive target rank)
for the unit fed to the compiler.  The raw #7113-caller invoices have r_max = 64 and k_min = 1, so they fail it literally.
The selected #7000 record applies the admitted strictification step instead (research/shared-wire-split-composition,
interval_gate.py: product power v = 1920, cutoff c = 11, completion floor b = 12, u = 1/7; the gate passes when
alpha = P_t/T_t < 1, gamma = P_{t+1/7}/(11^{1/7} T_t) < 31/32 and delta = 12*B/(11^C T_t) < 31/32, with t = 1 - C and B the
target count; the ambient cap needs max target < 153).

Checks
  1. Control: the #7000 invoice in research/shared-wire-split-composition/FULL-RESULT.json at its tested C gives the
     gamma and delta recorded there (to 1e-12), and its kappa root matches its raw bracket.
  2. For the #7546, #7605 and #7608 invoices (vendored data): the kappa root of sum (T_r - P_r) r^(1-C) = 0 reproduces the
     published kappa; raw r_max = 64 >= k_min = 1 (the literal hypothesis fails); max target < 153; and the gate passes
     (alpha < 1, gamma, delta < 31/32) at C = kappa - 7e-14.
  Negative control: the #7546 invoice with every paid count of rank >= 16 multiplied by 1.10 fails the gate (gamma >= 31/32
  or alpha >= 1 at the same C).
Prints PASS_SEPARATION_GATE.
"""
import hashlib, json, os, sys
from decimal import Decimal as D, getcontext

getcontext().prec = 60
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
PINS = {
    'data/invoice-7546.json': '151d26b47dce7567c349e5c6455740c10221226ba1f89aef58cf72e1ec8dc676',
    'data/invoice-7605.json': 'b38afd7ca590b5c4c301ee4fbe0e123f0c7220c2bd1f40c66adf208652e3ce15',
    'data/invoice-7608.json': '4d89c9e1dc564d420dee20e456f5bdfcfccd13ab1ee7d224ea388b3b8c5eae3c',
}
FULL = 'research/shared-wire-split-composition/FULL-RESULT.json'
KAPPA = {  # published values (#7546 ToikY, #7605 aliromman, #7608 ours, conditional)
    '7546': D('0.003648411294790845'),
    '7605': D('0.0036504442446'),
    '7608': D('0.00365074956598367712940081'),
}


def fail(msg):
    print('FAIL:', msg); sys.exit(1)


def expect(name, got, want):
    ok = got == want
    print(('ok   ' if ok else 'FAIL ') + name + ': ' + str(got))
    if not ok: fail(name)


def load(rel, sha):
    b = open(os.path.join(ROOT if sha is None else HERE, rel), 'rb').read()
    if sha is not None and hashlib.sha256(b).hexdigest() != sha: fail('sha256 mismatch ' + rel)
    return json.loads(b)


def hist(h): return {int(k): D(v) for k, v in h.items() if int(v) > 0}


def mom(H, x): return sum(c * (D(r).ln() * x).exp() for r, c in H.items())


def root(T, P):
    lo, hi = D('0.001'), D('0.006')
    f = lambda C: mom(T, 1 - C) - mom(P, 1 - C)
    if not (f(lo) > 0 > f(hi)): fail('root not bracketed')
    for _ in range(140):
        mid = (lo + hi) / 2
        if f(mid) > 0: lo = mid
        else: hi = mid
    return lo


def gate(T, P, C):
    t = 1 - C
    Tt, Pt = mom(T, t), mom(P, t)
    Pu = mom(P, t + D(1) / 7)
    alpha = Pt / Tt
    gamma = Pu / ((D(11).ln() / 7).exp() * Tt)
    delta = 12 * sum(T.values()) / ((D(11).ln() * C).exp() * Tt)
    return alpha, gamma, delta


def passes(a, g, d): return a < 1 and g < D(31) / 32 and d < D(31) / 32


def main():
    full = load(FULL, None)
    T, P = hist(full['invoice']['T']), hist(full['invoice']['P'])
    tested = D(full['gate']['tested'].split('/')[0]) / D(full['gate']['tested'].split('/')[1])
    a, g, d = gate(T, P, tested)
    expect('#7000 control: gamma, delta at its tested C agree with FULL-RESULT.json to 1e-12',
           (abs(g - D(repr(full['gate']['gamma'][0]))) < D('1e-12'), abs(d - D(repr(full['gate']['delta'][0]))) < D('1e-12')),
           (True, True))
    k0 = root(T, P)
    lo, hi = [D(x.split('/')[0]) / D(x.split('/')[1]) for x in full['gate']['raw_bracket']]
    expect('#7000 control: kappa root lies in the recorded raw bracket', lo - D('1e-25') <= k0 <= hi + D('1e-25'), True)
    for name in ('7546', '7605', '7608'):
        inv = load('data/invoice-%s.json' % name, PINS['data/invoice-%s.json' % name])
        T, P = hist(inv['targets']), hist(inv['paid'])
        k = root(T, P)
        digits = len(str(KAPPA[name]).split('.')[1]) - 1
        expect('#%s: kappa root matches the published kappa to %d digits' % (name, digits),
               abs(k - KAPPA[name]) < D(10) ** (-digits), True)
        rmax, kmin, kmax = max(P), min(T), max(T)
        expect('#%s: raw r_max, k_min (literal r_max < k_min fails), max target < 153' % name,
               (rmax, kmin, rmax < kmin, kmax < 153), (64, 1, False, True))
        C = k - D('7e-14')
        a, g, d = gate(T, P, C)
        print('     #%s: B %d, alpha %.12f, gamma %.6f, delta %.6f' % (name, sum(T.values()), a, g, d))
        expect('#%s: strictification gate passes (alpha < 1, gamma, delta < 31/32)' % name, passes(a, g, d), True)
        if name == '7546':
            P2 = {r: (c * D('1.10') if r >= 16 else c) for r, c in P.items()}
            a2, g2, d2 = gate(T, P2, C)
            expect('negative control: paid mass of rank >= 16 scaled by 1.10 fails the gate', passes(a2, g2, d2), False)
    print('PASS_SEPARATION_GATE')


if __name__ == '__main__':
    main()
