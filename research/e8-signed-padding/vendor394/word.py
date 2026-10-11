"""Insert helper uncompute ('in') gates into a gcert/1 word after given A++B gate indices (0-based, original word);
recompute blocks/N exactly as gx.check1 counts them.  Own code."""
import copy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxkernel import rehist


def insert(c, sinks):
    """sinks: dicts with sink_helper, cut_group (insert after this original gate), frame, uncompute=[[donor, a, b]]
    meaning sink += (a/b)*donor.  Several gates at one cut keep list order."""
    c = copy.deepcopy(c); nA = len(c['A']); by = {}
    for s in sinks: by.setdefault(s['cut_group'], []).append(s)
    A, B = [], []
    for i, g in enumerate(c['A'] + c['B']):
        (A if i < nA else B).append(g)
        for s in by.get(i, []):
            (A if i < nA else B).append(['in', s['frame'], s.get('target', s['sink_helper']), [list(x) for x in s['uncompute']]])
    c['A'], c['B'] = A, B
    return rehist(c)


def origmap(c, sinks):
    """index in the inserted word -> original cut index"""
    by = {}
    for s in sinks: by.setdefault(s['cut_group'], []).append(s)
    m = []
    for i in range(len(c['A']) + len(c['B'])):
        m.append(i); m.extend(i for _ in by.get(i, []))
    return m


def sixths(gs):
    """Rewrite a two-donor uncompute r += a*p + (a/2)*q (quarter coefficient) as three same-frame gates
    p += q/2;  r += a*p;  p -= q/2, so every intermediate entry stays in sixths (gxcore E5 units) and every
    coefficient has denominator <= 2.  The donor p is restored immediately; the net scalar map is identical."""
    from fractions import Fraction as F
    out = []
    for g in gs:
        u = g['uncompute']
        if all(b in (1, 2, 3, 6) for _, _, b in u): out.append(g); continue
        assert len(u) == 2
        (p, a1, b1), (q, a2, b2) = sorted(u, key=lambda x: x[2])
        a, bq = F(a1, b1), F(a2, b2); h = bq / a
        assert h.denominator <= 2 and a.denominator <= 2
        base = dict(sink_helper=g['sink_helper'], cut_group=g['cut_group'], frame=g['frame'])
        out += [dict(base, target=p, uncompute=[[q, h.numerator, h.denominator]]),
                dict(base, uncompute=[[p, a.numerator, a.denominator]]),
                dict(base, target=p, uncompute=[[q, -h.numerator, h.denominator]])]
    return out
