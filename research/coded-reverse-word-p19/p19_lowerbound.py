#!/usr/bin/env python3
"""Route 2 lower bound: can independent scalar rows realise the design frames at all?

For M_new = T D T^-1 the coefficient of the monomial d_k is the rank-one matrix
(column k of T) x (row k of T^-1), so row i of that coefficient is nonzero exactly when
T_ik is nonzero.  Hence

    frame(row i of M_new) = union of stages(d_k) over { k : T_ik != 0 }

and the only monomials a row may use without widening its frame are those whose support lies
inside the target frame.  Two rows with the same frame must therefore be independent
combinations of the monomials available inside that frame.

This receipt computes, per p, how many diagonal monomials lie inside each design frame.  If a
design frame has fewer available monomials than the number of rows that need it, the rows are
forced to be proportional and T is singular: no T exists, and the route closes without a
search.
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

def main():
    mod = load('c4940_lb', ROOT/'research/coded-reverse-controller/verify.py')
    C = mod.C
    out = {'status': 'DESIGN_FRAME_LOWER_BOUND', 'cases': {}}
    for p, pat in ((3, 'IT'), (4, 'IIT'), (5, 'IITT')):
        thick = frozenset(range(1, 2*p, 2))
        co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
        base = C.factor(mod.thin(co, thick))
        need(base is not None, 'controller factorises at p=%d' % p)
        D_list = base['diagonal']
        d_supp = [{s for s, b in enumerate(k[1:]) if b} & thick for k in D_list]

        full = frozenset(range(2*p+1)); outs = [full, full]
        for i, ch in enumerate(pat, 1):
            outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
        des = [s & thick for s in outs]

        need_for = Counter(frozenset(f) for f in des)
        available = {F: [k for k, s in enumerate(d_supp) if s <= F] for F in need_for}
        feasible = {str(sorted(F)): {'rows_needing_it': n, 'monomials_inside': len(available[F]),
                                     'independent_rows_possible': len(available[F]) >= n}
                    for F, n in need_for.items()}
        ok = all(v['independent_rows_possible'] for v in feasible.values())
        print('p=%d %-4s diagonal monomial supports %s' % (p, pat, [sorted(s) for s in d_supp]))
        for F, v in feasible.items():
            print('     frame %s: %d rows need it, %d diagonal monomials lie inside  %s'
                  % (sorted(F), v['rows_needing_it'], v['monomials_inside'],
                     'ok' if v['independent_rows_possible'] else 'IMPOSSIBLE'))
        out['cases']['p%d_%s' % (p, pat)] = {'diagonal_supports': [sorted(s) for s in d_supp],
                                             'feasibility': feasible, 'feasible': ok}
        print('     => independent T exists: %s\n' % ok)

    allok = all(v['feasible'] for v in out['cases'].values())
    out['status'] = 'PASS_T_FEASIBLE' if allok else 'CLOSED_NO_INDEPENDENT_T'
    out['consequence'] = ('if every design frame has at least as many inside monomials as rows needing it, a T exists '
                          'in principle and the question becomes cost; otherwise no T exists at all and the route is '
                          'closed')
    (HERE/'P19_LOWERBOUND.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
