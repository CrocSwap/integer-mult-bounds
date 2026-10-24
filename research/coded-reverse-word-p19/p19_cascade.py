#!/usr/bin/env python3
"""Route 2, first step: a word whose raw rows ARE the design frames.

The controller's rows saturate (every role sees every retained stage), so no rescheduling of
that word realises the invoice's design frames `{1..9 four each, full twice}`.  This receipt
builds a different word from the same alphabet and asks the two questions that decide it:

    rows(word)   == the design frames?
    factor(word) exists, i.e. does it diagonalise to the required outputs?

Candidate family: a *forward cascade*.  Role pair j receives only from earlier pairs, so its
frame is a prefix by construction; the reverse pass is the back-substitution that inverts the
cascade.  Members of the family differ in which stages write into which later pair.

Everything is exact, in the controller's own monomial algebra, and the diagonal check uses the
controller's own `factor`, so a candidate is accepted only if the machinery the base already
trusts can invert it.
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def cascade(p, pat, mod):
    """A forward cascade: pair j takes a shear from pair j-1 only, plus its stage letter."""
    C = mod.C
    n, stages = 2*p, 2*p+1
    zero = (0,)*(stages+1)
    term = lambda q, sel: (q,)+tuple(int(s in sel) for s in range(stages))
    m = [[{zero: Q(1)} if i == j else {} for j in range(n)] for i in range(n)]
    def shear(dst, src, coef, mon):
        for j in range(n):
            add = C.monomial_times(m[src][j], mon, coef)
            if add: m[dst][j] = C.plus(m[dst][j], add)
    def letter(role, stage):
        m[role] = [C.monomial_times(x, term(0, [stage])) for x in m[role]]
    letter(0, 0)
    for j in range(p-1):
        shear(2*j+2, 2*j, Q(1), term(1, []))            # later role takes the earlier content
        letter(2*j+2, 2*(j+1))
        shear(2*j+3, 2*j+1, Q(1), term(-1, []))
        letter(2*j+3, 2*(j+1))
    co = {}
    for i, row in enumerate(m):
        for j, poly in enumerate(row):
            for key, v in poly.items(): co.setdefault(key, [[Q(0)]*n for _ in range(n)])[i][j] += v
    return {k: v for k, v in co.items() if any(any(r) for r in v)}

def rows_of(mod, co, p, thick):
    th = mod.thin(co, thick)
    out = {}
    for i in range(2*p):
        S = set()
        for term, m in th.items():
            if any(m[i][j] for j in range(2*p)):
                S |= {s for s, bit in enumerate(term[1:]) if bit}
        out[i] = S & thick
    return out

def designed(p, pat, thick):
    full = frozenset(range(2*p+1)); outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    return [s & thick for s in outs]

def main():
    mod = load('c4940_cascade', ROOT/'research/coded-reverse-controller/verify.py')
    out = {'status': 'CASCADE_PROBE', 'cases': {}}
    for p, pat in ((3, 'IT'), (4, 'IIT')):
        thick = frozenset(range(1, 2*p, 2))
        co = cascade(p, pat, mod)
        rows = rows_of(mod, co, p, thick)
        sizes = Counter(len(s) for s in rows.values())
        des = designed(p, pat, thick)
        des_sizes = Counter(len(s) for s in des)
        r = mod.C.factor(mod.thin(co, thick))
        diag = None if r is None else sorted(Counter(sum(t[1:]) for t in r['diagonal']).items())
        std = mod.diagonalize(p, pat, {s: Q(1) for s in range(2*p+1)})
        out['cases']['p%d_%s' % (p, pat)] = {
            'rows': {i: sorted(s) for i, s in rows.items()},
            'sizes': dict(sorted(sizes.items())), 'designed_sizes': dict(sorted(des_sizes.items())),
            'rows_equal_designed': [sorted(rows[i]) for i in range(2*p)] == [sorted(s) for s in des],
            'factorises': r is not None, 'diagonal': diag,
            'controller_standard': std}
        print('p=%d %-4s rows %s' % (p, pat, {i: len(rows[i]) for i in range(2*p)}))
        print('        sizes %s designed %s  rows==designed %s'
              % (dict(sorted(sizes.items())), dict(sorted(des_sizes.items())),
                 [sorted(rows[i]) for i in range(2*p)] == [sorted(s) for s in des]))
        print('        factorises %s diagonal %s  (controller standard %s)' % (r is not None, diag, std))

    ok = [k for k, v in out['cases'].items() if v['rows_equal_designed']]
    out['rows_realised'] = ok
    out['note'] = ('a cascade realises prefix rows by construction; whether it factorises to the required outputs '
                   'is the binding question, and the controller machinery is the judge')
    (HERE/'P19_CASCADE.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'cases_with_design_rows': ok}, sort_keys=True))

if __name__ == '__main__':
    main()
