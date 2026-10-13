"""Barnes-Wall BW16 as a unit for the E8-style decoder screen: the checks behind README.md (no kappa claim).

Run from the repository root:  python3 -B research/bw16-unit-screen/bw16_check.py
Standard library only. The ceiling X(s, h, k, x) is #595's certified function, imported unchanged from
research/format-limits/scripts/skel.py, exactly as research/e8-decoder-floors-and-cold14-notes/ade_screen.py uses it."""
import collections
import itertools
import json
import operator
import os
import sys
from fractions import Fraction as Fr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'research', 'format-limits', 'scripts'))
from skel import X  # noqa: E402

N_CHECKS = 0


def check(name, ok, detail=''):
    global N_CHECKS
    N_CHECKS += 1
    print('%-4s %-46s %s' % ('ok' if ok else 'FAIL', name, detail), flush=True)
    if not ok:
        sys.exit(1)


# 1. BW16 = RM(1,4) + 2 RM(3,4) + 4 Z^16 (Construction D); minimal norm 8 in this scaling.
def rm(r, m=4):
    pts = list(itertools.product((0, 1), repeat=m))
    rows = [tuple(int(all(p[i] for i in S)) for p in pts)
            for k in range(r + 1) for S in itertools.combinations(range(m), k)]
    code = {(0,) * 16}
    for row in rows:
        code |= {tuple((a + b) % 2 for a, b in zip(c, row)) for c in code}
    return code


RM1, RM3 = rm(1), rm(3)
check('RM(1,4) and RM(3,4)', len(RM1) == 32 and len(RM3) == 2 ** 15 and RM1 <= RM3, '32 and 32768 words, nested')
check('RM(1,4) weights', sorted({sum(c) for c in RM1}) == [0, 8, 16], '0, 8, 16')
check('RM(3,4) = even-weight code', all(sum(c) % 2 == 0 for c in RM3), '')


def member(x):
    c1 = tuple(v % 2 for v in x)
    if c1 not in RM1:
        return False
    return tuple(((v - a) // 2) % 2 for v, a in zip(x, c1)) in RM3


# A vector of norm <= 8 has at most 8 odd coordinates, and they form a word of RM(1,4): 0 or 8 of them.
#  8 odd: the odd entries are +-1 (norm already 8) and the rest 0, so shape (+-1^8) on a weight-8 word.
#  0 odd: x = 2y with |y|^2 <= 2 and y mod 2 an even-weight word, so y = +-e_i +- e_j: shape (+-2^2).
# So the minimal vectors are exactly these two families; both are enumerated in full.
vecs = []
for i, j in itertools.combinations(range(16), 2):
    for a, b in itertools.product((2, -2), repeat=2):
        v = [0] * 16
        v[i] = a
        v[j] = b
        vecs.append(tuple(v))
check('shape (2^2): all in the lattice', all(member(v) for v in vecs), '%d vectors' % len(vecs))
n_odd_tried = 0
for c in sorted(RM1):
    if sum(c) != 8:
        continue
    idx = [i for i in range(16) if c[i]]
    for sg in itertools.product((1, -1), repeat=8):
        v = [0] * 16
        for i, s in zip(idx, sg):
            v[i] = s
        n_odd_tried += 1
        if member(tuple(v)):
            vecs.append(tuple(v))
check('shape (1^8): half of each sign class', n_odd_tried == 30 * 256 and len(vecs) == 480 + 30 * 128,
      '%d of %d sign patterns lie in the lattice' % (len(vecs) - 480, n_odd_tried))
check('minimal vectors = kissing number of BW16', len(vecs) == 4320, '4320')
# The only norm < 8 candidates are x = 2y with |y|^2 = 1 (the 8-odd family already has norm 8).
check('no nonzero vector of norm < 8', not any(member(tuple(2 * sg * int(k == i) for k in range(16)))
                                               for i in range(16) for sg in (1, -1)), 'x = +-2 e_i excluded')

lines = sorted({v if next(a for a in v if a) > 0 else tuple(-a for a in v) for v in vecs})
v_lines = len(lines)
check('lines', v_lines == 2160, '2160')


def ip(u, w):
    return sum(map(operator.mul, u, w))


# 2. inner-product classes, for every line; nonorth[i] is the bitmask of lines not orthogonal to line i
nonorth = []
profile_ok = True
for k, L in enumerate(lines):
    cnt = collections.Counter()
    m = 0
    for j, M in enumerate(lines):
        if j == k:
            continue
        g = abs(ip(L, M))
        cnt[g] += 1
        if g:
            m |= 1 << j
    nonorth.append(m)
    profile_ok &= dict(cnt) == {0: 855, 2: 1024, 4: 280}
check('|<x,y>| profile of every line', profile_ok, '{0: 855, 2: 1024, 4: 280}: two nonzero classes, degree 1304')

# 3. a 72-line set K of pairwise non-orthogonal lines (frozen in data/, reproduced by a deterministic greedy)
index = {L: k for k, L in enumerate(lines)}
K = [tuple(L) for L in json.load(open(os.path.join(HERE, 'data', 'clique72.json')))]
check('frozen clique lines are BW16 lines', all(L in index for L in K) and len(set(K)) == 72, '72 distinct lines')
check('frozen clique is pairwise non-orthogonal', all(ip(a, b) != 0 for a, b in itertools.combinations(K, 2)),
      str(dict(sorted(collections.Counter(abs(ip(a, b)) for a, b in itertools.combinations(K, 2)).items()))))
shapes = collections.Counter('(1^8)' if 1 in map(abs, L) else '(2^2)' for L in K)
G, cand = [], (1 << v_lines) - 1
while cand:
    i = max((i for i in range(v_lines) if cand >> i & 1), key=lambda i: ((nonorth[i] & cand).bit_count(), -i))
    G.append(i)
    cand &= nonorth[i]
check('deterministic greedy reproduces the clique', sorted(lines[i] for i in G) == sorted(K),
      'max degree in the candidate set, ties to the smallest index; shapes %s' % dict(shapes))

# E8 reference (doubled coordinates): 120 lines, 63 orthogonal neighbours each, largest non-orthogonal set exactly 8
E8 = [tuple(2 * (k == i) + 2 * s * (k == j) for k in range(8))
      for i, j in itertools.combinations(range(8), 2) for s in (1, -1)]
E8 += [sg for sg in itertools.product((1, -1), repeat=8) if sg[0] == 1 and sg.count(-1) % 2 == 0]
e8_nb = [sum(1 << j for j in range(120) if j != i and ip(E8[i], E8[j])) for i in range(120)]
e8_best = [0]


def grow(P, size):                                                   # exhaustive branch and bound
    if size + P.bit_count() <= e8_best[0]:
        return
    if not P:
        e8_best[0] = size
    while P and size + P.bit_count() > e8_best[0]:
        u = P.bit_length() - 1
        P &= ~(1 << u)
        grow(P & e8_nb[u], size + 1)


grow((1 << 120) - 1, 0)
check('E8 reference', len(E8) == 120 and all(119 - m.bit_count() == 63 for m in e8_nb) and e8_best[0] == 8,
      '63 orthogonal neighbours per line; largest non-orthogonal set 8 (exact)')

# 4. window bounds at the decoder pattern of format-limits C.6 (B_TS = 0 where G_TS != 0, B_TT = 1, over F2).
# On K the pattern forces B[K, K] = I, so window = rank B >= |K|. The pattern's natural decoder B0 = I + [orthogonal]
# (the analogue of E8's B0 = (J + G) mod 2) satisfies it, so its F2 rank bounds the least window from above.
def f2_rank(rows):
    piv = {}
    r = 0
    for row in rows:
        while row:
            h = row.bit_length() - 1
            if h in piv:
                row ^= piv[h]
            else:
                piv[h] = row
                r += 1
                break
    return r


full = (1 << v_lines) - 1
B0 = [(full & ~nonorth[i]) for i in range(v_lines)]                 # orthogonal lines and the diagonal
check('B0 obeys the pattern', all((B0[i] >> i) & 1 and not (B0[i] & nonorth[i]) for i in range(v_lines)), '')
c_lo, c_hi = len(K), f2_rank(B0)
check('window bracket', c_lo <= c_hi, '%d <= c_min <= rank_F2(B0) = %d (E8: c = 9)' % (c_lo, c_hi))

# 5. main's ADE screen: h = lattice rank, k = 1, x = c*h/v (ade_screen.py), here at the certified c >= 72
h_bw = 16
x_bw = Fr(c_lo * h_bw, v_lines)
check('copy proxy x = c*h/v at c = 72', x_bw == Fr(8, 15), '8/15')
S = range(3, 40, 2)
e8_bit = X(5, 8, 1, Fr(63, 111))                                     # #595 A.3: X* = 6.0005e-3, bit P111
e8_full = X(5, 8, 1, Fr(3, 5))                                       # full 120-line E8, c = 9: x = 3/5
check('E8 bit ceiling reproduced', abs(float(e8_bit['lo']) - 6.0005e-3) < 1e-7, '%.6e at s = 5' % e8_bit['lo'])
bw = {s: X(s, h_bw, 1, x_bw) for s in S}
best_s = max((s for s in S if bw[s]), key=lambda s: bw[s]['hi'])
check('BW16 ceiling below E8 bit at every s in 3..39', all((r is None) or r['hi'] < e8_bit['lo'] for r in bw.values()),
      'max %.4e at s = %d; E8 bit %.4e (ratio %.3f)' % (bw[best_s]['hi'], best_s, e8_bit['lo'],
                                                       float(bw[best_s]['hi'] / e8_bit['lo'])))
check('BW16 ceiling below full-E8 ceiling', all((r is None) or r['hi'] < e8_full['lo'] for r in bw.values()),
      'E8 x = 3/5: %.4e' % e8_full['lo'])
free = X(3, h_bw, 1, Fr(0))
check('copy-free BW16 would beat E8 (loss is the copy charge)', free['lo'] > e8_bit['hi'], 'X(3, 16, 1, 0) = %.4e' % free['lo'])


# X is non-increasing in x (#595 A.2), so the break-even c is found at s = 3 (binding here) and then checked at
# every s, at c and at c - 1.
def loses(c, stages):
    xc = Fr(c * h_bw, v_lines)
    return all((r is None) or r['hi'] < e8_bit['lo'] for r in (X(s, h_bw, 1, xc) for s in stages))


c_be = next(c for c in range(73) if loses(c, (3,)))
check('break-even window', c_be < c_lo and loses(c_be, S) and not loses(c_be - 1, S),
      'BW16 loses at every s in 3..39 iff c >= %d; certified c >= %d' % (c_be, c_lo))
print('PASS_BW16_UNIT_SCREEN (%d checks)' % N_CHECKS)
