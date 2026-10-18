"""A. Format ceiling, rev. 2: where the frontier words lose against the s = 9 skeleton (gap decomposition).

All roots are certified upper ends of the pressure root at the word's own (m, D); every step keeps the rank mass
m W - D fixed.  Steps:
  A  theorem skeleton (R-free, idle slots charged at cap max(r, h));
  B  literal R = 0 profile (each idle slot one child of its own rank);
  C  B with the real data-register runs and the real copy children;
  D  C plus every helper run paid as its own child, unhosted (the idle slots stay paid in full; this is the only step
     whose rank mass differs: it adds the helper mass, as if helpers lived on their own bank wires at the same D);
  E  the real word (helpers hosted whole into idle frame changes; the idle remainders paid).
#555 (bit): data, helper and copy runs are replayed from the published word (bitE8mut-p111.json.gz) and the idle
remainder is the published global profile minus s T times the per-stage local profile.
#568 (complex): the data-register runs per call are measured on the four-cold provider word of #569 (the same x/y
ladders as #568's providers); the paid idle remainder is an input recorded from #568's hosting (data/ceiling/
gap568-inputs.json); the helper runs are the published global profile minus data, centres and idle remainder.
"""
from collections import Counter, defaultdict
from fractions import Fraction as Fr
import sys

import numpy as np

from cert import root_bracket
from report import DATA, REPO, VENDOR, check, finish, load_json, main_file
from skel import idle_slots

EXPECTED = {
    '#555': {'A': 4.6072e-3, 'B': 4.5661e-3, 'C': 3.7868e-3, 'D': 1.6183e-3, 'E': 1.7331e-3},
    '#568': {'A': 3.9946e-3, 'B': 3.9631e-3, 'C': 3.1544e-3, 'D': 1.3517e-3, 'E': 1.5987e-3},
}
EXPECTED_555_RUNS = {'x': {1: 317, 2: 209, 3: 10, 4: 3}, 'y': {1: 10, 2: 92, 5: 92, 6: 10, 7: 9},
                     'h': {1: 994, 2: 1041, 3: 70, 4: 44, 5: 10}}
EXPECTED_568_DATA = {1: 718, 2: 74, 3: 60, 4: 92, 5: 42, 6: 28}


def add(*ds):
    c = Counter()
    for d in ds:
        for r, z in d.items():
            c[r] += z
    return c


def mul(d, n):
    return {r: z * n for r, z in d.items()}


def skeleton(s, h, v, T, cst):
    a, K = h - 1, (s - 1) // 2
    idle_r, idle_cap = Counter(), Counter()
    for r in idle_slots(K, a):
        idle_r[r] += 2 * v * T
        cap = max(r, h)
        idle_cap[Fr(cap)] += Fr(2 * r * v * T, cap)
    return {a: 2 * v * s * T}, {h: Fr(s * T * cst, h)}, idle_r, idle_cap


def roots(name, cases, m, D):
    out = {}
    for key, p in cases.items():
        lo, hi = root_bracket(dict(p), m, D, hi=Fr(1, 50))
        out[key] = float(hi)
    masses = {key: sum(r * z for r, z in p.items()) for key, p in cases.items()}
    hosted = sum(r * z for r, z in cases['D'].items()) - sum(r * z for r, z in cases['C'].items())
    ok = (all(abs(out[k] / EXPECTED[name][k] - 1) < 1.2e-4 for k in out)      # 5 significant digits
          and masses['A'] == masses['B'] == masses['C'] == masses['E']
          and masses['D'] == masses['E'] + hosted)
    check('A4.gap.' + name, ok, '  '.join('%s %.4e' % (k, out[k]) for k in out) + '  (rank mass %s)' % {k: int(v) for k, v in masses.items()})
    lnAE = np.log(out['A'] / out['E'])
    shares = {'literal': np.log(out['A'] / out['B']), 'fragmentation': np.log(out['B'] / out['C']),
              'helpers': np.log(out['C'] / out['D']), 'hosting': np.log(out['D'] / out['E'])}
    print('     log shares of ln(A/E) = %.3f: ' % lnAE + ', '.join('%s %.0f%%' % (k, 100 * v / lnAE) for k, v in shares.items()))
    return out


# ---- #555 (bit, s = 9, v = 111, cst = 63, T = 32, h = 8, m = 64)
s, h, v, T, m = 9, 8, 111, 32, 64
D = T * ((s - 1) * v - s * 63)
e555 = load_json(VENDOR / 'pr555' / 'EXPECTED.json')
w = load_json(VENDOR / 'pr555' / 'bitE8mut-p111.json.gz')
lines = np.array(w['lines'], float)
dims = [int(np.linalg.matrix_rank(lines[F])) if F else 0 for F in w['frames']]
cur = list(w['start'])
runs = defaultdict(list)
for ph in 'DABC':
    for f, dst, srcs in w[ph]:
        for r in [dst] + list(srcs):
            if cur[r] != f:
                runs[r].append(abs(dims[f] - dims[cur[r]]))
                cur[r] = f
for r in range(len(cur)):
    if cur[r] != w['final'][r]:
        runs[r].append(abs(dims[w['final'][r]] - dims[cur[r]]))
cls = lambda r: 'x' if r < v else ('y' if r < 2 * v else 'h')
H = {c: Counter() for c in 'xyh'}
for r, L in runs.items():
    for d in L:
        H[cls(r)][d] += 1
check('A4.runs.#555', all(dict(H[c]) == EXPECTED_555_RUNS[c] for c in 'xyh')
      and sum(r * z for r, z in H['h'].items()) == 8 * w['R'],
      'per-stage runs x %s, y %s, helpers %s (helper mass 8R = %d)' % (dict(sorted(H['x'].items())),
                                                                      dict(sorted(H['y'].items())),
                                                                      dict(sorted(H['h'].items())), 8 * w['R']))
S = s * T
local = add(H['x'], H['y'], H['h'], {7: 9})
check('A4.local.#555', dict(local) == {int(k): z for k, z in e555['word']['local_histogram'].items()},
      'replayed runs + 9 copy children of rank 7 = the published per-stage local histogram')
real = {int(r): z for r, z in e555['nine']['profile'].items()}
rem = Counter(real)
for r, z in mul(local, S).items():
    rem[r] -= z
rem = {r: z for r, z in rem.items() if z}
data1, cop, idle_r, idle_cap = skeleton(s, h, v, T, 63)
datareal = mul(add(H['x'], H['y']), S)
helpers = mul(H['h'], S)
cases = {'A': add(data1, cop, idle_cap), 'B': add(data1, cop, idle_r), 'C': add(datareal, {7: 9 * S}, idle_r),
         'D': add(datareal, {7: 9 * S}, idle_r, helpers), 'E': add(datareal, {7: 9 * S}, helpers, rem)}
hosted = sum(r * z for r, z in helpers.items())
idlemass = sum(r * z for r, z in idle_r.items())
check('A4.hosted.#555', hosted == 288 * 3512 and idlemass == 1342656,
      'hosted helper mass %d = 75.3%% of the skeleton idle mass %d; paid idle remainder %s' % (hosted, idlemass, rem))
roots('#555', cases, m, D)

# ---- #568 (complex, s = 9, v = 112, cst = 64, T = 8, h = 9, m = 73)
s, h, v, T, m = 9, 9, 112, 8, 73
D = T * ((s - 1) * v - s * 64)
S = s * T
sys.path.insert(0, str(main_file('research/direct-delivery504-global/vendor/gk/gk_word.py').parent))
import gk_common as co   # noqa: E402  (#531's word helpers on main)
import gk_word as g      # noqa: E402
g.V = co.V = 112
co.DATA = g.DATA = 7168
word = load_json(VENDOR / 'pr569' / 'fourcold-eight-FULL-WORD.json.gz')
V = 112
cur = {r: ((word['ports'][r],) if r < V else ()) for r in range(2 * V)}
paid = Counter()


def climb(r, F):
    if r >= 2 * V:
        return
    F = g.basis(F)
    o = cur[r]
    assert g.basis(list(o) + list(F)) == F, 'frame violation'
    if o != F:
        paid[len(F) - len(o)] += 1
        cur[r] = F


for seq in (word['A'], word['B']):
    for e in seq:
        for r in [e[1]] + ([e[2]] if e[0] == 'add' else []):
            climb(r, e[-1])
for r in range(2 * V):
    climb(r, g.FULL if r < V else g.perp(word['ports'][r - V]))
check('A4.data.#568', dict(paid) == EXPECTED_568_DATA and sum(r * z for r, z in paid.items()) == 2 * 112 * 8,
      'data-register runs per call %s (mass 2 v a = 1792)' % dict(sorted(paid.items())))
p568 = load_json(VENDOR / 'pr568' / 'PLAN.json.gz')
real = {int(r): z for r, z in p568['profile'].items()}
inp = load_json(DATA / 'ceiling' / 'gap568-inputs.json')
idle_rem = {int(r): z for r, z in inp['idle_remainder'].items()}
datareal = mul(dict(paid), S)
cent = {8: 8 * S}
hel = Counter(real)
for r, z in add(datareal, cent, idle_rem).items():
    hel[r] -= z
check('A4.inputs.#568', sum(idle_rem.values()) == 4018 and all(z >= 0 for z in hel.values()) and max(r for r, z in hel.items() if z) <= 6,
      'recorded idle remainder has 4018 children (= the "4,018 positive idle remainders" of #568\'s README); implied helper '
      'histogram %s is nonnegative with ranks <= 6 <= h' % dict(sorted((r, z) for r, z in hel.items() if z)))
hel = {r: z for r, z in hel.items() if z}
data1, cop, idle_r, idle_cap = skeleton(s, h, v, T, 64)
cases = {'A': add(data1, cop, idle_cap), 'B': add(data1, cop, idle_r), 'C': add(datareal, cent, idle_r),
         'D': add(datareal, cent, idle_r, hel), 'E': add(datareal, cent, hel, idle_rem)}
roots('#568', cases, m, D)
finish()
