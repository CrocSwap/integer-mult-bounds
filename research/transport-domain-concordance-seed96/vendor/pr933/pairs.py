"""Depth-two extension: every legal first relocation m1 (any class of search.py, including across the scatter), then
every relocation m2 of the resulting word whose source gate touches a register of m1's moved operands or of m1's
remainder gate, then the exact frame optimum.

This is the interacting part of the two-move neighbourhood: m2 is enumerated on the word after m1 (its slots are those
of the changed order), so chains of the form "neutral move, then improving move" on a common register are covered.
Pairs whose moved operands share no register are outside this class.

Usage: pairs.py WORD.json.gz C [--jobs N] [--out FILE] [--first JSON_LIST_OF_FIRST_MOVES]
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0.
"""
import json
import os
import sys
import time
from collections import Counter
from fractions import Fraction
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reframe as R
import search as S


class View:
    """a Word with replaced phase-A/phase-B gate lists"""

    def __init__(self, word, A, B):
        self.__dict__.update(word.__dict__)
        self.A, self.B = A, B


def moved_regs(word, cand):
    kind, sec, i, s = cand[:4]
    f, t, ss = getattr(word, sec)[i]
    own = {t, s} if kind in ('summand', 'xsummand') else {t, *ss}
    return own | {t, *ss}  # the moved operands and the remainder gate's operands


_W = _Z = None


def _init(path, z):
    global _W, _Z
    _W = R.Word(R.load(path))
    _Z = z


def _eval(m1s):
    out = []
    for m1 in m1s:
        A1, B1 = S.apply(_W, m1)
        if R.optimum(_W, A1, B1, _Z) is None:
            continue
        w1 = View(_W, A1, B1)
        regs = moved_regs(_W, m1)
        n = legal = 0
        best = None
        prof = Counter()
        for m2 in S.candidates(w1, regs) + S.cross_candidates(w1, regs):
            assert moved_regs(w1, m2) & regs
            n += 1
            A2, B2 = S.apply(w1, m2)
            o = R.optimum(_W, A2, B2, _Z)
            if o is None:
                continue
            legal += 1
            key = tuple(sorted(o['profile'].items()))
            prof[key] += 1
            if best is None or o['cost'] < best[0]:
                best = (o['cost'], m2, o['profile'])
        out.append((m1, n, legal, best, dict(prof)))
    return out


def main():
    path = sys.argv[1]
    c = Fraction(sys.argv[2])
    z = float(c)
    jobs = int(sys.argv[sys.argv.index('--jobs') + 1]) if '--jobs' in sys.argv else os.cpu_count()
    outp = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    t0 = time.time()
    word = R.Word(R.load(path))
    base = R.optimum(word, word.A, word.B, z)
    cands = S.candidates(word) + S.cross_candidates(word)
    if '--first' in sys.argv:  # restrict the first moves (used by the positive control)
        cands = [tuple(m) for m in json.loads(sys.argv[sys.argv.index('--first') + 1])]
    batches = [cands[k:k + 16] for k in range(0, len(cands), 16)]
    rows = []
    with Pool(jobs, initializer=_init, initargs=(path, z)) as pool:
        for part in pool.imap(_eval, batches):
            rows.extend(part)
    pairs = sum(r[1] for r in rows)
    legal = sum(r[2] for r in rows)
    profiles = Counter()
    for r in rows:
        for k, n in r[4].items():
            profiles[k] += n
    allbest = sorted((r[3][0] - base['cost'], r[0], r[3][1], r[3][2]) for r in rows if r[3] is not None)
    report = dict(
        word=os.path.basename(path), c=str(c), base_profile=base['profile'], base_cost=base['cost'],
        first_candidates=len(cands), first_moves=len(rows), pairs=pairs, legal_pairs=legal,
        improving_pairs=sum(1 for r in rows if r[3] is not None and r[3][0] - base['cost'] < -1e-9),
        distinct_optimal_profiles=len(profiles),
        pairs_with_base_profile=profiles.get(tuple(sorted(base['profile'].items())), 0),
        best=[dict(delta=d, m1=list(a), m2=list(b), profile=p) for d, a, b, p in allbest[:10]],
        profiles=[[dict(k), n] for k, n in sorted(profiles.items(), key=lambda x: (-x[1], x[0]))],
        seconds=round(time.time() - t0, 1))
    js = json.dumps(report, indent=1, default=str)
    if outp:
        open(outp, 'w').write(js + '\n')
    print(js)


if __name__ == '__main__':
    main()
