"""Frame-intersection certificate (README Lemma 3.3) and the realisation-free floors of Corollary 3.4.  Exact bitmask arithmetic; standard library only.
For each unit: all maximal cliques of the orthogonality graph (frames = cliques of size T), all 2^h - 1 label classes (supports of the
nonzero vectors of col B, B = dense pairing), and for each class: does it contain a T-frame, or is it certified by clause (c)?"""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from collections import Counter
from frames import *

U = units(); R = {}
t0 = time.time()
for n, (L, T) in U.items(): R[n] = analyse(L, T)
print('   (analysis %.0f s)' % (time.time() - t0))
exp = {  # name: (v, T, h, alpha_orth, #T-frames, classes with a T-frame, certified by (c), uncertified, uncertified sizes, contains 2-dim subspace)
    'D4': (12, 4, 3, 4, 3, 7, 0, 0, [], False), 'D6': (30, 6, 5, 6, 15, 16, 15, 0, [], False),
    'E7': (63, 7, 7, 7, 135, 64, 63, 0, [], False), 'E8': (120, 8, 9, 8, 2025, 391, 120, 0, [], False),
    'P104': (104, 8, 9, 8, 759, 375, 104, 32, [52], False), 'P112': (112, 8, 9, 8, 1260, 383, 112, 16, [56], False),
    'E7-frame': (56, 7, 7, 7, 64, 57, 56, 14, [24, 32], True),
    'E6': (36, 6, 7, 4, 0, 0, 0, 127, [16, 20, 36], True), 'D5': (20, 5, 5, 4, 0, 0, 0, 31, [8, 12, 20], True)}
for n, e in exp.items():
    a = R[n]
    got = (a['v'], a['T'], a['h'], a['alpha'], a['nframes'], len(a['has_frame']), len(a['cert_c']), len(a['unc']),
           sorted(set(popcount(w) for _, w in a['unc'])), a['sub2'])
    check('c3.table.' + n, got == e, '%s: v,T,h,alpha_orth,#T-frames,#classes with T-frame,#certified by (c),#uncertified,sizes,2-dim subspace of uncertified = %s' % (n, got))
# the classes certified by clause (c) are exactly the neighbourhoods N(alpha); any other classes without a T-frame remain uncertified
for n in ('D6', 'E7', 'E8', 'P112', 'P104', 'E7-frame'):
    L, T = U[n]; a = R[n]; G = gram(L); v = len(L)
    N = set(sum(1 << s for s in range(v) if s != x and G[x][s] != 0) for x in range(v))
    ws = set(w for _, w in a['cert_c'])
    check('c3.N.' + n, ws == N, '%s: the %d classes certified by clause (c) are exactly the %d neighbourhoods N(alpha); uncertified classes are counted separately' % (n, len(ws), len(N)))
# E8: every frame not through alpha meets N(alpha) in exactly 4 lines
L, T = U['E8']; G = gram(L); a = R['E8']
meets = Counter()
for al in range(0, 120, 7):
    Na = sum(1 << s for s in range(120) if s != al and G[al][s] != 0)
    for f in a['frames']:
        if not f >> al & 1: meets[popcount(f & Na)] += 1
check('c3.e8meet', set(meets) == {4}, 'E8: every 8-frame not through alpha meets N(alpha) in exactly 4 lines (alpha ranging over 18 lines; W(E8) is transitive): %s' % dict(meets))
# P104 and P112: with delta <= 1 on each side the pair ranks of the uncertified-or-full supports give the floor
for n, want in (('P104', 56), ('P112', 56)):
    L, T = U[n]; a = R[n]; v = len(L); Br = a['Br']; full = (1 << v) - 1; basis = a['basis']; h = a['h']
    def rows_rank(S):                       # dim of span of the F2 row-coordinates of the lines of S in col(B)  (delta = h - this)
        # coordinates of line t w.r.t. 'basis': c_t(i) = bit t of ... use the row space description instead: rank of the matrix B[S, :]
        return rank_f2([Br[t] for t in bits(S)])
    comp = [full & ~w for _, w in a['unc']] + [full]
    okd = all(h - rows_rank(c) == 1 for c in comp[:-1]) and rows_rank(full) == h
    cnt = Counter(blk(Br, bits(R_), bits(A_)) for R_ in comp for A_ in comp)
    check('c3.pairs.' + n, okd and min(cnt) * T == want, '%s: (uncertified-or-full) x (uncertified-or-full) pair ranks %s; each uncertified class has deficiency exactly 1; floor T*min = %d' % (n, dict(sorted(cnt.items())), T * min(cnt)))
# D5 / E6: no T-frame, every class uncertified (nothing claimed beyond the Gram realisation)
check('c3.noframes', R['E6']['nframes'] == 0 and R['D5']['nframes'] == 0 and R['E6']['alpha'] == 4 and R['D5']['alpha'] == 4, 'E6 and D5: alpha_orth = 4 < T, no T-frame (realisation-free statement not available)')
finish()
