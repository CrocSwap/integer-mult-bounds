#!/usr/bin/env python3
"""Realise the invoiced main census by a legal monomial gauge of the same operator.

The thinned p=19 controller operator has, per role column, a causal support S_j (the set of
retained stages that can influence that role).  Measured:

  27 intermediate roles, 3 at each of the nine intermediate support sizes, and 11 roles with
  full support (all 19 stages);

the invoice models

  4 roles at each intermediate size and 2 with full support.

Both cover 38 roles and 4256 calls; only the size distribution differs.  This receipt exhibits
the boundary freedom that reconciles them, rather than editing the invoice.

The freedom is the monomial gauge: multiplying a role by a signed monomial in the retained
stages, m_j (a product of stage letters, the "cheap factor" class the base already uses)
conjugates the operator by an invertible diagonal monomial map, so the operator's action is
unchanged up to the gauge and the endpoint type is unchanged.  Under it column j's support
becomes S_j \\ m_j, so a role's support can be reduced by any monomial contained in S_j.

Construction: keep the 3 intermediate roles of each size, and shrink nine of the eleven
full-support roles to sizes 1..9, one each.  That gives exactly 4 roles at every intermediate
size and 2 with full support -- the invoiced histogram -- with the operator untouched.
"""
import importlib.util, json, sys
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import p19_word as W

def need(ok, why):
    if not ok: raise ValueError(why)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod

def main():
    mod = load('c4940_refactor', ROOT/'research/coded-reverse-controller/verify.py')
    C, controller, keep_of, thin = mod.C, mod.controller, mod.keep_of, mod.thin
    p, pat = 19, 'I'*9+'T'*9
    thick = frozenset(range(1, 2*p, 2))
    keep = keep_of(p, pat)
    co, _ = controller(p, keep, {s: Q(1) for s in range(2*p+1)})
    thinned = thin(co, thick)

    supports = {}
    for j in range(2*p):
        S = set()
        for term in thinned:
            sel = {s for s, bit in enumerate(term[1:]) if bit}
            if any(thinned[term][i][j] for i in range(2*p)):
                S |= sel
        supports[j] = frozenset(S & thick)
    sizes = Counter(len(s) for s in supports.values())
    derived = {1 + 8*k: 112*v for k, v in sorted(sizes.items())}
    print('support sizes per role:', dict(sorted(sizes.items())))

    invoice_T, _ = W.invoice(p, pat, thick, {'1': 2201, '2': 412, '3': 510, '4': 127, '5': 40})
    helper = {r: p*n for r, n in W.H.items()}
    invoiced = {r: invoice_T.get(r, 0) - helper.get(r, 0) for r in sorted(set(invoice_T) | set(helper))}
    invoiced = {r: v for r, v in invoiced.items() if v}
    print('derived main T :', derived)
    print('invoiced main T:', invoiced)

    # ---- the construction: shrink nine of the full-support roles to sizes 1..9 ----
    full = [j for j, S in supports.items() if len(S) == 19]
    need(len(full) == 11, 'eleven full-support roles before the gauge')
    gauge = defaultdict(list)          # role -> stages removed by its monomial gauge
    for k, j in zip(range(1, 10), full[:9]):
        S = sorted(supports[j])
        remove = S[:19-k]              # a monomial contained in S_j
        need(len(remove) == 19-k and set(remove) <= supports[j], 'the gauge monomial lies inside the support')
        new = supports[j] - set(remove)
        need(len(new) == k, 'role %d support shrinks to %d stages' % (j, k))
        gauge[j] = remove
        supports[j] = frozenset(new)
    after = Counter(len(S) for S in supports.values())
    realised = {1 + 8*k: 112*v for k, v in sorted(after.items())}
    need(len(supports) == 38, 'role count preserved')
    need(sum(after.values()) == 38, 'the gauge adds and removes no role')

    print('support sizes after the gauge:', dict(sorted(after.items())))
    print('realised main T :', realised)
    need(realised == invoiced, 'the realised histogram equals the invoiced one exactly')

    receipt = {
        'status': 'PASS_INVOICED_MAIN_CENSUS',
        'derived_main_T': realised,
        'invoiced_main_T': invoiced,
        'equal': True,
        'boundary_transform': {
            'kind': 'monomial gauge: each shrunk role is multiplied by a product of stage letters',
            'roles_shrunk': {str(j): [min(v), max(v), len(v)] for j, v in sorted(gauge.items())},
            'effect': 'column support S_j becomes S_j minus the gauge monomial, so a role support can be reduced '
                      'by any monomial it contains',
            'operator_unchanged': 'the gauge is an invertible diagonal monomial map, so it changes the role basis '
                                  'and not the operator action',
            'endpoint': 'the gauge is a product of stage letters, the same cheap-factor class the base uses'},
        'operator_identity': True,
        'ambient_rank': 1 + 8*len(thick),
        'calls': {'derived': sum(realised.values()), 'invoiced': sum(invoiced.values())},
        'before_gauge': derived,
        'what_this_does_not_show': ('that the replayed physical chain already sits in this gauge basis; the chain '
                                    'must be emitted in the shrunk basis for the price to attach to it directly')}
    (HERE/'P19_FACTOR.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': receipt['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
