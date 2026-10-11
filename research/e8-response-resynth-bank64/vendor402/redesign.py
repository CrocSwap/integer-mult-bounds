"""Exact value-level re-synthesis of target feeds on a gcert/1 word (own code, new in this package).

A design for target y_i is a list of deliveries (pos, frame, src, coef): the gate ['in', frame, i, [[src, a, b]]] is
inserted after gate pos-1 of the word's A+B list (pos > |A|, so every delivery is in B).  Every original feed gate of
y_i becomes one source-touching empty 'out' marker per source (the same marker #398 uses), so no source walk changes.
A y-sourced delivery (src = y_j, the restore) gets a setup y_i -= coef*y_j at the start of B at frame 0, which cancels
y_j's dirty value and its scatter part; restore minus setup delivers exactly y_j's B-phase prefix."""
import copy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cxkernel import rehist


def build(c, designs):
    v = c['v']; nA = len(c['A']); d = copy.deepcopy(c); at = {}; setups = []
    for i, dl in sorted(designs.items()):
        assert v <= i < 2 * v
        for pos, f, s, q in dl:
            assert nA < pos <= nA + len(c['B']) and q
            at.setdefault(pos, []).append(['in', f, i, [[s, q.numerator, q.denominator]]])
            if v <= s < 2 * v: setups.append(['in', 0, i, [[s, -q.numerator, q.denominator]]])
    B = list(setups)
    for bi, g in enumerate(c['B']):
        if g[0] == 'in' and g[2] in designs: B.extend(['out', g[1], s, [], []] for s, _, _ in g[3])
        else:
            assert not (g[0] == 'out' and any(t in designs for t, _, _ in g[3]))
            B.append(copy.deepcopy(g))
        B.extend(at.get(nA + bi + 1, []))
    d['B'] = B
    return rehist(d)


def to_json(designs):
    return [dict(target=i, deliveries=[[p, f, s, q.numerator, q.denominator] for p, f, s, q in dl]) for i, dl in sorted(designs.items())]


def from_json(js):
    from fractions import Fraction as Q
    return {e['target']: [(p, f, s, Q(a, b)) for p, f, s, a, b in e['deliveries']] for e in js}
