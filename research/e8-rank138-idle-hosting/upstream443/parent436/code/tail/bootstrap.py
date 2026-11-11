"""Own reimplementation of PR #392's (rohanarun) exact pricing tail, as used by PR #395:
  certify24: complex coarse root to 24 decimals by both PR #315 engines with the 10^-16 fallback;
  refine:    six fixed ordinary-bootstrap levels (beta = eta = 10^-18, saving backoff 10^-24), PR #315 outer assembly,
             47 strict constraints, next grid point and invalid parameters rejected.
Standard library only; engines are the unchanged PR #315 files (same git blobs as #392's)."""
from fractions import Fraction as Q
from e8core import moment, other, outer

def certify24(H, m, W):
    H = {int(k): v for k, v in H.items()}
    root = moment.certify(H, m, W, True); lo = Q(root['lower']); hi = Q(root['upper']); assert hi - lo == Q(1, 10**24)
    assert moment.moment(H, m, W, lo, True)[1] < 1 < moment.moment(H, m, W, hi, True)[0]
    fb = 32 * m * m * sum(H.values()); dens = Q(1, 10**16)
    _, up = other.moment(m, W, list(H.items()), lo); _, bad = other.moment(m, W, [(1, fb)], lo)
    low, _ = other.moment(m, W, list(H.items()), hi); badl, _ = other.moment(m, W, [(1, fb)], hi)
    assert up + dens * bad < 1 < low + dens * badl
    return lo, hi

BRIDGE = dict(proof='PROOF.md', representation='Unchanged PR390 inherited finite envelope; fixed-depth PR185 ordinary wrappers restore internal rows',
              semantic=dict(G=dict(base=2, exponent=30000), E=dict(base=2, exponent=100000), B_upper=dict(base=2, exponent=100001),
                            C0=dict(base=2, exponent=210000), C1=1, strict_literal_gap=1, induction_gap_lower=1),
              rows=dict(coefficient=20161, degree=10**6, suffix_slope=4 * 10**6, degree_gap=Q(10**6) - Q(51 * 20161, 25)))

def refine(b, c, depth=6):
    grid = Q(1, 10**18); eta = beta = Q(1, 10**18); backoff = Q(1, 10**24)
    s = (1 - beta) * b - backoff
    assert Q(0) < s < min(c, (1 - beta) * b) < b < Q(1, 32)
    x0 = Q(384599, 10**10); chain = [x0]
    for j in range(depth):
        old = chain[-1]; a = (1 - s) * s + s * old
        assert old < a < s < 1 - a and a == s - s**(j + 1) * (s - x0)
        assert min(s - a, 1 - a - s, 1 - a - s * (1 - old), 1 - s) > 0
        chain.append(a)
    a = chain[-1]; q = a * (1 - 2 * eta); mn = (1 - eta) * q / (1 + q); t = mn / grid; k = grid * ((t.numerator - 1) // t.denominator)
    asm = outer.assembly(a, b, BRIDGE, k, eta=eta, beta=beta)
    assert len(asm['strict_constraints']) == 47 and all(x > 0 for x in asm['strict_constraints'].values()) and asm['minimum_margin'] == mn
    rej = []
    for name, kk, e, be in [('next_grid', k + grid, eta, beta), ('zero_eta', k, Q(0), beta), ('zero_beta', k, eta, Q(0)), ('unit_beta', k, eta, Q(1))]:
        try: outer.assembly(a, b, BRIDGE, kk, eta=e, beta=be)
        except AssertionError: rej.append(name)
        else: raise AssertionError('accepted invalid witness ' + name)
    assert k < mn < b / (1 + b) < k + grid
    a5 = chain[-2]; q5 = a5 * (1 - 2 * eta); assert (1 - eta) * q5 / (1 + q5) < k
    return k, rej
