#!/usr/bin/env python3
"""The critical invariant for Route 2: can two-sided monomial factors shrink a row frame?

For M' = L M R with L, R diagonal role-wise monomial factors:

  * left multiplication by l_i scales every entry of row i by the same monomial, so it can
    remove exactly the stages that divide EVERY monomial of the row -- the per-stage minimum
    exponent across the row.  Nothing else.
  * right multiplication by r_j scales column j; monomials in different columns occupy
    different matrix positions, so they can never cancel each other, and within a column
    multiplying by a fixed invertible monomial is injective, so no two monomials can merge.

Hence the row frame of M' is
    frame(M'_i) = (frame(M_i) \\ stages(l_i)) U stages(r_1..r_n)
which is a SUPERSET of frame(M_i) \\ stages(l_i): the frames can only grow or stay, never
shrink below what the common factor allows.

So the achievable row sizes are exactly { |frame(M_i) \\ g_i| : g_i divides every monomial of
row i }.  This receipt computes that set and compares it with the design list.  If the design
sizes are not in it, Route 2 cannot be closed by monomial conjugation of this operator, and no
exhaustive search is needed.
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

def analyse(mod, p, pat):
    thick = frozenset(range(1, 2*p, 2))
    co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
    th = mod.thin(co, thick)
    rows = {}
    for i in range(2*p):
        keys = []
        for term, m in th.items():
            if any(m[i][j] for j in range(2*p)):
                keys.append(tuple(term[1:]))
        need(keys, 'row %d is non-empty' % i)
        frame = {s for k in keys for s, b in enumerate(k) if b} & thick
        mins = tuple(min(k[s] for k in keys) for s in range(len(keys[0])))
        removable = {s for s, v in enumerate(mins) if v >= 1} & thick
        rows[i] = {'frame': sorted(frame), 'removable': sorted(removable),
                   'min_frame': sorted(frame - removable), 'monomials': len(keys)}
    full = frozenset(range(2*p+1)); outs = [full, full]
    for i, ch in enumerate(pat, 1):
        outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
    des = [sorted(s & thick) for s in outs]
    return rows, des, thick

def main():
    mod = load('c4940_invariant', ROOT/'research/coded-reverse-controller/verify.py')
    out = {'status': 'INVARIANT_CHECK', 'cases': {}}
    for p, pat in ((3, 'IT'), (4, 'IIT'), (5, 'IITT')):
        rows, des, thick = analyse(mod, p, pat)
        min_sizes = Counter(len(rows[i]['min_frame']) for i in range(2*p))
        des_sizes = Counter(len(s) for s in des)
        realised_sizes = Counter(len(rows[i]['frame']) for i in range(2*p))
        print('p=%d %-4s realised %s | smallest achievable %s | designed %s'
              % (p, pat, dict(sorted(realised_sizes.items())), dict(sorted(min_sizes.items())),
                 dict(sorted(des_sizes.items()))))
        for i in range(2*p):
            print('   role %d frame %s removable %s -> min %s (designed %s)'
                  % (i, rows[i]['frame'], rows[i]['removable'], rows[i]['min_frame'], des[i]))
        # the design sizes must be individually achievable, per role, and as a multiset
        reachable = all(len(rows[i]['min_frame']) <= len(des[i]) for i in range(2*p))
        multiset = dict(sorted(min_sizes.items())) == dict(sorted(des_sizes.items()))
        out['cases']['p%d_%s' % (p, pat)] = {
            'realised_sizes': dict(sorted(realised_sizes.items())),
            'smallest_achievable_sizes': dict(sorted(min_sizes.items())),
            'designed_sizes': dict(sorted(des_sizes.items())),
            'per_role_design_size_reachable_or_above': reachable,
            'multiset_matches_at_the_minimum': multiset,
            'rows': {str(i): rows[i] for i in range(2*p)}, 'designed': des}
        print('   per-role design sizes reachable: %s | multiset matches at the minimum: %s\n'
              % (reachable, multiset))

    all_multiset = all(v['multiset_matches_at_the_minimum'] for v in out['cases'].values())
    out['verdict'] = ('a two-sided monomial conjugation can only shrink a row by the monomial common to every '
                      'monomial of that row, and can otherwise only widen; the smallest achievable multiset is '
                      'recorded above, and it %s the design multiset' % ('matches' if all_multiset else 'does not match'))
    out['consequence'] = ('if the smallest achievable multiset does not equal the design multiset, no L, R exist and '
                          'Route 2 is closed for this operator family without any search')
    (HERE/'P19_INVARIANT.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(out['verdict'])
    print(json.dumps({'multiset_matches': all_multiset}, sort_keys=True))

if __name__ == '__main__':
    main()
