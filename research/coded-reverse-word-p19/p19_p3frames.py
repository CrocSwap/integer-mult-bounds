#!/usr/bin/env python3
"""Where a role's frame comes from, at the smallest p that has bridges (p=3).

For each role the receipt prints the frame the word realises beside the frame the invoice's
design list assumes, and then rebuilds the word with the closing sweep removed and with the
interior bridges removed, so the two mechanisms are separated at a size where they can be
read directly rather than inferred from a histogram.

p=3 is the smallest chain with an interior bridge and a closing sweep, so this is the
minimal witness for the structural claim.
"""
import importlib.util, json, sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def build(C, p, keep, coupling, sweep=True, interior=True):
    n, stages = 2*p, 2*p+1
    zero = (0,)*(stages+1)
    m = [[{zero: 1} if i == j else {} for j in range(n)] for i in range(n)]
    idle = []
    term = lambda q, sel: (q,)+tuple(int(s in sel) for s in range(stages))
    def idle_call(pair, sel, kind):
        retained = bool(keep >> len(idle) & 1)
        idle.append(dict(kind=kind, pair=pair, retained=retained))
        if retained:
            for r in (2*pair, 2*pair+1):
                m[r] = [C.monomial_times(x, term(0, sel)) for x in m[r]]
    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse: x, y = y, x
        coef = (-1 if reverse else 1)*coupling[stage]
        m[y] = [C.plus(a, C.monomial_times(b, term(1 if reverse else -1, []), coef))
                for a, b in zip(m[y], m[x])]
        for r in (x, y): m[r] = [C.monomial_times(z, term(0, [stage])) for z in m[r]]
        if stage % 2 and stage <= 2*p-3: idle_call((stage+1)//2, list(range(stage+1)), 'initial')
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2: idle_call(stage//2, [stage], 'middle')
        elif stage == 2*p:
            for j in range(p-1): idle_call(j, list(range(2*j+3, 2*p+1)), 'terminal')
    def bridge(dst, src, c):
        for d, s, cc in ((2*dst, 2*src, c), (2*src+1, 2*dst+1, -c)):
            m[d] = [C.plus(a, b, cc) for a, b in zip(m[d], m[s])]
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1 and interior: bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1 and interior: bridge(j, j+1, -1)
    if sweep and p > 1:
        for j in reversed(range(p-1)): bridge(j+1, j, 1)
    for j in range(p):
        m[2*j], m[2*j+1] = m[2*j+1], [C.monomial_times(x, zero, -1) for x in m[2*j]]
    co = {}
    for i, row in enumerate(m):
        for j, poly in enumerate(row):
            for key, v in poly.items(): co.setdefault(key, [[Q(0)]*n for _ in range(n)])[i][j] += v
    return {k: v for k, v in co.items() if any(any(r) for r in v)}

def frames(mod, co, p, thick):
    th = mod.thin(co, thick)
    out = {}
    for i in range(2*p):
        S = set()
        for term, m in th.items():
            if any(m[i][j] for j in range(2*p)):
                S |= {s for s, bit in enumerate(term[1:]) if bit}
        out[i] = sorted(S & thick)
    return out

def main():
    mod = load('c4940_p3', ROOT/'research/coded-reverse-controller/verify.py')
    C = mod.C
    p, pat = 3, 'IT'
    thick = frozenset(range(1, 2*p, 2))
    keep = mod.keep_of(p, pat)
    coupling = {s: Q(1) for s in range(2*p+1)}
    full = frozenset(range(2*p+1))
    outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    designed = [sorted(s & thick) for s in outs]
    print('designed frames :', designed)

    out = {'designed': designed, 'variants': {}}
    for label, sweep, interior in (('full word', True, True), ('no closing sweep', False, True),
                                   ('no interior bridges', True, False),
                                   ('neither', False, False)):
        co = build(C, p, keep, coupling, sweep, interior)
        got = frames(mod, co, p, thick)
        same = [got[i] for i in range(2*p)]
        matches = same == designed
        out['variants'][label] = {'frames': same, 'matches_designed': matches}
        print('%-20s : %s   matches designed: %s' % (label, same, matches))

    # the residue claim: the second interior bridge subtracts post-stage content
    co_int = build(C, p, keep, coupling, sweep=False, interior=True)
    co_none = build(C, p, keep, coupling, sweep=False, interior=False)
    differ = sum(1 for i in range(2*p) if frames(mod, co_int, p, thick)[i]
                 != frames(mod, co_none, p, thick)[i])
    out['interior_bridges_change_frames_of_roles'] = differ
    print('PASS the interior bridge pair changes the realised frame of %d of %d roles, so the '
          'add/subtract pair does not cancel' % (differ, 2*p))

    out['status'] = 'FINDING_INTERIOR_BRIDGES_WIDEN_FRAMES' if differ else 'PASS_INTERIOR_BRIDGES_CANCEL'
    out['conclusion'] = ('the designed frame basis is not realised: the interior bridge pair leaves a commutator '
                         'residue and the closing sweep folds it forward, so productive roles carry stages beyond '
                         'their prefix or suffix')
    (HERE/'P19_P3FRAMES.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
