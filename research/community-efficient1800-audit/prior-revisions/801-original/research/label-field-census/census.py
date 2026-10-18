"""Label-field census: can a different lattice or label field beat the E8 unit inside the B_K format ceiling?

For each line configuration (rational root systems, the Eisenstein E8 = Witting configuration, the Hurwitz E8) this
script computes, exactly:

* v      number of ports (lines), and n = dimension over the label field (so rational window h/k = n),
* omega  the largest set of pairwise non-orthogonal lines (a clique of the non-orthogonality graph),
* per-frame-vector support cliques, for the decoder N = sum over an orthogonal frame of rank-one coordinate totals
  (N_TS != 0 exactly when the lines are not orthogonal, as for the E8-linear decoder of research/format-limits),
* x_lb = sum of the support cliques / v, a lower bound on the copy cost per port of THAT coordinate-total decoder:
  B_TT = 1 and B_TS = 0 whenever N_TS != 0 force B[K, K] = I on every clique K inside a total's readers and sources,
  so rank B[R_j, A_j] >= |K|.  (Scope: coordinate totals in the stated frame; other decoders are not covered.)
* the certified format-ceiling root X(s, w = n, x_lb) of research/format-limits-corrected (skel.X, rational
  intervals), maximised over odd s in 3..13.  X is an upper bound on the supplier saving for that unit, because X is
  non-increasing in x (section A.2 of that package) and x >= x_lb.

General k: the format theorem shows X depends only on (s, h/k, x/k).  A Q(w)-line is a rank-2 rational label and a
Hurwitz line a rank-4 rational label; their ranks over the residue field (F_4, or the 2x2 / 4x4 F_2 blocks) scale
by the same k, so cliques are counted in field units and n is the dimension over the field.

No network, word or kappa claim.  Run:  python3 -B census.py [--json OUT]
"""
import argparse
import itertools
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'research/format-limits-corrected/scripts'))
from e8units import first_clique, hamming_e8  # noqa: E402
from skel import X  # noqa: E402

S_LIST = (3, 5, 7, 9, 11, 13)


def max_clique(nodes, adjacent):
    nodes = list(nodes)
    adj = [[i != j and adjacent(nodes[i], nodes[j]) for j in range(len(nodes))] for i in range(len(nodes))]
    k = 1
    while first_clique(adj, k + 1):
        k += 1
    return k


# --------------------------------------------------------------------------------------------- rational configurations
def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def lines_up_to_sign(vectors):
    seen, out = set(), []
    for r in vectors:
        r = tuple(r)
        if r in seen or tuple(-x for x in r) in seen:
            continue
        seen.add(r)
        out.append(r)
    return out


def rational_unit(name, lines, frame):
    v, n = len(lines), len(frame)
    assert all(dot(frame[i], frame[j]) == 0 for i in range(n) for j in range(i))
    orth = lambda i, j: dot(lines[i], lines[j]) == 0
    nonorth = lambda i, j: not orth(i, j)
    # Gram identity G = sum_f (L f)(L f)^T / |f|^2 requires the frame to span the ambient space
    supports = [[i for i in range(v) if dot(lines[i], f) != 0] for f in frame]
    cliques = [max_clique(S, nonorth) for S in supports]
    return dict(name=name, field='Q', k=1, v=v, n=n, omega=max_clique(range(v), nonorth),
                orth_degrees=sorted({sum(orth(i, j) for j in range(v) if j != i) for i in range(v)}),
                support_sizes=[len(S) for S in supports], support_cliques=cliques)


def d4():
    roots = [r for r in itertools.product((-1, 0, 1), repeat=4) if sum(map(abs, r)) == 2]
    return rational_unit('D4 root lines', lines_up_to_sign(roots),
                         [(1, 1, 0, 0), (1, -1, 0, 0), (0, 0, 1, 1), (0, 0, 1, -1)])


def f4():
    long_ = [tuple(2 * x for x in r) for r in itertools.product((-1, 0, 1), repeat=4) if sum(map(abs, r)) == 2]
    short = [tuple(2 * x for x in r) for r in itertools.product((-1, 0, 1), repeat=4) if sum(map(abs, r)) == 1]
    half = list(itertools.product((-1, 1), repeat=4))
    return rational_unit('F4 root lines', lines_up_to_sign(long_ + short + half),
                         [(2, 0, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), (0, 0, 0, 2)])


def e8_and_e7():
    L, _ = hamming_e8()
    lines = [tuple(int(x) for x in r) for r in L]
    e8 = rational_unit('E8 root lines (Hamming frame)', lines, lines[:8])
    # E7: lines orthogonal to the fixed root line 0; frame: the 7 remaining coordinate lines are orthogonal to it
    e7_lines = [r for r in lines if dot(r, lines[0]) == 0]
    e7 = rational_unit('E7 root lines (in E8, orthogonal to a root)', e7_lines, lines[1:8])
    return e8, e7


# ------------------------------------------------------------------------------------------ Eisenstein (Witting) E8
# Eisenstein integers a + b w with w^2 = -1 - w, stored as pairs.
def emul(x, y):
    a, b = x
    c, d = y
    return (a * c - b * d, a * d + b * c - b * d)


def econj(x):
    a, b = x
    return (a - b, -b)


def eadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def witting():
    """The 40 rays of the Witting configuration: E8 as a Z[w]-lattice, 240 roots / 6 units.

    theta = sqrt(-3) = 1 + 2w; rays theta e_i, and for each zero position z the 9 rays sigma_z * (1, w^mu, w^nu) on the
    other three coordinates, where the sign vectors sigma_z are pairwise orthogonal mod 3 (the lattice condition).
    """
    Z, theta, units = (0, 0), (1, 2), [(1, 0), (0, 1), (-1, -1)]
    sig = {0: (0, 1, 1, 1), 1: (1, 0, 1, -1), 2: (1, -1, 0, 1), 3: (1, 1, -1, 0)}
    rays = []
    for i in range(4):
        r = [Z] * 4
        r[i] = theta
        rays.append(tuple(r))
    for z in range(4):
        o = [j for j in range(4) if j != z]
        for mu in units:
            for nu in units:
                r = [Z] * 4
                r[o[0]] = (sig[z][o[0]], 0)
                r[o[1]] = emul((sig[z][o[1]], 0), mu)
                r[o[2]] = emul((sig[z][o[2]], 0), nu)
                rays.append(tuple(r))

    def herm(u, w):
        s = Z
        for a, b in zip(u, w):
            s = eadd(s, emul(a, econj(b)))
        return s

    v = len(rays)
    norm = lambda x: x[0] * x[0] - x[0] * x[1] + x[1] * x[1]
    G = [[herm(rays[i], rays[j]) for j in range(v)] for i in range(v)]
    assert {G[i][i] for i in range(v)} == {(3, 0)}
    assert {norm(G[i][j]) for i in range(v) for j in range(v) if i != j} == {0, 3}   # |<u,w>|^2 in {0, 3}
    orth = lambda i, j: G[i][j] == Z
    nonorth = lambda i, j: not orth(i, j)
    supports = [[i for i in range(v) if rays[i][a] != Z] for a in range(4)]           # frame: the rays theta e_a
    return dict(name='Eisenstein E8 = Witting configuration (rank-2 rational labels)', field='Q(w)', k=2, v=v, n=4,
                omega=max_clique(range(v), nonorth),
                orth_degrees=sorted({sum(orth(i, j) for j in range(v) if j != i) for i in range(v)}),
                support_sizes=[len(S) for S in supports], support_cliques=[max_clique(S, nonorth) for S in supports])


# ------------------------------------------------------------------------------------------- Hurwitz (quaternionic) E8
def qmul(p, q):
    a1, b1, c1, d1 = p
    a2, b2, c2, d2 = q
    return (a1 * a2 - b1 * b2 - c1 * c2 - d1 * d2, a1 * b2 + b1 * a2 + c1 * d2 - d1 * c2,
            a1 * c2 - b1 * d2 + c1 * a2 + d1 * b2, a1 * d2 + b1 * c2 - c1 * b2 + d1 * a2)


def qconj(p):
    return (p[0], -p[1], -p[2], -p[3])


def hurwitz():
    """E8 as a Hurwitz-lattice: 240 roots / 24 units = 10 left quaternionic lines in H^2: H(1,0), H(0,1) and
    H(1, y) for the 8 units y = +-1, +-i, +-j, +-k (those congruent to 1 mod 1+i).  Hermitian form a c* + b d*."""
    one, zero = (1, 0, 0, 0), (0, 0, 0, 0)
    ys = [tuple(s * (t == i) for t in range(4)) for i in range(4) for s in (1, -1)]
    rays = [(one, zero), (zero, one)] + [(one, y) for y in ys]

    def herm(u, w):
        return tuple(x + y for x, y in zip(qmul(u[0], qconj(w[0])), qmul(u[1], qconj(w[1]))))

    v = len(rays)
    orth = lambda i, j: herm(rays[i], rays[j]) == zero
    nonorth = lambda i, j: not orth(i, j)
    supports = [[i for i in range(v) if rays[i][a] != zero] for a in range(2)]
    return dict(name='Hurwitz E8 (rank-4 rational labels)', field='H', k=4, v=v, n=2,
                omega=max_clique(range(v), nonorth),
                orth_degrees=sorted({sum(orth(i, j) for j in range(v) if j != i) for i in range(v)}),
                support_sizes=[len(S) for S in supports], support_cliques=[max_clique(S, nonorth) for S in supports])


# ------------------------------------------------------------------------------------------------- ceiling evaluation
def ceiling(n, x):
    best = None
    for s in S_LIST:
        r = X(s, n, 1, x)
        if r is None:                     # D_s <= 0: no saving at all at this s
            continue
        if best is None or r['hi'] > best['hi']:
            best = dict(s=s, hi=r['hi'], m=r['m'], D=r['D'])
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json')
    args = ap.parse_args()
    e8, e7 = e8_and_e7()
    units = [e8, e7, d4(), f4(), witting(), hurwitz()]
    rows = []
    for u in units:
        x_lb = Fr(sum(u['support_cliques']), u['v'])
        c = ceiling(u['n'], x_lb)
        row = dict(u, x_lb=str(x_lb), x_lb_decimal=float(x_lb),
                   ceiling=None if c is None else dict(s=c['s'], X_upper=str(c['hi']), X_decimal=float(c['hi']),
                                                       kappa_upper_decimal=float(c['hi'] / (1 + c['hi']))))
        rows.append(row)
        print('%-62s v=%3d n=%d omega=%2d supp-cliques=%s x_lb=%-7s ceiling: %s' % (
            u['name'], u['v'], u['n'], u['omega'], u['support_cliques'], x_lb,
            'no positive saving for s <= 13' if c is None else 'X <= %.6g at s=%d' % (float(c['hi']), c['s'])))
    # calibration rows: the realised frontier units (x from the shipped decoders), same certified engine
    calib = {}
    for name, (h, x) in {'bit P111 frontier unit (h=8, x=63/111)': (8, Fr(63, 111)),
                         'complex P112 frontier unit (h=9, x=64/112)': (9, Fr(64, 112)),
                         'complex-side Witting analogue (window >= omega = 7, x >= 7/10)': (7, Fr(7, 10))}.items():
        c = ceiling(h, x)
        calib[name] = dict(s=c['s'], X_upper=str(c['hi']), X_decimal=float(c['hi']))
        print('%-62s ceiling: X <= %.6g at s=%d' % (name, float(c['hi']), c['s']))
    # Certified ceilings for copy costs proved elsewhere (cost in field rank units over v ports; window n):
    # Eisenstein E8: any decoder costs >= 22 (#798), coordinate totals >= 28 (this census), open up to 40 (#798);
    # Gaussian E8: floor 40 on 60 lines (#738, #770); Hurwitz E8: exactly 10 on 10 lines (#703).
    sweep = {}
    for name, v, n, costs in (('Eisenstein E8 (40 lines, n=4)', 40, 4, range(22, 41)),
                              ('Gaussian E8 (60 lines, n=4)', 60, 4, (40,)),
                              ('Hurwitz E8 (10 lines, n=2)', 10, 2, (10,))):
        for cost in costs:
            c = ceiling(n, Fr(cost, v))
            sweep['%s cost=%d' % (name, cost)] = None if c is None else dict(
                s=c['s'], X_upper=str(c['hi']), X_decimal=float(c['hi']),
                kappa_upper_decimal=float(c['hi'] / (1 + c['hi'])))
            print('%-48s cost=%2d x=%-6s %s' % (name, cost, Fr(cost, v),
                  'no positive saving for s <= 13' if c is None else 'X <= %.6g at s=%d' % (float(c['hi']), c['s'])))
    if args.json:
        Path(args.json).write_text(json.dumps(dict(units=rows, calibration=calib, copy_cost_sweep=sweep),
                                              indent=1) + '\n')


if __name__ == '__main__':
    main()
