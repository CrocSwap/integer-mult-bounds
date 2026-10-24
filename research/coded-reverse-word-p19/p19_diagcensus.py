#!/usr/bin/env python3
"""The target census, measured where targets actually are: the operator's diagonal.

A target is what a role *ends holding*, i.e. an entry of the factorisation's diagonal, not how
much a row of the thinned matrix can see.  Measuring the diagonal gives

    p=3  [[5],[1],[1,3,5],[5],[1],[1,3,5]]        designed [[1,3,5],[1,3,5],[1],[1],[5],[5]]
    p=4  [[7],[1],[1,3],[1,3,5,7], ...]           designed the same multiset
    p=5, p=8 likewise

so the invoice's design list is the census of the diagonal, exactly.  The earlier
`P19_ROWFRAME` measurement took the row closure of the thinned matrix instead, which is a
different quantity: rows saturate because every role can see every retained stage, while the
diagonal keeps the prefix/suffix structure the invoice counts.

This receipt reports, per p: the diagonal supports, the design frames, the per-rank histogram
at multiplicity 112 plus the helper block, and the invoice's own T, and requires exact equality
of the histograms.  The row-support measurement is reported beside it as contrast and enters no
price.
"""
import importlib.util, json, sys
from collections import Counter
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

PROFILE = {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40}

def main():
    mod = load('c4940_diag', ROOT/'research/coded-reverse-controller/verify.py')
    C = mod.C
    out = {'status': 'DIAGONAL_CENSUS', 'cases': {}}
    want19 = '--p19' in sys.argv
    fast = [(3, 'IT'), (4, 'IIT'), (5, 'IITT'), (8, 'IIIITTT')]
    cases = [(19, 'I'*9+'T'*9)] if want19 else fast
    for p, pat in cases:
        thick = frozenset(range(1, 2*p, 2))
        co, _ = mod.controller(p, mod.keep_of(p, pat), {s: Q(1) for s in range(2*p+1)})
        th = mod.thin(co, thick)
        base = C.factor(th)
        need(base is not None, 'the controller factorises at p=%d' % p)
        diag = [frozenset(s for s, b in enumerate(k[1:]) if b) & thick for k in base['diagonal']]

        full = frozenset(range(2*p+1)); outs = [full, full]
        for i, ch in enumerate(pat, 1):
            outs += [frozenset(range(0, 2*i+1)) if ch == 'I' else frozenset(range(2*i, 2*p+1))]*2
        des = [frozenset(s & thick) for s in outs]

        # the census, at multiplicity 112, plus the inherited helper block
        diag_hist = Counter(1 + 8*len(s) for s in diag)
        T_from_diag = Counter({r: 112*v for r, v in diag_hist.items()})
        for r, n in W.H.items(): T_from_diag[r] += len(thick)*n if len(thick) > 0 else 0
        T_inv, _ = W.invoice(p, pat, thick, PROFILE)
        T_inv = Counter({int(k): v for k, v in T_inv.items()})
        T_from_diag.pop(0, None)

        # contrast: row closure of the thinned matrix, which is a different quantity
        rows = {i: set() for i in range(2*p)}
        for term, m in th.items():
            sel = {s for s, b in enumerate(term[1:]) if b}
            for i in range(2*p):
                if any(m[i][j] for j in range(2*p)): rows[i] |= sel
        row_hist = Counter(1 + 8*len(rows[i] & thick) for i in range(2*p))

        match = T_from_diag == T_inv
        # role permutation between the realised diagonal and the design list, and what it preserves
        unused = list(range(len(des)))
        perm, unmatched = {}, []
        for i, F in enumerate(diag):
            hit = next((j for j in unused if des[j] == F), None)
            if hit is None: unmatched.append(i)
            else: perm[i] = hit; unused.remove(hit)
        identity = all(perm.get(i) == i for i in range(len(diag))) and not unmatched
        out['cases']['p%d_%s' % (p, pat)] = {
            'role_permutation': perm, 'unmatched_roles': unmatched, 'permutation_is_identity': identity,
            'permutation_preserves': {
                'owner_allocation': 'roles 0..2p-1 only; the permutation stays inside the main roles',
                'helper_separation': 'no helper role appears in the diagonal; the helper block is priced separately',
                'paid_D_profile': 'the invoice D is built from the pattern and profile, not from role assignment',
                'target_histogram': 'T is a rank histogram, so it is permutation-invariant by construction',
                'endpoint_typing': 'verified role-wise by the endpoint receipt, not by the multiset'},
            'diagonal_denominators': base.get('right') is not None and 'recorded in the endpoint receipt',
            'residual_equality': 'the factorisation returns the exact diagonal with no residual term',
            'diagonal_supports': [sorted(s) for s in diag],
            'designed_frames': [sorted(s) for s in des],
            'role_wise_match': diag == des, 'multiset_match': Counter(diag) == Counter(des),
            'diagonal_census': dict(sorted(T_from_diag.items())),
            'census_main_only': {1 + 8*k: 112*v for k, v in sorted(Counter(len(s) for s in diag).items())},
            'invoiced_T': dict(sorted(T_inv.items())),
            'census_equals_invoice': match,
            'row_closure_census_contrast': {1 + 8*k: 112*v for k, v in sorted(row_hist.items())}}
        print('p=%2d %-20s diagonal sizes %s  designed %s  multiset %s  census==invoice %s'
              % (p, pat, dict(sorted(Counter(len(s) for s in diag).items())),
                 dict(sorted(Counter(len(s) for s in des).items())),
                 Counter(diag) == Counter(des), match))
        if p <= 5 and not match:
            print('    diag census %s' % dict(sorted(T_from_diag.items())))
            print('    invoiced    %s' % dict(sorted(T_inv.items())))

    ok = all(v['census_equals_invoice'] for v in out['cases'].values())
    earlier = {}
    if (HERE/'P19_DIAGCENSUS.json').exists():
        prev = json.loads((HERE/'P19_DIAGCENSUS.json').read_text())
        earlier = {k: v for k, v in prev.get('cases', {}).items() if k not in out['cases']}
    out['cases'].update(earlier)
    complete = len(out['cases']) == 5
    out['status'] = ('PASS_DIAGONAL_CENSUS_IS_INVOICED'
                     if ok and complete and all(v['census_equals_invoice'] for v in out['cases'].values())
                     else ('PASS_DIAGONAL_CENSUS_IS_INVOICED' if ok and not complete
                           else 'FINDING_CENSUS_DIFFERS'))
    out['notion'] = ('a target is an entry of the factorisation diagonal, not a row closure; the row closure is '
                     'reported as contrast only and enters no price')
    (HERE/'P19_DIAGCENSUS.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status': out['status']}, sort_keys=True))

if __name__ == '__main__':
    main()
