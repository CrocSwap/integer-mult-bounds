#!/usr/bin/env python3
"""Which step changes a role's target frame: the closing sweep, or the swap?

The invoice counts targets in the designed frame basis: two roles per stage carrying the
prefix up to the stage (I) or the suffix from it (T), plus the two initial full roles.  At
p=19 with I^9 T^9 that is 4 roles at each intermediate size and 2 full-stack roles.

The realised thinned operator has 3 intermediate and 11 full-stack instead.  This receipt
locates the step responsible by rebuilding the word with the closing reversed bridge sweep
and/or the closing signed swap omitted, and measuring each role's frame after each variant.
No operator claim is made about the variants: they exist only to attribute the change.
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

def build(C, mod, p, keep, coupling, sweep=True, swap=True):
    n, stages = 2*p, 2*p+1
    zero = (0,)*(stages+1)
    matrix = [[{zero: 1} if i == j else {} for j in range(n)] for i in range(n)]
    idle = []
    term = lambda q, sel: (q,)+tuple(int(s in sel) for s in range(stages))
    def idle_call(pair, sel, kind):
        retained = bool(keep >> len(idle) & 1)
        idle.append(dict(kind=kind, pair=pair, retained=retained))
        if retained:
            for role in (2*pair, 2*pair+1):
                matrix[role] = [C.monomial_times(x, term(0, sel)) for x in matrix[role]]
    def local(stage, pair, reverse):
        x, y = 2*pair, 2*pair+1
        if reverse: x, y = y, x
        coef = (-1 if reverse else 1)*coupling[stage]
        matrix[y] = [C.plus(a, C.monomial_times(b, term(1 if reverse else -1, []), coef))
                     for a, b in zip(matrix[y], matrix[x])]
        for role in (x, y): matrix[role] = [C.monomial_times(z, term(0, [stage])) for z in matrix[role]]
        if stage % 2 and stage <= 2*p-3: idle_call((stage+1)//2, list(range(stage+1)), 'initial')
        elif stage % 2 == 0 and 2 <= stage <= 2*p-2: idle_call(stage//2, [stage], 'middle')
        elif stage == 2*p:
            for j in range(p-1): idle_call(j, list(range(2*j+3, 2*p+1)), 'terminal')
    def bridge(dst, src, c):
        for d, s, cc in ((2*dst, 2*src, c), (2*src+1, 2*dst+1, -c)):
            matrix[d] = [C.plus(a, b, cc) for a, b in zip(matrix[d], matrix[s])]
    local(0, 0, False)
    for j in range(p):
        local(2*j+1, j, True)
        if j < p-1: bridge(j, j+1, 1)
        local(2*j+2, j, False)
        if j < p-1: bridge(j, j+1, -1)
    if sweep:
        for j in reversed(range(p-1)): bridge(j+1, j, 1)
    if swap:
        for j in range(p):
            matrix[2*j], matrix[2*j+1] = matrix[2*j+1], [C.monomial_times(x, zero, -1) for x in matrix[2*j]]
    co = {}
    for i, row in enumerate(matrix):
        for j, poly in enumerate(row):
            for key, v in poly.items(): co.setdefault(key, [[Q(0)]*n for _ in range(n)])[i][j] += v
    return {k: m for k, m in co.items() if any(any(r) for r in m)}

def frames(mod, th, p, thick):
    rows = {i: set() for i in range(2*p)}
    for term, m in th.items():
        sel = {s for s, bit in enumerate(term[1:]) if bit}
        for i in range(2*p):
            if any(m[i][j] for j in range(2*p)): rows[i] |= sel
    sizes = Counter(len(S & thick) for S in rows.values())
    return dict(sorted(sizes.items())), {1 + 8*k: 112*v for k, v in sorted(sizes.items())}

def main():
    mod = load('c4940_frames', ROOT/'research/coded-reverse-controller/verify.py')
    C = mod.C
    p, pat = 19, 'I'*9+'T'*9
    thick = frozenset(range(1, 2*p, 2))
    keep = mod.keep_of(p, pat)
    coupling = {s: Q(1) for s in range(2*p+1)}

    designed_sizes = Counter()
    full = frozenset(range(2*p+1))
    outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    for s in outs: designed_sizes[len(s & thick)] += 1
    designed = {1 + 8*k: 112*v for k, v in sorted(designed_sizes.items())}
    print('designed  frames %s -> T %s' % (dict(sorted(designed_sizes.items())), designed))

    out = {'designed_frames': dict(sorted(designed_sizes.items())), 'designed_T': designed, 'variants': {}}
    for label, sweep, swap in (('full word', True, True), ('no closing sweep', False, True),
                               ('no sweep, no swap', False, False), ('swap only', True, False)):
        th = mod.thin(build(C, mod, p, keep, coupling, sweep, swap), thick)
        sizes, T = frames(mod, th, p, thick)
        out['variants'][label] = {'frames': sizes, 'T': T, 'T_equals_designed': T == designed}
        print('%-18s frames %s -> T %s   equals designed: %s'
              % (label, sizes, T, T == designed))

    match = [k for k, v in out['variants'].items() if v['T_equals_designed']]
    out['status'] = 'PASS_DESIGN_FRAMES_PRE_SWEEP' if match else 'FINDING_NO_VARIANT_MATCHES_DESIGN'
    out['matching_variants'] = match
    out['attribution'] = ('the closing reversed bridge sweep is the step that widens the frames' if
                          'no closing sweep' in match else
                          'no variant matches; the widening is not attributable to the sweep or the swap alone')
    (HERE/'P19_FRAMES.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status'], 'matching': match}, sort_keys=True))

if __name__ == '__main__':
    main()
