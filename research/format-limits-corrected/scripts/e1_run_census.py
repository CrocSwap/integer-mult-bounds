"""E. Moment-cost census by register class on the frontier words #555 (bit) and #569 (complex).

Each register's chain of frame dimensions is replayed from the published word.  A run is one paid child (one change
of frame); its moment cost at the word's own root q is phi(r) = r((m/r)^q - 1), and the published global profile has
sum phi = D at q.  For each class the script prints the number of registers, runs, mean run rank, interior stops per
register, its share of sum phi (F-share), and the 'all-single-run ceiling': the supplier value if every register of the
class climbed in one child (one run of rank = its total climb), with hosting held proportional (the idle remainder
absorbs the change of hosted helper mass), i.e. the most any re-scheduling of that class's stops could give.
#555: s = 9, T = 32 (288 stage-replicas), m = 64, D = 10272; #569: 72 calls, m = 73, D = 2560, with the width-7
provider word used for all 72 calls in the class shares (the 9 four-cold calls differ in a handful of runs).
"""
from collections import Counter, defaultdict
import sys

import numpy as np

from report import DATA, VENDOR, check, finish, load_json, main_file, near_all


def root(P, m, D, hi=0.05):
    f = lambda q: sum(z * r * ((m / r) ** q - 1) for r, z in P.items() if z) - D
    lo = 0.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if f(mid) < 0:
            lo = mid
        else:
            hi = mid
    return hi


def runs_of(ch):
    return [abs(b - a) for a, b in zip(ch, ch[1:])]


def hist_of(pats):
    h = Counter()
    for ch, z in pats.items():
        for r in runs_of(ch):
            h[r] += z
    return h


def proportional(m, D, base, rem, hel_new, hmass_new, hmass0):
    """root of base + hel_new + rem rescaled so the total hosted-plus-remainder mass stays fixed"""
    remmass = sum(r * z for r, z in rem.items())
    scale = (remmass + hmass0 - hmass_new) / remmass
    P = Counter()
    for h in (base, hel_new):
        for r, z in h.items():
            P[r] += z
    for r, z in rem.items():
        P[r] += z * scale
    return root(P, m, D)


# ------------------------------------------------------------------ #555 (bit)
EXP555 = {  # class: (n, runs, mean run, stops per register, F-share %, all-single-run ceiling %)
    'A line-born carriers (0,1,2,..)': (205, 1120, 1.46, 4.46, 29.5, 14.75),
    'B cell-born (0,2,..)': (153, 686, 1.78, 3.48, 21.2, 9.60),
    'C line -> quad/D6 keepers and totals (0,1,4|6,..)': (80, 349, 1.83, 3.36, 10.7, 4.35),
    'D quad-born (0,4,..)': (1, 4, 2.00, 3.00, 0.1, 0.05),
}
EXP555_DATA = {'x': (539, 1.44, 14.1), 'y': (213, 3.65, 10.4), 'copies': 0.7, 'remainder': 13.4}
w = load_json(VENDOR / 'pr555' / 'bitE8mut-p111.json.gz')
e555 = load_json(VENDOR / 'pr555' / 'EXPECTED.json')
lines = np.array(w['lines'], float)
dims = [int(np.linalg.matrix_rank(lines[F])) if F else 0 for F in w['frames']]
cur = list(w['start'])
chain = {r: [dims[cur[r]]] for r in range(len(cur))}
for ph in 'DABC':
    for f, dst, srcs in w[ph]:
        for r in [dst] + list(srcs):
            if cur[r] != f:
                chain[r].append(dims[f])
                cur[r] = f
for r in range(len(cur)):
    if cur[r] != w['final'][r]:
        chain[r].append(dims[w['final'][r]])
v, R, S, m, D = 111, w['R'], 288, 64, 10272
real = {int(r): z for r, z in e555['nine']['profile'].items()}
pats = Counter(tuple(chain[r]) for r in range(2 * v, 2 * v + R))
hel0 = hist_of(pats)
dat = hist_of(Counter(tuple(chain[r]) for r in range(2 * v)))
rem = Counter(real)
for h in (dat, hel0, {7: 9}):
    for r, z in h.items():
        rem[r] -= z * S
rem = {r: z for r, z in rem.items() if z}
base = Counter({r: z * S for r, z in dat.items()})
base[7] += 9 * S
c0 = root(real, m, D)
phi = lambda r: r * ((m / r) ** c0 - 1)
F = lambda h, k=S: sum(z * k * phi(r) for r, z in h.items())
hmass0 = S * sum(r * z for r, z in hel0.items())
check('E1.#555.root', abs(c0 / 1.733052825e-3 - 1) < 1e-8 and abs(F(real, 1) - D) < 1e-6 * D,
      'root of the published profile %.9e; sum phi = D' % c0)
classes = {
    'A line-born carriers (0,1,2,..)': lambda p: p[1] == 1 and p[2] == 2,
    'B cell-born (0,2,..)': lambda p: p[1] == 2,
    'C line -> quad/D6 keepers and totals (0,1,4|6,..)': lambda p: p[1] == 1 and p[2] != 2,
    'D quad-born (0,4,..)': lambda p: p[1] == 4,
}
for name, fn in classes.items():
    sub = Counter({p: z for p, z in pats.items() if fn(p)})
    h = hist_of(sub)
    n, nr, mass = sum(sub.values()), sum(h.values()), sum(r * z for r, z in h.items())
    hel = Counter(hel0)
    for r, z in h.items():
        hel[r] -= z
    hel[8] += n
    c1 = proportional(m, D, base, rem, {r: z * S for r, z in hel.items()}, S * sum(r * z for r, z in hel.items()), hmass0)
    got = (n, nr, mass / nr, (nr - n) / n, 100 * F(h) / D, 100 * (c1 / c0 - 1))
    check('E1.#555.' + name.split()[0], near_all(got, EXP555[name], (None, None, 2, 2, 1, 2)),
          '%s: n %d, runs %d, mean run %.2f, stops/register %.2f, F-share %.1f%%, all-single-run ceiling %+.2f%% c'
          % ((name,) + got))
for k, rng in (('x', range(v)), ('y', range(v, 2 * v))):
    h = hist_of(Counter(tuple(chain[r]) for r in rng))
    nr, mass = sum(h.values()), sum(r * z for r, z in h.items())
    got = (nr, mass / nr, 100 * F(h) / D)
    check('E1.#555.data-' + k, near_all(got, EXP555_DATA[k], (None, 2, 1)), 'data %s: runs %d, mean run %.2f, F-share %.1f%%' % ((k,) + got))
got = (100 * F({7: 9}) / D, 100 * F(rem, 1) / D)
check('E1.#555.copies-remainder', near_all(got, (EXP555_DATA['copies'], EXP555_DATA['remainder']), (1, 1)),
      'copies %.1f%%, idle remainder %.1f%% of sum phi' % got)

# ------------------------------------------------------------------ #569 (complex)
EXP569 = {'factory': (216, 1304, 1.49, 5.04, 32.5, 16.4), 'face': (168, 696, 1.98, 3.14, 21.9, 9.1),
          'M': (112, 504, 1.43, 3.50, 12.4, 4.9)}
EXP569_OTHER = {'data': 28.3, 'centres': 1.8, 'remainder': 3.0}
sys.path.insert(0, str(main_file('research/direct-delivery504-global/vendor/gk/gk_word.py').parent))
import gk_common as co   # noqa: E402
import gk_word as g      # noqa: E402
g.V = co.V = 112
co.DATA = g.DATA = 7168
V = 112


def chains_gk(word):
    """frame-dimension chain per register and the paid runs per register (gk_word.profile semantics: a centre's copy
    descents to its served levels are paid at the cut and its later climbs start again from the centre frame)."""
    R = word['report']['R']
    n = 2 * V + R
    P = word['ports']
    cur = {}
    for r in range(n):
        if r < V:
            cur[r] = (P[r],)
        elif r >= 2 * V and str(r) in word.get('start_extra', {}):
            cur[r] = g.basis(word['start_extra'][str(r)])
        else:
            cur[r] = ()
    ch = {r: [len(cur[r])] for r in range(n)}
    paid = {r: [] for r in range(n)}

    def climb(r, F):
        F = g.basis(F)
        o = cur[r]
        assert g.basis(list(o) + list(F)) == F, 'frame violation'
        if o != F:
            ch[r].append(len(F))
            paid[r].append(len(F) - len(o))
            cur[r] = F
    lev = {int(t): g.basis(E) for t, E in word.get('target_levels', {}).items()}
    for seq, part in ((word['A'], 'A'), (word['B'], 'B')):
        if part == 'B':
            for r, f in zip(word['centers'], word['center_frames']):
                o = g.basis(f)
                assert cur[r] == o, 'centre frame'
                served = sorted({lev.get(e[1] - V, ()) for e in word['cut'] if e[2] == r}, key=lambda E: -len(E))
                for Lv in served:
                    if Lv != o:
                        paid[r].append(len(o) - len(Lv))
                        o = Lv
        for e in seq:
            for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
                climb(r, e[-1])
    for r in range(n):
        climb(r, g.FULL if (r < V or r >= 2 * V) else g.perp(P[r - V]))
    return ch, paid, R, set(word['centers'])


ch7, paid7, R, ctr = chains_gk(load_json(VENDOR / 'pr569' / 'width7-eight-FULL-WORD.json.gz'))
chF, paidF, RF, ctrF = chains_gk(load_json(VENDOR / 'pr569' / 'fourcold-eight-FULL-WORD.json.gz'))
runs = lambda paid, regs: Counter(x for r in regs for x in paid[r])
m, D, CALLS = 73, 2560, 72
dat = hist_of(Counter(tuple(ch7[r]) for r in range(2 * V)))
cen = runs(paid7, ctr)
hel = hist_of(Counter(tuple(ch7[r]) for r in range(2 * V, 2 * V + R) if r not in ctr))
locF = runs(paidF, range(2 * V + RF))
loc7 = runs(paid7, range(2 * V + R))
calls = load_json(DATA / 'prices' / 'pr569-provider-calls.json')['calls']    # #569's per-call dispatch
n7 = sum(1 for _, prov in calls if prov == 'width7_eight')
assert len(calls) == CALLS and n7 == 63
rem = {3: 1200, 7: 48, 48: 1808}   # #569's idle remainder (its hosting control is recomputed in e2_helper_prices.py)
P = Counter()
for r, z in loc7.items():
    P[r] += z * n7
for r, z in locF.items():
    P[r] += z * (CALLS - n7)
for r, z in rem.items():
    P[r] += z
PUB = {1: 169056, 2: 41184, 3: 25968, 4: 13824, 5: 4032, 6: 4032, 7: 48, 8: 576, 48: 1808}
check('E1.#569.profile', dict(P) == PUB and 73 * 7168 - sum(r * z for r, z in PUB.items()) == D,
      '63 width-7 calls + 9 four-cold calls + idle remainder = the published global profile; D = %d' % D)
b0 = root(PUB, m, D)
phi = lambda r: r * ((m / r) ** b0 - 1)
F = lambda h, k=CALLS: sum(z * k * phi(r) for r, z in h.items())
helall = Counter({r: z * CALLS for r, z in hel.items()})
hmass0 = sum(r * z for r, z in helall.items())
datg = Counter({r: z * CALLS for r, z in dat.items()})
ceng = Counter({r: z * CALLS for r, z in cen.items()})
base_b = proportional(m, D, datg + ceng, rem, helall, hmass0, hmass0)
cls = lambda h: 'factory' if h < 224 else ('face' if h < 392 else 'M')
for k in ('factory', 'face', 'M'):
    sub = Counter(tuple(ch7[r]) for r in range(2 * V, 2 * V + R) if r not in ctr and cls(r - 2 * V) == k)
    h = hist_of(sub)
    n, nr, mass = sum(sub.values()), sum(h.values()), sum(r * z for r, z in h.items())
    single = Counter()
    for p, z in sub.items():
        single[p[-1] - p[0]] += z
    hel2 = Counter(helall)
    for r, z in h.items():
        hel2[r] -= z * CALLS
    for r, z in single.items():
        hel2[r] += z * CALLS
    b2 = proportional(m, D, datg + ceng, rem, hel2, hmass0, hmass0)
    got = (n, nr, mass / nr, (nr - n) / n, 100 * F(h) / D, 100 * (b2 / base_b - 1))
    check('E1.#569.' + k, near_all(got, EXP569[k], (None, None, 2, 2, 1, 1)),
          '%s: n %d, runs %d, mean run %.2f, stops/register %.2f, F-share %.1f%%, all-single-run ceiling %+.1f%% b'
          % ((k,) + got))
got = (100 * F(dat) / D, 100 * F(cen) / D, 100 * F(rem, 1) / D)
check('E1.#569.data-centres-remainder', near_all(got, tuple(EXP569_OTHER.values()), (1, 1, 1)),
      'data %.1f%%, centres %.1f%%, idle remainder %.1f%% of sum phi' % got)
finish()
