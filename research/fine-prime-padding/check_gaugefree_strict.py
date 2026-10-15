"""Strengthen the byte-preserved PR1758 finite gauge/circuit checks.

The predecessor has one `assert ... or True` and reports circuit errors
without asserting them. This wrapper checks the full corrected identity
and the reported replay errors, while leaving the predecessor unchanged.
Numerical samples remain evidence, not an all-size analytic proof.
"""
import math
import runpy
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must be enabled')
P = Path(__file__).resolve().parent
ns = runpy.run_path(str(P/'vendor/pr1758/outer/check_gaugefree.py'), run_name='__main__')
sp = ns['sp']
b0, lam, dl, x, y = (ns[k] for k in ('b0', 'lam', 'dl', 'x', 'y'))
correct = -b0*((1-lam)*x*x-lam*(1-lam)*y*y+dl*dl-dl*dl/lam+2*dl*(1-lam)*y)
assert sp.simplify(ns['sub']-correct) == 0
wrong_constant = correct-2*b0*dl*dl/lam
assert sp.simplify(ns['sub']-wrong_constant) != 0
rows = ns['rowsE']
assert len(rows) == 12
for row in rows:
    assert math.isfinite(row['max_error']) and row['max_error'] < 1e-9
    if row['n'] <= 16:
        assert math.isfinite(row['peak_prefix_norm']) and row['peak_prefix_norm'] < 1e6
    else:
        assert row['peak_prefix_norm'] is None

# Additional high-precision symbol samples in the new theta=Theta(p^-2)
# range. The analytic lower bound is the retained proof's mathematical input.
mp = ns['mp']
mp.mp.dps = 100
tests = 0
for p in (32, 64, 128, 256):
    th = mp.mpf(1)/(3*p*p)
    rho = 1+th
    alpha = int(mp.ceil(mp.sqrt(4/mp.pi*mp.log(16*p))))
    for kind in ('narrow', 'broad'):
        gamma = mp.pi*alpha**2*rho if kind == 'narrow' else mp.pi/(alpha**2*rho)
        base_shift = (mp.mpf('0.5')-th/2)/rho if kind == 'narrow' else mp.mpf('0.5')*(1-th)
        for sign in (-1, 1):
            shift = sign*base_shift
            mu = (1-mp.exp(-gamma*(1-2*abs(shift))))*mp.exp(-mp.pi**2/(3*gamma))
            assert mu > 0
            U = int(mp.sqrt(300/gamma))+8
            for angle in (mp.mpf(0), mp.pi/3, mp.pi/2, mp.pi):
                symbol = mp.exp(gamma*shift**2)*mp.fsum(
                    mp.exp(-gamma*(u-shift)**2)*mp.exp(-1j*u*angle)
                    for u in range(-U, U+1))
                assert symbol.real > mu*(1-mp.mpf('1e-50'))
                tests += 1
print('PASS_STRICT_GAUGEFREE_REPLAY', 'circuit cases', len(rows), 'fine-theta symbol samples', tests)
