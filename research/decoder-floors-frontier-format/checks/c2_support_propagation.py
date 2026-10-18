"""Lemma 1.1 (support propagation) census and the survivor pair ranks behind Theorem P (IDEAL3 THEORY §1.1-1.3).  Exact bitmask arithmetic, standard library only.
A label class O is the support of a nonzero vector of col B (B = dense pairing, rank h).  O is *deficient* in a rank-T realisation M iff some functional
h* != 0 kills p0(O).  Lemma 1.1: for every T-frame E write h* = sum_e c_e q0(e); then c_e = 0 on E cap O, and for every T-frame F,
supp(c) subset (E \\ O) cap union_{g in F \\ O} Nbar(g), Nbar(x) = {lines non-orthogonal to x} (x itself included).  Iterate to the fixed point; if some S_E becomes
empty then O is non-deficient in EVERY rank-T realisation.  Survivors = classes that are not certified."""
import sys, os, time, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from report import check, finish
from units import *

from supprop import setup, propagate, census

t0 = time.time()
L112 = sub(P112_IDX); L104 = sub(unit_idx('P104H4'))
from roots import D4, D6, E7, E8
exp = {  # name: (lines, T, #frames, #classes, #survivors, survivor sizes)
    'D4': (D4, 4, 3, 7, 0, []), 'D6': (D6, 6, 15, 31, 0, []), 'E7': (E7, 7, 135, 127, 0, []),
    'E8': (E8, 8, 2025, 511, 0, []), 'P112': (L112, 8, 1260, 511, 8, [56]), 'P104': (L104, 8, 759, 511, 16, [52])}
R = {}
for n, (L, T, nf, ncl, nsurv, sizes) in exp.items():
    r = census(L, T); R[n] = r
    got = (r['nframes'], r['nclasses'], len(r['unc']), sorted(set(popcount(w) for _, w in r['unc'])))
    check('c2.cert.' + n, got == (nf, ncl, nsurv, sizes), '%s (T=%d, h=%d): %d T-frames, %d label classes, %d not certified by Lemma 1.1, sizes %s' % (n, T, r['h'], got[0], got[1], got[2], got[3]))
print('   (census %.0f s)' % (time.time() - t0))
# survivors: no 2-dim subspace; each survivor is the set of live lines orthogonal to one removed root f in F0 (P112) / in F0 u F1 (P104) and has Q-rank 7
for n, L, removed in (('P112', L112, F0), ('P104', L104, F0 + H4F1)):
    unc = R[n]['unc']; cos = set(c for c, _ in unc)
    sub2 = any((a ^ b) in cos for a, b in itertools.combinations(sorted(cos), 2))
    check('c2.nosub2.' + n, not sub2, '%s: the %d survivor classes contain no 2-dimensional subspace of the label space (a ^ b is never a survivor)' % (n, len(unc)))
    ws = set(w for _, w in unc); want = set()
    for f in removed:
        want.add(sum(1 << i for i, r in enumerate(L) if dot(r, E8[f]) == 0))
    check('c2.perp.' + n, ws == want, '%s: the survivors are exactly the sets of live lines orthogonal to one removed root (%d of them)' % (n, len(want)))
    rk = set(rank_q([list(L[i]) for i in range(len(L)) if w >> i & 1]) for w in ws)
    check('c2.qrank.' + n, rk == {7}, '%s: each survivor spans a 7-dimensional space over Q (Gram-deficient), rank_Q = %s' % (n, sorted(rk)))
# pair ranks  rank_F2 B[V \ O, V \ O'] over all survivor pairs (O = O' included)
for n, L in (('P112', L112), ('P104', L104)):
    unc = R[n]['unc']; Br = R[n]['Br']; v = len(L); full = (1 << v) - 1; out = {}
    for (_, O), (_, O2) in itertools.product(unc, unc):
        k = blk(Br, bits(full & ~O), bits(full & ~O2)); out[k] = out.get(k, 0) + 1
    want = {8: 64} if n == 'P112' else {8: 192, 7: 64}
    check('c2.pairs.' + n, out == want, '%s: rank_F2 B[V\\O, V\\O\'] over all %d ordered survivor pairs (O = O\' included) takes the values %s (value: count); the minimum is %d, i.e. every term costs at least %d' % (n, len(unc) ** 2, out, min(out), min(out)))

# exactness of the per-term rank: Def(V \\ O) = {0, w_O} for every survivor O (so the pair ranks above are the ranks of the pairs (Def(R), Def(A)) = (<w_O>, <w_O'>)),
# and the single-deficiency ranks rank B[V \\ O, V] (the (1, 0) and (0, 1) cases)
for n, L in (('P112', L112), ('P104', L104)):
    unc = R[n]['unc']; Br = R[n]['Br']; v = len(L); full = (1 << v) - 1; classes = span_vectors(colspace_basis(Br))
    ok = all(sorted(w for _, w in classes if w & ~O == 0) == [O] for _, O in unc)
    check('c2.def.' + n, ok, '%s: for every survivor O the classes with support inside O are exactly {O} itself, so Def(V \\ O) is the one-dimensional space <w_O>' % n)
    single = set(blk(Br, bits(full & ~O), list(range(v))) for _, O in unc)
    check('c2.single.' + n, single == {8}, '%s: rank_F2 B[V \\ O, V] = %s for every survivor O (a single deficiency costs one unit of rank: 9 - 1)' % (n, sorted(single)))
# gauge: dense B has rank h and the survivors are the only non-certified classes => Theorem P's per-term floor 9 - delta(R) - delta(A) >= 8 with delta <= 1
for n in ('P112', 'P104', 'E8', 'E7'):
    h = R[n]['h']; check('c2.rankB.' + n, h == (7 if n == 'E7' else 9), '%s: rank_F2 of the dense pairing is %d' % (n, h))
finish()
