"""Seeded random cross-check of the depth-two optimum: primary (reframe.py) versus independent (independent_check.py).

Draws legal first moves m1 and, for each, one interacting second move m2 from the primary generator (pairs.py's
class). Each pair is rebuilt twice, by search.apply and by independent_check.build (separate code, translated move
descriptions), and its exact optimal profile (or illegality) is computed by both implementations. This checks the
optimum on two-move words, not the pair enumeration (the generator is the depth-one generator, whose class count the
independent enumeration reproduces).

Usage: pair_sample_check.py WORD.json.gz C N SEED [--jobs J]
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import gzip
import json
import os
import random
import sys
from collections import Counter
from fractions import Fraction
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import independent_check as I
import reframe as R
import search as S
from pairs import View, moved_regs


def describe(cand):
    """search.py move tuple -> independent_check.build description (section, i, source, destination, index)"""
    if len(cand) == 6:
        kind, sec, i, s, dst, q = cand
        return (sec, i, s, dst, q)
    kind, sec, i, s, p = cand
    return (sec, i, s, sec, p)


_W = _P = _Z = None


def _init(path, z):
    global _W, _P, _Z
    _W = R.Word(R.load(path))
    w = json.load(gzip.open(path, 'rt'))
    w['_z'] = z
    _P = I.Problem(w)
    _Z = z


def _job(pairs):
    out = []
    for m1, m2 in pairs:
        A1, B1 = S.apply(_W, m1)
        A2, B2 = S.apply(View(_W, A1, B1), m2)
        o = R.optimum(_W, A2, B2, _Z)
        prim = None if o is None else o['profile']
        a1, b1 = I.build(_P.w, *describe(m1))
        w1 = dict(_P.w, A=[[0, t, list(ss)] for t, ss in a1], B=[[0, t, list(ss)] for t, ss in b1])
        a2, b2 = I.build(w1, *describe(m2))
        assert [(t, tuple(ss)) for f, t, ss in A2] == a2 and [(t, tuple(ss)) for f, t, ss in B2] == b2, (m1, m2)
        ind = _P.optimum(a2, b2)
        out.append((m1, m2, prim, ind))
    return out


def main():
    path, c, n, seed = sys.argv[1], Fraction(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else os.cpu_count()
    z = float(c)
    word = R.Word(R.load(path))
    rng = random.Random(seed)
    firsts = S.candidates(word) + S.cross_candidates(word)
    sample = []
    while len(sample) < n:
        m1 = rng.choice(firsts)
        A1, B1 = S.apply(word, m1)
        if R.optimum(word, A1, B1, z) is None:
            continue
        w1 = View(word, A1, B1)
        regs = moved_regs(word, m1)
        seconds = S.candidates(w1, regs) + S.cross_candidates(w1, regs)
        if seconds:
            sample.append((m1, rng.choice(seconds)))
    with Pool(jobs, initializer=_init, initargs=(path, z)) as pool:
        rows = [x for part in pool.imap(_job, [sample[k:k + 16] for k in range(0, n, 16)]) for x in part]
    base = R.optimum(word, word.A, word.B, z)['profile']
    agree = sum(p == q for _, _, p, q in rows)
    kinds = Counter('illegal' if p is None else 'base' if p == base else 'other' for _, _, p, _ in rows)
    print(json.dumps(dict(seed=seed, pairs=n, agree=agree, disagree=n - agree, primary_outcomes=dict(kinds),
                          first_disagreements=[[list(a), list(b), p, q] for a, b, p, q in rows if p != q][:3])))
    if agree != n:
        sys.exit(1)


if __name__ == '__main__':
    main()
