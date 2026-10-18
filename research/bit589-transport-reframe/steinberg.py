"""Exhaustive Steinberg 3 -> 2 rewrites (PR548's mechanism, re-run greedily by PR589's tuner) with exact reframing.

Over F2, for single-source gates b: bt ^= bs and e reading or writing b's operands,
  case 1 (e: et ^= bt reads b's target):  b ; e  =  e ; b ; c   with c: et ^= bs,
  case 2 (e: bs ^= es writes b's source): b ; e  =  e ; b ; c   with c: bt ^= es,
so when e can be brought next to b and c can be brought next to them through commuting gates (the conditions of
PR589's tune.find_triples), the three gates b, e, c are replaced by e ; b at b's place. Every rewritten word is checked
by an exact F2 replay of D, A, scatter, B and the rebuilt literal-reverse C on all columns, and then gets the exact
optimum over all frame assignments (reframe.optimum). Single-source gates within one phase only.

Usage: steinberg.py WORD.json.gz C [--out FILE] [--independent] [--control]
  --independent: recompute every optimum with independent_check.py's implementation and require agreement.
  --control: expand PR589's phase A by one inverse rewrite (e ; b -> b ; e ; c on an adjacent pair, c relocated to its
  farthest commuting slot; seeded choice); the triple search on it must recover W's phase A exactly.
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import json
import os
import random
import sys
from collections import Counter, defaultdict
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reframe as R
import search as S


def f2_ok(word, A, B):
    """exact F2 endpoint of D, A, scatter, B, C (C = literal reverse of the z-destination gates of A then B)"""
    w = word.w
    V = word.V
    N = word.N
    val = [1 << i for i in range(N)]
    for f, t, ss in w['D']:
        for s in ss:
            val[t] ^= val[s]
    for f, t, ss in A:
        for s in ss:
            val[t] ^= val[s]
    snap = [val[q] for q in w['ret']]
    for t, ks in enumerate(w['scatter']):
        for k in ks:
            val[V + t] ^= snap[k]
    for f, t, ss in B:
        for s in ss:
            val[t] ^= val[s]
    for f, t, ss in reversed([g for g in A + B if g[1] < V or g[1] >= 2 * V]):
        for s in ss:
            val[t] ^= val[s]
    return all(val[r] == ((1 << r) ^ (1 << (r - V)) if V <= r < 2 * V else 1 << r) for r in range(N))


def triples(L):
    single = [len(g[2]) == 1 for g in L]
    pair, bysrc, bydst = defaultdict(list), defaultdict(list), defaultdict(list)
    for k, (f, t, ss) in enumerate(L):
        if single[k]:
            pair[(t, ss[0])].append(k)
            bysrc[ss[0]].append(k)
            bydst[t].append(k)
    out = []
    for pl, (fb, bt, bss) in enumerate(L):
        if not single[pl]:
            continue
        bs = bss[0]
        cands = [(1, pk, (L[pk][1], bs)) for pk in bysrc[bt] if pk > pl] + \
                [(2, pk, (bt, L[pk][2][0])) for pk in bydst[bs] if pk > pl]
        for case, pk, cp in cands:
            if not single[pk] or not all(S.commute(L[pk], L[j]) for j in range(pl + 1, pk)):
                continue
            for pq in pair.get(cp, []):
                if len({pl, pk, pq}) < 3:
                    continue
                lo, hi = min(pl, pq), max(pl, pq)
                if all(S.commute(L[pq], L[j]) for j in range(lo, hi + 1) if j not in (pk, pl, pq)):
                    out.append((case, pl, pk, pq))
    return out


def rewrite(L, pl, pk, pq):
    rest = [g for j, g in enumerate(L) if j not in (pl, pk, pq)]
    q = pl - (pq < pl)
    return rest[:q] + [L[pk], L[pl]] + rest[q:]


def search(word, z, indep=None):
    """all rewrites of the word; with indep (an independent_check.Problem), every optimum is recomputed by the
    independent implementation and must agree"""
    base = R.optimum(word, word.A, word.B, z)
    rows = []
    for sec in 'AB':
        L = getattr(word, sec)
        for case, pl, pk, pq in triples(L):
            new = rewrite(L, pl, pk, pq)
            A, B = (new, word.B) if sec == 'A' else (word.A, new)
            assert f2_ok(word, A, B), ('rewrite changes the map', sec, pl, pk, pq)
            o = R.optimum(word, A, B, z)
            if indep is not None:
                h = indep.optimum([(t, tuple(ss)) for f, t, ss in A], [(t, tuple(ss)) for f, t, ss in B])
                assert h == (None if o is None else o['profile']), ('implementations disagree', sec, pl, pk, pq)
            rows.append(((sec, case, pl, pk, pq), None if o is None else o['profile'],
                         None if o is None else o['cost'] - base['cost']))
    return base, rows


def expand_control(word, seed=14):
    """positive control for the triple finder and the rewrite. Under exact reframing every inverse expansion of this
    word is neutral, so the control tests detection and exact recovery rather than a cost gain: one adjacent
    single-source pair e ; b of phase A (case 1 in reverse: e: et ^= bt then b: bt ^= bs) becomes b ; e ; c with
    c: et ^= bs, and c is then relocated through commuting gates to the farthest slot. The map must be unchanged, and
    the 3 -> 2 search on the expanded word must list a triple whose rewrite gives back W's phase A exactly."""
    rng = random.Random(seed)
    L = word.A
    idx = [k for k in range(len(L) - 1) if len(L[k][2]) == 1 and len(L[k + 1][2]) == 1
           and L[k][2][0] == L[k + 1][1] and L[k][1] != L[k + 1][2][0] and L[k][1] != L[k + 1][1]]
    rng.shuffle(idx)
    for k in idx:
        e, b = L[k], L[k + 1]
        c = (e[0], e[1], (b[2][0],))
        stem = L[:k] + [b, e] + L[k + 2:]
        far = max(S.slots(stem, c, k + 2), key=lambda p: abs(p - (k + 2)))
        if far == k + 2:
            continue
        new = stem[:far] + [c] + stem[far:]
        assert f2_ok(word, new, word.B), 'expansion changes the map'
        return dict(pair_index=k, c_slot=far, moved_by=far - (k + 2)), new
    raise SystemExit('no control expansion found')


def main():
    path, c = sys.argv[1], Fraction(sys.argv[2])
    z = float(c)
    word = R.Word(R.load(path))
    report = {}
    if '--control' in sys.argv:
        info, new = expand_control(word)
        tr = triples(new)
        hits = [t for t in tr if rewrite(new, *t[1:]) == word.A]
        o = R.optimum(word, rewrite(new, *hits[0][1:]), word.B, z) if hits else None
        report = dict(info, triples_in_expanded_A=len(tr), recovering_triples=[list(t) for t in hits],
                      recovered_word_identical=bool(hits),
                      recovered_profile=None if o is None else {str(k): v for k, v in o['profile'].items()})
    else:
        indep = None
        if '--independent' in sys.argv:
            import gzip
            import independent_check as I
            w = json.load(gzip.open(path, 'rt'))
            w['_z'] = z
            indep = I.Problem(w)
        base, rows = search(word, z, indep)
        out = Counter('illegal' if p is None else 'same' if p == base['profile'] else
                      'better' if d < -1e-9 else 'worse' for _, p, d in rows)
        report = dict(word=os.path.basename(path), c=str(c), triples=len(rows),
                      by_section_case=dict(Counter('%s/case%d' % (r[0][0], r[0][1]) for r in rows)),
                      f2_checked=len(rows), independent_agree=len(rows) if indep is not None else None,
                      outcome=dict(out),
                      profiles=[p for _, p, _ in rows if p is not None])
    js = json.dumps(report, default=str)
    if '--out' in sys.argv:
        open(sys.argv[sys.argv.index('--out') + 1], 'w').write(js + '\n')
    print(js if '--control' in sys.argv else json.dumps({k: v for k, v in report.items() if k != 'profiles'}))


if __name__ == '__main__':
    main()
